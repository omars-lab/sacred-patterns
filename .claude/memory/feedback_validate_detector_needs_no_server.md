---
name: validate-detector-needs-no-server
description: qiyas validate-detector starts an inline feedback server by default and hangs after compute; always pass --no-server for non-interactive / loop / CI runs
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When running `qiyas validate-detector` non-interactively (autonomous loop, CI, any backgrounded local run), always pass `--no-server`. By default the CLI starts an inline localhost feedback server bound to the process lifetime, so the process does NOT exit after the detector pass finishes — it blocks on the server until Ctrl-C. A backgrounded run looks like a 20+ minute "hang" (process pinned at ~99% CPU then idle on the server) when the compute actually finished much earlier.

**Why:** 2026-05-28, validating the #299 split-assignment edit via the conda `workspace` env (Docker was out of host disk — GHA-free fallback per [[feedback_never_block_on_gha]]). The first invocation omitted `--no-server`; the process ran ~25 min CPU with a 0-byte buffered output (piped through `tail`), looking wedged. Root cause was the default feedback server, not slow compute. The `--help` text says so explicitly: "By default also starts an inline localhost feedback server bound to this process's lifetime — Ctrl-C stops both. Pass `--no-server` to skip."

**How to apply:**
- Non-interactive ratchet run: `qiyas validate-detector --corpus <dir> --no-server --report /tmp/report.json` — `--report` writes JSON to a file you can Read regardless of stdout buffering (don't rely on stdout through a `tail` pipe; it buffers and SIGTERM loses it).
- Only omit `--no-server` when you actually want the interactive PM/engineer feedback dashboard in a browser.
- The validator walks the `renders/` tree directly (`discover_constructions`), so it scores every `pattern.gt.json` under the corpus dir regardless of split — see [[feedback_qiyas_baseline_emit_vtx0_catchall_drift]] for the related index-vs-tree-walk hygiene issue (qiyas#656).

**Companion to:** [[feedback_never_block_on_gha]] (conda env is the GHA-free local path when Docker is unavailable), [[reference_qiyas_calibration_log]].
