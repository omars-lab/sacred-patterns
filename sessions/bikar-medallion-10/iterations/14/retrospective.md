# Iter 14 — retrospective

## What I changed

Single edit to Layer 0 of pattern.bkr: added `connect every 3 on C1` alongside the existing `connect every 4 on C1`. Everything else byte-for-byte identical to iter 13.

## What I expected vs what happened

| | Expected | Actual |
|---|---|---|
| rhombus-v4 in inner-star | MISSING → PASS (8–12/10) | MISSING (0/10) — unchanged |
| composite_score | 0.81–0.84 | 0.7842 |
| structural_score | 1/18 → 2/18 | 1/18 (unchanged: 1 gained, 1 lost) |

Predicted Δcomposite +0.05–0.08, actual +0.021. Below predicted but positive.

## Why the prediction was wrong

The prediction model was: `void detect on {10/4} ∪ {10/3} → 10 rhombic faces classified as rhombus-v4`. That model assumed the void detector's face-finding would identify each star-edge intersection region as a discrete 4-vertex polygon.

In reality, the void detector found more `polygon-v0` (no specific vertex count) faces and lost some existing `star-v6` faces. The intersections fragmented existing structure rather than crystallizing into clean rhombi. Two failure modes appear to be at play:

1. **Concentric stars on the same circle don't produce rhombi by intersection.** {10/4} and {10/3} share their 10 vertices on C1; their edges cross between vertices but the bounded regions are mostly triangles and irregular polygons, not rhombi.
2. **The ref's rhombi are likely constructed from outside C1.** Looking at the iter-12 retrospective (Cmid radius tuning), inner-star rhombi most likely come from edges that *cross through* the inner-star zone from the middle ring (Cmid2 at radius 50, currently doing {10/4}). The reference photo shows the rhombi as being bounded by middle-ring edges that pass through, not from edges within C1.

## What this teaches the meta-loop

**For the BIKAR translation table** (qiyas-warning → DSL idiom): "A6 baseline-shape MISSING with vertex_count=4" should NOT translate to "overlay another `connect every K`". A more reliable translation:
- For rhombi specifically: identify the radial position of the missing rhombi, find which two construction circles bound that region, and verify that edges from both circles cross through.
- Alternative: explicit `connect cycle` defining one rhombic wedge through known intersection points + `rotate N`.

**For the warning ranker (qiyas#75 calibration data):** the `inner-star--rhombus-v4` warning predicted PASS-on-fix counterfactual_score_delta of ~0.05; actual gain was 0 for that specific shape (though +0.021 came from other side-effects). This is a *non-trivial calibration error* worth recording — the counterfactual transformer assumes adding a missing shape gives the full (1/18)·(structural_weight) lift, but that ignores construction interactions where adding edges creates *and destroys* shapes simultaneously.

**For the iter-15 directive:** stop chasing rhombus-v4 with same-circle overlays. Either (a) try a different construction approach (mid-ring edges that pass through inner-star zone), or (b) shift focus to A5 bands (currently 17/45 crossings; this is a real construction gap not a vocabulary issue, and the path forward — adding strapwork or band rendering — is well-understood).

Recommend (b) for iter 15: it's a higher-leverage gap with a known DSL idiom (`strapwork width N crossing alternating` per pattern-construction skill).

## Findings to capture (Phase 1.5)

- **bikar/skill** (translation table gap): "A6 baseline-shape MISSING vertex_count=N" needs nuanced treatment beyond "add another connect every". Recommend appending row to `iterate-pattern-from-qiyas-warnings/SKILL.md` once a second instance occurs.
- **qiyas calibration** (warnings#75 data point): A6-MISSING counterfactual_score_delta over-estimates fix lift when target shape requires construction-interaction (not just additive edges). Record actual=+0 vs predicted=+0.05 for this shape.
- **No qiyas/bikar issue file warranted yet** (single instance — wait for second to confirm pattern).
