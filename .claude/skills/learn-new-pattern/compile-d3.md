# Compile pattern.json to D3.js HTML

Guide for translating a `pattern.json` declarative definition into a self-contained D3.js v7 HTML file.

## Output Format

The output must be a single `.html` file that:
- Loads D3.js v7 from CDN (`https://d3js.org/d3.v7.min.js`)
- Contains all rendering code inline in a `<script>` tag
- Creates an SVG element with dimensions from `canvas.width` and `canvas.height`
- Renders the pattern centered in the SVG
- Has NO external dependencies beyond D3 CDN
- Uses NO ES6 template literals (use string concatenation or `+` operator)
- Embeds any images as base64 data URIs
- Works when opened directly as a `file:///` URL

## HTML Template

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{pattern.name}</title>
    <style>
        body {
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: #111;
        }
    </style>
</head>
<body>
    <div id="pattern"></div>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script>
        // === Pattern Definition ===
        var config = {/* inline pattern.json values */};

        // === Rendering Code ===
        var width = config.canvas.width;
        var height = config.canvas.height;
        var cx = width / 2;
        var cy = height / 2;
        var scale = Math.min(width, height) / 2;

        var svg = d3.select('#pattern')
            .append('svg')
            .attr('width', width)
            .attr('height', height);

        // Background
        svg.append('rect')
            .attr('width', width)
            .attr('height', height)
            .attr('fill', config.canvas.background);

        // ... layer rendering code ...
    </script>
</body>
</html>
```

## Coordinate Mapping

Pattern.json uses normalized coordinates. Map them to SVG pixels:

```javascript
// Convert normalized coords to SVG pixels
function px(normalizedX) { return cx + normalizedX * scale; }
function py(normalizedY) { return cy - normalizedY * scale; } // Y-axis flipped
function pr(normalizedR) { return normalizedR * scale; }       // radius scaling

// Convert angle to radians (pattern.json uses degrees)
function toRad(degrees) { return degrees * Math.PI / 180; }
```

### Pi-Based Angle Computation

**Always compute angles from `n` and `pi` directly** — never hardcode degree values:

```javascript
// Preferred: derive from n and pi
var sector = 2 * Math.PI / n;         // full sector angle
var halfSector = Math.PI / n;          // half sector
var skipAngle = Math.PI * k / n;       // {n/k} star polygon skip

// Anti-pattern: hardcoded degrees
var sector = toRad(36);                // DON'T — hides the relationship to n=10
var halfSector = toRad(18);            // DON'T — what if n changes?
```

**Derive radii from trigonometry, not decimals:**

```javascript
// Preferred: trigonometric derivation
var rMid = R * Math.cos(Math.PI * k / n);
var rInner = R * Math.cos(Math.PI * k / n) / Math.cos(Math.PI / n);

// Anti-pattern: magic decimals
var rMid = R * 0.625;                 // DON'T — where does 0.625 come from?
var rInner = R * 0.333;               // DON'T — not self-documenting
```

**For polar point calculations**, use the sector directly:

```javascript
function polarPt(r, sectorIndex) {
    var angle = sectorIndex * sector - Math.PI / 2;  // -pi/2 rotates 0 to top
    return [cx + r * Math.cos(angle), cy + r * Math.sin(angle)];
}
```

When degree values ARE needed (e.g., for SVG `rotate()` transforms), compute them from pi:
```javascript
var rotDeg = (i * 360 / n);           // OK — derived from n
var rotDeg = (i * sector) * 180 / Math.PI;  // Also OK — from sector
```

### Partial Shape Rendering with Clip Paths

Many shapes in Islamic patterns are FRAGMENTS of regular polygons — a hexagon might only show 3 visible sides because the rest is behind a rosette. Render partial shapes using SVG clip paths:

```javascript
// Render a shape clipped to a region
function renderClipped(target, clipId, renderFn) {
    var g = target.append('g').attr('clip-path', 'url(#' + clipId + ')');
    renderFn(g);
}

// Define clip regions in <defs>
// Circle clip — shows only what's inside a circle
defs.append('clipPath').attr('id', 'inner-zone')
    .append('circle').attr('cx', cx).attr('cy', cy).attr('r', pr(0.48));

// Sector clip — shows only a wedge
// Use a polygon approximating the sector arc
function sectorClipPath(cx, cy, r, startDeg, endDeg) {
    var pts = [[cx, cy]];
    for (var a = startDeg; a <= endDeg; a += 1) {
        var rad = (a - 90) * Math.PI / 180;
        pts.push([cx + r * Math.cos(rad), cy + r * Math.sin(rad)]);
    }
    return pts.map(function(p) { return p[0] + ',' + p[1]; }).join(' ');
}

