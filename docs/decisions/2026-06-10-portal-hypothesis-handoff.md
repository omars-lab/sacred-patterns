---
# --- human-readable (kept, never machine-parsed) ---
status: ACCEPTED 2026-06-10 — Option A (deterministic seed + agent judgment, qiyas-owned review-verdict.json)
discovered: 2026-06-07 (named as the open follow-up in the loop-terminal-condition doc §7)
decided: 2026-06-10
owner: omareid
# --- machine-read structured keys (the contract) ---
status_token: ACCEPTED
picked_option: A
tag: portal-hypothesis-handoff
supersedes: []
superseded_by: []
related:
  - decision: docs/decisions/2026-06-07-loop-terminal-condition.md
  - skill: .claude/skills/iterate-construction-hypothesis/SKILL.md
  - plan: bikar .claude/plans/vectorized-squishing-pearl.md (the implementing plan, approved 2026-06-09)
---

# Portal annotations → hypothesis.md handoff — the review-verdict.json contract

When the art expert marks differences in the qiyas review portal, those marks
were saved as machine-readable `annotations.json` — and then went nowhere. A
human read the free-text `visual-verdict.md`, inferred the gap, and hand-wrote
the next iteration's `hypothesis.md`. Separately, the ACCEPTED loop-terminal
decision (2026-06-07, Option C) requires a machine-checkable
`portal_verdict_recorded(iter)` conjunct that did not exist. This note records
the shipped contract that does both jobs.

## 0. Premise check

**Premise:** no machine path existed from portal annotations to the next
hypothesis, and the loop's portal conjunct had no artifact to read.
**Verified against:** qiyas tree at fde78e3 (no verdict emitter, no
`review-path` command) and `tools/auto-iterate.py` at 412ed99 (converged on
metric alone). **LEDGER lookup:** no doc on this tag; the
loop-terminal-condition doc names this as its §7 follow-up, not a decision —
this note implements that follow-up, it does not re-decide Option C.

## The decision (Option A — deterministic seed + agent judgment)

**One bridge artifact, owned by qiyas:** `qiyas review-replay <annotations>
--emit hypothesis --output-dir iterations/N/` writes
`iterations/N/review-verdict.json` (schema v1, typed pydantic models in
`qiyas/src/qiyas/review/verdict.py`). It echoes the annotations'
`image_path` + `image_sha256`, counts right/wrong/unsure, sets
`verdict_recorded` / `review_passed`, and ranks gaps (structure before
pixels) with a deterministic `hypothesis_seed`.

**The binding predicate** (implemented in `tools/portal_verdict.py`):

```
portal_verdict_recorded(N) :=
    iterations/N/review-verdict.json exists
AND verdict.image_sha256 == sha256(iterations/N/render.svg)   # stale verdicts self-invalidate
AND verdict.verdict_recorded
```

**The honesty split:** the machine drafts only what is a pure function of
`annotations.json` + `pixel-diff.json` (gap ranking, drafted `gap_targeted`,
`predicted_lift` seed, evidence list). `construction_hypothesis`, `bkr_change`,
`predicted_cost`, and the Expected-visual prose are agent/human-only, emitted
as literal `TODO(judgment)` markers by `tools/seed-hypothesis.py` — a seed
with TODO markers is never a valid `hypothesis.md` (Tenet 24: a templated
expectation is a fudged one).

**Loop wiring:** `tools/auto-iterate.py` `terminal_state()` now returns
`converged | awaiting-portal-review (exit 4) | handback-stagnation |
handback-budget | not-terminal`; converged additionally requires
`portal_verdict_recorded AND review_passed`. A recorded-but-failing verdict is
not-terminal with a ready-made gap. No iteration number enters qiyas; no qiyas
slug is computed here — `qiyas review-path IMAGE` is the only seam.

## Options considered

- **A (picked): deterministic seed + agent judgment.** Machine drafts evidence;
  agent authors judgment. Shipped.
- **B (rejected): full auto-authoring of hypothesis.md.** Violates Tenet 24
  (Expected visual must be authored before viewing) and invites
  rubber-stamping the routing decision the skill exists to force.
- **C (rejected): keep the manual handoff, add only the verdict marker.**
  Satisfies the loop conjunct but leaves the annotation evidence unread —
  the gap this cascade exists to close.

## Witness (2026-06-10, medallion-10 iter-34)

The end-to-end run that validates the contract — and caught one real bug:
qiyas's default annotations-root was cwd-relative, so `review-path` invoked
from this repo missed sessions recorded from the qiyas repo (fixed
repo-anchored in qiyas 07e8221, with the witness as a regression test).
After the fix: `portal-handoff.py <session> 34` landed a sha-bound
`review-verdict.json` (right=0 wrong=2), and `seed-hypothesis.py` produced
`iterations/35/hypothesis-seed.md` whose evidence carries the reviewer's
"white bands far too fine — dense mesh instead of bold straps" — agreeing
with the hand-written `visual-verdict.md` finding it replaces.

## What would change this

- If renders become byte-unstable across re-runs (Tenet 8 violation), the
  sha binding false-negatives; degrade to location-binding with a logged
  warning. Verified stable on medallion-10 (two fresh renders byte-identical).
- If the seed's deterministic (rank, id) tie-break repeatedly picks an
  un-noted annotation over a noted sibling of the same rank, add note-presence
  as a secondary sort key in the qiyas emitter (schema-compatible change).
