# Petal-N-2ring K-range — refinement of Option D's `{2,3,4,6}`

**Status:** SURFACED 2026-05-06 — proceeding with reduced K set, owner can revise
**Discovered:** 2026-05-06, while authoring corpus K-sweep (#208)

## Symptom

The Option D cascade plan
(`.claude/plans/option-i-per-face-class-resolver.md`) lists the petal-N-2ring
K-sweep as `K ∈ {2, 3, 4, 6}` (lines 109, 134). On render at each K with the
new `for`-loop template:

| K | gt_G shapes | Status |
|---|---|---|
| 2 | error | adjacent ring-1 circles are tangent — `Y0.cpt1` doesn't exist |
| 3 | 1 | degenerate — adjacent circles barely overlap; almost no Y-petal area |
| 4 | 5 | works |
| 6 | 7 | works; matches manual reference |

## Why

In the petal-N-2ring construction, ring-1 circles are placed at distance R
from the central circle's center, each with radius R. Adjacent ring-1 circles
intersect at two points only when their centers are < 2R apart — i.e. when
N > 2π/something. At N=6 they touch tangentially in canonical Flower-of-Life;
the construction here uses the same `repeat at C0 depth 1` factory which
spaces them by `2 sin(π/N) · R`. At K=2 the centers are diametrically
opposite (no intersection); at K=3 they're far apart and barely touch.

The K=2 case isn't a `for`-loop bug — it's a geometric constraint of this
construction. The K=2 entry in `{2,3,4,6}` was a casual enumeration in the
cascade plan, not a geometry-validated choice.

## Proposal

Use **K ∈ {4, 6}** for the iter-8 multi-class fusion-delta validation. These
are the K values where the construction has both X-petals and Y-petals (i.e.
where the multi-class structure the iter-8 test exercises is actually
present). K=2 and K=3 either error out or produce a degenerate single-class
output that doesn't exercise face_class fusion at all.

Adding K=8, K=10 if more samples are wanted — the construction generalizes
to higher N cleanly (Y-petals only get smaller). But two K values is enough
to demonstrate parametric generalization for iter-8's purpose.

## Action

Proceeding with `K ∈ {4, 6}` in `regenerate.py` for #208. Owner can revise
to `{4, 6, 8, 10}` or back to `{2, 3, 4, 6}` (with K=2,3 as expected-fail
fixtures) without blocking. The iter-8 driver in #209 will be parameterized
to whatever K-list the corpus declares.
