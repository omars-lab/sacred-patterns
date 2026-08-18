---
name: A narrow corpus sweep cannot validate a tolerance bump
description: Constant tweaks (geometric tolerances, thresholds) require the FULL test-suite as the "no regression" bar — not a curated corpus subset, even if that subset spans every pattern family
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
When a fix takes the form of a constant tweak (a tolerance widening, a threshold loosening, an epsilon multiplier change), DO NOT use a corpus sweep alone as the "no regression" evidence. Run the full test suite before claiming the change is safe.

**Why:** 2026-05-19 bikar#424 Phase 1c attempted to close N∈{8,12,16,...} petal-N-ring face-extraction failures by widening `PointIndex(EPSILON*100)` → `PointIndex(EPSILON*1000)`. I ran a corpus sweep across hexagram-lens, medallion10-iter14, petal-6-full, single-petal, single-rhombus and saw zero regression — concluded "Option D ships." But the wider full vitest sweep (which I'd skipped before declaring success) surfaced `packages/core/tests/kernel/petal-debug.test.ts > layer 8 inner-triangle face` regressing — the wider tolerance dissolved 3 layer:8 faces in an N=6 pattern by over-merging endpoint vertices with adjacent intersection points. The corpus sweep missed it because petal-debug's `layer 8` pattern is a synthetic test fixture, not a corpus template.

The owner flagged this directly: *"changing tolerance doesn't feel like we are fundamentally solving problem... don't we have a tenant against going in circles in this regards"* — invoking tenet 7. The right call was to revert and pivot to the architectural fix (Option C — preserve curve identity through the merge), which the decision doc had identified as correct before the Option D detour.

**How to apply:** When the diff is "change a numeric constant" (any constant in `intersection-graph.ts`, `EPSILON`-derived tolerances, detector thresholds, fold-symmetry tolerances, etc.):
1. The minimum acceptance bar is full `vitest run` / `pytest` green, not a hand-picked corpus sweep.
2. If the constant change passes the full suite, you've cleared the regression bar but NOT the tenet-7 bar — separately confirm: was this the first tweak in service of the failing case? Do you have ≥2 independent witnesses? Is there a named rationale for the new value?
3. If a regression appears in the full suite, the constant-tweak approach is falsified — do NOT pivot to "per-call-site tolerance" or "scoped tolerance"; that's the second tweak tenet 7 names as the stop signal.
4. The architectural fix (preserve identity through the merge, refactor the function, distinguish two cases at the type level) is the alternative — author the decision doc for it, ship it, don't tune.
