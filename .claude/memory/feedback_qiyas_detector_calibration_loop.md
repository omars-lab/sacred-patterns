---
name: qiyas-detector-calibration-loop
description: When iterating qiyas detector to close identity-fidelity gaps, use the iterate-detector-calibration skill — it has loop-detection, web-search escalation, per-pattern overfit guards, and memory read/write discipline built in
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
When the task is "improve qiyas detector identity-fidelity against the
corpus" (e.g. closing macro_identity_fidelity gaps after running
`qiyas validate-detector`), do NOT iterate ad-hoc. Use the skill at
`qiyas/.claude/skills/iterate-detector-calibration/SKILL.md`.

**Why:** Omar explicitly asked for "loop detection, experimentation,
iteration, websearch when in loops" on 2026-05-04 when greenlighting
Option A (close the I1 gap aggressively). Without the skill's
discipline, detector tuning falls into the tenet-7 "tune until green"
trap — three small justified tweaks compound into a rewritten
algorithm overfit to one fixture (cf. F3 arrangement-classifier
session 2026-05-04 where ROTATION_RADIUS_TOL_FRAC + ANGLE_DEG +
confidence formula were all softened in sequence to fit one iter-14
satellite test).

**How to apply:** Before the FIRST detector parameter change in a
calibration session, read the skill end-to-end. The skill's "Hard
prerequisites" section forces reads of MEMORY.md, tally.json, and
the last 3 iter-NN.md files — that's how cross-conversation amnesia
is structurally prevented. The skill's three loop-detection triggers
(param-tweaked-twice, prediction-falsified-twice, per-pattern
divergence) are non-negotiable; if one fires, follow its specific
prescribed action (web search, redesign doc, revert).

The escalation rule (no_improvement_streak >= 5 → STOP and surface to
user) means you should never iterate detector calibration past 5
deep without owner input. The user accepted "no hard time cap" but
explicitly accepted this escalation gate.
