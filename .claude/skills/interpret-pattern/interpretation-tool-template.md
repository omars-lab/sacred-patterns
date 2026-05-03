# Interpretation Tool Template

Guide for generating the interactive `pattern-interpretation.html` file. Claude generates this HTML for each session based on the reference image and detected shapes.

For general design patterns (coordinate normalization, extraction channels, drag-conflict strategies, when to pre-generate vs compute in-browser), see `../collecting-feedback-on-components/feedback-tool-patterns.md`.

## Template-Based Generation

The tool is generated from a reusable template with session-specific data injected via placeholders.

### Placeholders

| Placeholder | Source | Example |
|---|---|---|
| `{{PATTERN_NAME}}` | `pattern-config.json` → `pattern.name` (title-cased) | `10 Fold Rosette Medallion` |
| `{{WIDTH}}` | `shapes.json` → `image_size[0]` | `753` |
| `{{HEIGHT}}` | `shapes.json` → `image_size[1]` | `722` |
| `{{REFERENCE_IMAGE_PATH}}` | Auto-detected from `input/reference.{jpg,png,webp}` | `reference.jpg` |
| `{{PATTERN_META_JSON}}` | `pattern-config.json` → `pattern` object | `{"name": "...", ...}` |
| `{{ZONES_JSON}}` | `pattern-config.json` → `zones` object | `{"inner-star": {...}, ...}` |
| `{{SHAPES_JSON}}` | `shapes.json` → `shapes` array (with defaults filled) | `[{"id": "shape-001", ...}, ...]` |

### Generation Protocol

```bash
# 1. Ensure shapes.json and pattern-config.json exist in input/
# 2. Generate HTML from template:
make interpret SESSION=<session-dir>
# or:
python3 tools/generate-interpretation.py <session-dir>
```

The script (`tools/generate-interpretation.py`) reads both JSON files, fills shape defaults (`count_tolerance`, `area_tolerance`, `visible`, `distance_from_center`), assigns overlay colors to shapes missing them, and writes the final HTML.

### Template Location

`templates/pattern-interpretation.html` — generic HTML with all CSS, toolbar, D3.js interaction logic. Only the 7 placeholders above are session-specific.

## Architecture

Single self-contained HTML file with inline CSS and JS. Uses D3.js v7 from CDN. No build step.

## Layout

Based on the `construction-overlay.html` pattern:

```
+--[Sidebar 340px]--+--[Main Canvas]--+
|  Shape List        |                 |
|  - [x] Star (10)   | Reference image |
|  - [x] Kites (10)  | as background   |
|  - [ ] Petals (10) |                 |
|  Properties Editor  | Edge overlay    |
|  - Type: [dropdown] | (toggle-able)   |
|  - Vertices: [num]  |                 |
|  - Zone: [dropdown] | SVG overlays    |
|  - Count: [num]     | on top          |
|  - Notes: [textarea]|                 |
|                     | Drag handles    |
|  Global Feedback    | on vertices     |
|  [textarea]         |                 |
|                     | Whole-shape     |
|  [x] Show Edges    | drag when       |
|                     | selected        |
|  [Add] [Del]       |                 |
|  [Reset] [Done]    |                 |
+--------------------+-----------------+
```

## HTML Structure

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Pattern Interpretation — {pattern_name}</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <style>/* inline styles */</style>
</head>
<body>
  <div id="sidebar">
    <h2>Shape Inventory</h2>
    <div id="shape-list"></div>
    <div id="property-editor"></div>
    <div id="global-feedback">
      <h3>Global Feedback</h3>
      <textarea id="feedback-text"></textarea>
    </div>
    <div id="toolbar">
      <button id="btn-add">Add Shape</button>
      <button id="btn-delete">Delete Selected</button>
      <button id="btn-done">Done</button>
    </div>
  </div>
  <div id="canvas">
    <svg id="main-svg"></svg>
  </div>
  <!-- Serialized output written by Done button -->
  <script type="application/json" id="interpretation-data"></script>