// Exclusion clip — shows everything EXCEPT a region
// Use clip-rule="evenodd" with a surrounding rect and the excluded shape
```

When a layer has a `clip` property, wrap its rendering in a clipped group. This is how fragments of hexagons, pentagons, or other regular polygons at the medallion boundary are rendered — draw the full shape, clip to the visible region.

### Negative Space Rendering

Some shapes in a pattern are NOT drawn — they are the background visible through gaps between overlapping elements. Render negative space by:

1. Drawing the background color first (e.g., dark navy circle)
2. Drawing colored tiles on top (these are the EXPLICIT shapes)
3. Drawing strapwork bands on top of tiles
4. Everything NOT covered by tiles or bands shows the background — these are the negative space shapes

Do NOT create explicit tile polygons for dark regions between white strapwork bands. Those are negative space.

## Layer Compilation

Process layers in array order (first = bottom/background, last = top/foreground).

### `star-polygon`

```javascript
function renderStarPolygon(svg, params, style) {
    var n = params.n;
    var k = params.k;
    var centerX = px(params.center ? params.center[0] : 0);
    var centerY = py(params.center ? params.center[1] : 0);
    var radius = pr(params.radius);
    var rotation = toRad(params.rotation || 0);

    // Generate n vertices
    var vertices = [];
    for (var i = 0; i < n; i++) {
        var angle = rotation + (2 * Math.PI * i / n) - Math.PI / 2;
        vertices.push([
            centerX + radius * Math.cos(angle),
            centerY + radius * Math.sin(angle)
        ]);
    }

    // Connect every k-th vertex
    var pathData = '';
    for (var i = 0; i < n; i++) {
        var from = vertices[i];
        var to = vertices[(i + k) % n];
        pathData += 'M' + from[0] + ',' + from[1] + 'L' + to[0] + ',' + to[1];
    }

    svg.append('path')
        .attr('d', pathData)
        .attr('stroke', resolveColor(style.stroke))
        .attr('stroke-width', style['stroke-width'] || 1)
        .attr('fill', style.fill === 'none' ? 'none' : resolveColor(style.fill))
        .attr('opacity', style.opacity || 1);
}
```

### `polygon`

```javascript
function renderPolygon(svg, params, style) {
    var sides = params.sides;
    var centerX = px(params.center ? params.center[0] : 0);
    var centerY = py(params.center ? params.center[1] : 0);
    var radius = pr(params.radius);
    var rotation = toRad(params.rotation || 0);

    var points = [];
    for (var i = 0; i < sides; i++) {
        var angle = rotation + (2 * Math.PI * i / sides) - Math.PI / 2;
        points.push(centerX + radius * Math.cos(angle) + ',' +
                    (centerY + radius * Math.sin(angle)));
    }

    svg.append('polygon')
        .attr('points', points.join(' '))
        .attr('stroke', resolveColor(style.stroke))
        .attr('stroke-width', style['stroke-width'] || 1)
        .attr('fill', style.fill === 'none' ? 'none' : resolveColor(style.fill));
}
```

### `circle` / `circle-ring`

```javascript
function renderCircle(svg, params, style) {
    svg.append('circle')
        .attr('cx', px(params.center ? params.center[0] : 0))
        .attr('cy', py(params.center ? params.center[1] : 0))
        .attr('r', pr(params.radius))
        .attr('stroke', resolveColor(style.stroke))
        .attr('stroke-width', style['stroke-width'] || 1)
        .attr('fill', style.fill === 'none' ? 'none' : resolveColor(style.fill));
}
```

### `radial-repeat`

```javascript
function renderRadialRepeat(svg, params, element) {
    var count = params.count;
    var radius = pr(params.radius);
    var rotationOffset = toRad(params.rotation_offset || 0);
    var rotateElements = params.rotate_elements !== false;

    for (var i = 0; i < count; i++) {
        var angle = rotationOffset + (2 * Math.PI * i / count);
        var elemCenterX = cx + radius * Math.cos(angle - Math.PI / 2);
        var elemCenterY = cy + radius * Math.sin(angle - Math.PI / 2);

        // Create a group translated and optionally rotated
        var g = svg.append('g');
        if (rotateElements) {
            g.attr('transform',
                'translate(' + elemCenterX + ',' + elemCenterY + ') ' +
                'rotate(' + (i * 360 / count + (params.rotation_offset || 0)) + ')');
        } else {
            g.attr('transform', 'translate(' + elemCenterX + ',' + elemCenterY + ')');
        }

        // Render the element within the group (center at 0,0)
        renderLayer(g, element, true); // true = local coords
    }
}
```

### `rosette`

```javascript
function renderRosette(svg, params, style) {
    var n = params.n;
    var centerX = px(params.center ? params.center[0] : 0);
    var centerY = py(params.center ? params.center[1] : 0);
    var innerR = pr(params.inner_radius);
    var outerR = pr(params.outer_radius);
    var rotation = toRad(params.rotation || 0);
    var petalShape = params.petal_shape || 'pointed';

    if (petalShape === 'pointed') {
        // Alternating inner/outer points
        var points = [];
        for (var i = 0; i < n; i++) {
            var outerAngle = rotation + (2 * Math.PI * i / n) - Math.PI / 2;
            var innerAngle = rotation + (2 * Math.PI * (i + 0.5) / n) - Math.PI / 2;
            points.push(centerX + outerR * Math.cos(outerAngle) + ',' +
                        (centerY + outerR * Math.sin(outerAngle)));
            points.push(centerX + innerR * Math.cos(innerAngle) + ',' +
                        (centerY + innerR * Math.sin(innerAngle)));
        }
        svg.append('polygon')
            .attr('points', points.join(' '))
            .attr('stroke', resolveColor(style.stroke))
            .attr('stroke-width', style['stroke-width'] || 1)
            .attr('fill', style.fill === 'none' ? 'none' : resolveColor(style.fill));
    }
    // For 'rounded' and 'ogee', use SVG path with bezier curves
}
```

### `line`

```javascript
function renderLine(svg, params, style) {
    svg.append('line')
        .attr('x1', px(params.from[0]))
        .attr('y1', py(params.from[1]))
        .attr('x2', px(params.to[0]))
        .attr('y2', py(params.to[1]))
        .attr('stroke', resolveColor(style.stroke))
        .attr('stroke-width', style['stroke-width'] || 1)
        .attr('opacity', style.opacity || 1);
}
```

### `flower-of-life`

```javascript
function renderFlowerOfLife(svg, params, style) {
    var centerX = px(params.center ? params.center[0] : 0);
    var centerY = py(params.center ? params.center[1] : 0);
    var radius = pr(params.radius);
    var levels = params.levels || 2;

    // Recursive surrounding circles
    var circles = {};
    function addCircle(x, y, r, level) {
        var key = Math.round(x) + ':' + Math.round(y) + ':' + r;
        if (circles[key] || level > levels) return;
        circles[key] = { x: x, y: y, r: r, level: level };
        if (level < levels) {
            for (var i = 0; i < 6; i++) {
                var angle = (Math.PI / 3) * i;
                addCircle(x + r * Math.cos(angle), y + r * Math.sin(angle), r, level + 1);
            }
        }
    }
    addCircle(centerX, centerY, radius, 0);

    Object.values(circles).forEach(function(c) {
        svg.append('circle')
            .attr('cx', c.x).attr('cy', c.y).attr('r', c.r)
            .attr('stroke', resolveColor(style.stroke))
            .attr('stroke-width', style['stroke-width'] || 1)
            .attr('fill', 'none');
    });
}
```

### `radial-gradient-fill`

```javascript
function renderRadialGradientFill(svg, params) {
    var defs = svg.select('defs').empty() ? svg.append('defs') : svg.select('defs');
    var gradId = 'radial-grad-' + Math.random().toString(36).substr(2, 6);

    var grad = defs.append('radialGradient')
        .attr('id', gradId)
        .attr('cx', '50%').attr('cy', '50%').attr('r', '50%');

    params.stops.forEach(function(stop) {
        grad.append('stop')
            .attr('offset', (stop.offset * 100) + '%')
            .attr('stop-color', resolveColor(stop.color));
    });

    // Apply gradient to a full-canvas rect behind existing content
    svg.insert('rect', ':first-child')
        .attr('width', width).attr('height', height)
        .attr('fill', 'url(#' + gradId + ')');
}
```

### `star-tiling`

```javascript
function renderStarTiling(svg, params, style) {
    var n = params.n;
    var centerX = px(params.center ? params.center[0] : 0);
    var centerY = py(params.center ? params.center[1] : 0);
    var rOuter = pr(params.radius);
    var rMid = rOuter * (params.r_mid_ratio || 0.625);
    var rInner = rOuter * (params.r_inner_ratio || 0.333);
    var rotation = params.rotation || 0;
    var step = 360 / n;
    var halfStep = step / 2;
    var sw = (style && style['stroke-width']) || 8;
    var strokeColor = resolveColor(style && style.stroke ? style.stroke : '#FFFFFF');

    function polarPt(r, deg) {
        var a = (deg + rotation - 90) * Math.PI / 180;
        return [centerX + r * Math.cos(a), centerY + r * Math.sin(a)];
    }

    function drawPoly(pts, fill) {
        svg.append('polygon')
            .attr('points', pts.map(function(p) { return p[0] + ',' + p[1]; }).join(' '))
            .attr('fill', resolveColor(fill))
            .attr('stroke', strokeColor)
            .attr('stroke-width', sw)
            .attr('stroke-linejoin', 'round');
    }

    // n kite tiles (star points)
    for (var i = 0; i < n; i++) {
        var a = i * step;
        drawPoly([
            polarPt(rOuter, a),
            polarPt(rMid, a + halfStep),
            polarPt(rInner, a),
            polarPt(rMid, a - halfStep)
        ], params.kite_colors[i]);
    }

    // n inner rhombus tiles (between star points)
    for (var i = 0; i < n; i++) {
        var a = i * step + halfStep;
        drawPoly([
            polarPt(rMid, a),
            polarPt(rInner, a + halfStep),
            polarPt(rInner * 0.55, a),
            polarPt(rInner, a - halfStep)
        ], params.rhombus_colors[i]);
    }

    // Central concave star (alternating inner/outer points)
    var darkStarPts = [];
    for (var i = 0; i < n; i++) {
        darkStarPts.push(polarPt(rInner * 0.6, i * step + halfStep));
        darkStarPts.push(polarPt(rInner, i * step));
    }
    drawPoly(darkStarPts, params.center_color || '$darkNavy');

    // Center decagon
    var centerPts = [];
    for (var i = 0; i < n; i++) {
        centerPts.push(polarPt(rInner * 0.48, i * step));
    }
    drawPoly(centerPts, params.center_color || '$darkNavy');
}
```

### `filled-rosette`

```javascript
function renderFilledRosette(svg, params, style) {
    var n = params.n;
    var centerX = px(params.center ? params.center[0] : 0);
    var centerY = py(params.center ? params.center[1] : 0);
    var radius = pr(params.radius);
    var rotation = params.rotation || 0;
    var step = 360 / n;
    var sepWidth = params.separation_width || 3;
    var coreRatio = params.center_star_radius_ratio || 0.25;
    var coreR = radius * coreRatio;

    function polarPt(r, deg) {
        var a = (deg + rotation - 90) * Math.PI / 180;
        return [centerX + r * Math.cos(a), centerY + r * Math.sin(a)];
    }

    // 1. Solid filled n-gon body
    var bodyPts = [];
    for (var i = 0; i < n; i++) {
        bodyPts.push(polarPt(radius, i * step));
    }
    svg.append('polygon')
        .attr('points', bodyPts.map(function(p) { return p[0] + ',' + p[1]; }).join(' '))
        .attr('fill', resolveColor(params.fill_color))
        .attr('stroke', 'none');

    // 2. Petal separation lines (radial lines from center to edge)
    var sepColor = resolveColor(params.separation_color || '$white');
    for (var i = 0; i < n; i++) {
        var a = i * step + step / 2; // between vertices
        var inner = polarPt(coreR * 0.8, a);
        var outer = polarPt(radius, a);
        svg.append('line')
            .attr('x1', inner[0]).attr('y1', inner[1])
            .attr('x2', outer[0]).attr('y2', outer[1])
            .attr('stroke', sepColor)
            .attr('stroke-width', sepWidth)
            .attr('stroke-linecap', 'round');
    }

    // 3. Small central n-pointed star
    var starPts = [];
    for (var i = 0; i < n; i++) {
        starPts.push(polarPt(coreR, i * step));
        starPts.push(polarPt(coreR * 0.4, i * step + step / 2));
    }
    svg.append('polygon')
        .attr('points', starPts.map(function(p) { return p[0] + ',' + p[1]; }).join(' '))
        .attr('fill', resolveColor(params.center_star_color))
        .attr('stroke', 'none');

    // 4. Inner dark dot
    var dotPts = [];
    for (var i = 0; i < n; i++) {
        dotPts.push(polarPt(coreR * 0.35, i * step));
    }
    svg.append('polygon')
        .attr('points', dotPts.map(function(p) { return p[0] + ',' + p[1]; }).join(' '))
        .attr('fill', resolveColor(params.center_dot_color || '$darkNavy'))
        .attr('stroke', 'none');
}
```

### `interstitial-tiles`

```javascript
function renderInterstitialTiles(svg, params, style) {
    var n = params.n;
    var centerX = px(params.center ? params.center[0] : 0);
    var centerY = py(params.center ? params.center[1] : 0);
    var rOuter = pr(params.star_outer_radius);
    var rMid = pr(params.star_mid_radius);
    var satDist = pr(params.satellite_distance);
    var satR = pr(params.satellite_radius);
    var step = 360 / n;
    var sw = (style && style['stroke-width']) || 5;
    var strokeColor = resolveColor(style && style.stroke ? style.stroke : '#FFFFFF');

    function polarPt(r, deg) {
        var a = (deg - 90) * Math.PI / 180;
        return [centerX + r * Math.cos(a), centerY + r * Math.sin(a)];
    }

    function drawPoly(pts, fill) {
        svg.append('polygon')
            .attr('points', pts.map(function(p) { return p[0] + ',' + p[1]; }).join(' '))
            .attr('fill', resolveColor(fill))
            .attr('stroke', strokeColor)
            .attr('stroke-width', sw)
            .attr('stroke-linejoin', 'round');
    }

    for (var i = 0; i < n; i++) {
        var a = i * step;
        var na = (i + 1) * step;
        var pa = ((i - 1 + n) % n) * step;
        var midA = a + step / 2;

        // Key reference points
        var sTip = polarPt(rOuter, a);
        var sNextTip = polarPt(rOuter, na);
        var baseR = polarPt(rMid, a + step / 2);
        var baseL = polarPt(rMid, a - step / 2);
        var satInner = polarPt(satDist - satR, a);
        var nextSatInner = polarPt(satDist - satR, na);
        var prevSatInner = polarPt(satDist - satR, pa);
        var gapM = polarPt(satDist * 0.78, midA);

        // Tile A: Kite from star tip toward gap midpoint
        var kSideL = polarPt(rOuter * 1.04, a + step * 0.25);
        var kSideR = polarPt(rOuter * 1.04, a - step * 0.25);
        drawPoly([sTip, kSideL, gapM, kSideR], params.tile_colors_a[i]);

        // Tile B: Triangle between two consecutive star tips
        var gapBetween = polarPt(rOuter * 0.95, midA);
        drawPoly([sTip, sNextTip, gapBetween], params.tile_colors_b[i]);

        // Tile C: Side kite toward current satellite
        var midToSat = polarPt(rOuter * 0.92, a + step * 0.39);
        drawPoly([kSideL, midToSat, satInner, baseR], params.tile_colors_c[i]);

        // Tile D: Side kite toward previous satellite
        var midToPrevSat = polarPt(rOuter * 0.92, a - step * 0.39);
        drawPoly([kSideR, midToPrevSat, prevSatInner, baseL], params.tile_colors_c[(i + n / 2) % n]);

        // Tile E: Connect gap midpoint to satellite
        drawPoly([gapM, midToSat, satInner], params.tile_colors_b[(i + 2) % n]);

        // Tile F: Connect gap to between-tips midpoint
        drawPoly([gapBetween, gapM, nextSatInner], params.tile_colors_a[(i + 3) % n]);

        // Tile G: Fill remaining triangle
        drawPoly([gapBetween, midToSat, gapM], params.tile_colors_b[(i + 6) % n]);
    }
}
```

### `radial-network`

```javascript
function renderRadialNetwork(svg, params, style) {
    var centerX = px(params.center ? params.center[0] : 0);
    var centerY = py(params.center ? params.center[1] : 0);
    var n = params.n;
    var rotation = params.rotation || 0;
    var step = 360 / n;
    var sw = (style && style['stroke-width']) || 9;
    var strokeColor = resolveColor(style && style.stroke ? style.stroke : '#FFFFFF');

    // Edge collector with deduplication
    var edges = [];
    var edgeSet = {};
    function edgeKey(from, to) {
        var ax = Math.round(from[0] * 100);
        var ay = Math.round(from[1] * 100);
        var bx = Math.round(to[0] * 100);
        var by = Math.round(to[1] * 100);
        // Canonical order: lower coordinate first
        if (ax < bx || (ax === bx && ay < by)) {
            return ax + ',' + ay + '-' + bx + ',' + by;
        }
        return bx + ',' + by + '-' + ax + ',' + ay;
    }
    function addEdge(from, to, ringId, layer) {
        var k = edgeKey(from, to);
        if (!edgeSet[k]) {
            edgeSet[k] = true;
            edges.push({ from: from, to: to, ring_id: ringId, layer: layer });
        }
    }

    // Compute vertex positions for a ring
    function computeRing(cxLocal, cyLocal, ring, parentN, parentRotation) {
        var count = ring.count || parentN;
        var ringStep = 360 / count;
        var angleOff = ring.angle_offset || 0;
        var r = pr(ring.radius);
        var vertices = [];
        for (var i = 0; i < count; i++) {
            var deg = parentRotation + angleOff + i * ringStep;
            var a = (deg - 90) * Math.PI / 180;
            vertices.push([
                cxLocal + r * Math.cos(a),
                cyLocal + r * Math.sin(a)
            ]);
        }
        return vertices;
    }

    // Connect a ring to its previous ring based on edges_to_prev
    function connectRings(prevVertices, currVertices, currRing, parentN, parentRotation) {
        var mode = currRing.edges_to_prev || 'aligned';
        var ringId = currRing.id;

        if (mode === 'none') return;

        if (mode === 'all') {
            // Each current vertex connects to ALL previous vertices
            for (var i = 0; i < currVertices.length; i++) {
                for (var j = 0; j < prevVertices.length; j++) {
                    addEdge(currVertices[i], prevVertices[j], ringId, 'radial');
                }
            }
        } else if (mode === 'aligned') {
            // Each current vertex connects to the angularly closest prev vertex
            // When counts match, this is a 1:1 mapping
            var currCount = currVertices.length;
            var prevCount = prevVertices.length;
            var currStep = 360 / currCount;
            var prevStep = 360 / prevCount;
            var currOff = currRing.angle_offset || 0;

            for (var i = 0; i < currCount; i++) {
                // Find the closest prev vertex by angular proximity
                var currAngle = currOff + i * currStep;
                var bestJ = 0;
                var bestDiff = 9999;
                for (var j = 0; j < prevCount; j++) {
                    // Compute prev angle (need prev ring's offset — stored as data)
                    var dx = prevVertices[j][0] - currVertices[i][0];
                    var dy = prevVertices[j][1] - currVertices[i][1];
                    var dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < bestDiff) {
                        bestDiff = dist;
                        bestJ = j;
                    }
                }
                addEdge(currVertices[i], prevVertices[bestJ], ringId, 'radial');
            }
        } else if (mode === 'nearest') {
            // Each current vertex connects to the 1-2 nearest prev vertices
            for (var i = 0; i < currVertices.length; i++) {
                // Sort prev vertices by distance
                var dists = [];
                for (var j = 0; j < prevVertices.length; j++) {
                    var dx = prevVertices[j][0] - currVertices[i][0];
                    var dy = prevVertices[j][1] - currVertices[i][1];
                    dists.push({ idx: j, d: Math.sqrt(dx * dx + dy * dy) });
                }
                dists.sort(function(a, b) { return a.d - b.d; });
                // Connect to nearest; also connect to second-nearest if within 20% of nearest
                addEdge(currVertices[i], prevVertices[dists[0].idx], ringId, 'radial');
                if (dists.length > 1 && dists[1].d < dists[0].d * 1.2) {
                    addEdge(currVertices[i], prevVertices[dists[1].idx], ringId, 'radial');
                }
            }
        }
    }

    // Process rings for a given center, building edges
    function processNetwork(cxLocal, cyLocal, rings, parentN, parentRotation) {
        var prevVertices = [[cxLocal, cyLocal]]; // Layer 0: center point

        for (var r = 0; r < rings.length; r++) {
            var ring = rings[r];
            var vertices = computeRing(cxLocal, cyLocal, ring, parentN, parentRotation);

            // Connect to previous ring (or center if first ring)
            connectRings(prevVertices, vertices, ring, parentN, parentRotation);

            // Lateral edges (within ring)
            if (ring.lateral_edges) {
                for (var i = 0; i < vertices.length; i++) {
                    addEdge(vertices[i], vertices[(i + 1) % vertices.length], ring.id, 'lateral');
                }
            }

            // Recurse into sub_network at each vertex
            if (ring.sub_network) {
                var subN = ring.sub_network.n || parentN;
                var subRings = ring.sub_network.rings || [];
                for (var i = 0; i < vertices.length; i++) {
                    var subRotation = parentRotation + (ring.angle_offset || 0)
                                    + i * (360 / (ring.count || parentN));
                    processNetwork(vertices[i][0], vertices[i][1], subRings, subN, subRotation);
                }
            }

            prevVertices = vertices;
        }
    }

    // Build the network
    processNetwork(centerX, centerY, params.rings, n, rotation);

    // Render all edges as strapwork bands on top
    var bandG = svg.append('g');
    for (var i = 0; i < edges.length; i++) {
        var e = edges[i];
        bandG.append('line')
            .attr('x1', e.from[0]).attr('y1', e.from[1])
            .attr('x2', e.to[0]).attr('y2', e.to[1])
            .attr('stroke', strokeColor)
            .attr('stroke-width', sw)
            .attr('stroke-linecap', 'butt');
    }
}
```

**Key implementation notes:**

1. **Edge deduplication** — Uses `edgeKey()` with canonical coordinate ordering so shared edges between rings are drawn exactly once.
2. **Center as Layer 0** — The first ring always connects to the center point `[cx, cy]` as its "previous ring" (a single-vertex ring). This ensures the full network is connected.
3. **Sub-network recursion** — When a ring has `sub_network`, each vertex becomes a local center. The sub-network's first ring connects back to that vertex, maintaining connectivity with the parent network.
4. **Coordinate space** — Ring radii are in normalized coordinates and converted to pixels via `pr()`. The center is converted via `px()`/`py()`. Sub-network radii are relative to their local center, also normalized.
5. **Blueprint mode** — To verify network topology, render ONLY this layer (comment out tile fill layers). The edge network should show the complete strapwork skeleton.

## Helper Functions

Always include these in the generated HTML:

```javascript
// Resolve palette references ($name -> hex)
var palette = config.palette.colors;
function resolveColor(color) {
    if (!color) return 'none';
    if (color.charAt(0) === '$') return palette[color.substring(1)] || color;
    return color;
}

