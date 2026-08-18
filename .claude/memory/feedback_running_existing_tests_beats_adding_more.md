---
name: When asked to "add tests" or "improve coverage," first check whether existing tests actually run in CI
description: Adding a coverage gate or new tests is wasted effort if the existing test suite isn't being executed by CI — silent-CI repos accumulate red tests invisibly, and the simplest broken thing is "turn CI back on"
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
When a user asks to "implement coverage" / "improve coverage" / "expand tests to surface issues," the first investigation step — before measuring baseline coverage, before adding @vitest/coverage-v8, before wiring fail-under thresholds — is to verify that the existing test suite actually runs in CI on every push to main.

**Why:** qiyas 2026-05-19 cascade. User asked: "lets implement coverage to see if exoanding our tests help address issue." I started implementing #343 (pytest-cov + vitest threshold gates) and burned ~45min on a baseline measurement that hung at 26min under coverage instrumentation. Pivoted to running the full uninstrumented suite — found 12 red tests on master. Investigated CI to understand why these weren't caught: **GitHub Actions has had zero runs on qiyas since 2026-05-03 (16 days, ~10 commits since)**. The last 5 runs all failed at lint with 18 ruff errors and never reached `uv run pytest`. After that, GitHub Actions appears to have stopped firing entirely — workflow trigger is correct (`on: push: branches: [main]`), but no run records exist.

The user's hypothesis ("expanded tests will surface issues") was *correct* — but the issues already exist in tests that are written, just not run. Coverage gates layer signal on top of a CI that isn't producing any signal at all. The lowest-tier broken thing was "CI is silently disabled," not "we need more tests."

**How to apply:** when triggered by "add coverage," "add tests," "improve test gates," or "tighten CI":
1. Before measuring baseline or designing thresholds, run `gh run list --workflow=<ci.yml> --branch=main --limit=10 --json status,conclusion,createdAt,headSha`.
2. If the most recent run is >5 days stale OR all of the last 5 are red, stop the coverage work and surface the CI status to the owner first.
3. Run the full test suite locally to confirm what would have been caught by a working CI — file those findings as separate tracked tasks before re-engaging the coverage work.
4. Coverage gate work resumes only after CI is producing green signal.

**Anti-pattern this names:** "the user asked for X so I'll implement X" — without checking whether X depends on infrastructure that's secretly broken. The coverage gate would have shipped, been correct in isolation, and added zero signal because CI wasn't running it. Per tenet 20 (fix the simplest broken thing first), CI-broken is lower-tier than coverage-missing — CI is the substrate that makes coverage gates load-bearing at all.

**Companion to tenet 17 (prove primitive before composing) and tenet 20 (simplest broken first):** the "primitive" for a test gate is "tests are running"; without that, every higher-tier gate is decoration. The "simplest broken thing" for a 12-red-tests-on-master situation is the gate that lets red tests accumulate, not the next gate one tier up.

*Failure mode this prevents:* the 2026-05-19 session where I burned 45min on baseline coverage measurement, then another 22min on full suite measurement, before realizing the meta-question (does CI run any of this?) was answerable in 30 seconds with one `gh run list` call.
