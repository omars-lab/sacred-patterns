---
name: never-block-on-gha
description: "The autonomous loop must never treat GHA (GitHub Actions) availability as a dependency; find local/alternative workarounds for deploy, CI, confidence"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

Never gate work, deployment, or confidence signals on GitHub Actions being available. GHA can be blocked for a long time (budget freeze, billing failure — assume ~1 month), and the loop must keep delivering value the entire time by finding alternative paths.

**Why:** The NaqshCoffee org's billable GHA budget was exhausted 2026-05-26, freezing CI across qiyas + bikar + sacred-patterns. The owner's standing direction: "never block on gha push / we should not depend on gha ... since it could be blocked for a while ... we need to find workarounds as needed / alternative ways for deployments, confidences, etc." Treating "held commits await GHA budget" as a terminal state is the failure mode — it idles the loop on an externality the owner has explicitly said to route around.

**How to apply:**
- **CI / confidence:** mirror what CI would run, locally — `make ci-local` / `make ci-local-fast` (qiyas), `npm run build -w packages/core && make test` (bikar), `make compile && npm test` (sacred-patterns). Local green IS the confidence signal; don't wait for the green check on GitHub. See [[feedback_mirror_ci_locally]] and [[feedback_run_ci_local_fast_before_push]].
- **Deployment:** prefer local/CLI deploy paths over CI-triggered ones. bikar edge-function deploy is `make local.deploy-compile-pattern` (Supabase CLI, bundles bikar-core locally — works without GHA). Package publish that normally fires on tag-push can be done manually via `npm publish` with a PAT when truly needed (still owner-OK for tags).
- **Pushes:** still batch + `[skip ci]` per [[feedback_minimize_push_gha_budget]] — but the point of batching is budget thrift, NOT a blocker. Local commits accumulate freely; pushing is decoupled from progress.
- **When a task's only blocker is "needs GHA":** find the local equivalent and do it; if there genuinely is none (e.g. a workflow can only run server-side), file the alternative-path investigation as the work rather than parking the task.

**Companion to:** bikar Tenet 22 / sacred-patterns Tenet 25 (minimize pushes — budget thrift), [[feedback_gha_budget_month_freeze]] (the loop must keep working under freeze), [[feedback_push_authorization_general]] (push autonomy after local-green). This memory is the *generalization*: GHA is never a hard dependency for any deliverable.
