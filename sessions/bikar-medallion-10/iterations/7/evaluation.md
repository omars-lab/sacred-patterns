# Iteration 7 Evaluation

## Context
- Layers: center hankin (layer 0) + satellite connect every 4 (layer 1)
- Satellite radius: 0.3 * $radius (isolated — no overlap between adjacent satellites)
- No strapwork — pure geometry focus per user feedback

## A1: Structure
- Segments: 220
- Faces: 320
- Face catalog: 100 triangles, 200 kites (4-sided), 10 decagons (10-sided), 9 20-gons, 1 outer
- 10 decagons = satellite star center voids (correct!)
- 200 kites = 20 per rosette (10 inner + 10 outer kites in {10/4})

## A2: Symmetry
- Expected: 10-fold
- Observed: EXACT — all face counts are multiples of 10

## A3: Face Distribution
- Expected: 11 rosettes (1 center + 10 satellites), each decomposed into kites + triangles + decagonal void
- Actual: 10 satellite rosettes clearly visible, center star visible but uses hankin (different construction)
- Match: GOOD for satellites, CENTER needs {10/4} matching construction
- Missing: interstitial zone between center and satellites is empty

## A4: Coverage
- Expected: full medallion with interstitial geometry filling gaps
- Observed: SPARSE — center star + 10 satellite rosettes with large empty ring between them
- Gaps: entire interstitial zone (the ring R=50 to R=70 roughly) is empty

## A5: Strapwork
- N/A — removed per user feedback to focus on structure

## A6: Visual Match
- Overall: 35% (structure is correct but coverage is sparse)
- Matching: 11 distinct rosettes ✅, 10-fold symmetry ✅, satellite star shape ✅
- Non-matching: empty interstitial zone, center star too large relative to satellites, no boundary

## Key Breakthrough
**First time seeing 11 distinct rosettes.** The combination of:
- `connect every 4 on @0.N` (full chords for proper {10/4} stars)
- `radius 0.3 * $radius` (prevents inter-satellite overlap)
- `layer` blocks (prevents center-satellite interference)

...produces the correct topology. Now need to fill the interstitial zone.

## Radius Experiments
| Radius | Faces | Result |
|--------|-------|--------|
| 0.5 * $radius | 22 | Too small — hankin rays don't intersect, just polygon outlines |
| 0.618 * $radius | 62 | Better but still too few intersections |
| 0.8 * $radius | 112 | Good density but satellites merge |
| 0.3 * $radius (connect every 4) | 320 | Perfect isolation — 11 distinct rosettes |
| 0.45 * $radius (connect every 4) | 483 | Adjacent satellites overlap |
| 0.5 * $radius (connect every 4) | 558 | Heavy satellite overlap |

## Next Steps
1. Fill interstitial zone — need geometry connecting center star to satellite ring
2. Match center star size to satellites (both should be {10/4} at similar scale)
3. Then: color refinement, boundary, strapwork (in that order)
