---
name: Post-I1 routing plan — consult before every loop pickup
description: Under /loop directive, read qiyas/.claude/plans/post-i1-task-routing.md FIRST to classify next work; extend the doc as part of the iteration
type: reference
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
The post-I1 phase routing plan lives at `qiyas/.claude/plans/post-i1-task-routing.md`. It is a **living document** — extended on every loop pickup, not authored-once.

**Why:** Without it, loop iterations re-derive routing from first principles every wake and rediscover the same structural blockers (cf_delta saturation on saturated meshes, owner-decision chains, production-input fidelity gap). The plan captures: §A blocker classes (7 categories with routing rules), §B system gaps the task list won't close (5 promotable items), §C cascade dependency graph (R1/R2/R3/R4), §D the 6-step routing protocol, §E phase-done criteria.

**How to apply:**
- On every `/loop` wake (whether dynamic or scheduled), READ the plan's §A and §C before consulting TaskList.
- Survey for new PROPOSED decision docs across all three repos' `docs/decisions/`; if found, add to §A Class 1 and update §C if the new decision gates anything.
- Pick the next iteration's work from Class 5 in leverage order (not ID order). When Class 5 empties, promote from §B before idling.
- After completing the iteration: update §A (move completed item), §C if cascade shifted, §B if new gap surfaced, and bump `Last updated`. Commit the doc update with the work it tracks.
- The two highest-leverage actions at plan-authoring time (2026-05-17): authoring B1 (round-trip elimination decision doc) and B2 (issue #371 Options A/B/C/D decision doc). Both are loop-authorable; both unblock R2 and dissolve issue clusters.
- Phase done when R1+R2+R3+R4 simultaneously green. Then archive the plan (move to `qiyas/.claude/plans/archived/`) and start a successor for the next phase (likely I2 — photo-input cascade currently DEFERRED in #303).
- Cross-repo applies (per `feedback_cross_repo_authority.md`): the plan lives in qiyas but routes work across qiyas + bikar + sacred-patterns interchangeably. Cross-references from the other two repos to this doc are added by the loop on first read.
