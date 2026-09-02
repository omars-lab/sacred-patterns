# CI report standard (pointer)

**Canonical source:** `qiyas/docs/ci-report-standard.md`. Do not fork this contract — read the qiyas copy.

## TL;DR for sacred-patterns

Every CI job that emits a failure report follows this duo:
- **Artifact** via `actions/upload-artifact@v4` — self-contained HTML (base64-inlined images), 90-day retention.
- **Step summary** via `$GITHUB_STEP_SUMMARY` — markdown index hyperlinking the artifact.

Pass = one-liner summary, no artifact (saves storage; simpler validation contract).

## When this lands in sacred-patterns

The first sacred-patterns workflow to need this pattern is the iteration-loop validation suite or the pixel-diff regression gate (iteration loops run locally today; CI-side validation is anticipated). When authored:

1. Read `qiyas/docs/ci-report-standard.md` — the canonical contract.
2. Copy `qiyas/tools/ci-report-validate.py` into `sacred-patterns/tools/` (the validator is self-contained Python 3 + `gh`).
3. Mirror the snippet at the bottom of the standard into the new workflow.
4. Update this file with the sacred-patterns-specific job name and expected artifact name.

## Related

- qiyas: `docs/ci-report-standard.md` (canonical)
- qiyas: `docs/decisions/2026-05-20-byte-strict-fixture-comparator-decay.md` (originating decision)
- bikar: `docs/ci-report-standard.md` (same pointer, different repo)
