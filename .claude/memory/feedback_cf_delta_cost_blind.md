---
name: cf_delta is upside-only — model the cost before iterating
description: qiyas warnings[0].counterfactual_score_delta predicts the upside of a fix but not the cost of the edit; on saturated meshes the cost dominates
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
qiyas's `counterfactual_score_delta` (the score-lift estimate attached to each warning) only models what would happen *if the warning were resolved*. It does NOT model what happens to OTHER metrics when you make the edit that resolves it. On a saturated polygon mesh (e.g. C1 with multiple connect-blocks already), an edit aimed at warnings[0] often costs more in fragmentation, symmetry interaction, or missed-classification than the warning's cf_delta promises in upside.

**Why:** bikar-medallion-10 iter-15/16/17 (2026-04 → 2026-05-03) all faithfully translated their iteration's warnings[0] into a mechanical edit and all three regressed by 0.10–0.18 composite vs the predicted +0.03 to +0.07. iter-17 calibration: adding one connect-block on saturated C1 produced 31 new extras and a fragmentation tax of ~0.16 composite. The pattern is structural — until qiyas plan #109 (counterfactual fragmentation/interaction tax) lands, every "follow warnings[0]" iteration on a mature pattern is gambling against an unmodeled cost term.

**How to apply:**
1. Before shipping an iteration that follows warnings[0], ask: is the targeted zone *saturated* (multiple existing edges/connects/lines passing through it)? If yes, the cf_delta is unreliable as a forward predictor — expect the edit to introduce extras and partial-shape regressions.
2. Prefer outer-zone edits where existing mesh density is low (one connect or fewer). The cf_delta is a better predictor when the cost-side is small.
3. If multiple consecutive iterations have falsified their predictions in the same direction (upside under-realized, cost under-modeled), STOP iterating and escalate to fix the predictor rather than running more iterations against a known-broken signal.
4. When writing iteration plans with predicted Δ, include a "cost terms not modeled" section listing what the cf_delta ignores (fragmentation, symmetry interaction, encoder reclassification). This forces the prediction to be honest and produces calibration data when it's wrong.