// Dispatch layer rendering
function renderLayer(target, layer, localCoords) {
    var style = layer.style || {};
    var params = layer.params || {};
    switch (layer.type) {
        case 'star-polygon': renderStarPolygon(target, params, style); break;
        case 'polygon': renderPolygon(target, params, style); break;
        case 'circle': case 'circle-ring': renderCircle(target, params, style); break;
        case 'line': renderLine(target, params, style); break;
        case 'radial-repeat': renderRadialRepeat(target, params, layer.element); break;
        case 'rosette': renderRosette(target, params, style); break;
        case 'flower-of-life': renderFlowerOfLife(target, params, style); break;
        case 'radial-gradient-fill': renderRadialGradientFill(target, params); break;
        case 'grid-repeat': renderGridRepeat(target, params, layer.element); break;
        case 'star-tiling': renderStarTiling(target, params, style); break;
        case 'filled-rosette': renderFilledRosette(target, params, style); break;
        case 'interstitial-tiles': renderInterstitialTiles(target, params, style); break;
        case 'radial-network': renderRadialNetwork(target, params, style); break;
        default: console.warn('Unknown layer type: ' + layer.type);
    }
}
```

## Blueprint Mode: Color-Coded Layer Legend

When rendering in blueprint mode (`?mode=blueprint`), color-code each strapwork layer by its **dependency depth** from the center point. This makes the network topology instantly readable.

### Layer Color Palette

| Depth | Color | Hex | Meaning |
|-------|-------|-----|---------|
| 0 | Red | `#cc0000` | Depends on center point directly (center→tips, star-polygon diagonals) |
| 1 | Blue | `#0066cc` | Depends on ring connected to center (tips→mid, tips→outer-kites) |
| 2 | Green | `#00aa44` | Depends on ring 2 layers from center (mid→inner, outer-kites→satellites) |
| 3 | Purple | `#8833cc` | Depends on ring 3 layers from center |
| lateral | Orange | `#cc8800` | Lateral edges within a ring (same-ring connections) |

