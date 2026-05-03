# Sacred-patterns iteration practice — status as of 2026-05-02

Where each iteration session stands, what tool path it's on, and what the next mover should do. Read this first when you (or a future agent) sit down to drive convergence on any of these patterns.

## TL;DR

| Session | Where | Iters | Last status | Tool path | Next move |
|---|---|---|---|---|---|
| `session-1` | `~/Dropbox/Data/sacred-patterns/session-1/` | 92 | Stuck at structural 5/7, A2 UNEVEN cv 10% | **Legacy** (arch-audit.py, no baseline) | Bring onto modern path: emit baseline, run orchestrator on iter 92 SVG, drive iter 93 from `overall.warnings[0]`. Tracked as #98. |
| `session-8-fold` | `~/Dropbox/Data/sacred-patterns/session-8-fold/` | 0 | Pre-skill GeoGebra session, marked `completed` in session.json (confidence 0.6) | n/a — never used the iteration loop | Out of scope for the iteration loop. If you want to revisit 8-fold convergence, start a fresh session with the modern interpret-pattern → orchestrator path. |
| `bikar-medallion-10` | `~/Dropbox/Data/sacred-patterns/bikar-medallion-10/` | 13 | Paused at iter 13, structural 1/18, "stop adding rings, pivot to wedge-and-rotate" | **Modern** (qiyas svg-audit + baseline.json) — but `qiyas score` was unavailable through iter 13, so `overall.warnings` was empty and the agent had to manually diff per-shape. Fixed in commits c6225ff (qiyas) + ee31307 (sacred-patterns) on 2026-05-02. | Restart from iter 12 base with wedge-and-rotate construction (see "bikar-medallion-10 restart entry point" below). Tracked as #85. |

## Why each session is where it is

### session-1 — first pattern, pre-baseline era

Started before `interpret-pattern` skill existed. Ran 92 iterations on `arch-audit.py` (the original A1–A6 audit script that lived in sacred-patterns before the qiyas migration). Plateaued at structural 5/7 (regressed from 6/7 in earlier iterations). No `baseline.json` ever produced, so A6 baseline-shape validation never ran. The signals available to the agent at iter 92 were limited to topology + symmetry + a hand-rolled architectural rubric.

The fundamental issue: convergence stalled on geometry the legacy audit couldn't measure (per-shape vertex counts, zone-by-zone shape distribution). The same pattern on the modern path would have been driven by `qiyas svg-audit --baseline input/baseline.json`'s per-shape PASS/PARTIAL/MISSING verdicts — a much sharper signal.

**To resurrect:** see `#98`. The mechanical steps are:

1. `qiyas baseline emit ~/Dropbox/Data/sacred-patterns/session-1/input/reference.jpg --out ~/Dropbox/Data/sacred-patterns/session-1/input/baseline.json`
2. `tools/iteration-validate.sh --svg .../iterations/92/output.svg --reference .../input/reference.jpg --baseline .../input/baseline.json --out .../iterations/92/validation` (re-validates iter 92 with the modern stack)
3. Read `validation.json → overall.warnings[0]` and use it to draft iter 93 — this is the first true qiyas-warnings-driven iteration on session-1.

Don't try to recover the legacy `arch-audit.json` history. It used different scoring; comparing across the cutover is misleading.

### session-8-fold — never used the iteration loop

`session.json` says `pre-skill manual session. GeoGebra-only construction using compass-and-straightedge methods.` `iterations/` is empty. `input/` doesn't exist. It's marked `completed` with `confidence_score: 0.6`. There's nothing to resume — it's a parked GeoGebra-derived artifact, not a halted iteration session.

**If you want 8-fold convergence work:** start a fresh session under a new name with the standard flow: place reference image in `input/reference.jpg`, run `interpret-pattern` to produce `baseline.json`, then drive iterations through the orchestrator. Don't try to "continue" session-8-fold.

### bikar-medallion-10 — paused mid-pivot

