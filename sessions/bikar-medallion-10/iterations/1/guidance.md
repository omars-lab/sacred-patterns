# Guidance for Iteration 2

## Priority: Architecture (G2 — fix structure before pixels)

### Changes
1. Remove `repeat at C0 depth 2` — use depth 1 only for now
2. Keep `connect every 4` + `connect every 2` for central star
3. Add `connect adjacent` for hexagonal frame edges
4. Improve fill rules:
   - `fill void where sides == 10 color navy` (central decagon)
   - `fill void where sides == 3 color turquoise` (triangles)
   - `fill void where sides == 4 color cobalt` (kites/rhombi)
   - `fill void where sides >= 5 color royal` (pentagons+)
5. Consider: reduce strapwork width from 8 to 6
6. Consider: add `polygon decagon` edges for the outer boundary
