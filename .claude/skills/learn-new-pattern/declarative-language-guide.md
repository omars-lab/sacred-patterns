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
