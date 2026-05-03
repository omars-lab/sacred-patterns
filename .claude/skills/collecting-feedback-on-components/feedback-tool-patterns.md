# Feedback Tool Patterns

Reusable design patterns for building browser-based tools where Claude presents work, the user reviews and corrects it, and Claude extracts the corrected data. Referenced by both `interpret-pattern` and `collecting-feedback-on-components`.

## The Core Pattern

```
Claude generates artifact → HTML tool renders it → User corrects in browser → Claude extracts via DOM → Corrected data feeds downstream
```

Every feedback tool in this project follows this loop. The specifics vary (overlays vs. cards, JSON vs. clipboard, shapes vs. colors), but the architecture is the same.

## Architecture: Two-Panel Layout

All feedback tools use a sidebar + canvas split:

```
+--[Sidebar 320-340px]--+--[Main Canvas]--+
|  Item list             | SVG or content  |
|  Property editor       | area            |
|  Global feedback       |                 |
|  Action toolbar        |                 |
+------------------------+-----------------+
```

**Why this layout:**
- Sidebar gives structured editing without occluding the visual
- Canvas fills remaining space, responsive to window size
- Dark theme (`#0a0a14` background) reduces eye strain when comparing overlays against colorful reference images

**CSS foundation:**
```css
body { display: flex; height: 100vh; background: #0a0a14; color: #e0e0e0; }
#sidebar { width: 340px; overflow-y: auto; border-right: 1px solid #333; }
#canvas { flex: 1; display: flex; align-items: center; justify-content: center; }
```

## SVG Layer Stack

When the tool overlays shapes on a reference image, the SVG layers matter:

```
Bottom:  <image> — reference image (always visible)
         <image> — edge overlay (toggle-able, from pre-generated PNG)
         <g id="overlays"> — shape polygons (semi-transparent, clickable)
Top:     <g id="handles"> — drag handles (above everything, only for selected shape)
```

**Why this order:**
- Reference image must be behind everything
- Edge overlay between reference and shapes so shapes remain clickable
- Handles above overlays so they're always grabbable even at polygon edges

## Coordinate System: Normalized 0-1

All vertex positions are stored as **normalized 0-1 fractions** relative to the canvas dimensions, not pixel values.

```javascript
// Store: [0.5, 0.3] meaning "50% across, 30% down"
// Render: [0.5 * WIDTH, 0.3 * HEIGHT] → actual pixel position
// On drag: vertex[0] = event.x / WIDTH
```

**Why normalized:**
- Resolution-independent — same data works on any canvas size
- Matches the downstream `baseline.json` schema (all distances relative to R)
- Avoids coupling tool output to the specific image dimensions

**Gotcha:** When adding zoom/pan in the future, the normalized system must survive. Pointer events under zoom need inverse-transform before normalization: `const [x, y] = d3.pointer(event, svg.node())` then apply inverse of current zoom transform before dividing by WIDTH/HEIGHT.

## Interaction Patterns

### Selection Model

Single-selection with toggle:

```javascript
let selectedId = null;
function selectShape(id) {
  selectedId = (selectedId === id) ? null : id;
  renderAll();
}
```

**Why toggle:** The user needs to deselect to see the unmodified reference underneath. Double-selection patterns (click to select, click elsewhere to deselect) create confusion about where "elsewhere" is on a busy canvas.

### Vertex Drag (Per-Handle)

For adjusting individual polygon vertices:

```javascript
const drag = d3.drag()
  .on('drag', function(event, d) {
    const x = Math.max(0, Math.min(WIDTH, event.x));
    const y = Math.max(0, Math.min(HEIGHT, event.y));
    d3.select(this).attr('cx', x).attr('cy', y);
    d.vertex[0] = x / WIDTH;
    d.vertex[1] = y / HEIGHT;
    updatePolygonPoints(d.shapeId);
  });
```

- Handles are `<circle r="5">` with `cursor: grab`
- Clamped to canvas bounds
- Updates the polygon points string in real time

### Whole-Shape Drag (Translate All Vertices)

For repositioning an entire shape without distorting it:

