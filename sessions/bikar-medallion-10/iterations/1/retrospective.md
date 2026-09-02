# Iteration 1 Retrospective

## What Worked
- Pattern compiles and renders
- 10-fold symmetry is structurally correct
- Blue palette colors are in the right range
- Strapwork renders with over/under crossings
- Basic {10/4} + {10/2} star structure present

## What Didn't Work
- **Pattern too large** — depth-2 repeat generates ring-1 (10 circles) AND ring-2 (100+ circles) which extends way beyond the medallion boundary. The reference only shows ~2 concentric rings of geometry.
- **No visible satellite rosettes** — in the reference, the outer ring has 10 distinct smaller 10-pointed stars. Our depth-2 repeat just extends the connect-every pattern, not creating separate rosette motifs.
- **Face coloring too uniform** — ring-based coloring assigns colors by distance from center, but the reference has specific face-type coloring (kites get one color, triangles another, pentagons another).
- **No boundary** — the reference has a clear scalloped circular boundary. Our pattern has no clipping or boundary.
- **Central star not prominent** — the reference's center is a very distinct dark navy 10-pointed star. Ours blends into the surrounding geometry.

## Hypotheses Updated
- CONFIRMED: 10-fold symmetry is correct
- CONFIRMED: {10/4} star polygon generates the primary structure
- CONFIRMED: strapwork with alternating crossings renders correctly
- DISPROVEN: simple depth-2 repeat does NOT produce satellite rosettes — it just extends the star pattern
- NEW QUESTION: How to create distinct satellite rosettes? Might need separate `connect` calls for ring-1 circles, not just inheriting from the central repeat.
- NEW QUESTION: How to create the scalloped boundary? May need a clipping mechanism.
- WORKING ASSUMPTION: Satellite rosettes may need `layer` blocks to isolate their geometry from the central pattern.

## Plan for Iteration N+1
1. **Reduce scope** — remove depth-2, use depth-1 only. Build the central star + inner ring first.
2. **Separate satellite construction** — manually place satellite rosettes at ring-1 circle positions using specific connect statements within layers.
3. **Improve face coloring** — use `classify` rules + `fill where sides ==` instead of just ring-based coloring.
4. **Central star emphasis** — ensure the central decagonal face is prominently colored navy.