</body>
</html>
```

## CSS Patterns

Dark theme matching the analysis tools:

```css
body {
  margin: 0; font-family: monospace;
  display: flex; height: 100vh;
  background: #0a0a14; color: #e0e0e0;
}
#sidebar {
  width: 320px; padding: 16px;
  overflow-y: auto; border-right: 1px solid #333;
  display: flex; flex-direction: column; gap: 12px;
}
#canvas {
  flex: 1; display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}
#main-svg { max-width: 100%; max-height: 100%; }

/* Shape list items */
.shape-item {
  padding: 8px; border: 1px solid #333; border-radius: 4px;
  cursor: pointer; display: flex; align-items: center; gap: 8px;
}
.shape-item.selected { border-color: #7af; background: rgba(119,170,255,0.1); }
.shape-item .swatch {
  width: 16px; height: 16px; border-radius: 3px;
}

/* Property editors */
.prop-group { margin-bottom: 8px; }
.prop-group label { display: block; font-size: 11px; color: #888; margin-bottom: 2px; }
.prop-group input, .prop-group select, .prop-group textarea {
  width: 100%; padding: 4px; background: #1a1a2e; color: #e0e0e0;
  border: 1px solid #333; border-radius: 3px;
}

/* Toolbar */
#toolbar { display: flex; gap: 8px; flex-wrap: wrap; }
#toolbar button {
  padding: 8px 16px; border: 1px solid #555; border-radius: 4px;
  background: #1a1a2e; color: #e0e0e0; cursor: pointer;
}
#btn-done { background: #2a5a2a; border-color: #4a8a4a; font-weight: bold; }

/* Drag handles */
.drag-handle {
  fill: #fff; stroke: #7af; stroke-width: 2;
  cursor: grab; r: 5;
}
.drag-handle:hover { r: 7; }
```

## SVG Canvas Setup

```javascript
const width = 800, height = 800;
const svg = d3.select('#main-svg')
  .attr('width', width)
  .attr('height', height)
  .attr('viewBox', `0 0 ${width} ${height}`);

// Background layer — reference image
svg.append('image')
  .attr('href', REFERENCE_IMAGE_DATA_URL)  // Base64-encoded or relative path
  .attr('width', width)
  .attr('height', height)
  .attr('preserveAspectRatio', 'xMidYMid meet');

// Shape overlay layer
const overlayGroup = svg.append('g').attr('id', 'overlays');

// Drag handle layer (above overlays)
const handleGroup = svg.append('g').attr('id', 'handles');
```

## Reference Image Handling

The reference image must be embedded or accessible. Two approaches:

1. **Base64 data URL** — Claude reads the image file, base64-encodes it, and embeds as `data:image/jpeg;base64,...`. Works offline, larger file size.
2. **Relative path** — Use `../reference.{ext}` relative to the HTML file location. Simpler but requires correct file placement.

Prefer approach 2 (relative path) since the HTML lives in `input/` alongside the reference image:

```javascript
const REFERENCE_IMAGE_PATH = 'reference.jpg';  // Same directory
```

## Shape Overlay Rendering

Each shape is rendered as a semi-transparent polygon with a colored stroke:

```javascript
function renderShapeOverlay(shape, isSelected) {
  const overlay = overlayGroup.append('polygon')
    .attr('points', shape.approximate_vertices.map(v =>
      `${v[0] * width},${v[1] * height}`).join(' '))
    .attr('fill', shape.overlay_color)
    .attr('fill-opacity', isSelected ? 0.4 : 0.2)
    .attr('stroke', isSelected ? '#fff' : shape.overlay_color)
    .attr('stroke-width', isSelected ? 2 : 1)
    .attr('data-shape-id', shape.id)
    .on('click', () => selectShape(shape.id));

  return overlay;
}
```

## Vertex Drag Behavior

D3 drag for moving shape vertices:

```javascript
const drag = d3.drag()
  .on('start', function(event) {
    d3.select(this).raise().attr('stroke-width', 3);
  })
  .on('drag', function(event, d) {
    const x = Math.max(0, Math.min(width, event.x));
    const y = Math.max(0, Math.min(height, event.y));
    d3.select(this).attr('cx', x).attr('cy', y);
    // Update shape vertex
    d.vertex[0] = x / width;
    d.vertex[1] = y / height;
    // Re-render the polygon
    updatePolygonPoints(d.shapeId);
  })
  .on('end', function() {
    d3.select(this).attr('stroke-width', 2);
  });

function renderDragHandles(shape) {
  handleGroup.selectAll(`.handle-${shape.id}`).remove();

  shape.approximate_vertices.forEach((v, i) => {
    handleGroup.append('circle')
      .attr('class', `drag-handle handle-${shape.id}`)
      .attr('cx', v[0] * width)
      .attr('cy', v[1] * height)
      .attr('r', 5)
      .datum({ shapeId: shape.id, vertexIndex: i, vertex: v })
      .call(drag);
  });
}
```

## Sidebar: Shape List

```javascript
function renderShapeList() {
  const list = d3.select('#shape-list');
  list.selectAll('.shape-item').remove();

  shapes.forEach(shape => {
    const item = list.append('div')
      .attr('class', `shape-item ${shape.id === selectedId ? 'selected' : ''}`)
      .on('click', () => selectShape(shape.id));

    item.append('input')
      .attr('type', 'checkbox')
      .property('checked', shape.visible !== false)
      .on('change', (e) => { shape.visible = e.target.checked; renderOverlays(); });

    item.append('div')
      .attr('class', 'swatch')
      .style('background', shape.overlay_color);

    item.append('span')
      .text(`${shape.id} (${shape.vertex_count}-gon, ×${shape.count})`);
  });
}
```

## Sidebar: Property Editor

When a shape is selected, show editable properties:

```javascript
function renderPropertyEditor(shape) {
  const editor = d3.select('#property-editor');
  editor.html('');  // Clear

  if (!shape) return;

  const fields = [
    { key: 'id', label: 'ID', type: 'text' },
    { key: 'type', label: 'Type', type: 'select',
      options: ['star','polygon','kite','petal','rhombus','pentagon','hexagon','bowtie','band-segment','custom'] },
    { key: 'vertex_count', label: 'Vertex Count', type: 'number' },
    { key: 'zone', label: 'Zone', type: 'select',
      options: ['inner-star','rosette','transition','satellite','outer'] },
    { key: 'count', label: 'Expected Count', type: 'number' },
    { key: 'count_tolerance', label: 'Count Tolerance', type: 'number' },
    { key: 'approximate_area_ratio', label: 'Area Ratio (0-1)', type: 'number', step: '0.01' },
    { key: 'area_tolerance', label: 'Area Tolerance (0-1)', type: 'number', step: '0.1' },
    { key: 'notes', label: 'Notes', type: 'textarea' },
  ];

  fields.forEach(f => {
    const group = editor.append('div').attr('class', 'prop-group');
    group.append('label').text(f.label);

    if (f.type === 'select') {
      const sel = group.append('select')
        .on('change', (e) => { shape[f.key] = e.target.value; });
      f.options.forEach(opt => {
        sel.append('option').attr('value', opt).text(opt)
          .property('selected', shape[f.key] === opt);
      });
    } else if (f.type === 'textarea') {
      group.append('textarea').attr('rows', 3)
        .property('value', shape[f.key] || '')
        .on('input', (e) => { shape[f.key] = e.target.value; });
    } else {
      group.append('input').attr('type', f.type)
        .attr('step', f.step || null)
        .property('value', shape[f.key] ?? '')
        .on('input', (e) => {
          shape[f.key] = f.type === 'number' ? +e.target.value : e.target.value;
        });
    }
  });
}
```

## Add Shape Mode

Toggle a mode where clicking on the canvas adds vertices to a new polygon:

```javascript
let addMode = false;
let newVertices = [];

d3.select('#btn-add').on('click', () => {
  addMode = !addMode;
  d3.select('#btn-add').text(addMode ? 'Finish Shape (click)' : 'Add Shape');
  if (!addMode && newVertices.length >= 3) {
    // Create new shape from collected vertices
    const newShape = {
      id: `shape-${Date.now()}`,
      type: 'custom',
      zone: 'transition',
      vertex_count: newVertices.length,
      count: 1,
      count_tolerance: 0,
      overlay_color: COLORS[shapes.length % COLORS.length],
      approximate_vertices: newVertices.slice(),
      notes: '',
    };
    shapes.push(newShape);
    newVertices = [];
    renderAll();
  }
});

svg.on('click', (event) => {
  if (!addMode) return;
  const [x, y] = d3.pointer(event);
  newVertices.push([x / width, y / height]);
  // Show preview dot
  overlayGroup.append('circle')
    .attr('class', 'preview-dot')
    .attr('cx', x).attr('cy', y).attr('r', 4)
    .attr('fill', '#7af');
});
```

## Done Button — DOM Serialization

The "Done" button serializes all state into a JSON element in the DOM:

```javascript
d3.select('#btn-done').on('click', () => {
  const output = {
    timestamp: new Date().toISOString(),
    shapes: shapes.map(s => ({
      id: s.id,
      type: s.type,
      zone: s.zone,
      vertex_count: s.vertex_count,
      count: s.count,
      count_tolerance: s.count_tolerance || 0,
      approximate_area_ratio: s.approximate_area_ratio || null,
      area_tolerance: s.area_tolerance || 0.3,
      distance_from_center: s.distance_from_center || null,
      approximate_vertices: s.approximate_vertices,
      notes: s.notes || '',
    })),
    feedback: document.getElementById('feedback-text').value,
    zones: currentZones,  // Zone definitions (editable if we add zone controls)
  };

  document.getElementById('interpretation-data').textContent = JSON.stringify(output);

  // Visual confirmation
  d3.select('#btn-done')
    .text('Saved!')
    .style('background', '#4a8a4a');
  setTimeout(() => {
    d3.select('#btn-done')
      .text('Done')
      .style('background', '#2a5a2a');
  }, 2000);
});
```

## Claude Extraction Protocol

After the user clicks "Done", Claude extracts the data:

```javascript
// Run via evaluate_script or javascript_tool
() => {
  const el = document.getElementById('interpretation-data');
  return el ? JSON.parse(el.textContent) : null;
}
```

If the result is `null`, the user hasn't clicked "Done" yet — prompt them to click it.

## Color Palette for Overlays

Distinct colors for up to 12 shape classes:

```javascript
const COLORS = [
  '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4',
  '#ffeaa7', '#dfe6e9', '#fd79a8', '#6c5ce7',
  '#00b894', '#e17055', '#0984e3', '#fdcb6e',
];
```

## Edge Overlay (Pre-Generated)

The tool loads a pre-generated edge detection PNG between the reference image and shape overlays. Produced by `tools/extract-shapes.py`, not computed in-browser.

### SVG Layer

Insert after the reference `<image>` and before the overlay `<g>`:

```javascript
const edgeOverlay = svg.append('image')
  .attr('id', 'edge-overlay')
  .attr('href', 'edges.png')
  .attr('width', WIDTH).attr('height', HEIGHT)
  .attr('opacity', 0.6)
  .style('display', 'none');  // Initially hidden
```

### Toggle Control

Checkbox in the sidebar before the toolbar:

```html
<div class="tool-row">
  <input type="checkbox" id="toggle-edges">
  <label for="toggle-edges">Show Edges</label>
</div>
```

```javascript
d3.select('#toggle-edges').on('change', function() {
  edgeOverlay.style('display', this.checked ? 'block' : 'none');
});
```

## Whole-Shape Drag

When a shape is selected, dragging the polygon body translates all vertices together. See `feedback-tool-patterns.md` for the full pattern and rationale.

Key points:
- Attach `shapeDrag` to polygon only when `isSelected` (non-selected polygons get click-to-select)
- Snapshot all vertex positions on `dragstart`, compute delta, never cumulative
- 2px dead zone: if no significant movement, treat as click-to-deselect
- Must update both polygon points AND handle circle positions during drag

```javascript
// In renderOverlays(), for selected shapes:
poly.datum({ shape: shape }).call(shapeDrag);
// cursor: 'move' for selected, 'pointer' for unselected
```

## Reset Button

Reverts all shapes to their initial positions (from Python extraction or Claude's generation).

```javascript
// At init, deep-copy shapes
const initialShapes = JSON.parse(JSON.stringify(shapes));

// Reset handler
d3.select('#btn-reset').on('click', function() {
  shapes = JSON.parse(JSON.stringify(initialShapes));
  selectedId = null;
  renderAll();
});
```

Button style: amber border (`#a86`), amber text (`#fc8`).

## Pre-Generation with extract-shapes.py

Before generating the HTML, Claude can run image analysis to produce pixel-accurate initial overlays:

```bash
python3 tools/extract-shapes.py reference.jpg --output shapes.json
```

This produces:
- `shapes.json` — detected shapes with normalized 0-1 vertices
- `edges.png` — Sobel edge overlay for the toggle

Claude reads `shapes.json` and uses its shapes as the initial `shapes` array in the HTML, replacing trig-based approximations with image-derived boundaries. The user then fine-tunes rather than placing from scratch.

## Multi-Select Pattern

By default, the tool uses single-select (`selectedIds` is a `Set` with 0 or 1 entries). Toggle "Select Multiple" to enter group mode, where clicking adds/removes shapes from the set.

```javascript
let selectedIds = new Set();
let groupMode = false;

function selectShape(id) {
  if (groupMode) {
    // Toggle Set membership
    selectedIds.has(id) ? selectedIds.delete(id) : selectedIds.add(id);
  } else {
    // Single-select with toggle
    if (selectedIds.size === 1 && selectedIds.has(id)) {
      selectedIds.clear();
    } else {
      selectedIds.clear();
      selectedIds.add(id);
    }
  }
  renderAll();
}

function primarySelectedShape() {
  if (selectedIds.size === 0) return null;
  return shapes.find(s => s.id === [...selectedIds][0]);
}
```

Only the **primary** selected shape (first in the Set) gets drag handles and the property editor. All selected shapes get highlighted overlays.

## Rotational Grouping

Groups model shapes that are rotational copies of each other around a center point.

**Data model:**
```javascript
let groups = [];
// Each group:
{ id, label, rotation_center: [x,y], count, angular_spacing, member_ids: [],
  propagate_edits: false, _collapsed: false }
```

- Created by selecting 2+ ungrouped shapes and clicking "Group as Rotations"
- Rotation center = centroid of all members' centroids
- Angular spacing = 360 / count
- All members adopt the first shape's overlay color
- Members display `shape.group = groupId`

**Shape list rendering:** Group headers render as collapsible rows above members. Ungrouped shapes render after all groups.

**Edit propagation:** When `group.propagate_edits` is ON, vertex edits on any member are rotated to all other members around the rotation center.

## Relationships Editor

Shapes can have semantic connections to other shapes:

```javascript
shape.relationships = [
  { type: 'partial-form', target: 'central-star', notes: '...' },
  { type: 'scaled-copy', target: 'central-star', scale: 0.5, notes: '' }
]
```

- Types: `partial-form`, `scaled-copy`, `custom`
- `scaled-copy` shows an additional scale input
- Teal dotted lines drawn from selected shape's centroid to each target's centroid
- Lines only visible when shape is selected (reduces clutter)

## Generation Checklist

When generating `pattern-interpretation.html`, Claude must:

1. **Run image analysis** — `python3 tools/extract-shapes.py reference.jpg` to get `shapes.json` + `edges.png`
2. Merge Claude's visual analysis with `shapes.json` data — update the shapes array in `shapes.json`
3. Write `input/pattern-config.json` with pattern metadata and zone definitions
4. **Generate HTML from template** — `make interpret SESSION=<session-dir>`
5. Open in browser for user review

The template handles all UI code (toolbar, drag, multi-select, reset, done). Claude only needs to produce the two JSON files.
