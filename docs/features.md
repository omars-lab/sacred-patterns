# Pattern Interpretation Tool — Feature Reference

Interactive D3.js overlay tool for reviewing and correcting Claude's geometric decomposition of a reference image. Located at `session-*/input/pattern-interpretation.html`.

## Toolbar

Compact icon buttons with hover tooltips. Buttons grey out when their action is unavailable.

| Icon | Button | Description |
|------|--------|-------------|
| **+** | Add Shape | Toggle add-shape mode. Click canvas to place vertices (min 3), click again to finish. |
| Trash | Delete Selected | Delete all selected shapes. Enabled when 1+ shapes selected. |
| Circle-X | Deselect All | Clear selection and shift-click anchor. Enabled when 1+ shapes selected. |
| Chain links | Group as Rotations | Group 2+ ungrouped selected shapes as rotational copies. Enters "pick center" mode — click any shape to set its centroid as the rotation center. |
| Dashed chain | Ungroup | Dissolve group membership for selected grouped shapes. |
| Reset arrow | Reset All Changes | Revert all shapes and groups to initial state. |
| Checkmark | Done | Serialize shape data to DOM for Claude extraction. |

## Selection Model

### Single Click
Click a shape in the sidebar or on the canvas overlay to select it. Click the same shape again to deselect.

### Cmd+Click (Multi-Select)
Hold **Cmd** (macOS) or **Ctrl** (Windows/Linux) and click to toggle individual shapes in/out of the selection set. Multiple shapes can be selected simultaneously.

### Shift+Click (Range Select)
Click a shape, then **Shift+click** another shape to select all shapes between them (in sidebar display order). The range anchor is the last shape clicked without Shift.

### Sidebar Order
Grouped shapes appear under their group header. Ungrouped shapes follow. Shift+click range selection follows this visual order.

## Shape Editing

### Vertex Handles
When a shape is selected, circular drag handles appear at each vertex. Drag a handle to move that vertex.

- **Double-click** a vertex handle to insert a new vertex at the midpoint of the next edge (the edge from that vertex to the next one)
- Click a handle to make it "active" (teal highlight) — this shows **+** midpoint markers on adjacent edges
- Click a **+** midpoint marker to insert a new vertex at that edge midpoint
- **Shift+click** an active vertex handle to delete that vertex (min 3 vertices enforced)

### Whole-Shape Drag
Drag the body of the primary selected shape to translate all its vertices together. A 2px dead zone prevents accidental drags during click-to-select.

### Property Editor
With a shape selected, the sidebar shows editable properties:
- **ID** — Unique shape identifier
- **Type** — polygon, star, kite, petal, rhombus, pentagon, hexagon, bowtie, band-segment, custom
- **Zone** — inner-star, rosette, transition, satellite, outer
- **Vertices** — Vertex count
- **Count** — Expected instance count in the pattern
- **Count Tolerance** — Acceptable variance in count
- **Area Ratio** — Proportional area relative to the pattern
- **Notes** — Free-text annotation

### Relationships
Add directional relationships between shapes (e.g., "adjacent_to", "rotation_of") via the Relationships section below the property editor.

## Canvas Controls

### Visibility Toggles
Each shape has a checkbox in the sidebar list. Uncheck to hide that shape's overlay on the canvas.

### Edge Overlay
The "Show Edges" checkbox toggles a pre-generated edge detection image (`edges.png`) over the reference, helping identify tile boundaries.

## Groups

Shapes can be grouped as rotational copies with a prototype/derived model:

### Creating a Group
1. Select 2+ ungrouped shapes (using Cmd+click or Shift+click)
2. Click the Group icon — enters **"pick center" mode** (crosshair cursor, status bar prompt)
3. Click any shape on canvas — that shape's centroid becomes the rotation center
4. The group is created: first selected shape becomes the **prototype**, all others become **derived**