### How to Assign Colors

Each ring in a `radial-network` has a **depth** = its index in the rings array. The edges connecting ring N to ring N-1 get the color for depth N. Lateral edges (within a ring) always get orange. `star-polygon` extended lines get depth 0 (red) since they originate from the star construction center.

### Legend Rendering

In blueprint mode, render a legend box in the top-left corner showing each color and its ring ID:

```javascript
if (renderMode === 'blueprint') {
    var legend = svg.append('g').attr('transform', 'translate(15, 20)');
    var legendColors = [
        { color: '#cc0000', label: 'Depth 0: center-connected' },
        { color: '#0066cc', label: 'Depth 1: ring-1 connections' },
        { color: '#00aa44', label: 'Depth 2: ring-2 connections' },
        { color: '#8833cc', label: 'Depth 3: ring-3 connections' },
        { color: '#cc8800', label: 'Lateral (within ring)' }
    ];
    // Add actual ring IDs dynamically from the rings array
    for (var li = 0; li < legendItems.length; li++) {
        legend.append('line')
            .attr('x1', 0).attr('y1', li * 18)
            .attr('x2', 20).attr('y2', li * 18)
            .attr('stroke', legendItems[li].color)
            .attr('stroke-width', 3);
        legend.append('text')
            .attr('x', 25).attr('y', li * 18 + 4)
            .attr('font-size', '11px')
            .attr('fill', '#333')
            .text(legendItems[li].label);
    }
}
```

