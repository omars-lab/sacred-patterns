---
name: interpret-pattern
description: Interactive review of Claude's geometric decomposition of a reference image. The user corrects shape inventory, producing a baseline.json that grounds the A6 architectural audit.
user_invocable: false
---

# interpret-pattern

Collaborative pattern interpretation step that runs between session initialization and iterative construction. Claude generates a visual overlay of detected shapes on the reference image; the user reviews and corrects it in the browser. The corrected inventory becomes `baseline.json` — ground truth for the A6 Baseline Shape Validation audit.

## Why This Exists

After 92 iterations on the first pattern, we discovered that the architectural audit (A2-A5) checks shapes are **present** but not that they are **correct**. The audit could report "kites PRESENT" when the output had crude hexagons in the kite zone. This skill closes that gap by:

1. Making Claude's interpretation visible and editable before iteration work begins
2. Producing a machine-readable baseline that the audit validates against every iteration

## Workflow

### 1. Claude Generates Shape Inventory

After analyzing the reference image (learn-new-pattern Step 2), Claude produces a shape inventory as a JSON array. Each shape has:

```json
{
  "id": "central-star",
  "type": "star|polygon|kite|petal|rhombus|pentagon|hexagon|bowtie|custom",
  "zone": "inner-star|rosette|transition|satellite|outer",
  "vertex_count": 10,
  "count": 1,
  "count_tolerance": 0,
  "approximate_area_ratio": 0.08,
  "area_tolerance": 0.3,
  "distance_from_center": { "min": 0, "max": 0.15 },
  "notes": "10-pointed star formed by {10/4} diagonal intersections",
  "overlay_color": "#ff6b6b",
  "approximate_vertices": [[0.5, 0.1], [0.55, 0.15], ...]
}
```

All distances are normalized 0-1 relative to the pattern radius R (detected from clip circles).

### 1b. Claude Runs Image Analysis (Optional)

Claude runs the pre-generation script to extract shape boundaries from the reference image:

```bash
python3 tools/extract-shapes.py <session>/input/reference.jpg \
    [--work-size 600] [--tolerance 60] [--connectivity 8] \
    [--luminance-threshold 240] [--edge-dilation 0] [--snap-radius 5] \
    [--simplify 3.0] [--colors 8] [--edge-threshold 30] [--min-area 200] \
    [--mode auto] [--morph-close 1] [--max-shapes 50]
```

This produces:
- `shapes.json` — detected tile boundaries with normalized 0-1 vertices and fill colors
- `edges.png` — Sobel edge overlay PNG
- `strapwork.png` — detected barrier mask (white = barrier, black = tile interiors)

CLI arguments:
| Argument | Default | Purpose |
|---|---|---|
| `--mode` | `auto` | Barrier detection mode: `auto`, `white-strapwork`, `general` |
| `--work-size` | 600 | Working resolution for processing (higher = sharper, slower) |
| `--tolerance` | 60 | Color tolerance in perceptual distance |
| `--connectivity` | 8 | BFS connectivity (4 or 8); overridden to 4 in white-strapwork mode |
| `--luminance-threshold` | 240 | Barrier brightness cutoff (0-255) |
| `--edge-dilation` | 0 | Edge barrier dilation radius in pixels (only used in general mode) |
| `--morph-close` | 1 | Morphological closing radius for sealing small gaps |
| `--max-shapes` | 50 | Maximum number of shapes to output |
| `--snap-radius` | 5 | Boundary-to-edge snapping search radius |
| `--simplify` | 3.0 | Douglas-Peucker simplification tolerance |
| `--colors` | 8 | Number of dominant colors to extract |
| `--edge-threshold` | 30 | Sobel edge magnitude threshold (0-255) |
| `--min-area` | 200 | Minimum component area in pixels; overridden to 100 in white-strapwork mode |

**Adaptive mode detection:** In `auto` mode, the tool classifies the image by luminance histogram. If >30% pixels are near-white (luminance > 245) and >20% are colored (luminance < 200) with <15% in between, it selects `white-strapwork` mode. This mode uses luminance-only barrier detection (no edge union, no dilation), which reduces barrier coverage from ~85% to ~59% on bimodal images, producing larger and more accurate tile regions.

**Validation after running:** Always visually inspect the outputs in the browser:
1. Open `strapwork.png` — white regions should trace only the strapwork bands, not colored tiles. If blue/cyan tiles appear white in the mask, the luminance threshold is too low.
2. Open `edges.png` — edges should trace tile boundaries sharply. If edges are too thick or bleeding, lower `--edge-threshold`.
3. Check console output for barrier coverage % — should be 55-65% for typical Islamic patterns with white strapwork (not 80%+, which indicates tiles are being caught as barrier).

