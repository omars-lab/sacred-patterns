---
name: Pinned encoder baselines decay silently under typing-only refactors
description: When a fixture comparator is byte-strict against pinned baselines and the codebase is mid-refactor (mypy strict, Pydantic migration), each typing commit can silently mutate serialization (key order, int↔float coercion, dict→model field naming). Pair byte-strict baselines with a tolerance fallback OR run the comparator in PR CI, not just main.
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
**The rule:** A byte-strict pinned-baseline comparator (qiyas's
`_summarise_drift` distinguishing `shape count change` / `dominant_fold`
/ `type histogram` from `byte-level encoding mismatch (sub-shape field
changed)`) is only as durable as the upstream encoder's *byte
determinism*. Mid-refactor codebases — mypy strict-mode adoption,
Pydantic model migration, dict→TypedDict migration — produce typing-
only commits that incidentally mutate serialization in ways the
comparator catches as "regression" but that are actually neutral wrt
the encoder's *meaning*.

**Why:** qiyas#469 (2026-05-19) was the first instance:
`bikar-medallion-10-strapwork` shape count 555→554 between Apple Silicon
dev and x86_64 CI. The fix (c7c33cb) was to pin the fixture to x86_64
and rebaseline. Within 24h, qiyas#474 (2026-05-20) surfaced the same
fixture failing CI with `byte-level encoding mismatch (sub-shape field
changed)` — same arch (x86_64), same shape count (554), same type
histogram, but a sub-shape field changed. The 25 commits in between
were almost all qiyas#339 mypy-strict typing fixes; semantic suspicion
falls on `64a5e23 Coerce warnings dicts → Warning models`,
`ccf36fe Cast Any-typed reads to declared return types`, etc. — typing
commits that incidentally coerce `42` ↔ `42.0` or reorder dict keys.

**The failure mode this names:** the byte-strict comparator is rigorous
*and* fragile. Under stable code it's a tight gate; under refactor it
fires on noise.

**How to apply:**
- When a codebase enters a typing-refactor era (mypy --strict adoption,
  Pydantic migration, dict→TypedDict), **don't keep byte-strict
  pinned-baseline gates in main CI** — either:
    (a) loosen the comparator to ignore field changes that don't shift
        the count/type-histogram/dominant-fold (warn-not-fail), or
    (b) move the gate to PR CI only, so the rebaseline is the merge
        author's burden (not "fix CI on main after-the-fact"), or
    (c) run the comparator in two modes: strict on the merger's branch
        (catches intent drift), tolerant on main (catches only
        structural regressions).
- Pair every byte-strict baseline with at least one *meaning-level*
  invariant (a property test on `len(shapes) ≈ expected_within_tol`,
  `dominant_fold == 10`, `type histogram includes "lens"`) — those
  survive serialization noise; byte equality doesn't.
- When debugging a recurring "CI red on the same baseline, different
  symptom each time" pattern: the answer is rarely "fix this commit";
  the answer is "the comparator's contract is wrong for the current
  state of the codebase." Reach for the comparator first, not the
  bisect.

**Reference commits / tasks:**
- qiyas c7c33cb — Rebaseline to x86_64 + arch-skip escape hatch (closed
  qiyas#469)
- qiyas#474 — Reopened the same gate within 24h with byte-drift
- qiyas#471 — Pre-existing follow-on: re-measure all pinned baselines
  on Linux CI; #474 is its first concrete trigger

**Companion to `feedback_ci_platform_portability.md`:** that memory
covers arch-divergence (different CPU → different encoder output);
this memory covers refactor-decay (same arch → same encoder, but
typing commits drift sub-shape fields).