### Edge Rendering in Blueprint Mode

When drawing edges in blueprint mode, assign colors based on `ring_id` depth:

```javascript
// Build ring depth map from the rings array
var ringDepths = {};
for (var ri = 0; ri < params.rings.length; ri++) {
    ringDepths[params.rings[ri].id] = ri;
}
var depthColors = ['#cc0000', '#0066cc', '#00aa44', '#8833cc', '#666666'];

for (var i = 0; i < edges.length; i++) {
    var e = edges[i];
    var depth = ringDepths[e.ring_id] || 0;
    var eColor = e.layer === 'lateral' ? '#cc8800' : (depthColors[depth] || '#333');
    bandG.append('line')
        .attr('x1', e.from[0]).attr('y1', e.from[1])
        .attr('x2', e.to[0]).attr('y2', e.to[1])
        .attr('stroke', eColor)
        .attr('stroke-width', 1.5)
        .attr('stroke-linecap', 'butt');
}
```

This makes it immediately obvious which edges belong to which network layer and helps diagnose connectivity issues, density problems, and topology mismatches vs the reference pattern.

## Blueprint-First Rendering Architecture

Islamic geometric patterns must be rendered in two distinct phases: **blueprint** (structural edges) then **fills** (colored regions). This prevents the double-edge problem and ensures uniform strapwork.

