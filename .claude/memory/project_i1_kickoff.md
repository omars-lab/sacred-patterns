---
name: i1-detector-calibration-kickoff
description: I1 detector-calibration cascade kicked off 2026-05-04 against macro_identity_fidelity = 0.002 baseline; user opted for Option A (aggressive close-the-gap) with self-aware loop discipline
type: project
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
I1 (qiyas#152) detector calibration started 2026-05-04 with these
parameters set by the user:

- **Mode:** Option A — close the gap aggressively, not Option B
  (per-gap tickets) or Option C (park it).
- **Discipline:** must use the iterate-detector-calibration skill.
  Skill enforces: predict→change→measure→log loop, three
  loop-detection triggers, web search on stuck, memory read on
  resume + write on lesson, escalation at no_improvement_streak >= 5.
- **Baseline at kickoff:** macro_identity_fidelity = 0.002 across the
  Phase 1.A corpus (medallion10-iter14, star10, star7). On
  medallion10-iter14: 37 truth classes vs 447 detector classes (12x
  over-fragmentation), 1 matched.
- **Open parameters at kickoff (need user decision before iter 1):**
  - Target macro fidelity (proposed: 0.7 strong, 0.5 floor)
  - Per-pattern floor (proposed: macro target + no individual < 0.4)
  - K-sweep / color-segmenter (#138-#140) in scope?
  - Iter-14 detector tuning ban — confirmed lifted?
  - Time budget — accepted "no hard cap, escalate at 5-deep no-improvement"

**Why:** Without these parameters fixed at kickoff, the loop's
"acceptance" question is undefined and the iteration will drift.

**How to apply:** Before kicking off iter-1, confirm the open
parameters above with the user. Then create
`qiyas/calibration/i1/iter-1.md`, run validate-detector to confirm
baseline matches the recorded 0.002, and start the recipe from the
skill.
