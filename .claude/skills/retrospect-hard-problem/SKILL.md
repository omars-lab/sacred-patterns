---
name: retrospect-hard-problem
description: Run a cross-repo retrospective on a long-running hard problem (default the image→DSL / construction-inference problem across bikar, qiyas, sacred-patterns) by mining the session transcripts in ~/.claude/projects. Answers "what have we tried, what worked, what failed, where did we REPEAT the same mistake, what alternatives remain, what should change in our tenets/skills." Distills 100s of MB of jsonl programmatically (never reads raw transcripts into context), maps over date-windowed chunks with subagents, then triangulates every claim against the durable record (decision-doc status chains, memory files, git log, living routing docs) before it enters the report. USE THIS when the owner asks to analyze our transcripts to figure out what we've tried / where we keep making the same mistakes, or to re-run that analysis on a different hard problem. Parameterized by --repos, --window, --theme.
user_invocable: true
argument: "[--theme REGEX] [--repos a,b,c] [--window START..END] [--include-subagents]"
---

# retrospect-hard-problem

This skill turns the raw, multi-hundred-megabyte session transcripts under
`~/.claude/projects/` into a **cited retrospective** of a hard problem and a
**tenet/skill-improvement recommendation set** — so the team can see what it has
tried, what worked, what failed, and (most valuably) **where it repeated the
same mistake**, instead of rediscovering each lesson from scratch.

## The plain-English problem this solves

We have spent weeks across three repos on one inverse problem: **given an image
of a geometric pattern, recover the bikar DSL that produces it.** That history —
every approach tried, falsified, shipped, or abandoned — is buried in session
transcripts too large to read (sacred-patterns alone is a single ~900 MB,
month-long session). The lessons exist but are not consultable. We suspect we
keep repeating mistakes (tuning constants for one fixture, validating composites
before primitives, committing at options-level before empirical validation,
re-deriving facts the DSL already knew). This skill mines the transcripts to
surface that pattern and recommend what should change.

## Hard guards (non-negotiable — these are why the skill is trustworthy)

1. **Never read a raw `.jsonl` into your context.** They are 10–900 MB. Only the
   Stage-1/3 scripts touch them, line-streamed. You read the small distilled
   artifacts and chunk packets.
2. **Never slurp.** No `jq -s`, no `json.load(file)` on a transcript. The
   library `scripts/lib_jsonl.py` line-streams and caps monster lines; use it.
3. **Triangulate before asserting.** Every finding gets a corroboration tier
   (A/B/C, defined below). Tier-C (transcript-only) findings are quarantined to
   an appendix and NEVER become recommendations. This mirrors the repos' own
   "trust but verify inherited claims" and "verify before claiming done" tenets.
4. **Weight by date-spread, not hit count.** The 900 MB session dominates by
   line volume; a mistake seen once early + once late outranks ten hits in the
   last window. Recency/volume bias is the #1 failure mode of this analysis.
5. **No silent gaps.** The report's source manifest states exactly what was
   parsed, what was discarded, and whether subagent bodies were analyzed.
6. **Report + recommendations only.** This skill does NOT edit any `CLAUDE.md`
   or skill. Tenet/skill edits are a separate, owner-approved step.

## Parameters

Read from the invocation `argument` (all optional; defaults target the
image→DSL problem). The same skill retrospects a *different* hard problem by
swapping `--theme` and `--repos`.

| Flag | Default | Meaning |
|------|---------|---------|
| `--repos` | `bikar,qiyas,sacred-patterns` | repos to analyze together |
| `--window` | `2026-04-28..2026-06-01` | date range (clamps git log + map focus) |
| `--theme` | the geometric-construction regex (see `scripts/extract_signals.py` `DEFAULT_THEME`) | recall booster + map-prompt focus; NOT a filter — corrections/summaries are extracted theme-independently |
| `--include-subagents` | off | promote `subagents/*.jsonl` bodies into the map (cost gate; headers are always indexed regardless) |

## Procedure

All intermediate artifacts go under a scratch `artifacts/` dir (gitignored).
Scripts live in `scripts/` next to this file; run them from there.

### Stage 0 — Manifest (script, no model)
```
scripts/discover_sources.sh --out artifacts --repos <repos>
```
Resolves every transcript / decisions-dir / memory-dir / living-doc path
(handling the path-encoding and the bikar worktree project dir) into
`artifacts/manifest.json`. Confirm each repo resolved ≥1 transcript OR a
decisions dir; a repo with neither is a red flag, not silently dropped.

