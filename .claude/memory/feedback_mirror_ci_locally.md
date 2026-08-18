---
name: Mirror CI exactly in pre-commit — wholesale, not staged-only
description: Pre-commit hooks scoped to staged files miss tree-wide drift; mirror CI's wholesale invocations (ruff check src tests, ruff format --check src tests) at commit time when the cost is negligible (~0.15s for qiyas)
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
Pre-commit hooks must mirror CI's invocations exactly — same commands, same scope (wholesale tree, not staged-files-only) — for any check whose wholesale cost is < ~5s. Owner's quote: "why do we keep running ci commands here and eating up our github budget?"

**Why:** Today (2026-05-20) closing qiyas#339 needed three separate CI re-runs (commits da0645b, 797664e + this fix) to surface preexisting drift: D205 in scorer.py, RUF046 in viz.py, and format drift across 7 unrelated files. Each was caught instantly by CI's `ruff check src tests` / `ruff format --check src tests`, but missed by pre-commit because pre-commit scoped ruff to only-staged-files (xargs ruff check $staged_py). The wholesale runs cost 0.15s on qiyas's tree — well below the threshold where staged-scoping is worth the divergence risk. Each CI re-run cost ~2 minutes of GHA budget + owner attention.

**How to apply:**
- For any qiyas / bikar / sacred-patterns CI step whose wholesale cost is < ~5s, run it wholesale in pre-commit, not staged-only.
- Cheap-and-wholesale candidates: ruff check, ruff format --check, eslint with cache, prettier --check, tsc --noEmit (already wholesale because of TS project refs).
- Expensive-and-wholesale (DON'T add to pre-commit): pytest, vitest, build, semgrep, bandit, gallery regen — keep these in `make ci-local` for explicit pre-push runs.
- Document the wholesale call in the hook with a WHY comment naming the CI step it mirrors. Tenet 11: one tool path per question (CI = source of truth; pre-commit is the cheap mirror).
- When a CI step burns more than once on the same drift class, IMMEDIATELY promote that step to the wholesale pre-commit list rather than continuing to push-and-recover.

**The general principle:** if CI's gate is wholesale, pre-commit's gate should be wholesale too (when cheap). The staged-only optimization is for slow checks (lint thousands of files), not fast ones. Drift in unrelated files accumulates silently otherwise — exactly the bug pattern this guards against.

**Reference commits (qiyas):** 2e67c7a (pre-commit wholesale ruff), 797664e (the 7-file format burn that triggered this lesson).
