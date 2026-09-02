---
name: Validate workflow YAML at commit time — silent workflow_run failures cost weeks
description: GitHub Actions workflow_run jobs that fail YAML validation produce zero job runs and zero notifications; add `python3 -c "import yaml; yaml.safe_load(...)"` as a wholesale pre-commit gate on every `.github/workflows/*.yml` file
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
GitHub Actions workflows with YAML parse errors **fail silently** under the `workflow_run` trigger — no job appears in the Actions tab, no email, no PR check. The only way to discover the failure is to (a) notice the downstream side-effect never happened, or (b) run the workflow's parent and inspect the "Workflows" → "All workflows" panel for the red error marker on the workflow itself.

**Why:** Owner discovered bikar's bump-peer-deps.yml had been broken since 68026ff (2026-04-22) — 4 weeks of bikar-core publishes that should have auto-PRed to coffee-house-design-kit produced zero PRs. Root cause: a `gh pr create --body "$(cat <<'BODY' ... BODY)"` heredoc body was at column 1, escaping the YAML `run: |` block scalar (indent 10). YAML parser saw `**What changed:**` as a new top-level key → `ScannerError at line 60`. The workflow never ran, so the manual `bikar-core` → `coffee-house-design-kit` PR was forgotten every release cycle.

**The witness that found it:**
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/bump-peer-deps.yml'))"
# ScannerError: while scanning a simple key in ".github/workflows/bump-peer-deps.yml",
# line 60, column 1, could not find expected ':' in ... line 62, column 1
```

**How to apply:**
- For any repo with GitHub Actions workflows, add a wholesale pre-commit gate that runs `python3 -c "import yaml; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml')]"` (or `actionlint` if installed — stricter, also catches schema errors). Cost: <50ms wholesale on the entire workflows dir.
- Tenet 18 codification: when fixing a broken workflow, the witness (`yaml.safe_load → ScannerError`) becomes the regression — encode it as a pre-commit check that fires on *every* commit touching `.github/workflows/`.
- Common YAML+shell tangle this prevents: heredoc bodies inside `run: |` block scalars. If the heredoc body indents to column 1 (the natural shell habit), it escapes the block scalar and the YAML parser sees the heredoc content as top-level keys. **Cleaner pattern:** `printf '%s\n' 'line' > $(mktemp)` then `--body-file "$BODY_FILE"` — no multi-line shell-string-inside-yaml-block-scalar.
- Other common heredoc-inside-yaml pitfalls: `<<'EOF'` (single-quoted) suppresses `$VAR` expansion silently; `<<EOF` (unquoted) expands but also expands backticks → command substitution where you didn't want it. The printf+tempfile pattern sidesteps both.

**The general principle:** any CI/workflow infrastructure whose failure mode is *silent* (no notification, no PR check, no email) demands a local validation gate. Loud failures (red CI badge, failed PR check) self-correct because the next push surfaces them. Silent failures rot for weeks. Workflow YAML parse errors are the canonical silent failure for `workflow_run`-triggered jobs.

**Reference commits:**
- bikar 4fc442b — the fix (printf+--body-file pattern)
- bikar 68026ff — the original broken commit (heredoc at column 1, 2026-04-22)
- qiyas 2e67c7a — sibling lesson, wholesale ruff in pre-commit (feedback_mirror_ci_locally.md)

**Companion memory:** `feedback_mirror_ci_locally.md` covers the "wholesale vs staged scope" axis for *running* CI checks locally. This memory covers the orthogonal axis: making sure the CI check *runs at all* (i.e., the YAML parses).
