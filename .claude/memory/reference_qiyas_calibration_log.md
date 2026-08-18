---
name: qiyas-i1-calibration-log
description: Detector calibration iteration log + persistent loop-detection state for qiyas#152 (I1) lives at qiyas/calibration/i1/
type: reference
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
The I1 detector-calibration loop's operational state lives at
`/Users/omareid/Workspace/git/qiyas/calibration/i1/`:

- `tally.json` — persistent loop-detection state. Contains
  macro_score_history, per_pattern_history, no_improvement_streak,
  param_change_counter, stuck_gaps, web_searches_run,
  redesigns_written. Read it at the start of every calibration
  iteration (the skill enforces this).
- `iter-NN.md` — per-iteration log: gap targeted, hypothesis,
  predicted lift, change made, per-pattern + macro scores
  before/after, verdict, lesson.
- `redesign-NN.md` — written when iteration trigger 2 fires
  (prediction falsified twice in a row); spells out the new mental
  model before iteration N+1 attempts it.
- `README.md` — schema doc for the directory.

The runbook that uses these files lives at
`/Users/omareid/Workspace/git/qiyas/.claude/skills/iterate-detector-calibration/SKILL.md`.

The validate-detector command that produces the score being tracked:
`uv run qiyas validate-detector --corpus tests/fixtures/corpus-phase1a`.
Today's baseline (pre-I1, 2026-05-04): macro_identity_fidelity = 0.002.
