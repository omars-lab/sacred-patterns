---
name: gha-budget-month-freeze
description: "GHA spending limit (#603) will not be raised for ~1 month; do not idle the autonomous loop waiting on it"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

Do NOT wait for #603 (GHA spending-limit raise) to unblock the autonomous loop. Assume a ~1-month freeze on the budget restoration. Keep working under the freeze: build locally, mirror CI locally (qiyas `make ci-local-fast`, bikar build+test), accumulate held commits, and pick up substantive work that doesn't require a push to be valuable.

**Why:** owner directive 2026-05-27. The loop's prior idle pattern ("heartbeat ScheduleWakeup pending #603") was wrong because it treated the GHA-budget unblock as imminent; it isn't. Three consecutive quiet ticks ending the loop is the wrong behavior when there is a month of work to do that doesn't require pushing.

**How to apply:**
- During autonomous ticks, do NOT cite "held commits await #603" as a reason to idle.
- The push-cost discipline (Tenet 22, [[feedback_minimize_push_gha_budget]]) still applies: don't push frivolously, batch docs, use `[skip ci]` / `paths-ignore`. But the held-commit backlog is the *baseline*, not a blocker.
- Pick up substantive non-push work from the backlog: medallion-10 iteration (#80/#85), detector calibration (#129/#132), Tier 0 primitive coverage, decision-doc drafting on owner-PENDING items, code/test fixes for the held commits.
- Routing terminal-state per `qiyas/.claude/plans/post-i1-task-routing.md` should be re-read with the assumption that "owner-gated on #603" is not a terminal state for the loop — only "owner-gated on decision intent" is.
- If a task GENUINELY requires a remote push to validate (e.g., a CI-only smoke that can't run locally), then defer it — but local mirroring should be the default.

**Companion to:** [[feedback_minimize_push_gha_budget]] (Tenet 22 — push discipline still holds), [[feedback_push_authorization_general]] (push auth still pre-granted, the discipline is *frequency*), [[feedback_multiday_candidates_authorized]] (multi-day scope is fair game).
