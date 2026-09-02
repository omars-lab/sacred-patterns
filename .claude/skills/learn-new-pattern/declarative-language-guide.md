# Declarative Pattern Language Guide

The pattern definition format (`pattern.json`) describes Islamic geometric patterns in terms of geometric primitives, symmetry, composition, and styling. It is the canonical representation — all output formats (D3.js HTML, GeoGebra, OpenSCAD) are compiled from it.

## Top-Level Schema

```json
{
  "name": "Pattern Name",
  "symmetry": {
    "group": "D8",
    "order": 8
  },
  "canvas": {
    "width": 800,
    "height": 800,
    "background": "#0a1929"
  },
  "palette": {
    "name": "Ottoman Blue",
    "colors": {
      "primary": "#7dd6e0",
      "secondary": "#2d4a7c",
      "accent": "#d4a843",
      "highlight": "#f5f5e8",
      "background": "#0a1929"
    }
  },
  "construction": {
    "center": [0, 0],
    "r0": 1.0,
    "radii": {
      "r1": { "value": 0.15, "purpose": "inner octagon vertices" },
      "r2": { "value": 0.35, "purpose": "primary star inner points" }
    },
    "angles": {
      "primary": 45,
      "secondary": 22.5
    }
  },
  "layers": [
    // ... layer definitions, rendered bottom-to-top
  ]
}
```

### Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Human-readable pattern name |
| `symmetry.group` | string | yes | Dihedral group (D4, D6, D8, D10, D12, D16) |
| `symmetry.order` | number | yes | Rotational symmetry order |
| `canvas.width` | number | yes | SVG width in pixels |
| `canvas.height` | number | yes | SVG height in pixels |
| `canvas.background` | string | yes | Background color (hex or palette ref) |
| `palette.name` | string | yes | Palette name for reference |
| `palette.colors` | object | yes | Named colors, referenced as `$name` in layers |
| `construction` | object | no | Construction geometry metadata (for documentation) |
| `layers` | array | yes | Ordered list of layers, rendered bottom-to-top |

### Palette References

In layer style properties, use `$colorName` to reference palette colors:
```json
{ "stroke": "$accent", "fill": "$primary" }
```

### Coordinate System

