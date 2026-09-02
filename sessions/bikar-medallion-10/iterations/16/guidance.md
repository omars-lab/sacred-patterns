# Iter 16 → Iter 17 — Guidance

## Decision: REVERT to iter 14 baseline

Iter 17 starts from `iterations/14/pattern.bkr` (composite 0.7842), NOT from iter-15 or iter-16. The strapwork block in any current crossing mode is a net regression.

## What NOT to do in iter 17

- Do NOT add `strapwork` block at all yet — it produces 185–250 extras regardless of crossing mode
- Do NOT try `crossing under` (mirror image of `crossing over` — same algorithm, same failure mode)
- Do NOT add the unimplemented `crossing rotational` (plan #108 PR2) — root-cause analysis suggests grouping is the issue, not crossing policy

## What to consider for iter 17

`warnings[0]` for iter-14 (the baseline we're reverting to) is what should drive iter-17. **Read iter-14's validation.json `overall.warnings[0]` and propose a fix for THAT** — not for the A5 problem that iter-15/16 were trying (and failing) to solve.

The A5 work is gated on a real fix in bikar — either (a) `assignStrands` becomes rotation-invariant by sector-folding edges before strand assignment, or (b) band-path generation merges fragments back into continuous strands across sectors. Both are bikar work, NOT next-iteration work.

## Bikar follow-up (for plan #108 v2)

1. Read `bikar/packages/core/src/kernel/strapwork.ts:assignStrands` and write down the actual graph-walk order. Confirm whether it's deterministic given the `EdgeGraph` structure but non-rotation-invariant.
2. Add a test: render a medallion-10 strapwork with `crossing over`, verify 10-fold rotation symmetry of the resulting strand IDs (hash strands by position, group by sector, check group equality).
3. If that test fails, the bug is in `assignStrands`. Fix is to sort/canonicalize edges by polar angle before walking.
4. If that test passes, the bug is in band-path rendering — different problem, different plan.

This work belongs in plan #108 as PR2-revised.

## Plan #109 (counterfactual fragmentation tax) — promote to high priority

Iter-15 and iter-16 are now both clean evidence cases. The cost of "fix that adds strapwork" can be quantified from iter-15's 185 extras and iter-16's 247 extras — both at composite ~−0.12 to −0.17. Plan #109 should be implemented next; without it the iteration loop will keep walking into this trap whenever `warnings[0]` says "missing band shapes."