### Pick Center Mode
- Status bar shows "Click a shape to set as rotation center."
- Group button shows active (highlighted) state
- Click any shape polygon to set center and finalize the group
- Click canvas background or Group button again to cancel
- Deselect All also cancels

### Prototype / Derived Model
- **Prototype** (first selected shape): fully editable with drag handles, vertex editing, property editing
- **Derived** members: reduced opacity, dashed stroke, no drag handles, non-editable
- Clicking a derived shape (on canvas or in sidebar) redirects selection to the prototype
- Sidebar shows derived shapes with "(derived)" label in italic
- All vertex edits on the prototype are automatically propagated to derived members via rotation around the center

### Visual Indicators
- **Crosshair marker** — red crosshair + dot drawn at the rotation center when a grouped shape is selected
- **Dashed stroke** — derived shapes render with `4,4` dash pattern at reduced opacity
- **Prototype info** — Group Properties panel shows which shape is the prototype

### Group Properties
When any group member is selected, the sidebar shows:
- **Label** — editable group name
- **Count** / **Angle Spacing** — member count and angular spacing (degrees)
- **Center X / Y** — rotation center coordinates (editable; changes trigger propagation)
- **Prototype** — read-only indicator of which shape is the prototype

### Other Group Operations
- Click a group header to collapse/expand its members
- Select any grouped shape and click Ungroup to dissolve the group

## Serialization

Clicking **Done** writes a JSON object to a `<script type="application/json" id="interpretation-data">` element in the DOM. Claude extracts this data to produce `baseline.json` for the A6 architectural audit. The output includes all shapes, groups, zones, and global feedback.

---

# Shape Extraction Tool — Feature Reference

Image-based shape extraction for pattern interpretation. Located at `tools/extract-shapes.py`.

## Pipeline

The extraction pipeline runs in 5 stages:

1. **Edge Detection** — Sobel filter on grayscale produces binary edge mask (`edges.png`)
2. **Image Classification + Barrier Detection** — Auto-classifies the image as `white-strapwork` or `general` by analyzing the luminance histogram. White-strapwork mode uses luminance-only barrier (no edge union, no dilation) with morphological closing to seal gaps. General mode preserves the original luminance-OR-edges approach. Outputs barrier mask as `strapwork.png`.
3. **Segmentation** — Two methods available (selectable via `--segmentation`):
   - **CCL** (Connected Component Labeling) — Default for `white-strapwork` mode. Inverts the barrier mask and labels connected foreground regions using a two-pass algorithm with Union-Find. Color-independent: two tiles of identical color separated by a 1px barrier get different labels. Uses 4-connectivity to prevent diagonal leakage.
   - **Watershed** — Default for `general` mode. Barrier-constrained flood fill that expands from seed pixels to color-similar neighbors. Falls back to per-color BFS if fewer than 3 regions found.
4. **Boundary Tracing + Refinement** — Moore neighborhood contour tracing, edge-guided boundary snapping, then simplification (Visvalingam-Whyatt for CCL mode, Douglas-Peucker for watershed), then geometry-aware polygon fitting (collinear merge, angle snapping to known Islamic geometry values, parallel edge snapping)
5. **Output** — All shapes sorted by area descending, with fill colors, normalized 0-1 vertices, zone classification

## Perceptual Color Distance

Color comparisons use a weighted Euclidean distance: `sqrt(2*dR^2 + 4*dG^2 + 3*dB^2)`. The green channel is weighted highest (4x) because human vision is most sensitive to green. This produces more perceptually uniform results than raw RGB distance.

## Adaptive Barrier Detection

The tool auto-classifies images into two modes based on their luminance histogram:

- **`white-strapwork`** — Detected when >30% of pixels are near-white (luminance > 245) and >20% are colored (luminance < 200) with <15% in the transition zone. Uses luminance-only barrier (no edge union, no dilation), sealed with morphological closing. This is the common case for Islamic patterns with white/cream strapwork bands.
- **`general`** — Fallback for non-bimodal images. Uses the original approach: barrier = bright pixels OR dilated edges.

