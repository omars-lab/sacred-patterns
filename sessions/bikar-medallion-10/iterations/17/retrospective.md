# Iter-17 Retrospective

## Hypothesis (from pattern.bkr header)

> Add `connect every 2 on C1`. The {10/2} on a 10-divided circle is a single 10-pointed star (decagram-2) whose outline traces 20 vertices — exactly inner-star--star-v20 (expected 1).
>
> Predicted Δcomposite vs iter 14: +0.03 to +0.06
> Predicted Δstructural: 1/18 → 2/18 or 3/18
> Predicted A2 cv: stays at iter-14's 0.067

## Outcome

- Δcomposite: **−0.0954** (predicted +0.03 to +0.06; off by ~0.13 in wrong direction)
- Δstructural: **0** (predicted +1 to +2)
- A2 cv: **0.049** (predicted 0.067 → actually slightly improved internally)
- New top warning: `symmetry-mismatch` (cf_delta=0.125) — recon vs ref symmetry diverged
- Extras: 0 → 31

## Root cause of prediction failure

Three layered errors in the reasoning:

1. **Encoder-classification assumption.** The plan assumed that drawing a {10/2} would generate a face that the encoder labels `star-v20`. But qiyas's encoder runs on the post-`voids detect` face graph, where the {10/2} edges cross the existing {10/4} and {10/3} edges and fragment the inner-star region into many small faces. The expected single 20-vertex star polygon never appeared as a single face.

2. **Monotonicity assumption.** The plan implicitly assumed that adding edges to a mesh either (a) creates new desired shapes or (b) is a no-op. In practice, adding edges to a face graph can *destroy* existing matches by splitting faces that previously matched a baseline expectation into smaller faces that don't match anything. Iter-17's 31 extras came from exactly this.

3. **Counterfactual delta is local.** qiyas's `counterfactual_score_delta` for `missing-shapes` (cf_delta=0.0667 in iter-14) models "what if these missing shapes were present." It does NOT model "what if you tried to add them and it cost you in fragmentation." This is exactly what task **#109 (counterfactual fragmentation tax)** is meant to fix.

## Calibration data for #109

iter-14 → iter-17 is a clean data point for the fragmentation-tax model:

| | iter-14 | iter-17 | Δ |
|---|---|---|---|
| edges added | 0 (baseline) | +1 connect block ({10/2}) | +1 |
| extras | 0 | 31 | +31 |
| missing | 45 | 41 | −4 |
| composite | 0.7842 | 0.6888 | −0.0954 |
| Naive cf_delta sum (missing only) | +0.0667 | — | predicted +0.0667 |
| Actual delta | — | — | −0.0954 |
| Implied fragmentation tax | — | — | **~0.16 per added connect-block on a saturated mesh** |

That tax (per-edit) is huge and domain-specific. It depends on whether the underlying mesh is already dense (saturated, where new edges fragment more than they create).

## What we should have done before shipping

Two checks that would have caught this in advance:

1. **Encoder classification probe.** Render a minimal test: just `divide C1 into 10 ; connect every 2 on C1 ; voids detect` (no other layers). Encode it. Confirm that the encoder produces a `star-v20` face. If it does — then the question becomes: "does the ADDITION to a saturated mesh still produce one?" If it doesn't even in isolation, the plan is dead at step 0.

2. **Counterfactual sanity check across layers.** Before shipping, use qiyas's diff against a synthetic "iter-14 + the targeted shape" output to confirm the fix moves the score in the predicted direction. (This requires plan #109's interaction modeling — chicken/egg.)

## Pattern across iter-15/16/17

All three iterations falsified their plan-level predictions:

- **iter-15:** `strapwork width 5 alternating` — predicted A5 PARTIAL gain; actual A2 collapsed (cv 0.067 → 0.1325). Composite −0.124. Reverted.
- **iter-16:** `strapwork width 5 over` — predicted A2 cv preserved (uniform crossings = symmetric); actual A2 collapsed worse (cv 0.2671). Composite −0.175. Reverted.
- **iter-17:** `add {10/2} to C1` — predicted +0.03/+0.06 from baseline-shape gain; actual −0.0954 from fragmentation extras. Reverted.

**Common thread:** all three predictions used the warnings array's `counterfactual_score_delta` as a forward predictor. None of them accounted for the cost-side (fragmentation, symmetry interaction, mesh saturation). Plan #109 is the right response — until counterfactual deltas model interaction and fragmentation, the iteration loop is flying blind on cost.

## What stays valid

- iter-14 baseline at composite=0.7842 remains the high-water mark.
- The {10/2}/{10/3}/{10/4} encoder-classification observation is a permanent piece of construction knowledge: "encoder classifies post-voids-detect faces, not the polylines you draw." Worth adding to construction-learnings.
