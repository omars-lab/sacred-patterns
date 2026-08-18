---
name: minimize-push-gha-budget
description: every git push to qiyas/bikar/sacred-patterns burns GitHub Actions minutes against a real account budget; mirror CI locally and batch pushes
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

Every `git push` to qiyas / bikar / sacred-patterns triggers GitHub Actions workflows that consume the org's billable Actions minutes. The budget is real and has been exhausted at least once (2026-05-26: qiyas + bikar CI both red with "recent account payments have failed or your spending limit needs to be increased"), which blocks the entire loop because §F routing depends on green CI as a signal.

**Why:** docs-only commits and routine routing/audit pushes were going up at near-tick frequency. Each push to qiyas main fires `lint-test` + `docker-build` + `review-portal-build`; each push to bikar main fires `Deploy to Cloudflare Pages`. None of these are free; the cost accumulates per push, not per substantive change. The autonomy contract granted push authority — it did NOT grant the right to spend budget without mirroring CI locally first.

**How to apply:**

1. **Before every push**, mirror what CI will do. For qiyas: `make ci-local-fast` (already standard per the existing `run-ci-local-fast-before-push` memory). For bikar: at minimum `npm run build -w packages/core` + `make test` if any code changed; for docs-only commits, no CI mirror needed but **batch the push**. For sacred-patterns: similar — run any locally-cheap lint/format/test before pushing.

2. **Batch docs-only pushes.** If a tick produces only docs / routing-plan / mental-model / decision-doc edits, do NOT push each commit immediately. Accumulate them within the tick (or across ticks if the next tick will also push) and ship in one push. The autonomy contract doesn't require per-commit pushes — it requires the work to be safe and reversible, which batched pushes are.

3. **Skip the push entirely for purely local audit-trail commits** when the next substantive commit will piggyback on it. Example: a §B5 routing-plan addendum that records "audit ran, no drift" doesn't need to fire a CI cycle by itself — let it ride with the next code commit.

4. **For docs-only commits, prefer `[skip ci]` / `[ci skip]` in the commit message** where the workflow respects it. GitHub Actions honors `[skip ci]` in the commit message head/body for push events on most workflows by default. Verify each repo's workflows respect it before relying on it (some custom workflows can override).

5. **Path-filter the workflows themselves.** The structural fix is `on.push.paths-ignore: ['**.md', 'docs/**', '.claude/**']` on every workflow that doesn't need to run for docs changes. This is a one-time PR per repo that pays back forever. File as cross-repo work when budget is restored.

6. **Stop rule:** if a tick produces 3+ commits and none of them touched code that the CI gates actually exercise, that's a batch-push signal — collapse to one push or hold for the next code commit. If a tick is pure docs and the next tick is also pure docs, hold.

**Companion to:** [[feedback_run_ci_local_fast_before_push]] (run ci-local-fast before push — same principle, this extends it to *whether* to push, not just *what* to verify), [[feedback_mirror_ci_locally]] (mirror CI wholesale at commit time), [[feedback_push_authorization_general]] (the authority — this constrains *when* to use it).

*Failure mode this prevents:* the 2026-05-26 cascade where docs-only commits (mental-model PRs, decision-doc addenda, routing-plan audit notes) each fired a separate qiyas CI run + bikar deploy, contributing to the GHA spending-limit breach that froze the entire loop. The autonomy was used correctly per the push-authorization grant; the cost — that the grant has a real budget — wasn't internalized until billing failed.

*Anti-pattern this names:* "I just edited a doc; let me ship it now" as a reflex. Each ship is a unit cost; reflexes don't price.
