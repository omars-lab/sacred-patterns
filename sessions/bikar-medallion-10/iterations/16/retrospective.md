# Iter 16 — Retrospective

## What we tried

Plan #108 PR1 (`crossing over` / `crossing under`) shipped end-to-end in bikar — tokens, parser, kernel branch, 6 new tests, full suite green (634 tests). Iter 16 used `crossing over` as the confirmatory experiment: same DSL as iter-15 but with the new symmetry-preserving mode.

## What we expected

- A2 cv stays ~0.067 (because over-mode is rotation-invariant)
- A5 PARTIAL preserved (~+0.03)
- composite vs iter-14: 0.74–0.79 (small dip from extras dominates the small A5 lift)
- 150–185 extras spawned

## What actually happened

- A2 cv **0.2671** — twice iter-15's value, four times iter-14's. Status BROKEN.
- A5 PARTIAL preserved (correct prediction)
- composite **0.6089** — −0.175 vs iter-14, even worse than iter-15
- **247** extras — 33% more than iter-15

The small-dip prediction was off by a factor of ~6×. The A2-preservation prediction was off by 4× in the wrong direction.

## Why the prediction failed

The plan modeled `crossing over` as a one-line policy change inside `assignStrands`. The kernel change matches that model: `isOver = true` always; no alternation toggle. The plan failed to model two things downstream of that:

1. **Strand grouping is sector-sensitive.** `assignStrands` walks the edge graph in graph-order. Two rotated copies of the same wedge can end up with different strand-ID assignments depending on which neighbor the walk visits first. Over/under uniformity does NOT make strand grouping uniform.

2. **Band rendering produces closed-form fragments per strand.** Each strand becomes a closed band path in the SVG. If strand grouping varies across sectors, the band shapes vary across sectors — and qiyas counts each closed band as a separate shape. 247 extras = 247 band fragments that don't pair against any reference shape.

The plan's geometry intuition ("uniform over-strands are rotationally invariant") was true in isolation but wrong about the algorithm that implements it. The algorithm was already non-rotation-invariant in its strand-grouping step; over-mode just exposed that more visibly.

## Calibration data for plan #109 (counterfactual fragmentation tax)

This iteration is a textbook example of the failure class plan #109 targets:
- `warnings[0]` = extra-shapes, cf_delta=0.2253. The counterfactual "if recon dropped the 247 extras" predicted +0.225 lift.
- The actual change (vs iter-14) was −0.175. So the counterfactual was directionally correct about the cost of extras, but didn't predict that *adding the strapwork block* would *create* those extras.
- A future "interaction tax" would say: "applying fix X (add strapwork to fix A5) is predicted to add ~250 extras based on prior iter-15 data → counterfactual A5 lift +0.03 minus tax ~0.20 = net −0.17 → DON'T DO THIS." That's exactly what would have prevented this iteration.

## Cross-tenet check

- **Tenet 2 (root cause, not fallback):** the bikar kernel change is itself a root-cause fix for "alternating breaks symmetry." The new failure (strand-grouping breaks symmetry independently) is a separate root cause that was previously masked. Not a fallback regression.
- **Tenet 4 (verify before claiming done):** plan #108 PR1 was claimed shipped after tests passed and one render. The render *succeeded* (svg generated) but I did not verify the *outcome metric* (A2 cv) before declaring the experiment a success. The plan was shipped; the experiment wasn't validated until now. This is the right place for the verification gate, but next time the experiment should be predicted-and-checked in the same step.
- **Tenet 6 (inherited claims):** plan #108's prediction "A2 cv stays under 0.08" was an inherited claim from the plan-mode session. I should have read it as a hypothesis to test, not a fact to rely on. Tenet 6 applied correctly here — I ran the experiment to falsify the claim instead of acting on it.

## What this means for plan #108

PR1 ships and stays — `crossing over` and `crossing under` are correct, well-tested DSL features. They just don't solve the medallion-10 strapwork problem. PR2 (rotational mode) and PR3 (weave mode) need to wait until we understand whether the root cause is in `assignStrands` (graph-order strand grouping) or downstream in band-path generation.

PR2 is now LESS likely to be the right next move — if grouping itself is the bug, no crossing-mode policy fixes it.
