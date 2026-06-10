---
title: "Retrospective — <PROBLEM THEME>"
date: <YYYY-MM-DD>
repos: [<repos>]
window: <START>..<END>
sources:
  transcripts: [<main jsonl paths>]
  decision_docs: <N>
  memory_files: <N>
  commits_scanned: <N>
  subagent_bodies_analyzed: <true|false>
generated_by: retrospect-hard-problem skill
---

<!--
HOW TO USE THIS TEMPLATE
- Every factual claim carries a tier tag: [A] durable-confirmed, [B]
  transcript-corroborated, [C] transcript-only. [C] lives ONLY in Appendix A.
- [A] claims MUST cite a real path/sha. No orphan cites.
- §4 (Repeated mistakes) is the point of the whole exercise — write it richest.
- Write §0 last.
-->

# 0. Executive summary

<3–5 sentences: the current approach in one line; the single biggest recurring
mistake; the top recommendation.>

# 1. The fundamental approach (what we are actually doing)

- **Pipeline as built:** <one paragraph — the stages, entry points, the two
  regimes (e.g. I1 SVG-direct shipped vs I2 photo cascade deferred).> [A: cite]
- **Why this shape:** <the tenet lineage that produced it — e.g. DSL-as-source-of-truth.> [A: cite]
- **Where it structurally caps out:** <the ceiling(s) — what this approach
  cannot do without a change of kind.> [tier: cite]

# 2. Tried and worked (keep doing)

| Approach | Evidence (tier + cite) | Why it worked | Now load-bearing? |
|----------|------------------------|---------------|-------------------|
| | | | |

# 3. Tried and failed / dead ends (stop doing)

| Approach | Failure mode | Evidence (tier + cite) | Superseded by |
|----------|--------------|------------------------|---------------|
| | | | |

# 4. Repeated mistakes  ← MOST VALUABLE

For each recurring mistake: how often, over what time-spread (NOT raw count —
spread is the signal), which tenet it violates, the durable-evidence chain
(decision-doc SUPERSEDED/REOPENED sequence where one exists), whether it is
already codified in a memory file, and why it kept recurring.

| Mistake | Times / date-spread | Tenet violated | Durable evidence chain | Codified? | Why it recurred |
|---------|---------------------|----------------|------------------------|-----------|-----------------|
| | | | | ✓ / ✗ | |

> The `✗ NEVER codified` rows are the highest-value inputs to the
> recommendations doc.

# 5. Not yet tried (open alternatives)

| Alternative | Feasibility | Governing tenet/skill | Source (tier + cite) |
|-------------|-------------|-----------------------|----------------------|
| | | | |

# 6. Recommendations (→ recommendations.md)

Ordered by value. Each: action · rationale · evidence tier · which tenet/skill
it touches.

1. ...

---

## Appendix A — Confidence ledger (Tier-C quarantine)

Transcript-only, unverified findings. Listed so they are not lost, but explicitly
NOT promoted to facts or recommendations.

- [C] ...

## Appendix B — Source manifest & noise budget

- Transcripts parsed: <paths + sizes + line counts>
- Lines kept vs discarded by type: <from extract_stats.json>
- Map windows: <count + date ranges>
- Decision docs / memory files / commits indexed: <counts>
- Subagent bodies analyzed: <yes/no — if no, headers-only were enumerated>