```javascript
const shapeDrag = d3.drag()
  .on('start', function(event, d) {
    d._dragStartX = event.x;
    d._dragStartY = event.y;
    d._didMove = false;
    d._dragStartVerts = d.shape.approximate_vertices.map(v => [v[0], v[1]]);
  })
  .on('drag', function(event, d) {
    const dx = (event.x - d._dragStartX) / WIDTH;
    const dy = (event.y - d._dragStartY) / HEIGHT;
    if (Math.abs(event.x - d._dragStartX) > 2 || Math.abs(event.y - d._dragStartY) > 2)
      d._didMove = true;
    d.shape.approximate_vertices.forEach((v, i) => {
      v[0] = d._dragStartVerts[i][0] + dx;
      v[1] = d._dragStartVerts[i][1] + dy;
    });
    updatePolygonPoints(d.shape.id);
    // Also update handle positions
  })
  .on('end', function(event, d) {
    if (!d._didMove) { selectedId = null; renderAll(); } // click-to-deselect
  });
```

**Design decisions:**
- Attached to the polygon `<polygon>` body, only when selected (non-selected polygons get click-to-select instead)
- Uses `_dragStartVerts` snapshot to compute delta from original, not cumulative — prevents drift
- 2px dead zone distinguishes click from drag (prevents accidental moves)
- `_didMove` flag: if the user clicks without dragging, it deselects (dual-purpose interaction)
- Must update both the polygon AND any visible drag handles during drag

### Conflict: Click vs Drag on Same Element

When a selected polygon has both whole-shape drag and click-to-deselect:

```
Selected polygon:   shapeDrag (drag to move, click-without-move to deselect)
Unselected polygon: .on('click', selectShape)  (click to select)
```

**Why not both on all polygons:** D3's drag behavior captures mousedown and prevents click events from firing. Separating the handlers by selection state avoids the conflict entirely.

## Reset Pattern

Every feedback tool should support reverting to initial state:

```javascript
// At initialization, deep-copy the shapes
const initialShapes = JSON.parse(JSON.stringify(shapes));

// Reset handler
d3.select('#btn-reset').on('click', function() {
  shapes = JSON.parse(JSON.stringify(initialShapes));
  selectedId = null;
  renderAll();
});
```

**Why deep copy:** The shapes array contains nested objects (vertices, distance_from_center). Shallow copy would share references, so mutations during editing would corrupt the "initial" state.

## Data Extraction Channels

Two patterns exist in this project for getting data from the browser back to Claude:

### Channel A: DOM Serialization (structured, for machines)

Used by `pattern-interpretation.html`. The "Done" button writes JSON into a hidden DOM element:

```javascript
document.getElementById('interpretation-data').textContent = JSON.stringify(output);
```

Claude extracts via:
```javascript
() => {
  const el = document.getElementById('interpretation-data');
  return el ? JSON.parse(el.textContent) : null;
}
```

**When to use:** When the output is structured data that feeds a downstream automated process (like `baseline.json` → `arch-audit.py`). The user never needs to read the raw JSON.

### Channel B: Clipboard Copy (human-readable, for text)

Used by the component showcase. A "Copy All Feedback" button gathers textarea values and copies markdown to clipboard. User pastes into chat.

**When to use:** When the output is free-form text that Claude interprets conversationally. Lower friction for the user (paste and chat), but Claude must parse unstructured text.

### Decision Guide

| Factor | DOM Serialization | Clipboard Copy |
|--------|-------------------|----------------|
| Output structure | Strongly typed JSON | Free-form markdown |
| Downstream consumer | Automated tool (audit, schema) | Claude conversation |
| User sees raw output? | No (hidden element) | Yes (they paste it) |
| Extraction reliability | 100% (JSON.parse) | Depends on parsing |
| User friction | Lower (just click Done) | Higher (copy, switch, paste) |

## Pre-Generation vs In-Browser Computation

When the tool needs heavy computation (edge detection, image analysis, shape extraction):

**Pre-generation in Python** (our choice):
```bash
python3 tools/extract-shapes.py reference.jpg → shapes.json + edges.png
```

Claude runs this BEFORE generating the HTML. Results are embedded as initial data or loaded as assets.

