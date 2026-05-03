# Plan: Replace Watershed with CCL + Sharper Polygon Fitting

## Context

After the adaptive barrier detection improvement (barrier 85% → 59%), we're extracting only 50 shapes when the pattern has 240+ tiles. Root cause: **watershed flood fill merges same-color adjacent tiles**. Two dark blue kites separated by a 2px white band get merged into one 13-vertex blob because their perceptual color distance is < 50. This explains:
- Zero 4-vertex shapes (kites/rhombi merged into larger regions)
- Only 7.87% area coverage (expected 60-70%)
- High vertex counts (13-19) from merged multi-tile boundaries

**Solution**: Replace watershed with Connected Component Labeling (CCL) on the inverse barrier mask. CCL doesn't care about color — it only cares about connectivity through the barrier. Two tiles of identical color separated by a 1px barrier get different labels.

## Files

Primary: `tools/extract-shapes.py` (~80 lines changed, ~30 new)
Secondary: `docs/features.md` (update pipeline description)

## Changes (3 steps)

### Step 1: Add two-pass CCL with Union-Find

New function `connected_component_label(mask, connectivity=4)`:
- Two-pass algorithm: first pass assigns provisional labels + records equivalences in Union-Find; second pass resolves to canonical labels
- Returns `label_map` (H×W int32 array) where each connected region has a unique integer
- Pure NumPy + dict-based Union-Find — O(N) time, no external deps
- 4-connectivity default (prevents diagonal leakage at strapwork intersections)

Add after the existing `find_connected_components()` function (which uses BFS — keep it for fallback).

### Step 2: Replace watershed with CCL in the pipeline

In `extract_shapes()`, replace Step 4:

**Current**: `watershed_segment()` → barrier-constrained flood fill with color tolerance
**New** (white-strapwork mode):
1. Invert barrier mask: `tile_mask = 1 - barrier_mask`
2. Run `connected_component_label(tile_mask, connectivity=4)` → label_map
3. For each label, collect pixel coordinates + compute mean color from original image
4. Filter by min_area
5. Result: same format as watershed output (`{'pixels': [...], 'mean_color': (...), 'area': N}`)

**General mode**: keep watershed as-is (backward compatible for non-geometric images)

### Step 3: Visvalingam-Whyatt simplification (replaces Douglas-Peucker for white-strapwork)

New function `visvalingam_whyatt(points, target_n)`:
- Iteratively removes the vertex forming the smallest-area triangle with its neighbors
- Stops when vertex count reaches `target_n` (or a minimum area threshold)
- Better than RDP for geometric tiles: naturally preserves sharp corners (large-area triangles) while removing noise points (small-area triangles)
- Target vertex count estimated from shape area: tiny tiles → 4-5 vertices, medium → 5-8, large → 8-12

In white-strapwork mode, use Visvalingam-Whyatt instead of Douglas-Peucker. Retain RDP for general mode.

## Updated CLI arguments

| Argument | Default | Change |
|---|---|---|
| `--max-shapes` | 50 → 200 | Raise cap to accommodate full tile count |
| `--segmentation` | (new) `auto` | `auto`, `ccl`, `watershed` — force segmentation method |

## Expected Results

| Metric | Current | After |
|---|---|---|
| Shape count | 50 | 150-250 |
| 4-vertex shapes | 0 | 30+ (kites, rhombi) |
| Area coverage | 7.87% | 50-65% |
| Vertex count range | 7-19 | 3-12 |
| Missing zones | all under-represented | proportional coverage |

## Verification

```bash
python3 tools/extract-shapes.py \
    /Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns/session-1/input/reference.jpg
```

1. Shape count > 100 (console: "Watershed regions" replaced by "CCL regions")
2. `shapes.json` includes 4-vertex shapes (kites)
3. Vertex count distribution spans 3-12 (not clustered at 7-19)
4. Strapwork.png unchanged (barrier detection not modified)
5. Regenerate HTML: `python3 tools/generate-interpretation.py .../session-1`
6. Open in browser — shapes should tile the pattern with minimal gaps
7. Visually confirm: adjacent same-color tiles are separate shapes
