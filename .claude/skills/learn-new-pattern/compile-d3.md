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
        // Add new types as the language grows
        default: console.warn('Unknown layer type: ' + layer.type);
    }
}
```

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
