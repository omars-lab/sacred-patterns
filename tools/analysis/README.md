# Geometric Analysis Tools

Interactive D3.js visualization tools for decomposing and understanding Islamic geometric patterns. Each tool is a self-contained HTML page — open as `file:///` URLs with query parameters.

## Tools

### 1. Star Intersection Map (`star-intersection-map.html`)

Maps ALL diagonal intersections of a {n/k} star polygon.

**What it shows:**
- Intersection points colored by radius group
- Concentric radius circles at each intersection distance
- All diagonal lines with tip labels (0..n-1)
- Parallel diagonal pairs highlighted
- Hover info for each intersection (which diags, exact radius)

**Key insight:** How many intersections exist? At what radii? Which diagonal pairs are parallel (and therefore create no intersections in the interstitial zone)?

**Parameters:**
```
?n=10&k=4&R=0.55
```

| Param | Default | Description |
|-------|---------|-------------|
| `n` | 10 | Number of star tips |
| `k` | 4 | Star polygon skip (connect every k-th vertex) |
| `R` | 0.55 | Star outer radius (normalized to canvas) |

**Example findings for {10/4}:**
- 40 total intersections at 4 concentric radii
- 5 parallel pairs: (0,5), (1,6), (2,7), (3,8), (4,9)
- Radii: r/R = 0.325, 0.382, 0.526, 1.000

---

### 2. Sector Decomposition (`sector-decomposition.html`)

For each interstitial sector (gap between adjacent star tips), shows which diagonals pass through it and whether they're parallel.

**What it shows:**
- Clickable sector buttons to select which sectors to analyze
- Highlighted sector wedge with the two diagonals passing through it
- Band edge lines (L/R offsets from center-line)
- Parallel/intersecting status with separation distance
- Summary of all sectors' parallel status

**Key insight:** Do the bands entering each gap cross or run parallel? This determines whether face decomposition can work in the interstitial zone.

**Parameters:**
```
?n=10&k=4&R=0.55&bandWidth=0.025&satDist=0.64&satR=0.22&sector=0,1,2
```

| Param | Default | Description |
|-------|---------|-------------|
| `n` | 10 | Number of star tips |
| `k` | 4 | Star polygon skip |
| `R` | 0.55 | Star outer radius |
| `bandWidth` | 0.025 | Half-width of strapwork bands |
| `satDist` | 0.64 | Satellite center distance from origin |
| `satR` | 0.22 | Satellite radius |
| `sector` | 0 | Comma-separated sector indices to highlight |

**Example findings for {10/4}:**
- All 10 sectors have exactly 2 parallel diagonals (separation ~0.34)
- No cross-bands — face decomposition fails in interstitial zone
- Must use Strategy 9 (per-sector explicit tile construction)

---

### 3. Tile Decomposition (`tile-decomposition.html`)

Computes and labels all tile vertices in ONE fundamental sector using intersection-based and line-circle geometry.

**What it shows:**
- Labeled tile outlines (kite, rhombus, petal, wing, between-band)
- Toggleable layers: star tiles, interstitial, band edges, vertices, labels, diagonals
- Vertex coordinates table with construction formulas
- Edge lengths and vertex angles for each tile
- Color-coded tiles by type

**Key insight:** What exact shapes fill each sector? What are their vertex coordinates?

**Parameters:**
```
?n=10&k=4&R=0.55&bandWidth=0.025&satDist=0.64&satR=0.22&sector=0
```

| Param | Default | Description |
|-------|---------|-------------|
| `sector` | 0 | Which sector to analyze (0 to n-1) |
| (others) | — | Same as sector-decomposition |

**Example findings for {10/4}, sector 0:**
- 8 tiles: Kite, Rhombus A, Rhombus B, Petal A, Petal B, Between-band, Wing A, Wing B
- Star tiles (kite + rhombi) use tipData() intersections
- Interstitial tiles use line-circle intersections at zone boundaries

---

