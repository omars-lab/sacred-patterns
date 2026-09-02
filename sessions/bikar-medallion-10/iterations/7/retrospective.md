# Iteration 7 Retrospective

## What Worked
- **Layer isolation + connect every 4 + small radius = isolated rosettes!** This is the combination that cracks satellite isolation.
- 0.3 * $radius keeps adjacent satellites completely separate (diameter 60 < center-to-center 61.8)
- `connect every 4` within a single circle produces proper {10/4} kite+triangle+decagon decomposition
- Removing strapwork makes it much easier to evaluate the structural geometry

## What Didn't Work
- Large empty interstitial zone between center and satellites
- Center star (hankin) is a different construction method and size than satellites (connect every 4)
- `hankin angle 54 on @0.N` at 0.5x produced 22 faces — hankin rays too short on small circles
- `connect every 4 on @0.N` at >= 0.45x causes inter-satellite overlap (adjacent chord intersection)

## Hypotheses Updated
- CONFIRMED: `connect every 4` on small isolated circles produces proper {10/4} rosette face catalog
- CONFIRMED: 0.3 * $radius is the sweet spot for satellite isolation with 10-fold symmetry
- CONFIRMED: layers prevent center-satellite interference
- DISPROVEN: hankin works for satellite rosettes at small radii — rays too short
- NEW: the interstitial zone in the reference is likely constructed explicitly (not from star ray overflow)
- NEW: center star should probably also be `connect every 4` at a matching radius for consistency

## Plan for Iteration 8
1. **Make center star also use `connect every 4`** — same construction as satellites for visual consistency
2. **Add interstitial geometry** — explicit `connect` statements or `face` declarations connecting center star points to satellite star points
3. **Consider a middle ring** — `repeat at C0 depth 2` to add a transitional ring of construction circles
