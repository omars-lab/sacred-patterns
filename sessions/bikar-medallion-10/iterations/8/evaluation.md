# Iteration 8 Evaluation

## Context
- Fix: `connect every 4 on C0` explicitly targets center circle (was defaulting to last ring-1 circle)
- All 11 rosettes now use `connect every 4` — uniform construction
- Layers isolate center (layer 0) from satellites (layer 1)

## A1: Structure
- Faces: 351
- Catalog: 110 triangles, 220 kites, 11 decagons, 9 × 20-gons, 1 outer
- 11 decagons = 1 center + 10 satellite voids ✅
- 220 kites = 20 per rosette × 11 ✅
- 110 triangles = 10 per rosette × 11 ✅

## A2: Symmetry
- 10-fold: EXACT (all satellite counts are multiples of 10)

## A3: Face Distribution
- Center rosette: 1 decagon + 10 kites + 10 triangles at d<50 ✅
- Satellites: 10 decagons + 200 kites + 100 triangles ✅
- Match: EXCELLENT for rosette topology

## A4: Coverage
- SPARSE — 11 isolated rosettes with empty interstitial zone
- Gap between center (d≈39) and satellites (d≈82) needs filling

## A5: Strapwork — N/A (deferred)

## A6: Visual Match — 40%
- Rosette topology: CORRECT ✅
- Interstitial zone: EMPTY (major gap)
- Center/satellite size mismatch (center much larger)

## Root Cause Found
`connect every 4` (no `on` clause) uses `env.lastDividedCircle` — after a `repeat` block, that's the LAST ring-1 circle, not C0. Fix: always use `connect every 4 on C0` when targeting the center circle in a pattern with repeat blocks.

## Feedback Addressed
- Face 295 (iter 7): satellite decagon looked different — likely the decagon from the duplicate `connect every 4` that was targeting @0.9 instead of C0