### 4. Construction Overlay (`construction-overlay.html`)

Master visualization combining all analysis layers into one labeled diagram.

**What it shows:**
- Full pattern rendering (star tiles + interstitial + satellites + strapwork)
- 10 toggleable layers: Diagonals, Band edges, Intersections, Radius circles, Sector boundaries, Star tiles, Interstitial tiles, Satellites, Strapwork bands, Tip labels
- Interactive parameter sliders (R, band width, satellite distance, satellite radius)
- Statistics panel (tile counts, intersection count, radii values)
- "All On" / "All Off" buttons for quick layer management

**Key insight:** See how all geometric elements relate to each other. Toggle layers to isolate specific structures.

**Parameters:**
```
?n=10&k=4&R=0.55&bandWidth=0.025&satDist=0.64&satR=0.22
```

All parameters from sector-decomposition, plus interactive sliders.

---

## Workflow: When to Use Each Tool

### Before First Iteration (Geometric Pre-Analysis)

1. **Star Intersection Map** — Establish the diagonal framework. How many intersections? At what radii? Any parallel pairs?
2. **Sector Decomposition** — Understand the interstitial zone. Do bands cross or run parallel? What decomposition strategy is needed?
3. **Tile Decomposition** — Compute exact tile vertices for one sector. Identify all tile shapes.
4. **Construction Overlay** — Verify the full pattern renders correctly with all elements. Use layer toggles to isolate problem areas.

### During Iterations

- Use **Construction Overlay** to compare your iteration output against the analysis tools' predictions
- Use **Tile Decomposition** to verify specific tile vertex coordinates when shapes look wrong
- Use **Sector Decomposition** to debug interstitial tile issues

### Shared Geometry Functions

All tools share these core functions (inlined in each HTML):

```javascript
lineIntersect(p1, p2, p3, p4)     // Line-line intersection
lineCircle(line, r, nearAngle)     // Line-circle intersection (nearest to angle)
edgeLine(di, side)                 // Band edge line (L/R offset from center-line)
distToLine(pt, line)               // Perpendicular distance point-to-line
tipData(s)                         // Per-tip intersection analysis
buildDiagonalFramework(n, k, R)    // Compute all diagonals with direction vectors
computeAllIntersections(diags)     // All pairwise intersections
identifyParallelPairs(n, k)        // Which diagonal pairs are parallel
```

### 5. SVG Census (`svg-census.html`)

Extracts a quantitative tile census from any iteration's SVG output.

**What it shows:**
- Total polygon, line, and circle counts
- Breakdown by vertex count (triangles, quads, pentagons, etc.)
- Breakdown by fill color with area totals
- Coverage percentage (total tile area / canvas area)
- SVG preview with original colors
- Tile map recolored by vertex count
- Exportable JSON census

**Key insight:** How many tiles does this iteration have? What shapes? How much coverage? Track quantitative progress across iterations.

**Usage:** Load an HTML or SVG file via the file picker, or paste SVG markup directly.

---

### 6. SVG Diff (`svg-diff.html`)

Compares two SVGs at the tile level using centroid proximity matching.

**What it shows:**
- Side-by-side diff-colored SVGs (green=matched, red=current only, blue=reference only)
- Overlay view combining both SVGs
- Census comparison table (polygon count, line count, coverage, color delta)
- By-vertex-count comparison (how many triangles/quads/pentagons in each)
- By-color comparison
- Configurable match tolerance (px)
- Exportable diff report JSON

**Key insight:** What tiles are extra? What tiles are missing? What's the match percentage between iterations or between an iteration and a reference recreation?

**Usage:** Load two HTML/SVG files (current iteration + reference), click "Run Diff".

---

## Adding New Tools

Each tool follows the same pattern:
1. Self-contained HTML with inline JS/CSS
2. D3.js v7 loaded from CDN
3. URL query parameters for all geometric inputs
4. Sidebar with controls + statistics
5. Main SVG canvas with the visualization
6. No build step — just open the file
