---
name: multiday-candidates-authorized
description: Do not hesitate to pick up multi-day candidates during autonomous loop; substantial work scope is not a routing blocker on its own
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

Under `/loop until we address all our issues`, do not hesitate to implement multi-day candidates. Substantial scope (2-4 days, multi-week cascades, design-skill work) is NOT a §F routing blocker on its own. The autonomous loop is authorized to chunk and drive these forward across many ticks if no shorter on-path RED candidate exists.

**Why:** the routing plan (`qiyas/.claude/plans/post-i1-task-routing.md`) has been firing §F STOP-and-idle repeatedly because it treats multi-day candidates as "doesn't fit a loop iteration." That's the wrong heuristic — the user's intent is steady forward progress on the system, not idle ticks waiting for a perfect 1-hour unit. Owner clarified 2026-05-25: "do not hesitate to implement multi day candidates — remember this."

**How to apply:**
1. When §F mechanical check finds RED ON_PATH unblocked empty, **do not idle** simply because remaining Class 5 candidates are substantial. Pick the highest-leverage substantial candidate (#132 corpus authoring, #25/#59/#60 A5 detector cascade, #74/#75/#77 V2 sub-commands, #362 Phase 1, etc.) and start chunking it.
2. Open the work with a tracked task + slice the multi-day candidate into commit-sized chunks (one ci-local-fast-green commit per chunk).
3. Persist progress in the routing plan AND in the candidate's own plan/decision doc so the next loop tick can resume cleanly.
4. Cross-session continuity matters more than per-tick completion: a multi-day candidate that gets 1 chunk per tick across 10 ticks ships in 10 ticks; idling 10 ticks ships nothing.
5. Only STOP-and-idle when ALL of: RED ON_PATH unblocked is empty AND no Class 5 candidate is actionable (truly blocked: missing data/tools/dependencies, not just "substantial").

**Companion to:**
- [[feedback_cross_repo_authority]] (loop can pick from any of qiyas/bikar/sacred-patterns)
- [[feedback_decision_pick_authorization]] (ship documented defaults on owner-PENDING)
- [[feedback_push_authorization_general]] (general push authority after ci-local-fast green)
- Tenet 19 (bias for action — substantial scope is not a permission ask)
- Tenet 20 (fix simplest broken thing first — within the chosen candidate, slice smallest-tier first)

**Failure mode this prevents:** the §F STOP-and-idle loop pattern observed 2026-05-25 where multiple back-to-back ticks idle 1800s because every actionable candidate is "multi-day." The loop ships nothing for hours while the user's standing directive (`/loop until we address all our issues`) is unsatisfied. With this rule, the loop ships a chunk per tick instead, and the cumulative progress closes issues across many ticks even when no single tick can ship a complete cascade.

**Anti-pattern this names:** treating "substantial" as a synonym for "owner-gated." Substantial work doesn't need permission; it needs chunking. The §F protocol's "no Class 5 fits a loop iteration" clause is too strict — it should read "no Class 5 chunk fits a loop iteration," and the loop should produce the chunking.