### The Problem with Polygon Strokes

When two adjacent tiles both have `stroke: white`, their shared edge is drawn TWICE — once by each polygon. The apparent strapwork width becomes 2x the stroke-width value. No parametric adjustment to stroke-width can fix this because the mechanism is architecturally wrong.

### The Blueprint-First Approach

**Phase 1: Compute the edge network (blueprint)**
Define ALL the structural lines of the pattern as a set of line segments. This is the "blueprint" — the skeleton that defines where every tile boundary falls.

```javascript
// Collect ALL edge segments
var edges = [];

// Star kite edges
for (var i = 0; i < n; i++) {
    edges.push({ from: starTip(i), to: midPt(i, 'L') });
    edges.push({ from: starTip(i), to: midPt(i, 'R') });
}
// {n/k} star polygon edges
for (var i = 0; i < n; i++) {
    edges.push({ from: starTip(i), to: starTip((i+k)%n) });
}
// Satellite kite edges
for (var s = 0; s < numSats; s++) {
    for (var p = 0; p < n; p++) {
        edges.push({ from: satTip(s,p), to: satMid(s,p,'L') });
        edges.push({ from: satTip(s,p), to: satMid(s,p,'R') });
    }
}
// ... all other structural edges
```

**Phase 2: Fill tile regions (no stroke)**
Draw every tile as a filled polygon with `stroke: 'none'`. The tiles are the colored regions BETWEEN the blueprint edges.

