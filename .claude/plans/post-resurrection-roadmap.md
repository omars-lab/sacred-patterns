# Post-resurrection roadmap — what's worth spending time on

## Context

As of 2026-05-02 the catch-22 is fully resolved. qiyas v0.1.1 ships
`score`/`baseline`/`fixtures` groups locally; the rollup fail-loud
guard surfaces missing tools instead of silently zeroing warnings;
session-1 has been resurrected onto the modern path; bikar-medallion-10
is unblocked for its iter-14 wedge-and-rotate restart.

The remaining task list is large but mixed — some items are real,
some are roadmap noise that would violate tenet 1 (simplicity over
complexity — don't build speculatively). This plan triages.

## Ranking

### Drive next (this session or the next sit-down)

1. **#82 — qiyas product vision doc.** Highest-ROI single-sitting
   item. Without a written "why does qiyas exist, who is the user,
   what's the value" doc, every V2.* prioritization is guesswork.
   ~30–60 min of writing. Pays back every triage conversation.

2. **#85 — bikar-medallion-10 iter 14 wedge-and-rotate restart.**
   Unblocked. The hand-off doc has a 5-step entry point. Real
   iteration learning happens here, AND every other roadmap item
   (#75, #77, #78) needs calibration data this run will produce.
   Constraint: requires the interactive bikar tool environment and
   user time to drive — not a background-agent task.

### Defer until calibration data exists

These are real ideas but premature without iteration data to ground
them:

- **#75 [V2.B] global warning optimizer (net-delta ranking).** Today
  `warnings[0]` ranks by isolated counterfactual delta — fixing one
  warning can regress another. A net-delta optimizer needs an
  *interaction matrix* calibrated against actual iteration outcomes.
  Build it AFTER #85 produces 5+ iterations with predicted-vs-actual
  delta data. Premature otherwise.
- **#77 [V2.E] auto-capture on GO.** Premature until at least one
  session reaches `go_no_go=converged`. Nothing to capture.
- **#78 [V2.F] escalate-qiyas-divergence skill.** Becomes valuable
  once #85 or #98 produces a real qiyas-vs-ground-truth divergence
  to escalate. Speculative otherwise.
- **#76 [V2.D] construction hints (`qiyas hint`).** Design spike.
  Should follow #75 — hints flow from how warnings are ranked.

### Defer because lower-urgency

- **#74 [V2.A] qiyas iter analyze.** Useful but only systematizes
  what the iteration agent does manually today. Real but not urgent.

### Cleanup, do when there's an idle slot

- **#79 — qiyas score backfill against historical iterations**
  missing `validation/` subdirs. Mechanical. Most valuable as
  calibration corpus for #75.
- **#100 — push v0.1.1 to ghcr.** Cosmetic for solo-dev workflow
  (Docker resolves local tags first); matters only when distributing
  the image. Blocked on PAT scope upgrade — don't unblock until
  someone else actually needs the image.

### Not yours to drive

- **#25 / #59 / #60** — A5 band-network detector slices in qiyas.
  Tracked upstream.
- **#80** — bikar-medallion-10 parent (closes when #85 does).

## The discipline this plan encodes

- **Tenet 1 (simplicity over complexity):** don't build #75/#76/#77
  speculatively before the data exists to calibrate them. The right
  size of the V2.B optimizer can only be derived from real predicted-
  vs-actual delta pairs.
- **Tenet 4 (verify before claiming done):** the gating signal for
  unblocking each V2.* item is named explicitly above (calibration
  data exists / first converged session exists / first divergence
  exists), not "feels ready."

## Open follow-ups

This plan replaces the ad-hoc roadmap conversation. When V2.* items
become ready, update this doc with the gating signal that flipped
and re-rank.

## Cross-references

- `docs/iteration-status.md` — per-session state for session-1,
  session-8-fold, bikar-medallion-10
- `qiyas/docs/issues/2026-05-02-orchestrator-warnings-empty-when-score-unavailable.md`
  — the catch-22 resolution that unblocked everything above
- `CLAUDE.md` "Engineering Tenets" — the lens these rankings apply
