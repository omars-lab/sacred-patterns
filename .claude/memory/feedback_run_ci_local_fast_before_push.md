---
name: Run ci-local-fast before pushing qiyas commits
description: qiyas Makefile has `make ci-local-fast` (5 steps, ~30s) that mirrors CI's lint-test gates; running it before push avoids burned CI cycles on routine format/cli-docs drift
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
Before `git push` on qiyas, ALWAYS run `make ci-local-fast`. It runs the 5 fast CI gates: workflow YAML parse, ruff check, ruff format --check, mypy --strict, and check-cli-docs (~30s total). The slow `pytest` step is skipped — that lives in `make ci-local`.

**Why:** 2026-05-20 Slice 5b shipment burned TWO CI cycles (26195833792 ruff-format, 26195952471 check-cli-docs) on issues the local gate would have caught in 30s. Both failures were routine drift: new files weren't ruff-formatted, and adding a new CLI subcommand makes `docs/cli-reference.md` stale automatically. Each cycle is ~2 minutes of CI wallclock + agent attention to triage + a follow-up commit.

The Makefile target's header comment explicitly names this rule:
> "The Stop hook (qiyas#463) and `git push` runners depend on it."

So there IS an enforcement mechanism, but I bypassed it by running `git push` from a non-hook context (Bash tool direct).

**How to apply:** In any loop iteration that ends with `git push origin main` (qiyas), the immediately-preceding command should be `make ci-local-fast`. If that gate fails, fix locally and re-run before pushing. Only skip when the change is docs-only (no `.py` edits, no CLI changes) — and even then, the workflow-YAML and format gates still apply if you touched `.github/` or `*.md`.

For bikar use `make test && make lint` (cheaper equivalent — bikar has no `ci-local-fast` target yet). For sacred-patterns, no analogous target exists (mostly docs).

*Failure mode this prevents:* the 2026-05-20 cascade where shipping Slice 5b looked complete after local pytest passed, but two routine-drift gates the local target *already runs* caught the issue at CI time anyway. The lesson isn't "add a gate" — the gate exists. The lesson is "use it on every push."