**Why not in-browser JavaScript:**
- Python has NumPy for matrix ops (Sobel convolution, flood-fill on large images)
- Pre-generated edge overlay (`edges.png`) avoids recomputing on every page load
- The HTML stays simple — it's a review tool, not a compute engine
- No dependency on browser image processing APIs (Canvas, OffscreenCanvas) which have CORS restrictions with `file://` URLs

**When in-browser IS appropriate:**
- Real-time visual feedback during editing (e.g., highlighting which zone a dragged shape falls into)
- Lightweight computations (centroid, area, distance-from-center)
- Anything that must respond to user interaction frame-by-frame

## Edge Overlay Pattern

Pre-rendered edge detection image layered between the reference and overlays:

```javascript
const edgeOverlay = svg.append('image')
  .attr('href', 'edges.png')
  .attr('width', WIDTH).attr('height', HEIGHT)
  .style('display', 'none');  // Initially hidden

d3.select('#toggle-edges').on('change', function() {
  edgeOverlay.style('display', this.checked ? 'block' : 'none');
});
```

**Why a separate toggle:** Edge overlays are useful for initial placement but distracting during fine-tuning. The user toggles as needed.

**Why pre-rendered PNG, not SVG:** The Sobel output is a pixel-based raster. Converting to vector paths would lose quality and increase file size. The PNG loads fast and renders at native resolution.

## Toolbar Button Conventions

Consistent across all tools:

| Button | Border Color | Text Color | Purpose |
|--------|-------------|------------|---------|
| Default | `#555` | `#e0e0e0` | Neutral actions (Add Shape) |
| Destructive | `#a44` | `#f88` | Delete |
| Warning/Reset | `#a86` | `#fc8` | Revert changes |
| Primary/Done | `#4a8a4a` | `#8f8` | Commit/serialize (bold, flex-grow) |
| Active mode | `#7af` border+text | `#7af` | Toggle states (Add mode active) |

## Building a New Feedback Tool: Checklist

When creating a new interactive review tool:

1. **Define the data model** — What fields does each item have? What's the downstream schema?
2. **Choose extraction channel** — DOM serialization (structured) or clipboard (conversational)?
3. **Decide on pre-generation** — Does Claude need to run Python analysis first, or can initial data come from Claude's own analysis?
4. **Start from the two-panel layout** — Copy the CSS foundation above
5. **Build the SVG layer stack** — Reference/background at bottom, overlays in middle, handles on top
6. **Implement selection + property editor** — Single-select toggle, sidebar fields bound to data model
7. **Add drag interactions** — Vertex drag for fine-tuning, whole-shape drag for repositioning
8. **Add Reset** — Deep-copy initial state, restore on click
9. **Add Done/extraction** — Serialize to DOM or clipboard
10. **Test in Chrome** — Check console for errors, test all interactions, verify extraction protocol

## Known Limitations and Future Work

**Zoom/Pan:** Not yet implemented in any tool. When adding, must handle:
- Inverse-transform pointer events for normalized coordinate system
- Drag handles need to remain at consistent visual size (counter-scale)
- Add-vertex click mode needs pointer-to-data coordinate mapping
- The `viewBox` approach (change viewBox on zoom) is simpler than CSS transform but requires recalculating all pointer interactions

**Undo/Redo:** No tool has undo. The Reset button is an all-or-nothing revert. Per-action undo would require a command history stack — implement only if users report needing it.

**Multi-select:** Implemented in `pattern-interpretation.html` (v1.1). Uses a `Set<string>` for selection IDs and a `groupMode` boolean toggle. Pattern:

```javascript
let selectedIds = new Set();
let groupMode = false;

function selectShape(id) {
  if (groupMode) {
    selectedIds.has(id) ? selectedIds.delete(id) : selectedIds.add(id);
  } else {
    if (selectedIds.size === 1 && selectedIds.has(id)) {
      selectedIds.clear();
    } else {
      selectedIds.clear();
      selectedIds.add(id);
    }
  }
  renderAll();
}
```

Key design decisions:
- Property editor shows the **primary** selected shape (first in Set)
- Drag handles only render for the primary shape
- All selected shapes get highlighted overlays
- "Select Multiple" button toggles `groupMode`; exiting keeps only primary
- Group mode enables "Group as Rotations" when 2+ ungrouped shapes selected
