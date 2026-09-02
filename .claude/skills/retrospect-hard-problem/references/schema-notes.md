# JSONL transcript schema notes (verified 2026-06-06)

The facts that shaped every script in this skill. Verified empirically against
the qiyas (64 MB) and sacred-patterns (900 MB) sessions, not from docs.

## Scale (why we never read raw transcripts)

| Session | Size | Span | Lines |
|---------|------|------|-------|
| sacred-patterns `ad36e137…` | ~900 MB | 2026-04-30 → 2026-06-01 | ~145k |
| qiyas `cb7c407a…` | ~64 MB | 2026-04-28 → 2026-05-12 | ~17k kept |
| bikar (worktree project dir) | ~8 MB | — | — |

Streaming the 900 MB file: **~4 s, ~60 MB peak RSS.** A naive `json.load(file)`
or `jq -s` would try to hold ~900 MB+ parsed in memory → OOM. **No-slurp is the
load-bearing rule.** `lib_jsonl.iter_events` line-streams and caps any single
line at `MAX_LINE_BYTES` (an inlined tool_result can be multiple MB).

## Line schema

Each line is one JSON object with a `type`. Observed types (varies by CLI
version — e.g. both `ai-title` and `custom-title` appear, and a bare `mode`):

| type | keep? | why |
|------|-------|-----|
| `user` | **yes** | human prompts (string content) + tool_result turns (list content) |
| `assistant` | **yes** | model turns: `text` blocks + `tool_use` blocks |
| `agent-name` / `slug` | yes | per-prompt topic label |
| `permission-mode`, `file-history-snapshot`, `attachment`, `queue-operation`, `last-prompt`, `ai-title`, `custom-title`, `system`, `mode` | **discard** | no analytic signal; ~40% of lines |

Relevant fields: `type`, `message.content` (str OR list of blocks),
`timestamp` (ISO), `gitBranch`, `isSidechain`, `toolUseResult`.

## The high-value signals (and their traps)

- **Human corrections** = `type:user`, `isSidechain:false`, `message.content`
  is a **string**, not a compaction summary. This is the gold "what was wrong"
  stream. Trap: many are trivial ("continue") — substance is the minority;
  weight accordingly.
- **Compaction summaries** = user string content starting *"This session is
  being continued from a previous conversation…"*. Dense distilled narrative.
  **Trap: ~2M tokens of them, and hash-dedup only catches verbatim repeats** —
  consecutive summaries are ~90% near-duplicate (each extends the prior). So
  packets carry only the SINGLE latest summary per window, truncated. And they
  are *Claude's own prior summarization* → Tier-B ceiling, never Tier-A alone.
- **Subagents are NOT inline.** Every top-level line has `isSidechain:false`.
  Subagent transcripts live in `<session-uuid>/subagents/*.jsonl`; large tool
  outputs externalize to `<session-uuid>/tool-results/*.txt`. So subagent
  analysis is a separate opt-in pass; headers are always cheap to index.

## Durable ground truth (the triangulation backbone)

- **Decision docs** `docs/decisions/*.md`: frontmatter `status: VERDICT DATE —
  rationale`. Verdicts: ACCEPTED / SUPERSEDED / REJECTED / REOPENED / PROPOSED /
  PENDING. The inline `— rationale` after a SUPERSEDED/REOPENED verdict often
  *names the mistake* (e.g. "premise was a stale fixture, not a metric"). A
  `related:` block carries task (`qiyas#NNN`) and `commit:` refs. Counts at
  index time: qiyas 40, bikar 18, sacred-patterns 3.
- **Memory files** `memory/feedback_*.md` / `project_*.md` + `MEMORY.md`:
  already-codified lessons. sacred-patterns' project-memory dir has ~87 — a
  recurring mistake that has NO memory file is the strongest recommendation.
- **Git log** `--since=<window>` filtered to theme-or-`revert/fix` subjects:
  mechanical evidence of failed approaches (a revert/replace pair).
- **Living routing docs**: `qiyas/.claude/plans/post-i1-task-routing.md`,
  `sacred-patterns/docs/iteration-status.md` — small enough to pass whole.

## Path encoding

A repo working dir maps to its project dir by `s#/#-#g` (every `/` → `-`).
Worktrees get a `--claude-worktrees-…` suffix dir (bikar's real work lives
there; the bare `-bikar` project dir is memory-only). `discover_sources.sh`
resolves all of this.
