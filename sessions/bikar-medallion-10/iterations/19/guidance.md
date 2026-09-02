# Iter 19 — partial-shape cascade pickup (extend satellite stars beyond their natural radius)

## Premise

Iter-18 (slice-1 re-render gate) cleared with composite 0.6888 → 0.7985 (+0.11). The cascade rotated: A2 symmetry warning dropped out of top-N; new top warnings are:

- **#3 (sev=error):** `missing-shapes — 39 ref shape(s) not found in recon (28% of 139), cf_adj=-0.0285`
- **#1 (sev=warn):** `extra-shapes — 31 extra shape(s) in recon not present in ref (22%), cf_adj=+0.0275`

Both point at the partial-shape cascade (sacred-patterns#106). The reference has half-rosettes / partial stars at boundaries; our recon draws each satellite only within its 0.3·R circle (lines 67-77 in iter-18 pattern.bkr — `connect every 4 on @0.0` ... `@0.9`). When satellites *would* extend into neighbor space, those clipped edges are missing from recon, hence the 39 missing shapes; and our construction-element excess in the central rosette mesh shows up as 31 extras.

## The edit (no spec change, only DSL)

bikar ships the four partial-shape primitives (`boundary`, `intersect`, `clip pattern to`, `extend connect ... beyond <factor>`). Iter-19 applies the *minimal* one — `extend` on the 10 satellite `connect every 4` statements — to let satellite stars reach into adjacent satellite space.

Concretely, swap each of:

```
connect every 4 on @0.k
```

for:

```
extend connect every 4 on @0.k beyond 1.5
```

The 1.5x factor is the simplest reasonable guess: each satellite has radius 0.3·R and sits at distance 1.0·R from origin; the nearest-neighbor satellite center is `2 * 0.3 * sin(π/10) ≈ 0.185·R` away (using the unit-circle centers), so 1.5x reach is `0.45·R` from satellite center — enough to cross into the adjacent satellite's territory and produce the intersection geometry the reference shows.

## Predictions

- **A6 missing-shapes:** 39 → ≤25 (the satellite extensions should populate `inner-star--star-v8`, `inner-star--polygon-v0`, `inner-star--rhombus-v4` MISSING shapes via new inter-satellite intersections).
- **A6 extra-shapes:** 31 → 25-40 (extending creates new intersection sub-faces; some are real, some are noise. Net could go either way; the test is whether the missing count drops MORE than extra count rises).
- **structural_score:** 0/18 → expected 2-5/18 (slot-filling on the now-CLIPPED-MISSING zones).
- **overall.composite_score:** 0.7985 → expected +0.02 to +0.06 (cascade design doc §Verification predicts +0.05 to +0.10 from a single `extend` edit; this is a conservative half-budget since the iter-18 baseline is already higher than the iter-14 figure the doc used).
- **A2 cv:** 0.127 → similar (no new symmetry-breaking statements; `extend` preserves 10-fold).
- **A5 status:** BROKEN → BROKEN or PARTIAL (extensions create more crossings, but A5 still needs the band-detector recovery work outside cascade #106).

## Stop conditions

- **missing-shapes count rises** → `extend` direction is wrong; the cascade primitive isn't the right tool here. Try a smaller factor (1.2) or fall back to per-shape investigation.
- **composite drops > 0.02** → unexpected interaction; missing-shapes gain didn't compensate for extra-shapes noise. Triage the new extras.
- **structural_score stays 0/18** → the `extend` is technically working but the new intersection shapes don't match expected vertex counts. Likely need `clip pattern to medallion_outline` to gate which extensions count.
- **Render fails** → bikar parser/evaluator bug under our specific use of `extend`. Bisect against a single-satellite test.

## Why NOT also add `clip pattern to medallion_outline`

The cascade plan's full sequencing is `boundary → extend → clip pattern → intersect`. But Tenet 7 says don't tune multi-knob — iter-19 tests `extend` alone. If `extend` raises composite but introduces enough extras to need clipping, iter-20 adds the `clip pattern to`.

## What this iter does NOT do

- No new layer/circle/divide changes.
- No `boundary` or `clip pattern to` statements.
- No `intersect` auxiliary points.
- No fill rule changes (the existing `fill void where sides == X` rules cover any shape the extensions produce).

## Cross-task

- Tests the predicted leverage of cascade #106 on the SVG-direct path (orchestrator's `qiyas-diff` does not use VTracer, so the #371 residue-starvation blocker does NOT apply here).
- If green, advances #85 (medallion-10 convergence) and confirms the missing-shapes warning is partial-shape-cascade-actionable.
- If red, falsifies the prediction that `extend` alone is sufficient — informs whether `clip pattern to` is required for the primitive to take effect.