### Stage 1 — Extract signals (script, no model)
For each repo's main jsonl(s) in the manifest:
```
scripts/extract_signals.py --jsonl <main.jsonl> --out artifacts/<repo> \
    --theme <theme> --subagent-dir <subagents-dir>
```
Emits `corrections.jsonl` (the gold human-steering stream),
`compaction_summaries.jsonl` (hash-deduped distilled narratives — treat as
Tier-B at best, they're Claude's own prior summaries), `timeline.jsonl` (the
segment spine), `tool_errors.jsonl`, `theme_hits.jsonl`,
`subagent_index.jsonl` (headers only), and `extract_stats.json` (the noise
budget). **Verify row counts are non-zero and sane before proceeding.** On the
64 MB qiyas session this runs in ~0.3 s; on the 900 MB session ~4 s at ~60 MB
RSS — if it is slow or memory-hungry, something is slurping; stop and fix.

### Stage 2 — Ground-truth index (script, no model)
```
scripts/index_ground_truth.py --repo-root <root> --decisions-dir <dir> \
    --repo-memory <dir> --project-memory <dir> --out artifacts/<repo> \
    --living <doc> ... --since <window-start> --theme <theme>
```
Emits `ground_truth.json`: decision docs with parsed `status`
(ACCEPTED/SUPERSEDED/REJECTED/REOPENED/PROPOSED) + inline supersede/falsification
rationale + related task/commit refs; memory files with first paragraph; the
theme-or-revert-filtered git log; and the living routing docs verbatim. **The
SUPERSEDED/REOPENED chains are the engine of the repeated-mistakes section** —
they are inherently cross-time, so they re-thread what windowing splits.

### Stage 3 — Map over chunk packets (Workflow fan-out)
```
scripts/build_chunk_packets.py --in artifacts/<repo> --out artifacts/<repo>/packets
```
Packs the segment spine into ~5–15 date-windowed packets of ~65k tokens each
(curated extract — corrections + in-window theme_hits/tool_errors + segment
headers + the single latest compaction summary, truncated). Then fan out **one
subagent per packet** via the **Workflow tool** (independent, identical-shaped,
parallel; bounded concurrency + auto collection). Each subagent reads ONE packet
and returns the structured schema in `templates/map-output-schema.json`:
`{approaches_tried:[{what, outcome, evidence_ts}], mistakes:[{description,
tenet_violated, evidence_ts}], pivots, open_questions}`, citing timestamps and
not speculating beyond the packet. Write results to
`artifacts/<repo>/map/window_NN.json`. (If the Workflow tool is unavailable,
fall back to capped sequential `Agent` calls — packets are order-independent.)
If `--include-subagents`, build packets from `subagent_index.jsonl` bodies too.

### Stage 4 — Triangulate (you, in this context — judgment)
Merge all `window_*.json` into candidate findings. Reconcile each against
`ground_truth.json` and assign a **corroboration tier**:
- **Tier A — durable-confirmed:** matches a decision-doc status/rationale, a
  memory file, or a commit. Stated as fact, with the cite.
- **Tier B — transcript-corroborated:** appears in ≥2 independent windows (or a
  window + a compaction summary) but has no durable doc. Stated as "strongly
  evidenced."
- **Tier C — transcript-only:** single source, no durable echo. Quarantined to
  Appendix A; never a recommendation.
For the repeated-mistakes section, link findings sharing a problem/tenet across
windows, and anchor each chain to a decision-doc SUPERSEDED/REOPENED sequence
where one exists. Flag each recurring mistake `codified ✓` (a memory file
already names it) or `NEVER codified ✗` (no memory file) — **the ✗ rows are the
highest-value recommendations.** Write `artifacts/<repo>/reconciled_findings.json`.

### Stage 5 — Synthesize (you, in this context)
Fill `templates/retrospective.md` and `templates/recommendations.md` from the
reconciled findings, cross-repo. Write to
`sacred-patterns/docs/retrospectives/<today>-<theme-slug>-retrospective.md` and
`...-recommendations.md`. Verify every Tier-A claim cites a real
decision-doc path / commit sha (no orphan cites) and every Tier-C claim sits in
the appendix only. The recommendations doc proposes (as diffs-in-prose, not
applied): new/amended tenet, a new `memory/feedback_*.md` for each un-codified
recurring mistake, or a new/edited skill guard — each carrying a tier.

## Companion skills

- `present-options` / `handle-falsification` — the decision-doc lifecycle this
  retrospective mines; recommendations often feed back into these.
- `iterate-construction-hypothesis` / `iterate-detector-calibration` (qiyas) —
  the loops where the mined mistakes happen; recommendations may harden them.
- `escalate-qiyas-divergence` — where cross-repo workaround mistakes surface.

## References

- `references/schema-notes.md` — the verified JSONL event schema, the discard
  set, and the gotchas (no-slurp, summary near-dup explosion, subagents are
  external files) that shaped every script.
