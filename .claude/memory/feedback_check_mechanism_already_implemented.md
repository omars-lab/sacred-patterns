---
name: Verify proposed mechanism doesn't already exist before estimating rework
description: Before authorizing or estimating a multi-day architectural option, read the relevant module to confirm its proposed mechanism isn't already in place — the cost of the read is bounded; the cost of an option built on a false premise is the entire estimate
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
When a decision doc proposes a multi-day fix whose mechanism is "switch to algorithm X" or "add stage Y to the pipeline," the first step before estimating cost or authorizing is to read the relevant module and check whether X / Y is already implemented under another name.

**Why:** bikar#424 Phase 1h (2026-05-19) — owner authorized Option G ("CGAL-style arc pre-subdivision in buildIntersectionGraph, 3-5 days") to fix multi-circle pass-through bug at N ∈ {4, 8, 12, 16}. Investigation found `splitAndAddArc` already emits per-arc-piece edges via `emitConsecutiveEdges(allPoints, ...)` — the proposed mechanism was in place since the kernel's first commit. The N=4 origin already has 8 outgoing half-edges (4 circles × 2 directions), confirmed by `/tmp/probe-G-arc-split.mjs`. The actual bug is in the downstream linkage layer, not the absence of subdivision. The 3-5 day estimate would have been spent rebuilding a mechanism that exists, surfacing the same linkage-layer bug at the end.

**How to apply:** when a decision doc names an algorithm-class fix:
1. Before estimating cost, grep the target module for the algorithm's signature operations (split, subdivide, sweep, intersect).
2. If they exist, the option is falsified at premise — write a Phase-1h-style "mechanism already implemented" section in the decision doc and pivot to a different option.
3. Probe directly (small script asserting the post-condition the mechanism would create) before assuming the mechanism is absent.
4. Don't reach for big architectural options when small probes haven't run. Read first.

**Anti-pattern this names:** estimating "this is a 1-week CGAL rework" from the cascade-narrative alone, without 30 minutes of code-read to verify the mechanism doesn't exist. The narrative-driven estimate is unfalsifiable until implementation begins; the read-driven check terminates in minutes.

**Companion to feedback_canonical_algo_web_search.md** — that memory says "find the reference implementation when stuck"; this one says "before adopting the reference implementation's mechanism, verify your codebase doesn't already have it."
