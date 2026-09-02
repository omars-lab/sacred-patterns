# baseline.json Schema

Machine-readable ground truth for the A6 Baseline Shape Validation audit. Generated from the user-corrected pattern interpretation tool.

## Full Schema

```json
{
  "version": "1.2",
  "pattern": {
    "name": "pattern-name",
    "symmetry_order": 10,
    "star_notation": "{10/4}"
  },
  "zones": {
    "inner-star": { "r_min": 0, "r_max": 0.35 },
    "rosette": { "r_min": 0.35, "r_max": 0.55 },
    "transition": { "r_min": 0.55, "r_max": 0.86 },
    "satellite": {
      "centers_at_distance": 0.64,
      "radius": 0.22
    },
    "outer": { "r_min": 0.86, "r_max": 1.0 }
  },
  "expected_shapes": [
    {
      "id": "central-star",
      "type": "star",
      "zone": "inner-star",
      "vertex_count": 10,
      "count": 1,
      "count_tolerance": 0,
      "approximate_area_ratio": 0.08,
      "area_tolerance": 0.3,
      "distance_from_center": { "min": 0, "max": 0.15 },
      "notes": "10-pointed star formed by {10/4} diagonal intersections"
    },
    {
      "id": "transition-tile",
      "type": "polygon",
      "zone": "transition",
      "vertex_count": 7,
      "count": 10,
      "group": "group-transition-tiles",
      "relationships": [
        { "type": "partial-form", "target": "central-star", "notes": "truncated at band crossing" }
      ]
    }
  ],
  "groups": [
    {
      "id": "group-transition-tiles",
      "label": "Transition Tiles",
      "rotation_center": [0.5, 0.5],
      "count": 10,
      "angular_spacing": 36,
      "member_ids": ["transition-tile"]
    }
  ],
  "user_feedback": "Global notes from the user about the pattern interpretation"
}
```

## Field Reference

### Top Level

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | yes | Schema version, currently `"1.1"` |
| `pattern` | object | yes | Pattern metadata |
| `zones` | object | yes | Zone boundary definitions (normalized 0-1 relative to pattern radius R) |
| `expected_shapes` | array | yes | Shape expectations for A6 validation |
| `groups` | array | no | Rotational grouping definitions (v1.1+) |
| `user_feedback` | string | no | Global feedback from user review |

### pattern

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Human-readable pattern name |
| `symmetry_order` | integer | yes | N-fold symmetry (e.g., 10 for decagonal) |
| `star_notation` | string | no | Star polygon notation e.g., `"{10/4}"` |

### zones

Each zone defines a radial band. All values are normalized 0-1 where 1.0 = pattern radius R (the clip circle radius).

**Radial zones** have `r_min` and `r_max`:

| Field | Type | Description |
|-------|------|-------------|
| `r_min` | number | Inner boundary as fraction of R |
| `r_max` | number | Outer boundary as fraction of R |

**Satellite zone** is special — defined by center positions and radius:

| Field | Type | Description |
|-------|------|-------------|
| `centers_at_distance` | number | Distance from pattern center to satellite centers, as fraction of R |
| `radius` | number | Satellite circle radius as fraction of R |

### expected_shapes[]

