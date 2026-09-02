# Iter-17 Evaluation — REVERT to iter-14

## Decision: REVERT

Composite **0.6888** vs iter-14 baseline **0.7842** → **Δ = −0.0954**.

Predicted Δ was **+0.03 to +0.06**. Off by ~0.13 in the wrong direction.

## What was measured

| Metric | iter-14 | iter-17 | Δ |
|---|---|---|---|
| composite | 0.7842 | 0.6888 | −0.0954 |
| pixel | 74.1% | 74.0% | −0.1pt |
| structural (A6 PASS / total) | 1/18 | 1/18 | 0 |
| topology_complete | False | False | — |
| go_no_go | iterate | iterate | — |
| A2 status | APPROXIMATE | APPROXIMATE | — |
| A2 cv (internal) | 0.067 | 0.049 | actually improved |
| extras (validate.json) | 0 | 31 | +31 |
| missing (validate.json) | 45 | 41 | −4 |

## Top warning shifted

**iter-14:** `missing-shapes` (cf_delta=0.0667) was the leading lever.
**iter-17:** `symmetry-mismatch` (cf_delta=0.125) is now top — recon's detected symmetry diverged from the reference's.

## A6 unchanged

The targeted shape `inner-star--star-v20` (expected 1, found 0) is **still MISSING**. The {10/2} decagram added on C1 did not produce a 20-vertex star polygon as encoder-classified. A6 distribution is identical to iter-14: 1 PASS, 11 MISSING, 4 PARTIAL, 2 EXCESS.

## Why the prediction failed

The plan reasoned that `connect every 2 on C1` would draw a 10-pointed star whose outline traces 20 vertices, populating `inner-star--star-v20`. Two things went wrong:

1. **The encoder did not classify the produced shape as star-v20.** A {10/2} on a 10-divided circle produces a single connected decagram. Whether qiyas's encoder sees this as one 20-vertex star polygon vs. ten overlapping line segments depends on whether bikar's `voids detect` finds the inner-star face cleanly or fragments it via intersections with the existing {10/4} and {10/3}. Empirically: it fragmented.

2. **Adding more edges generated 31 extras.** The new {10/2} edges intersect {10/4} and {10/3} at additional points; `voids detect` carved up the inner-star zone into many small faces, none of which match a baseline expectation. Net effect: the A6 verdicts didn't move, and the validate-side `extra-shapes` count jumped from 0 to 31.

3. **Cascading symmetry divergence.** Even though internal A2 cv improved (0.067 → 0.049), the symmetry-mismatch warning compares recon-symmetry to ref-symmetry. The added {10/2} mesh changed the recon's *detected* symmetry signature in a way that diverged further from the reference's signature.

## Cross-tenet check

- **Tenet 6 (trust but verify inherited claims):** iter-14's guidance.md asserted that diff-level "missing-shapes" warnings were encoder-vocabulary noise and that the real signal was the A6 list. That claim is still correct as far as I can tell, but the plan's translation step — "A6 inner-star--star-v20 MISSING → add {10/2}" — assumed a deterministic encoder mapping that doesn't hold. The mechanical edit was rationally derived but the encoder's classification behavior wasn't verified before shipping.
- **Tenet 4 (verify before claiming done):** the iteration shipped end-to-end, but the hypothesis was not confirmed until validation ran. Same lesson as iter-15/16.

## What this tells us about the next move

- Adding more polygon-mesh edges to the existing {10/4}+{10/3} on C1 is **not** monotonically beneficial. The encoder's face-classification depends on the global mesh, and adding edges can *destroy* baseline-shape matches as easily as create them.
- The `inner-star--star-v20` baseline expectation may be unreachable via "more decagrams" — it may require a different construction (e.g., explicit polygon shapes, not chord intersections).
- Iter-14's top warning `missing-shapes` (cf_delta=0.0667) is misleading at the iteration-loop level if every available edit makes it worse. **Plan #109 (counterfactual fragmentation tax)** is now urgent — qiyas's counterfactual delta needs to model the cost of mesh fragmentation, not just the upside of adding shapes.