Override auto-detection with `--mode white-strapwork` or `--mode general`.

### Why adaptive matters

The original approach (luminance > 200 OR dilated edges) produced 85% barrier coverage on bimodal images because light blue/cyan tiles (luminance ~206) were caught as "bright," and edge dilation expanded barriers 5-8px into tile centers. The adaptive approach drops this to ~59%, correctly isolating only the white bands.

### Morphological operations

- **Dilation** — Expands foreground regions by N pixels (shifted-array OR)
- **Erosion** — Shrinks foreground via complement dilation
- **Closing** (dilate then erode) — Seals 1-2px gaps in strapwork without expanding the overall boundary. Controlled by `--morph-close` (default 1).

## Geometry-Aware Polygon Fitting

After Douglas-Peucker simplification, three geometric refinements are applied:

1. **Collinear merge** — Removes vertices where consecutive edges form angles within 10 degrees of 180 (redundant collinear points)
2. **Angle snapping** — Snaps interior angles to known Islamic geometry values: 36, 45, 54, 60, 72, 90, 108, 120, 135, 144, 150, 160, 170, 180 degrees (within 8 degree tolerance)
3. **Parallel edge snapping** — For even-sided polygons, makes nearly-parallel opposite edges exactly parallel (within 5 degree tolerance)

## Output Format

`shapes.json` contains:
- `image_size` — `[width, height]` of the original image
- `edge_overlay_path` — filename of the edge detection PNG
- `strapwork_overlay_path` — filename of the strapwork barrier PNG
- `shapes` — array of shape objects, each with:
  - `id`, `type`, `zone`, `vertex_count`, `count`
  - `approximate_vertices` — normalized 0-1 coordinates
  - `approximate_area_ratio` — area as fraction of total image
  - `fill_color` — mean RGB color of the detected region (e.g., `rgb(38, 97, 191)`)
  - `overlay_color` — hex color for visualization
  - `notes` — auto-generated description

## CLI Arguments

| Argument | Default | Purpose |
|---|---|---|
| `--mode` | `auto` | Barrier detection mode: `auto`, `white-strapwork`, `general` |
| `--work-size` | 600 | Working resolution (higher = sharper, slower) |
| `--tolerance` | 60 | Color tolerance in perceptual distance |
| `--connectivity` | 8 | BFS connectivity (4 or 8); overridden to 4 in white-strapwork mode |
| `--luminance-threshold` | 240 | Barrier brightness cutoff (0-255) |
| `--edge-dilation` | 0 | Edge barrier dilation radius (only used in general mode) |
| `--morph-close` | 1 | Morphological closing radius for gap sealing |
| `--segmentation` | `auto` | Segmentation method: `auto` (CCL for white-strapwork, watershed for general), `ccl`, `watershed` |
| `--snap-radius` | 5 | Boundary-to-edge snapping radius |
| `--simplify` | 3.0 | Douglas-Peucker tolerance |
| `--colors` | 8 | Dominant colors to extract |
| `--edge-threshold` | 30 | Sobel edge threshold (0-255) |
| `--min-area` | 200 | Minimum component area in pixels; overridden to 100 in white-strapwork mode |

## Validation

After running `extract-shapes.py`, always visually inspect the outputs:

1. **`strapwork.png`** — Open in browser. White regions = barrier, black = tile interiors. White should trace only the strapwork bands, not colored tiles. If blue/cyan tiles appear white in the mask, the luminance threshold is too low.
2. **`edges.png`** — Edges should trace tile boundaries sharply. Overly thick/bleeding edges suggest `--edge-threshold` is too low.
3. **Console output** — Check barrier coverage %. For typical Islamic patterns with white strapwork, expect 55-65%. Coverage above 80% indicates tiles are being misclassified as barrier.
4. **`shapes.json`** — Check zone distribution (should span all zones, not just satellite) and area range (should vary, not cluster at one size).