The most recently active session, and the one with the cleanest path forward. 13 iterations into a 10-fold decagonal medallion. Iters 1–13 used:
- BIKAR DSL (`pattern.bkr` files; rendered to `render.svg` via the bikar tool)
- Modern orchestrator (`tools/iteration-validate.sh`) producing `validation.json`
- Modern `qiyas svg-audit` with `baseline.json` (produced by `qiyas baseline emit`, the catch-22 unblock from #81)

The **first three iters of this session** (11, 12, 13) revealed two issues:

1. **`overall.warnings = []`** because the published `ghcr.io/naqshcoffee/qiyas:v0.1.0` Docker image had a flat `qiyas score` command from before the score-group split. The orchestrator silently recorded `qiyas_score.available = false` and the agent had to manually diff `A6.shapes[]` between iterations to find improvements. Documented in `qiyas/docs/issues/2026-05-02-orchestrator-warnings-empty-when-score-unavailable.md`. **Fixed 2026-05-02:** v0.1.1 image rebuilt locally; `QIYAS_IMAGE` default bumped (sacred-patterns commit ee31307). Push to ghcr still pending PAT scope upgrade (#100), but local Docker resolves the local tag first so this doesn't block iteration.

2. **The "more rings → more shapes" hypothesis failed.** Iters 11→12→13 each added a construction ring (Cmid radius 65, then 80) hoping to fill zone shape deficits. Net-negative: A6 binary score stayed 1/18 across all three; A2 symmetry got *worse* (cv 0.0748 → 0.0878 → 0.067). Each new ring's intersections shifted classification of *existing* shapes faster than it added new correct ones. Iter 13's retrospective concluded: stop adding rings; pivot to wedge-and-rotate.

The pivot — replace `connect every K on <ring>` with explicit `connect cycle [...]` wrapped in `rotate 10 around C0.mpt` — forces exact 10-fold symmetry by construction (one wedge × 10 rotations) instead of relying on every ring's intersections happening to fall in the same per-sector positions. The bikar pattern-construction skill documents this technique (`bikar/.claude/skills/pattern-construction/SKILL.md` "The Wedge-and-Rotate Strategy").

#### bikar-medallion-10 restart entry point

When you're ready to drive iter 14:

1. **Base:** copy `iterations/12/pattern.bkr` to `iterations/14/pattern.bkr`. Iter 12 had the best A6 net delta (+3 vs iter 11) and only one important regression (rosette star-v6). Don't start from iter 13 — that ring-addition made things worse.
2. **Translate layer 2 only.** Layers 0 (central rosette on C1) and 1 (10 satellite rosettes on @0.0…@0.9) are already symmetric by construction. The breakage came from layer 2's `connect every 3 on Cmid`. Replace it with one `connect cycle [...]` describing the wedge for sector 0, wrapped in `rotate 10 around C0.mpt`. Per tenet "simplicity over complexity": one wedge first; verify the symmetry pillar improves before generalizing.
3. **Predict before running.** Write iter 14's prediction (expected A2 cv, A6 PASS count, pixel) into `guidance.md` *before* rendering. This is calibration data for qiyas#75 (V2.B global warning optimizer); see iter 12 retrospective's "Calibration data point" section for the format.
4. **Run the orchestrator** (now real warnings):
   ```
   tools/iteration-validate.sh \
     --svg iterations/14/render.svg \
     --reference input/reference.jpg \
     --baseline input/baseline.json \
     --out iterations/14/validation
   ```
   `overall.warnings[0]` is now populated (verified against the iter 11 fixture on 2026-05-02 — composite=1.0, top_warning landed in the array).
5. **Read `overall.warnings[0]`** and use its `counterfactual_rationale` to draft iter 15. The G1–G5 hard gates in `CLAUDE.md` apply.

#### What changed in the tooling between iter 13 and now

Anything you read in iter 11/12/13's retrospectives about empty `overall.warnings` or "tool friction: agent had to manually diff A6.shapes[]" is **stale**. The fixes from 2026-05-02:

- `ghcr.io/naqshcoffee/qiyas:v0.1.1` (local) ships `score` (run/replay/explain), `baseline` (emit), `fixtures` (capture/check/list) groups
- `iteration-validate.sh` defaults to v0.1.1 (sacred-patterns commit ee31307)
- When `qiyas score` is unavailable, the rollup adds a loud `blocking_issues` entry instead of silently zeroing `overall.warnings` (sacred-patterns commit d5c7c23, intentionally **no** synthesized fallback — see `docs/validation-overall.md` "No synthesized warnings fallback (intentional)")

## Cross-references

- `qiyas/docs/issues/2026-05-02-orchestrator-warnings-empty-when-score-unavailable.md` — the orchestrator-warnings-empty failure mode and its resolution
- `bikar/.claude/skills/pattern-construction/SKILL.md` "The Wedge-and-Rotate Strategy" — the construction technique iter 14 should adopt
- `bikar/.claude/skills/iterate-pattern-from-qiyas-warnings/SKILL.md` — the BIKAR-side iteration playbook (translation table from qiyas warning codes to DSL edits)
- `.claude/skills/learn-new-pattern/iteration-guide.md` — the general iteration loop steps; bikar sessions follow the bikar skill above instead
- `CLAUDE.md` "Engineering Tenets" — the review framing that applies to any iteration code
- `CLAUDE.md` "HARD GATES — Iteration Rules" — G1–G5 (immutability, architecture-before-pixels, mandatory deliverables, reference-grounded, skill-prefixed task naming)

## Open follow-ups visible from this status

- `#85` — bikar-medallion-10 wedge-and-rotate restart (now unblocked)
- `#98` — session-1 resurrection on modern path (now unblocked)
- `#100` — push qiyas v0.1.1 to ghcr (cosmetic for local users; matters for distribution)
- `#79` — qiyas score backfill against historical iterations missing validation/ subdirs
