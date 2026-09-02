---
name: Experiment vs ship distinction
description: When a code change is also a confirmatory experiment, treat "ship" and "validate hypothesis" as separate gates — code-tested is not hypothesis-confirmed
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
When a planned PR explicitly carries a hypothesis ("this change will improve metric X by Y"), do NOT declare the work done after the code ships and unit tests pass. The PR is shipped; the hypothesis is not confirmed until the *outcome metric* is checked against the prediction.

**Why:** Iter-16 of bikar-medallion-10 (2026-05-03) shipped bikar plan #108 PR1 (`crossing over` mode) with full test coverage and a successful render. I declared PR1 "shipped" and started the experiment. The actual experiment falsified the plan's central hypothesis (A2 cv 0.067 → 0.2671, composite −0.175 vs iter-14, worse than the regression it was meant to fix). The plan's prediction was off by ~6× on composite delta and 4× in the wrong direction on A2 cv. Code working ≠ hypothesis confirmed.

**How to apply:** When a plan documents a numeric prediction (composite, cv, count), the workflow has three gates, not two:
1. Code ships (tests pass, render succeeds)
2. Outcome metric measured (run the validation, read the JSON)
3. Prediction vs measurement compared — if they diverge, treat the prediction as falsified and update the plan with the falsification finding before continuing to subsequent PRs in the same plan

This is especially important for plans that bundle PRs in sequence ("PR1 unblocks PR2 unblocks PR3") — falsifying PR1's hypothesis often invalidates the rationale for PR2/PR3, and silently moving forward to PR2 wastes the next iteration.
