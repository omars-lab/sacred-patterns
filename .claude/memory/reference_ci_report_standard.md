---
name: CI report standard — artifact + step summary duo
description: Cross-repo default for every CI report (qiyas, bikar, sacred-patterns); canonical contract lives in qiyas
type: reference
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
Every CI job that emits a failure report follows this duo:
- **Artifact** via `actions/upload-artifact@v4` — self-contained HTML with base64-inlined images, 90-day retention.
- **Step summary** via `$GITHUB_STEP_SUMMARY` — markdown index hyperlinking the artifact.

On pass: one-liner summary, no artifact (saves storage; simpler validation).

**Canonical contract:** `qiyas/docs/ci-report-standard.md` — single source of truth. Bikar and sacred-patterns hold one-paragraph pointer docs under the same filename that redirect to qiyas.

**Validator:** `qiyas/tools/ci-report-validate.py` — JSON-on-stdout helper for inspection skills (autonomous-loop, babysit-prs, future cross-repo skills). Exit 0 conformant, 1 `REPORT_EMIT_REGRESSION`, 2 usage error. Copy this script into bikar/sacred-patterns when their first reporting job lands; do not re-implement.

**First production use:** qiyas `lint-test` fixture-drift gate (qiyas#474 Slice 4, commit 699f8ea, 2026-05-20).

**Why this duo (not PR sticky comment, not GitHub Pages per-run):** the artifact carries the full visual evidence; the step summary is the entry point on the workflow run page. PR comments add noise on green runs; GitHub Pages per-run isn't natively supported (open `actions/deploy-pages#50`).

**When inspecting a CI run:** if a job is in the failure list and the standard says it emits a report, run the validator before declaring root cause — a missing artifact on a failing job is `REPORT_EMIT_REGRESSION`, its own incident.