```javascript
function drawTile(target, pts, fill) {
    target.append('polygon')
        .attr('points', pts.map(function(p) { return p[0]+','+p[1]; }).join(' '))
        .attr('fill', resolveColor(fill))
        .attr('stroke', 'none');  // ALWAYS none — edges come from the blueprint
}
```

**Phase 3: Draw the blueprint (strapwork bands)**
Draw each edge segment as a white line ON TOP of all tile fills. Each edge is drawn exactly ONCE, ensuring uniform apparent width.

```javascript
var bandG = g.append('g');  // on top of all tiles
for (var i = 0; i < edges.length; i++) {
    var e = edges[i];
    bandG.append('line')
        .attr('x1', e.from[0]).attr('y1', e.from[1])
        .attr('x2', e.to[0]).attr('y2', e.to[1])
        .attr('stroke', palette.white)
        .attr('stroke-width', STRAP)
        .attr('stroke-linecap', 'butt');
}
```

### Layer Order

1. **Full-bleed background** — colored polygon covering the entire medallion area (eliminates white gaps)
2. **Tile fills** — all colored polygons with `stroke: 'none'`, drawn in back-to-front order
3. **Strapwork bands** — all structural edge lines drawn on top with uniform width
4. **Over-under crossings** — crossing overlay effects (shadow + white segments)
5. **Clipping** — boundary clip-path applied to the container group

### Benefits

- Every shared edge is drawn exactly ONCE → uniform apparent width
- No oscillation between "too thick" and "too thin"
- Changing STRAP affects ALL edges uniformly
- Blueprint can be verified independently (draw ONLY the edges to check topology)
- Fills can be verified independently (draw ONLY the tiles to check coverage)

### Anti-Pattern: Polygon Stroke for Strapwork

**NEVER** use polygon `stroke` to create strapwork. This includes:
- `drawTileWithStroke(pts, fill, STRAP)` — draws shared edges twice
- `.attr('stroke', white).attr('stroke-width', STRAP)` on tile polygons
- Any approach where adjacent tiles both contribute to a shared edge

The ONLY valid use of polygon stroke is for isolated shapes that don't share edges with neighbors (rare in Islamic geometric patterns).

## Layered Network Construction