All coordinates are normalized to the canvas center:
- `[0, 0]` is the canvas center
- `radius` values are fractions of `Math.min(width, height) / 2`
- Angles are in degrees, 0 = right (3 o'clock), counterclockwise positive

### Pi-Based Mathematical Conventions

All angles and radii in Islamic geometric patterns are derived from integer relationships with pi and the symmetry order `n`. Express them as such — never as unexplained decimals.

**Angles as fractions of pi:**

| Expression | Meaning | For n=10 |
|-----------|---------|----------|
| `2*pi/n` | One sector (full-turn divided by symmetry order) | 36 deg = pi/5 |
| `pi/n` | Half-sector | 18 deg = pi/10 |
| `pi*k/n` | Star polygon skip angle (k vertices) | k=4: 72 deg = 2*pi/5 |
| `pi*(n-2)/(2*n)` | Interior angle of regular n-gon | 72 deg = 2*pi/5 |

**Radii as trigonometric expressions:**

| Radius | Formula | Meaning |
|--------|---------|---------|
| Star outer | `R` (given) | Circumscribed circle |
| Star mid-ring | `R * cos(pi*k/n)` | {n/k} edge intersection with bisector |
| Star inner | `R * cos(pi*k/n) / cos(pi/n)` | Second intersection ring |
| Satellite distance | `R + bandWidth + R_sat` | Additive: star tip + gap + satellite |
| Satellite radius | `satDist * sin(pi/n)` | Half the chord between adjacent satellite centers |

**In pattern.json**: Use degree values (for human readability) but document the pi-fraction in a comment or the `construction` block:
```json
{
  "construction": {
    "angles": {
      "sector": "2*pi/10 = 36 deg",
      "half_sector": "pi/10 = 18 deg",
      "star_skip": "4*pi/10 = 72 deg"
    },
    "radii": {
      "r_mid": "R * cos(4*pi/10) = R * cos(72 deg)",
      "r_inner": "R * cos(4*pi/10) / cos(pi/10)"
    }
  }
}
```

**In code (compile-d3.md)**: Use `Math.PI` expressions directly:
```javascript
var sector = 2 * Math.PI / n;       // NOT: 360 / n * Math.PI / 180
var halfSector = Math.PI / n;        // NOT: 18 * Math.PI / 180
var skipAngle = Math.PI * k / n;     // NOT: 72 * Math.PI / 180
var rMid = R * Math.cos(skipAngle);  // NOT: R * 0.309
```

**Anti-patterns:**
- `0.625` — write `cos(pi*k/n) / cos(pi/n)` or document the derivation
- `22.5` — write `360 / (2*n)` or `pi/n` in radians
- `0.309` — write `cos(4*pi/10)` or `cos(72 deg)`
- `0.56` — write `R + bandWidth + R_sat` and show each term

**Principle**: Every number in the pattern should trace back to `n`, `k`, `pi`, and the base radius `R` through a documented chain of geometric reasoning.

### Negative Space and Partial Shapes

Two fundamental construction principles in Islamic geometric patterns:

**Negative Space**: Many apparent "shapes" in a pattern are NOT explicitly drawn — they are the background showing through gaps between overlapping elements. Before adding a shape as an explicit tile:
1. Ask: "Would this shape appear naturally if I just overlap the surrounding elements correctly?"
2. Dark shapes between white strapwork bands are almost always negative space
3. The correct approach is often: draw a background color, draw the colored tiles ON TOP, draw white bands ON TOP of those — the dark gaps between bands ARE the pattern, not something you need to draw

In `pattern.json`, negative space shapes are NOT listed as layers. They emerge from the `canvas.background` color visible through gaps in the layers above.

**Partial Shapes**: Regular polygons often appear as FRAGMENTS at boundaries. A hexagon might only show 3 sides because the rest is hidden behind a rosette. A kite might be truncated by the medallion boundary.

Partial shapes are rendered using the `clip` property on any layer:

```json
{
  "type": "regular-polygon",
  "params": {
    "n": 6, "center": [0.3, 0.1], "radius": 0.15
  },
  "clip": {
    "type": "circle",
    "center": [0, 0],
    "radius": 0.76
  }
}
```

Or using `clip: { "type": "sector", "start_angle": 0, "end_angle": 36 }` to show only a wedge of a shape.

Or using `clip: { "type": "exclude", "elements": ["satellites"] }` to clip away regions covered by other named elements.

When analyzing a reference, look for shapes at boundaries that appear to be "cut off" — these are partial shapes. The underlying full shape may extend well past what's visible, but only the fragment within the medallion or between rosettes is drawn. Record these in `discoveries.md` under "Partial Shape Observations."

---

## Layer Types

Layers are rendered in array order (first = bottom, last = top). Each layer has a `type` and `params` object, plus optional `style`.

### Geometric Primitives

#### `star-polygon`

An {n/k} star polygon — connects every k-th vertex of a regular n-gon.

```json
{
  "type": "star-polygon",
  "params": {
    "n": 8,
    "k": 3,
    "center": [0, 0],
    "radius": 0.52,
    "rotation": 0
  },
  "style": {
    "stroke": "$primary",
    "stroke-width": 2,
    "fill": "none"
  }
}
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `n` | number | required | Number of vertices |
| `k` | number | required | Step size (1 = regular polygon, 2+ = star) |
| `center` | [x, y] | [0, 0] | Center point (normalized) |
| `radius` | number | required | Outer radius (fraction of half-canvas) |
| `rotation` | number | 0 | Rotation in degrees |

**Rendering:** Generate n points on a circle at `radius`, connect point i to point (i+k) % n. For k > 1, this produces a star with n points. The inner radius (where edges cross) is `radius * cos(k*pi/n) / cos((k-1)*pi/n)`.

#### `polygon`

A regular polygon (3-12 sides).

```json
{
  "type": "polygon",
  "params": {
    "sides": 8,
    "center": [0, 0],
    "radius": 0.45,
    "rotation": 22.5
  },
  "style": {
    "stroke": "$accent",
    "stroke-width": 1.5,
    "fill": "none"
  }
}
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `sides` | number | required | Number of sides (3-12) |
| `center` | [x, y] | [0, 0] | Center point |
| `radius` | number | required | Circumscribed radius |
| `rotation` | number | 0 | Rotation in degrees |

#### `circle`

A single circle.

```json
{
  "type": "circle",
  "params": {
    "center": [0, 0],
    "radius": 0.5
  },
  "style": {
    "stroke": "$accent",
    "stroke-width": 1,
    "fill": "none"
  }
}
```

#### `circle-ring`

A circle used as a decorative ring (alias for `circle` but semantically marks it as a visible ring rather than a construction circle).

```json
{
  "type": "circle-ring",
  "params": {
    "center": [0, 0],
    "radius": 0.95
  },
  "style": {
    "stroke": "$highlight",
    "stroke-width": 2,
    "fill": "none"
  }
}
```

#### `line`

A single line segment.

```json
{
  "type": "line",
  "params": {
    "from": [0, 0],
    "to": [0.5, 0.5]
  },
  "style": {
    "stroke": "$accent",
    "stroke-width": 1,
    "opacity": 0.3
  }
}
```

---

### Interlace & Strapwork

#### `interlace-network`

A system of bands with over-under weaving at crossings.

```json
{
  "type": "interlace-network",
  "params": {
    "bands": [
      {
        "path": "concentric-polygon",
        "sides": 8,
        "radius": 0.45,
        "rotation": 22.5
      },
      {
        "path": "concentric-polygon",
        "sides": 8,
        "radius": 0.75,
        "rotation": 0
      }
    ],
    "band_width": 0.02,
    "weave_rule": "alternating",
    "shadow_offset": 1
  },
  "style": {
    "fill": "$highlight",
    "stroke": "$accent",
    "stroke-width": 0.5
  }
}
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `bands` | array | required | Band path definitions |
| `band_width` | number | 0.02 | Width of bands (normalized) |
| `weave_rule` | string | "alternating" | Over-under rule: "alternating", "always-over", "always-under" |
| `shadow_offset` | number | 1 | Shadow size in px at crossings (0 = no shadow) |

**Band path types:**
- `"concentric-polygon"` — band follows a polygon path
- `"concentric-circle"` — band follows a circular path
- `"radial"` — band radiates from center to edge
- `"custom"` — explicit point array

#### `strapwork-band`

A single decorative band along a path.

```json
{
  "type": "strapwork-band",
  "params": {
    "path": [[0.1, 0], [0.3, 0.2], [0.5, 0]],
    "width": 0.02,
    "closed": false
  },
  "style": {
    "fill": "$highlight",
    "stroke": "$accent",
    "stroke-width": 0.5
  }
}
```

---

### Rosettes & Florals

#### `rosette`

An n-fold petal pattern.

```json
{
  "type": "rosette",
  "params": {
    "center": [0, 0],
    "n": 12,
    "inner_radius": 0.08,
    "outer_radius": 0.15,
    "petal_shape": "pointed",
    "rotation": 0
  },
  "style": {
    "stroke": "$secondary",
    "stroke-width": 1.5,
    "fill": "$primary"
  }
}
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `n` | number | required | Number of petals |
| `inner_radius` | number | required | Inner radius (petal base) |
| `outer_radius` | number | required | Outer radius (petal tip) |
| `petal_shape` | string | "pointed" | "pointed", "rounded", "ogee" |
| `rotation` | number | 0 | Rotation in degrees |

**Rendering:** For "pointed" petals, generate 2n points alternating between inner and outer radii. For "rounded", use quadratic bezier curves. For "ogee", use S-curves (cubic bezier).

#### `arabesque`

Curvilinear vegetal scrollwork filling a region.

```json
{
  "type": "arabesque",
  "params": {
    "region": {
      "type": "annular-sector",
      "inner_radius": 0.5,
      "outer_radius": 0.8,
      "start_angle": 0,
      "end_angle": 45
    },
    "motif": "vine-scroll",
    "density": 0.5,
    "symmetry": "bilateral"
  },
  "style": {
    "stroke": "$accent",
    "stroke-width": 1,
    "fill": "none"
  }
}
```

---

### Tiling & Composition

#### `radial-repeat`

Repeat an element n times around a center at a given radius.

```json
{
  "type": "radial-repeat",
  "params": {
    "count": 8,
    "radius": 0.65,
    "rotation_offset": 0,
    "rotate_elements": true
  },
  "element": {
    "type": "star-polygon",
    "params": { "n": 8, "k": 2, "radius": 0.15 },
    "style": { "stroke": "$secondary", "fill": "none" }
  }
}
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `count` | number | required | Number of copies |
| `radius` | number | required | Distance from center |
| `rotation_offset` | number | 0 | Starting angle offset in degrees |
| `rotate_elements` | boolean | true | Whether each copy rotates to face outward |

**Rendering:** Place copies at angles `rotation_offset + i * (360/count)` for i = 0..count-1. If `rotate_elements` is true, each copy is rotated by the same angle.

#### `radial-network`

A connected network of concentric rings radiating from a center point. Each ring contains vertices at a given radius, with edges connecting vertices between adjacent rings (radial edges) and optionally within the same ring (lateral edges). Ring vertices can contain nested sub-networks for self-similar sub-patterns (e.g., satellite rosettes).

This construct produces an **edge list** (the strapwork skeleton), not tile fills. It is rendered ON TOP of tile fill layers (`star-tiling`, `filled-rosette`, `interstitial-tiles`) to create the white band network.

```json
{
  "type": "radial-network",
  "params": {
    "center": [0, 0],
    "n": 10,
    "rotation": 0,
    "rings": [
      {
        "id": "star-tips",
        "radius": 0.48,
        "count": 10,
        "angle_offset": 0,
        "edges_to_prev": "all",
        "lateral_edges": false
      },
      {
        "id": "mid-ring",
        "radius": 0.30,
        "count": 10,
        "angle_offset": 18,
        "edges_to_prev": "nearest",
        "lateral_edges": false
      },
      {
        "id": "connectors",
        "radius": 0.52,
        "count": 10,
        "angle_offset": 18,
        "edges_to_prev": "aligned",
        "lateral_edges": true
      },
      {
        "id": "satellites",
        "radius": 0.56,
        "count": 10,
        "angle_offset": 18,
        "edges_to_prev": "aligned",
        "lateral_edges": false,
        "sub_network": {
          "n": 10,
          "rings": [
            {
              "id": "sat-tips",
              "radius": 0.18,
              "count": 10,
              "angle_offset": 0,
              "edges_to_prev": "all"
            }
          ]
        }
      }
    ]
  },
  "style": {
    "stroke": "$white",
    "stroke-width": 9
  }
}
```

**Ring Properties:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | string | required | Unique identifier for cross-referencing |
| `radius` | number | required | Distance from parent center (normalized) |
| `count` | number | inherits `n` | Number of vertices in this ring |
| `angle_offset` | number | 0 | Rotation offset in degrees from the parent's base angle |
| `edges_to_prev` | string | `"aligned"` | How to connect to previous ring: `"all"`, `"aligned"`, `"nearest"`, `"none"` |
| `lateral_edges` | boolean | false | Whether to draw edges between consecutive vertices within this ring |
| `sub_network` | object | null | Nested `radial-network` centered at each vertex of this ring |

**Connection Types (`edges_to_prev`):**

- **`"aligned"`** — Each vertex connects to the vertex in the previous ring at the closest angle. Default; works when both rings have the same count.
- **`"nearest"`** — Each vertex connects to the 1-2 nearest vertices in the previous ring by angle. Works when rings have different counts.
- **`"all"`** — Each vertex connects to every vertex in the previous ring. Creates a dense web — use for small rings only.
- **`"none"`** — No edges to previous ring. Vertices connect only through `sub_network` or `lateral_edges`.

**Self-Similar Sub-Networks:**

When a ring has `sub_network`, each vertex of that ring becomes a local center. The sub-network's rings radiate from that local center. The sub-network's first ring connects to the parent vertex (the junction point), ensuring network connectivity. This is how satellite rosettes connect to the main pattern: the satellite center IS a vertex in the parent network, and the satellite petals ARE rings in the sub-network.

**Output:**

The construct produces an edge list. Each edge has:
- `from`: [x, y] coordinates
- `to`: [x, y] coordinates
- `ring_id`: which ring the edge belongs to
- `layer`: `"radial"` (between rings), `"lateral"` (within ring), or `"sub"` (sub-network)

**Relationship to tile fill constructs:**

`radial-network` does NOT replace `star-tiling`, `filled-rosette`, or `interstitial-tiles`. Those define colored tile regions. `radial-network` defines the edge/strapwork skeleton rendered on top. A complete pattern uses both: tile fills (rendered first, no stroke) + `radial-network` (rendered on top as strapwork bands).

#### `grid-repeat`

Tile an element in a periodic grid.

```json
{
  "type": "grid-repeat",
  "params": {
    "repeat_x": 3,
    "repeat_y": 3,
    "spacing_x": 0.5,
    "spacing_y": 0.5,
    "offset_alternate_rows": false,
    "origin": [-0.5, -0.5]
  },
  "element": {
    "type": "star-polygon",
    "params": { "n": 8, "k": 3, "radius": 0.12 }
  }
}
```

#### `flower-of-life`

Recursive surrounding circles (uses the existing `Circle.surroundWithFlowersRecursively`).

```json
{
  "type": "flower-of-life",
  "params": {
    "center": [0, 0],
    "radius": 0.2,
    "levels": 3
  },
  "style": {
    "stroke": "$primary",
    "stroke-width": 1,
    "fill": "none"
  }
}
```

#### `girih-tile`

One of the 5 girih tile shapes.

```json
{
  "type": "girih-tile",
  "params": {
    "shape": "decagon",
    "center": [0, 0],
    "edge_length": 0.1,
    "rotation": 0
  },
  "style": {
    "stroke": "$accent",
    "fill": "$primary"
  }
}
```

| `shape` values | Sides | Interior angles |
|---------------|-------|----------------|
| `"decagon"` | 10 | 144 each |
| `"pentagon"` | 5 | 108 each |
| `"bowtie"` | 6 | 72, 72, 216, 72, 72, 216 |
| `"rhombus"` | 4 | 72, 108, 72, 108 |
| `"hexagon"` | 6 | 72, 144, 144, 72, 144, 144 |

#### `muqarnas-projection`

2D projection of muqarnas tier geometry.

```json
{
  "type": "muqarnas-projection",
  "params": {
    "center": [0, 0],
    "tiers": 3,
    "base_radius": 0.8,
    "tier_ratio": 0.7,
    "base_sides": 8
  },
  "style": {
    "stroke": "$accent",
    "fill": "none"
  }
}
```

---

### Calligraphic

#### `calligraphic-frame`

A border zone or cartouche where calligraphy would be placed.

```json
{
  "type": "calligraphic-frame",
  "params": {
    "shape": "rectangle",
    "center": [0, 0.9],
    "width": 0.6,
    "height": 0.08,
    "corner_style": "pointed"
  },
  "style": {
    "stroke": "$accent",
    "fill": "$background"
  }
}
```

---

### Color & Depth

#### `radial-gradient-fill`

Map fill color to distance from center across previously rendered elements.

```json
{
  "type": "radial-gradient-fill",
  "params": {
    "center": [0, 0],
    "stops": [
      { "offset": 0, "color": "$primary" },
      { "offset": 0.5, "color": "$secondary" },
      { "offset": 1.0, "color": "#1a2c4d" }
    ]
  }
}
```

#### `region-color-map`

Assign colors to closed regions by classification.

```json
{
  "type": "region-color-map",
  "params": {
    "rules": [
      { "match": "star-center", "fill": "$primary" },
      { "match": "star-point", "fill": "$secondary" },
      { "match": "background-tile", "fill": "$background" }
    ]
  }
}
```

---

### Filled Tilings (Tile Mosaics)

These constructs render patterns as filled tile faces — the fundamental approach for Islamic geometric patterns. Unlike wireframe `star-polygon` which draws connecting lines, these produce solid colored tile regions.

#### `star-tiling`

A {n/k} star rendered as distinct filled kite tiles, inner rhombus tiles, and a central polygon. Each tile can have an individual color. This is the **tiling** version of `star-polygon`.

```json
{
  "type": "star-tiling",
  "params": {
    "n": 10,
    "k": 4,
    "center": [0, 0],
    "radius": 0.48,
    "r_mid_ratio": 0.625,
    "r_inner_ratio": 0.333,
    "kite_colors": ["$mediumBlue", "$cornflower", "$cyan", "$royalBlue", "$mediumBlue",
                    "$cornflower", "$royalBlue", "$mediumBlue", "$cyan", "$cornflower"],
    "rhombus_colors": ["$cyan", "$royalBlue", "$mediumBlue", "$cornflower", "$cyan",
                       "$royalBlue", "$mediumBlue", "$cornflower", "$cyan", "$royalBlue"],
    "center_color": "$darkNavy",
    "rotation": 0
  },
  "style": {
    "stroke": "$white",
    "stroke-width": 8
  }
}
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `n` | number | required | Number of star points (typically 8, 10, 12) |
| `k` | number | required | Star step size (determines point sharpness) |
| `center` | [x, y] | [0, 0] | Center point (normalized) |
| `radius` | number | required | Outer tip radius (normalized) |
| `r_mid_ratio` | number | 0.625 | Ratio of mid-ring radius to outer radius (kite base width) |
| `r_inner_ratio` | number | 0.333 | Ratio of inner-ring radius to outer radius (concavity depth) |
| `kite_colors` | array | required | n colors, one per star point kite tile |
| `rhombus_colors` | array | required | n colors, one per inter-point rhombus tile |
| `center_color` | string | "$darkNavy" | Fill color for the central concave star/decagon |
| `rotation` | number | 0 | Rotation in degrees |

**Geometry:** Each star point is a kite (quadrilateral) with vertices at: tip (outer radius), two base points (mid-ring at ±half-step angles), and inner point (inner radius). Between kites, rhombus tiles fill the angular gaps. The center is a concave n-pointed polygon.

**Ratios guide:**
- `r_mid_ratio` controls kite width — higher = wider kites, lower = thinner points
- `r_inner_ratio` controls concavity depth — lower = deeper center void
- For {10/4}: typical ratios are `r_mid_ratio: 0.625`, `r_inner_ratio: 0.333`
- For {8/3}: typical ratios are `r_mid_ratio: 0.6`, `r_inner_ratio: 0.35`

#### `filled-rosette`

A solid rosette drawn as a filled dark disk with petal separations carved on top. This produces the characteristic solid dark appearance of satellite rosettes in Islamic patterns, rather than individually drawn petals that leave gaps.

```json
{
  "type": "filled-rosette",
  "params": {
    "n": 10,
    "center": [0, 0],
    "radius": 0.20,
    "fill_color": "$darkNavy",
    "separation_color": "$white",
    "separation_width": 3,
    "center_star_radius_ratio": 0.25,
    "center_star_color": "$royalBlue",
    "center_dot_color": "$darkNavy",
    "rotation": 0
  }
}
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `n` | number | required | Number of petals |
| `center` | [x, y] | [0, 0] | Center point (normalized) |
| `radius` | number | required | Outer radius of the rosette |
| `fill_color` | string | required | Solid fill color for the entire rosette body |
| `separation_color` | string | "$white" | Color of petal separation lines |
| `separation_width` | number | 3 | Width of petal separation lines in pixels |
| `center_star_radius_ratio` | number | 0.25 | Inner star radius as fraction of outer radius |
| `center_star_color` | string | required | Fill color for the small central star |
| `center_dot_color` | string | "$darkNavy" | Color of the innermost dot |
| `rotation` | number | 0 | Rotation in degrees |

**Rendering approach:**
1. Draw a filled n-gon (or circle) in `fill_color` — this is the solid body
2. Draw n radial separation lines from center to edge in `separation_color`
3. Draw a small n-pointed star at center in `center_star_color`
4. Draw an innermost dot in `center_dot_color`

This "solid disk + carve separations" approach matches the reference appearance where petals blend into a near-continuous dark region.

#### `interstitial-tiles`

Fill the angular gap zone between a central star and a ring of satellites with colored tiles. Rather than computing exact tessellation, this generates a series of kite/triangle tiles in each 360/n-degree sector that fill the gap.

```json
{
  "type": "interstitial-tiles",
  "params": {
    "n": 10,
    "center": [0, 0],
    "star_outer_radius": 0.48,
    "star_mid_radius": 0.30,
    "satellite_distance": 0.56,
    "satellite_radius": 0.20,
    "tile_colors_a": ["$cyan", "$cornflower", "$royalBlue", "$mediumBlue", "$cyan",
                      "$cornflower", "$royalBlue", "$mediumBlue", "$cyan", "$cornflower"],
    "tile_colors_b": ["$royalBlue", "$cyan", "$mediumBlue", "$cornflower", "$royalBlue",
                      "$cyan", "$mediumBlue", "$cornflower", "$royalBlue", "$cyan"],
    "tile_colors_c": ["$mediumBlue", "$royalBlue", "$cornflower", "$cyan", "$mediumBlue",
                      "$royalBlue", "$cornflower", "$cyan", "$mediumBlue", "$royalBlue"]
  },
  "style": {
    "stroke": "$white",
    "stroke-width": 5
  }
}
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `n` | number | required | Symmetry order (matches central star) |
| `center` | [x, y] | [0, 0] | Pattern center |
| `star_outer_radius` | number | required | Central star's outer tip radius |
| `star_mid_radius` | number | required | Central star's mid-ring radius |
| `satellite_distance` | number | required | Distance from center to satellite centers |
| `satellite_radius` | number | required | Radius of each satellite rosette |
| `tile_colors_a/b/c` | array | required | n colors each for three tile types per sector |

**Rendering:** For each of n sectors (angular width 360/n degrees), generates tiles that connect the star's outer edges to the satellite inner edges. Each sector produces 5-7 tiles (kites, triangles, quadrilaterals) that together fill the gap with no white space.

---

## Composition Rules

1. **Layer order matters** — layers render bottom-to-top. Background elements first, foreground last.
2. **Nested elements** — `radial-repeat` and `grid-repeat` contain an `element` field with a full layer definition (any type).
3. **Style inheritance** — if a nested element has no `style`, it inherits from the parent layer.
4. **Palette references** — use `$name` in any style string to reference `palette.colors.name`.
5. **Coordinate normalization** — all positions and radii are fractions of `min(width,height)/2`, centered at canvas center.

## Adding New Layer Types

The declarative language is extensible. To add a new layer type:

1. Define its `params` schema in this guide
2. Add rendering logic to `compile-d3.md`
3. Add GeoGebra translation to `compile-geogebra.md`
4. If it requires a new TypeScript primitive, document in `library-extension-guide.md`
