# GeoGebra Guide

How to generate GeoGebra outputs from a learning session. This guide covers both the paste-in script and the `.ggb` archive file.

## Overview

GeoGebra output serves two purposes:
1. **Verification** — the GeoGebra construction can be opened and manipulated to verify geometric relationships
2. **Education** — the construction shows step-by-step how the pattern is built, which is useful for understanding and teaching

## Two Output Formats

### 1. GeoGebra Script (`.txt`)

A plain text file of GeoGebra commands that can be pasted into GeoGebra Classic's input bar.

**When to generate:** During finalization (Step 5 of the skill workflow), after the pattern is stable.

**How:** Follow the script generation rules in `compile-geogebra.md`, translating the final `pattern.json` into GeoGebra commands.

**Reference:** See `session-abc/geogebra-script.txt` for a complete working example.

### 2. GeoGebra Archive (`.ggb`)

A ZIP file that GeoGebra can open directly, containing the full construction with styling and a thumbnail.

**When to generate:** During finalization, after the script is verified.

**How:** Follow the archive building process in `compile-geogebra.md`.

## Template Files

Template files are stored in this skill's `templates/` directory:

| File | Source | Purpose |
|------|--------|---------|
| `geogebra_defaults2d.xml` | `session-8-fold/8-Fold Rosette/` | 2D view default settings |
| `geogebra_defaults3d.xml` | `session-8-fold/8-Fold Rosette/` | 3D view default settings |
| `geogebra_javascript.js` | `session-8-fold/8-Fold Rosette/` | Minimal JS stub |

These files are copied verbatim into the `.ggb` archive. They provide sensible defaults for GeoGebra's GUI (axis visibility, grid settings, font sizes, etc.).

## Construction Approach

GeoGebra constructions should mirror the compass-and-straightedge tradition of Islamic geometric art:

1. **Start with a center point and unit circle** — `O = (0, 0)`, `c = Circle(O, r0)`
2. **Define axes of symmetry** — radial lines at the pattern's angular divisions
3. **Build construction circles** — at each significant radius
4. **Find key intersection points** — where construction lines/circles meet
5. **Connect points into polygons** — the final visible shapes
6. **Style** — colors, line thickness, fill opacity

This mirrors the approach in `session-8-fold`, which builds an 8-fold rosette from a fundamental tile found at the intersection of a base circle and an auxiliary circle, then mirrors it across all 8 symmetry axes.

## Tips

- Use `r0 = 4` as the base unit (large enough for clear visualization, matching session-abc)
- Make construction elements auxiliary: `SetAuxiliary(element, true)` — this hides them from the algebra view
- Hide all labels: `ShowLabel(element, false)` — labels clutter geometric patterns
- For star polygons {n/k}: list vertices in step order (0, k, 2k, ...) in the Polygon command
- Use `Rotate(object, angle, center)` for radial repetition — cleaner than manual point calculation
- GeoGebra angles are in degrees by default
- For filled polygons, set opacity with `SetFilling(polygon, opacity)` where 0.0 is transparent and 1.0 is opaque

## Verification

After generating the `.ggb` file:

1. Note in the session output that the file was generated
2. Provide the file path for the user to open in GeoGebra Classic
3. Common issues to check:
   - All expected elements are visible
   - Colors match the pattern.json palette
   - Symmetry is correct (rotate view to verify)
   - No stray construction elements are visible (should be auxiliary)
