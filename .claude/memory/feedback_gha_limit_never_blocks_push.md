---
name: gha-spend-limit-never-blocks-push
description: "GHA spending limit / billing freeze is NEVER a reason to hold a push; push first, let GHA fail loudly if budget is exhausted — held commits accumulating in local trees is worse than red CI runs"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

GHA spending-limit / billing-freeze status (e.g. qiyas#603) is NOT a push-gate. After local CI mirrors (`make ci-local-fast` for qiyas, `npm test` for bikar, equivalent for sacred-patterns) are green, push immediately — even if CI is known to fail loud on the remote due to billing. Held commits accumulating in local trees ("waiting on #603 to clear") is worse than a queue of red CI runs the user can ignore until billing is restored.

**Why:** 2026-05-30 — the autonomous loop held 58 commits (bikar 12, qiyas 40, sacred-patterns 6) across multiple ticks waiting for #603 (raise GHA spending limit) to clear, treating "GHA budget exhausted" as a push-blocker. The owner corrected: "GHA spending limit should not block push, push anyway and remember this." Held trees obscure what's actually shipped, create rebase/conflict risk if other agents push to main, and make `git log origin/main..main` an unreliable proxy for "in-flight work."

**How to apply:** When considering whether to push:
1. Run the relevant local CI mirror (qiyas `make ci-local-fast`; bikar `npm test`; sacred-patterns equivalent). If green → proceed to push.
2. Do NOT add a "is GHA budget OK?" / "is #603 cleared?" / "will CI run?" check. GHA-state has no veto on push.
3. If push fails with a non-budget error (rebase needed, hook failure, real test failure), handle that; if it succeeds, done — even if the resulting CI run is destined to be red on billing.
4. Never schedule a heartbeat with reason "waiting on #603 to clear" / "held commits push-ready when budget clears." Push them.

**Stop rule:** if you find yourself writing "held commits await #603" in any tick reason, you're applying the wrong policy — push them.

**Companion to:** [[feedback_never_block_on_gha]] (the general rule that no deliverable hard-depends on GHA — this specializes it to the push action specifically), [[feedback_minimize_push_gha_budget]] (mirror CI locally + batch docs-only commits — still applies; but "batched and locally-green" is what triggers push, not GHA-budget-clear).

**Failure mode this prevents:** the 2026-05-30 idle-tick cascade — 15 consecutive ticks reporting "58 held, all gated on #603" when the correct action every tick after local-CI-green was just `git push`.
