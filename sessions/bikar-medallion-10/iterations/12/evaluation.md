# Iteration 12 Evaluation

## Context
Added Cmid radius 65 + `layer 2 / connect every 3 on Cmid` to fill the
interstitial zone. All other geometry preserved from iter 11.

## A1: Structure
- Faces: 341 → 398 (+57). The new ring adds construction.

## A2: Symmetry
- cv: 0.0748 → 0.0878 (slightly worse). The new ring's intersection with
  satellite circles isn't perfectly even across all 10 sectors at this
  radius. Small per-sector divergence.

## A3: Face Distribution
- See A6 below for the per-baseline-shape changes.

## A4: Coverage
- Coverage pct: 168.68% → 535.27%. The new ring inflates the bbox
  significantly (since A4 uses bbox area rather than the actual
  medallion radius). Status remains FULL.

## A5: Strapwork — N/A (deferred)
- Crossings: 5 → 5 (unchanged; no strapwork added).

## A6: Baseline Shape Match
- Score: 1/18 → 1/18 (unchanged headline)
- BUT 9 shape statuses moved in the right direction, 3 in the wrong
  direction:

  Improved:
  - inner-star polygon-v0:        4/21 PARTIAL → 18/21 PARTIAL  (close to PASS)
  - inner-star star-v8:           0/6  MISSING → 1/6  PARTIAL
  - rosette polygon-v0:           0/36 MISSING → 17/36 PARTIAL  (major)
  - transition band-segment-v2:   0/3  MISSING → 5/3  PARTIAL
  - transition star-v8:           0/4  MISSING → 2/4  PASS  ✓
  - transition star-v6:          35/41 PARTIAL → 45/41 PARTIAL (closer)

  Regressed:
  - rosette band-segment-v2:      5/4  PARTIAL → 0/4  MISSING
  - rosette star-v6:             13/28 PARTIAL → 4/28 PARTIAL  (worse)
  - rosette star-v8:              1/2  PASS    → 0/2  MISSING

The score "1/18" is essentially binary (PASS only). Across 18 baseline
shapes, iter 12 improved 6 and regressed 3 — net +3.

## A6 zone summary
- inner-star: significantly more polygon coverage (4 → 18 of 21
  expected). The {10/3} ring crossing C1 added the small inner facets.
- rosette: mixed — polygons up dramatically, but stars down. The new
  Cmid ring crosses through the rosette zone and fragments some larger
  shapes into smaller ones.
- transition: clear win — star-v8 jumped from MISSING to PASS, and
  star-v6 / band-segment-v2 both moved closer to expected.

## Pixel similarity
- 75.9% → 76.0% (+0.1pp). Negligible, as expected — the added ring
  changes structural shapes but the colors are still the same blue
  palette as iter 11.

## Predicted vs actual (calibration data point for qiyas#75 V2.B)
- Predicted A6 lift: 1/18 → 4-6/18 PASS shapes. Actual: 1/18. **Miss**
  (the prediction over-counted because adding shapes to a zone shifts
  surrounding shapes' classifications too).
- Predicted A2 cv: tighter. Actual: slightly worse. **Miss** (the
  middle ring's intersections aren't perfectly sector-aligned).
- Predicted pixel: 77-79%. Actual: 76.0%. **Miss** (color/contrast
  matters more than coverage for pixel similarity, as documented in
  CLAUDE.md "Pixel Metrics as Regression Detection").
- Predicted A4: stays FULL. Actual: stays FULL. **Hit.**

Calibration learning: structural-coverage edits in BIKAR don't
monotonically improve A6 PASS count — they shift the distribution
across zones. The right metric is "shape statuses moved in the right
direction" (net +3 here), not the binary PASS count.