When building the edge network, think of it as **concentric layers radiating from a central midpoint**. Each layer's endpoints become the attachment points for the next layer's edges. This creates a naturally connected network.

### The Layer Model

```
Layer 0: Central midpoint
    ↓ (radial edges)
Layer 1: First ring of junction points (e.g., star vertices, mid-ring points)
    ↓ (connector edges)
Layer 2: Second ring of junction points (e.g., satellite approach points)
    ↓ (attachment edges)
Layer 3: Satellite centers (each is a secondary midpoint)
    ↓ (radial edges at satellite scale)
Layer 4: Satellite internal junction points (satellite tip vertices)
```

### How to Apply

1. **Start from the center.** Define Layer 0 (the pattern origin) and Layer 1 (the first radial ring — star vertices, mid-ring points, etc.)

2. **Build outward.** Layer 2 edges connect Layer 1 junction points to Layer 2 positions. The KEY constraint: every Layer 2 edge must START from a Layer 1 junction point. This ensures connectivity.

3. **Satellite attachment.** Layer 3 (satellite centers) are reached via Layer 2 edges. Each satellite center becomes a LOCAL Layer 0, and its internal structure (Layer 4) radiates from it.

4. **Shared junction points.** When a satellite's innermost edges need to connect to the main network, they must share EXACT endpoint coordinates with the interstitial connector edges (Layer 2→3). Don't just position them "nearby" — use the SAME computed point.

### Code Pattern

```javascript
// Layer 1: radial from center
var layer1 = [];
for (var i = 0; i < N; i++) {
    layer1.push(polarPt(cx, cy, r1, i * STEP));
}

// Layer 2: connect layer1 to satellite approach points
var layer2 = [];
for (var i = 0; i < N; i++) {
    var approach = polarPt(cx, cy, r2, i * STEP);
    layer2.push(approach);
    addEdge(layer1[i], approach, 'connector');  // connected to layer1!
}

// Layer 3: satellite center, reached FROM layer2
for (var i = 0; i < N; i++) {
    addEdge(layer2[i], satCenters[i], 'connector');  // connected to layer2!
    // Layer 4: satellite internals radiate from satCenters[i]
    for (var p = 0; p < N; p++) {
        var tip = polarPt(satCenters[i][0], satCenters[i][1], satR, ...);
        addEdge(satCenters[i], tip, 'satellite');
    }
}
```

### Anti-Pattern: Independent Construction

**NEVER** compute satellite vertices independently and hope they align with the main network:
```javascript
// BAD: satellite computed from scratch, not connected to network
var satTip = polarPt(satCenter[0], satCenter[1], satR, angle);
addEdge(satCenter, satTip);  // no shared junction with main network!
```

Instead, compute shared junction points FIRST, then use them as attachment points:
```javascript
// GOOD: shared junction point connects both networks
var junction = layer2[i];  // same point used by interstitial connector
addEdge(junction, satTip);  // satellite edge starts from shared junction
```

## Construction from Central Origin

All geometry must be constructed from the center point outward using polar coordinates and trigonometric derivations. Never use arbitrary scaling factors.

**Core principle:** Every radius and position is a function of `R` (circumscribed circle radius), `n` (symmetry order), and `k` (star step), computed via trigonometry.

**Deriving key radii for a {n/k} star polygon:**

```javascript
// Given: R = outer radius, n = points, k = step
var step = 360 / n;
var halfStep = step / 2;

// Star tip radius (outermost points) = R itself
var rOuter = R;

// Mid-ring radius: where adjacent star edges intersect.
// Two edges from neighboring tips cross at this distance from center.
// For a {n/k} star: adjacent edges from tip i and tip i+1,
// each going to vertex (i+k) and (i+1+k), intersect at:
var alpha = Math.PI * k / n;  // half-angle of the star point
var rMid = R * Math.cos(alpha) / Math.cos(alpha - Math.PI / n);

// Inner radius: where edges from tip i cross edges from tip i+2
// (or use the second intersection ring)
var rInner = R * Math.cos(2 * Math.PI * k / n) / Math.cos(Math.PI / n);
// Verify these by checking that the resulting points lie on the expected edges.

// Satellite distance: additive, not a magic multiplier
// satDist = rOuter + bandWidth + satRadius
// where bandWidth and satRadius are derived from the pattern's strapwork geometry
```

**Anti-patterns to avoid:**
- `rMid = rOuter * 0.625` -- arbitrary ratio, will be wrong for different n/k
- `satDist = R * 0.58` -- hides the geometric relationship
- `rInner = rOuter * 0.333` -- should be derived from edge intersections

**When a ratio is truly needed** (e.g., from the reference image), document it as: "measured ratio 0.62, expected from {10/4} geometry: `cos(2*pi/5)/cos(pi/10)` = 0.618". This makes the intent auditable.

## Compilation Checklist

Before saving the HTML file:

1. All `pattern.json` layers are compiled to rendering code
2. Palette colors are resolved correctly (no unresolved `$` references)
3. Coordinates are properly mapped from normalized to pixel space
4. SVG dimensions match `canvas.width` and `canvas.height`
5. Background color is applied as the first element
6. Layer order matches the pattern.json array (bottom-to-top)
7. No ES6 template literals — only `+` string concatenation
8. D3.js v7 CDN URL is correct
9. File opens correctly when loaded as `file:///path/to/output.html`