Claude merges the image-extracted shapes with its own visual analysis to produce more accurate initial overlays.

### 1.5c. Claude Writes pattern-config.json

Claude writes `input/pattern-config.json` with pattern metadata and zone definitions:

```json
{
  "pattern": {
    "name": "10-fold-rosette-medallion",
    "symmetry_order": 10,
    "star_notation": "{10/4}"
  },
  "zones": {
    "inner-star": { "r_min": 0, "r_max": 0.35 },
    "rosette": { "r_min": 0.35, "r_max": 0.55 },
    "transition": { "r_min": 0.55, "r_max": 0.86 },
    "satellite": { "centers_at_distance": 0.64, "radius": 0.22 },
    "outer": { "r_min": 0.86, "r_max": 1.0 }
  }
}
```

### 1.5d. Generate Interactive HTML from Template

```bash
make interpret SESSION=<session-dir>
# or directly:
python3 tools/generate-interpretation.py <session-dir>
```

This injects `shapes.json` and `pattern-config.json` into the HTML template at `.claude/skills/interpret-pattern/templates/pattern-interpretation.html`, producing `input/pattern-interpretation.html`.

### 2. User Reviews in Browser (formerly "Claude Generates Interactive HTML")

The generated `pattern-interpretation.html` shows:

- **Reference image** as background `<image>` in SVG
- **Edge overlay** toggle (loads pre-generated `edges.png`)
- **Shape overlays** as semi-transparent colored polygons
- **Sidebar** with shape list, property editors, and feedback textarea
- **Toolbar** with Add Shape, Delete, Reset, and Done buttons

### 3. User Reviews in Browser

Claude opens the HTML in the browser. The user:

- Clicks shapes to select them, edits properties in the sidebar
- Drags vertices to correct shape boundaries (per-vertex handles)
- Drags selected shape body to translate all vertices together (whole-shape drag)
- Toggles edge overlay to see detected tile boundaries
- Adds shapes Claude missed, deletes incorrect ones
- Uses Reset to revert all shapes to initial positions if needed
- Writes per-shape notes and global feedback
- Clicks "Done" when satisfied

### 4. Claude Extracts Corrected Data

After the user clicks "Done", Claude reads the serialized data from the DOM:

```javascript
// Extraction protocol — run via evaluate_script or javascript_tool
() => {
  const el = document.getElementById('interpretation-data');
  return el ? JSON.parse(el.textContent) : null;
}
```

The "Done" button serializes all shape data + feedback into a `<script type="application/json" id="interpretation-data">` element.

### 5. Claude Generates baseline.json

Claude writes `baseline.json` to the session's `input/` directory using the extracted data. See `baseline-schema.md` for the full schema.

### 6. Gate: baseline.json Required

**Step 2 (Analyze Pattern) cannot begin until `baseline.json` exists in `input/`.** This ensures that the user has reviewed and corrected Claude's interpretation before any iteration work starts.

The baseline is used by:
- `qiyas svg-audit --baseline input/baseline.json` (run via `tools/iteration-validate.sh`) — A6 audit validates SVG output against expected shapes
- Evaluation templates — iteration evaluations reference baseline shape expectations
- Guidance — when shapes are MISSING or PARTIAL in A6, guidance targets those specific shapes

## Integration with learn-new-pattern

This skill is invoked as **Step 1.5** in the learn-new-pattern workflow:

```
Step 1:    Initialize Session (existing)
Step 1.5a: Claude analyzes reference image visually, identifies shape classes
Step 1.5b: Claude runs `python3 tools/extract-shapes.py reference.jpg` → shapes.json + edges.png
Step 1.5c: Claude writes input/pattern-config.json (pattern metadata + zones)
Step 1.5d: `make interpret SESSION=<session>` → generates pattern-interpretation.html
Step 1.5e: User reviews in browser, corrects overlays, clicks Done
Step 1.5f: Claude extracts data, writes baseline.json
Step 2:    Analyze Pattern (now grounded by baseline)
Step 4:    Iteration Loop (qiyas svg-audit runs A6 with --baseline)
```

## End-to-End Regression Test

After modifying the template (`templates/pattern-interpretation.html`), run this test sequence to verify nothing is broken. Regenerate the HTML, reload the browser, and run the scripted test via `evaluate_script`.