Each entry describes a class of shapes expected in the SVG output.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique identifier (e.g., `"central-star"`, `"kites"`, `"hex-petals"`) |
| `type` | string | yes | Shape type: `circle` (v1.2+), `star`, `polygon`, `kite`, `petal`, `rhombus`, `pentagon`, `hexagon`, `bowtie`, `band-segment`, `custom`. **v1.2 (qiyas#138 Option G, 2026-05-24):** `type` is the sole authoritative discriminator. Circles serialize as `type=circle, vertex_count=0` (was `type=polygon, vertex_count=0, notes="qiyas type: circle"` in v1.1). |
| `zone` | string | yes | Which zone this shape lives in: `inner-star`, `rosette`, `transition`, `satellite`, `outer` |
| `vertex_count` | integer | yes | Expected number of vertices per polygon |
| `count` | integer | yes | Expected number of instances |
| `count_tolerance` | integer | no | Acceptable deviation from count (default: 0). Use for shapes where exact count may vary due to clipping |
| `approximate_area_ratio` | number | no | Expected average area of one instance as fraction of total medallion area |
| `area_tolerance` | number | no | Acceptable fractional deviation from area ratio (default: 0.3 = 30%) |
| `distance_from_center` | object | no | `{ "min": 0, "max": 0.5 }` — centroid distance range, normalized to R |
| `notes` | string | no | User/Claude notes about this shape. **v1.2:** informational only — never parsed as a discriminator. Single-qiyas-type buckets drop `notes`; only multi-type collapses (e.g. equilateral/isoceles/right triangle → polygon[vc=3]) retain it for human review. |
| `group` | string | no | Group ID if this shape belongs to a rotational group (v1.1+) |
| `relationships` | array | no | Semantic connections to other shapes (v1.1+) |

### relationships[] (per shape, optional)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | yes | `partial-form`, `scaled-copy`, or `custom` |
| `target` | string | yes | ID of the related shape |
| `scale` | number | no | Scale factor (only for `scaled-copy`) |
| `notes` | string | no | Free-text annotation |

### groups[] (top-level, optional)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Unique group identifier |
| `label` | string | yes | Human-readable label |
| `rotation_center` | [number, number] | yes | Center of rotation in normalized 0-1 coords |
| `count` | integer | yes | Number of member shapes |
| `angular_spacing` | number | yes | Degrees between rotational copies (360/count) |
| `member_ids` | string[] | yes | IDs of shapes in this group |

## Shape Matching Rules (A6 Audit Logic)

For each entry in `expected_shapes`, the audit:

1. **Filter by vertex count** — Select SVG polygons with exactly `vertex_count` vertices
2. **Filter by zone** — Keep only polygons whose centroid falls within the zone's radial band. For satellite zone: centroid within `radius` of any satellite center
3. **Check count** — Compare filtered count against `count ± count_tolerance`
4. **Check area** (if `approximate_area_ratio` provided) — Compute average polygon area as fraction of medallion area. Compare against expected ± `area_tolerance` fraction
5. **Report status**:
   - **PASS** — Count matches (within tolerance) and area approximately correct
   - **PARTIAL** — Some found but count is off (outside tolerance)
   - **MISSING** — Zero polygons match the filters
   - **EXCESS** — Found significantly more than expected (> count + count_tolerance)

## Normalization

All distances in baseline.json are normalized 0-1 relative to pattern radius R.

The audit tool (`qiyas svg-audit`) auto-detects R from the encoding's pattern radius and scales baseline values to pixel coordinates:

```python
# In qiyas svg-audit's A6 audit:
pixel_distance = normalized_distance * R_px
pixel_area = normalized_area * medallion_area_px
```

This means baseline.json is resolution-independent — the same file works whether the SVG is 800px or 2000px.

## Example: 10-fold Rosette Pattern

```json
{
  "version": "1.0",
  "pattern": {
    "name": "10-fold-rosette-medallion",
    "symmetry_order": 10,
    "star_notation": "{10/4}"
  },
  "zones": {
    "inner-star": { "r_min": 0, "r_max": 0.35 },
    "rosette": { "r_min": 0.35, "r_max": 0.55 },
    "transition": { "r_min": 0.55, "r_max": 0.86 },
    "satellite": { "centers_at_distance": 0.64, "radius": 0.22 }
  },
  "expected_shapes": [
    {
      "id": "central-star",
      "type": "star",
      "zone": "inner-star",
      "vertex_count": 10,
      "count": 1,
      "count_tolerance": 0,
      "approximate_area_ratio": 0.08,
      "area_tolerance": 0.3,
      "distance_from_center": { "min": 0, "max": 0.15 }
    },
    {
      "id": "kites",
      "type": "kite",
      "zone": "rosette",
      "vertex_count": 4,
      "count": 10,
      "count_tolerance": 2,
      "distance_from_center": { "min": 0.2, "max": 0.5 }
    },
    {
      "id": "hex-petals",
      "type": "petal",
      "zone": "rosette",
      "vertex_count": 6,
      "count": 10,
      "count_tolerance": 2,
      "distance_from_center": { "min": 0.35, "max": 0.55 }
    },
    {
      "id": "interstitial-tiles",
      "type": "polygon",
      "zone": "transition",
      "vertex_count": 5,
      "count": 20,
      "count_tolerance": 5,
      "distance_from_center": { "min": 0.5, "max": 0.85 }
    },
    {
      "id": "satellite-inner-stars",
      "type": "star",
      "zone": "satellite",
      "vertex_count": 10,
      "count": 10,
      "count_tolerance": 2
    },
    {
      "id": "satellite-kites",
      "type": "kite",
      "zone": "satellite",
      "vertex_count": 4,
      "count": 100,
      "count_tolerance": 20
    },
    {
      "id": "band-segments",
      "type": "band-segment",
      "zone": "transition",
      "vertex_count": 4,
      "count": 50,
      "count_tolerance": 15,
      "notes": "White strapwork band quadrilaterals"
    }
  ]
}
```