### Setup

```bash
make interpret SESSION=<session-dir>
# Reload the page in browser (ignore cache)
# Verify: no JS console errors
```

### Scripted Test (run via evaluate_script in the browser)

The test creates a group, verifies derived behavior, checks plus buttons, crosshair, sidebar labels, and Done output — all in one script. The expected results are:

| # | Test | Expected |
|---|------|----------|
| 1 | Multi-select 2 shapes | `selectedIds` has 2 entries |
| 2 | Click Group → picking mode | `pickingCenterMode=true`, status = "Click a shape to set as rotation center.", button active |
| 3 | Click a shape → group created | `prototype_id` set to first selected, center = clicked shape's centroid, second shape `isDerived=true` |
| 4 | Click derived → redirects to prototype | `selectedIds` contains only the prototype |
| 5 | Click vertex handle → plus buttons | `selectedVertexIndex` set, 2 `edge-midpoint` elements in DOM |
| 6 | Crosshair at rotation center | 2 `<line>` + 1 `<circle>` in `#handles` (beyond drag handles) |
| 7 | "(derived)" label in sidebar | `shape-list` text contains "(derived)" |
| 8 | No propagate checkbox, prototype info shown | `prop-fields` contains "Prototype", does NOT contain "Propagate vertex" |
| 9 | Done output has `prototype_id` | `groups[0].prototype_id` present, no `propagate_edits` field |

### Script

```javascript
() => {
  const results = [];

  // 1. Multi-select two shapes
  selectShape('shape-011', {});
  selectShape('shape-012', { metaKey: true });
  results.push({ test: '1-multiselect', pass: selectedIds.size === 2 });

  // 2. Enter picking mode
  document.getElementById('btn-group').click();
  results.push({ test: '2-pickingMode', pass: pickingCenterMode === true
    && document.getElementById('status').textContent.includes('rotation center') });

  // 3. Click a shape to set center
  document.querySelector('[data-shape-id="shape-005"]')
    .dispatchEvent(new MouseEvent('click', { bubbles: true }));
  results.push({ test: '3-groupCreated', pass: groups.length === 1
    && groups[0].prototype_id === 'shape-011'
    && isDerivedGroupMember('shape-012') });

  // 4. Click derived → redirect
  selectedIds.clear(); renderAll();
  selectShape('shape-012', {});
  results.push({ test: '4-derivedRedirect', pass: primarySelectedId() === 'shape-011' });

  // 5. Plus buttons
  selectedVertexIndex = null; renderOverlays();
  document.querySelectorAll('.drag-handle')[0]
    .dispatchEvent(new MouseEvent('click', { bubbles: true }));
  results.push({ test: '5-plusButtons', pass: selectedVertexIndex === 0
    && document.querySelectorAll('.edge-midpoint').length === 2 });

  // 6. Crosshair
  results.push({ test: '6-crosshair',
    pass: document.querySelectorAll('#handles line').length === 2
      && document.querySelectorAll('#handles circle:not(.drag-handle):not(.edge-midpoint)').length === 1 });

  // 7. Derived label
  results.push({ test: '7-derivedLabel',
    pass: document.getElementById('shape-list')?.innerText.includes('(derived)') });

  // 8. Group properties
  const html = document.getElementById('prop-fields')?.innerHTML || '';
  results.push({ test: '8-groupProps',
    pass: html.includes('Prototype') && !html.includes('Propagate vertex') });

  // 9. Done output
  document.getElementById('btn-done').click();
  const output = JSON.parse(document.getElementById('interpretation-data').textContent);
  const g = output.groups?.[0];
  results.push({ test: '9-doneOutput',
    pass: g?.prototype_id === 'shape-011' && !g?.hasOwnProperty('propagate_edits') });

  return results;
}
```

All tests should return `pass: true`. If any fail, the template change introduced a regression.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | This file — skill definition and workflow |
| `baseline-schema.md` | Documents `baseline.json` schema and shape matching rules |
| `interpretation-tool-template.md` | Guide for generating the interactive HTML tool |
| `templates/pattern-interpretation.html` | Reusable HTML template with `{{PLACEHOLDER}}` tokens |
| `tools/generate-interpretation.py` | Injects session data into template → HTML |
| `tools/extract-shapes.py` | Pre-generation script: image → shapes.json + edges.png |
| `../collecting-feedback-on-components/feedback-tool-patterns.md` | Reusable design patterns for browser-based feedback tools |
