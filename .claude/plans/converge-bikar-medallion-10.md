# Drive bikar-medallion-10 to convergence

## Context

Why this is now the top priority: every roadmap item beyond here (V2.B optimizer #75, V2.E auto-capture #77, V2.F escalate-divergence #78) is *gated* on calibration data and a converged session. We don't have either yet. Past iteration sessions stalled at iter 13 (bikar-medallion-10) and iter 92 (session-1) — both are real un-converged work, not roadmap noise.

bikar-medallion-10 is the cleaner restart: 13 iters in, modern qiyas path (v0.1.1 with real warnings), top warning is now `symmetry-mismatch` (δ 0.125) at composite=0.6644 — a much sharper signal than session-1's iter 92 (composite 0.7448 with 51 missing inner-star shapes spread across many shape types). Convergence here also unblocks #80 (parent task), produces the calibration data #75 needs, and exercises every part of the loop (interpret-pattern → orchestrator → bikar DSL edit → render → re-validate) under the tooling that actually exists today.

The user's explicit request: drive bikar-medallion-10 to convergence and, along the way, improve qiyas / bikar / our skills wherever the iteration loop surfaces gaps. The Phase 1.5 capture checklist that already ships in `tools/auto-iterate.py` is the mechanism for that meta-loop discipline — it routes per-iteration findings to the right repo (qiyas issues, bikar DSL gaps, BIKAR translation skill rows, sacred-patterns construction techniques).

Convergence target (per `docs/validation-overall.md` and the orchestrator): `overall.go_no_go = converged`. Concretely that means topology_complete=true, structural_score high (target ≥15/18 PASS), pixel_similarity respectable (≥0.85), and no `severity=error` warnings remaining.

## Grounding facts (verified today)

- **Iter 13 is the right base.** Composite 0.6644 with structural 1/18 and `top_warning=symmetry-mismatch` (δ 0.125, severity=warn). Counterfactual rationale: *"if recon's dominant fold + rotational orders matched ref"*. Iter 12 was composite 0.5835. The hand-off doc's "start from iter 12" guidance is stale (tenet 6 — the doc was written before iter-13's score was re-computed under v0.1.1; verified directly today).
- **Iter 13's pattern.bkr structure** (read directly): 4 layers — Layer 0 central rosette `connect every 4 on C1`, Layer 1 ten satellite rosettes `connect every 4 on @0.0..@0.9`, Layer 2 middle ring `connect every 3 on Cmid` (radius 80), Layer 3 inner middle ring `connect every 4 on Cmid2` (radius 50). Layers 0/1 are symmetric by construction; Layers 2/3 use `connect every K` which depends on intersection topology happening to land symmetrically.
- **The wedge-and-rotate technique** lives in `bikar/.claude/skills/pattern-construction/SKILL.md` ("The Wedge-and-Rotate Strategy"). Pattern: define one sector with `connect cycle [...]`, wrap in `rotate 10 around C0.mpt`. Forces 10-fold symmetry by construction.
- **The translation table** for warning→DSL edit is in `bikar/.claude/skills/iterate-pattern-from-qiyas-warnings/SKILL.md`. `n-fold-broken` (which the symmetry-mismatch warning maps to) prescribes refactoring non-rotational layers into `rotate N around C0.mpt` blocks. This is exactly the iter 14 edit.
- **The harness exists.** `tools/auto-iterate.py` ships Phase 1 (manual edit), Phase 1.5 (post-iter capture checklist), Phase 2 (autonomous edit via `claude --print`). It already enforces upfront BIKAR-DSL detection and capture-destination preflight. Each iteration auto-routes any "yes" answer in the capture checklist to `qiyas/docs/issues/`, `bikar/docs/dsl-gaps.md`, the BIKAR translation skill, or `sacred-patterns/.claude/skills/generate-drawing/learnings/construction-techniques.md`.

## The loop

Each iteration is a single pass through:

1. **Read directive.** Open `iterations/<N>/validation/validation.json` → `overall.warnings[0]`. The `id` + `context.counterfactual_rationale` are the next-action contract. Don't re-derive from screenshots.
2. **Predict.** Write `iterations/<N+1>/guidance.md` *before* rendering: planned edit, predicted Δcomposite (use `warnings[0].counterfactual_score_delta`), predicted A2 cv / A6 PASS count / pixel similarity. Calibration data point.
3. **Edit.** Apply the warning→edit translation from the BIKAR translation skill. Author `iterations/<N+1>/pattern.bkr`. One change per iteration (smallest chunk that addresses `warnings[0]`).
4. **Render.** Compile via the `compileDSL` snippet from the bikar skill (writes `render.svg`).
5. **Validate.** Run `tools/iteration-validate.sh --svg iterations/<N+1>/render.svg --reference input/reference.jpg --baseline input/baseline.json --out iterations/<N+1>/validation`.
6. **Reflect.** Write `iterations/<N+1>/evaluation.md` (vs reference) and `iterations/<N+1>/retrospective.md` (predicted vs actual Δ, what changed, why). G3 mandatory.
7. **Capture.** Run the Phase 1.5 checklist (5 yes/no questions). Any "yes" routes to the appropriate sibling-repo artifact. CaptureError on routing failure = fail loop loudly (tenet 3).
8. **Stop or continue.** If `overall.go_no_go == "converged"` → done. Otherwise → loop to step 1 with N+1 as the new base.

Hard gates apply (CLAUDE.md G1–G5): iter-N is frozen once it renders, architecture before pixels (structural < 18 → next iter must target structural), reference-grounded verification, evaluation/retrospective/guidance always written.

## Iter 14 — add inner-star rhombi

**Step zero (DONE 2026-05-03):** built `qiyas:dev` locally, re-validated iter 13 under the patched detector. Composite jumped from 0.6644 → **0.7632** (+0.099) just from removing the bogus symmetry-mismatch warning — no pattern.bkr changes.

**Iter-13 revalidation results (`/tmp/iter13-revalidate/validation.json`):**
- `overall.composite_score` = 0.7632, `go_no_go` = `iterate`
- `overall.warnings[0]`: `missing-shapes` δ=0.107 — *but the literal rationale is misleading*. Diff.json categorization: 53 missing = **37 circle + 15 lens + 1 girih_rhombus**. Circles and lenses are encoder-vocabulary artifacts from the photo-traced reference (round photo regions classified as circles/lenses), not constructions our SVG should render. Following the literal rationale ("add 53 missing shapes") would chase noise. **Tenet 6 trigger: inherited claim verified, found stale.**
- Real construction signals from `svg-audit.json → audits.A6.shapes`:
  - **`inner-star--rhombus-v4`: MISSING (0/10)** — zone has zero 4-vertex shapes, expected 10. Concrete, addressable.
  - `inner-star--star-v8`: MISSING (0/6) — zone has 2 8-vertex candidates but none survive distance filter
  - `inner-star--star-v20`: MISSING (0/1) — no 20-vertex shapes detected
  - `rosette--star-{v8,v10,v14,v20}`: MISSING — multi-star variants not constructed
  - `transition--band-segment-v2`: MISSING (0/3)
  - A5 bands BROKEN: 0 band_crossings (expected ~45 for n=10) — separate, larger gap
  - A2 UNEVEN cv=6.7% — sectors disagree by 35 mismatches; secondary signal

**Iter-14 directive: add 10 rhombi to the inner-star zone.** Smallest concrete chunk that ships value (tenet 1). Single A6 shape goes from MISSING → PASS. Doesn't touch the working layers (G2-safe).

**Mechanical edit:** Layer 0 currently does `connect every 4 on C1` to make the central {10/4} rosette. Adding `connect every 3 on C1` produces a {10/3} star polygon overlaid on the same circle — the {10/3} edges intersect the {10/4} edges at 10 rhombic intersection regions in the inner-star zone. After `voids detect`, those rhombi become 4-sided faces and get filled by the `fill void where sides == 4 color royal` rule already present.

**Predicted Δcomposite:** A6 PASS count 1 → 2 (~+0.05 structural) plus likely +0.02 from reduced "missing shapes" baseline noise once rhombi register. Total predicted ~+0.05 to +0.08.

**Stop conditions specific to this iter:**
- If render fails or rhombi don't appear: revert to `connect every 4` only, log as DSL gap, escalate.
- If composite drops > 0.02: revert, file as qiyas-side issue (rhombi added but scored as regression).

**Critical files (iter 14):**
- (read-only) `~/Dropbox/Data/sacred-patterns/bikar-medallion-10/iterations/13/pattern.bkr`
- (write) `~/Dropbox/Data/sacred-patterns/bikar-medallion-10/iterations/14/{pattern.bkr,render.svg,guidance.md,evaluation.md,retrospective.md,validation/}`
- (driver) `tools/auto-iterate.py ~/Dropbox/Data/sacred-patterns/bikar-medallion-10 --max-iters 1`

## Driving mode

Two viable modes; pick per session based on user availability:

- **Manual + harness Phase 1**: `python3 tools/auto-iterate.py <session-dir> --max-iters 1` — harness handles validation/capture/run-log; user (or this conversation) authors `pattern.bkr`. Best for the first 2-3 iters where the wedge-and-rotate translation needs human judgment to get right.
- **Autonomous Phase 2**: `python3 tools/auto-iterate.py <session-dir> --auto --max-iters 5 --auto-budget-usd 2` — Phase 2 shells `claude --print` to author each edit. Use once the translation pattern is well-established and the predicted-vs-actual deltas are tracking within tolerance.

Default to manual mode for iter 14. Switch to autonomous once two consecutive iterations land within ±50% of predicted.

## Meta-loop — improving qiyas / bikar / skills

The Phase 1.5 capture checklist (already shipped) routes findings:

| Finding type | Routes to | Resulting work |
|---|---|---|
| qiyas misclassified a shape / wrong detector / wrong score | `qiyas/docs/issues/YYYY-MM-DD-<slug>.md` | qiyas-side bug fix (file open issue, triage when it surfaces) |
| BIKAR DSL can't express a needed construction | `bikar/docs/dsl-gaps.md` (append) | bikar DSL feature (line-item, batched into a future bikar PR) |
| BIKAR translation table lacks a row for this warning id | `bikar/.claude/skills/iterate-pattern-from-qiyas-warnings/SKILL.md` (append "Pending row") | sacred-patterns + bikar coordination (formalize the row when 2+ instances appear) |
| Reusable construction technique discovered | `sacred-patterns/.claude/skills/generate-drawing/learnings/construction-techniques.md` (append) | learnings doc grows; future sessions consult it |

Predicted-vs-actual delta is auto-recorded in `auto-iterate-run.md` by the harness — no manual question. That row is the calibration data point for #75.

When a captured finding accumulates enough instances or severity to warrant work-in-flight, file a follow-up task. Examples that would warrant it:
- 3+ qiyas issues filed against the same detector → upstream fix becomes priority over the next iteration
- 2+ DSL gaps in the same area (e.g. wedge-and-rotate ergonomics) → bikar feature work
- A converged session is reached → trigger #77 (auto-capture on GO) gating

These are *emergent* tasks, not pre-planned ones. Don't pre-allocate them.

## Stop conditions

Convergence (success): `overall.go_no_go == "converged"` for two consecutive iterations.

Non-convergence (escalate, don't grind):
- 5 consecutive iterations with no positive Δcomposite → predicted-vs-actual model is broken; pause iteration, file qiyas issue under "warning ranking quality", consider whether baseline.json needs human refinement via interpret-pattern.
- A finding routed in step 7 turns out to be load-bearing for the next edit (e.g. discovered a DSL gap that blocks the `n-fold-broken` fix) → pause sacred-patterns iteration, drive the bikar-side fix to completion first, resume.
- 15 iterations without convergence → step back. Either the baseline.json needs human refinement (re-run interpret-pattern in the browser to correct shape expectations), or the construction approach is wrong at a higher level than per-warning edits can fix (start a fresh `iterations/<M>/` from the rosette skeleton, treating it as a sub-pivot rather than a continuation).

## Critical files

- (read-only base) `~/Dropbox/Data/sacred-patterns/bikar-medallion-10/iterations/13/pattern.bkr`
- (read-only contracts) `~/Dropbox/Data/sacred-patterns/bikar-medallion-10/iterations/13/validation/validation.json`, `~/Dropbox/Data/sacred-patterns/bikar-medallion-10/input/{reference.jpg, baseline.json}`
- (write per iter) `~/Dropbox/Data/sacred-patterns/bikar-medallion-10/iterations/<N+1>/{pattern.bkr, render.svg, guidance.md, evaluation.md, retrospective.md, validation/}`
- (driver) `tools/auto-iterate.py`, `tools/auto_iterate_capture.py`, `tools/iteration-validate.sh`
- (skills consulted) `bikar/.claude/skills/iterate-pattern-from-qiyas-warnings/SKILL.md`, `bikar/.claude/skills/pattern-construction/SKILL.md` (wedge-and-rotate), `.claude/skills/learn-new-pattern/iteration-guide.md`
- (capture destinations, no-op until "yes" answers route there) `qiyas/docs/issues/`, `bikar/docs/dsl-gaps.md`, `bikar/.claude/skills/iterate-pattern-from-qiyas-warnings/SKILL.md`, `.claude/skills/generate-drawing/learnings/construction-techniques.md`

## Verification — end of each iteration

1. `iterations/<N+1>/render.svg` exists and renders visually (no JS errors when loaded in browser if relevant).
2. `iterations/<N+1>/validation/validation.json` exists, well-formed; `overall.composite_score`, `overall.warnings[]`, `overall.go_no_go` all populated (no `tools.qiyas_score.available=false`).
3. `iterations/<N+1>/{evaluation,retrospective,guidance}.md` all written.
4. `auto-iterate-run.md` row added with predicted vs actual Δcomposite.
5. Phase 1.5 capture checklist run; any routed artifacts present and valid.

End of session (when convergence reached or stop-condition triggered): summary in `tools-journal.md` with iteration count, final composite, the path of warnings consumed (one line per iter), and any captured artifacts cross-linked.

## Out of scope

- Driving session-1 to convergence (separate session; resume after bikar-medallion-10 stops, with calibration data from this run informing the approach).
- Pushing qiyas v0.1.1 to ghcr (#100 — cosmetic until someone else needs the image).
- V2.* roadmap items (#74, #75, #76, #77, #78) — explicitly gated on this run producing calibration data and/or a converged session. Don't pre-build.
- Auto-iterate Phase 3 (further harness work) — Phase 1+1.5+2 already cover this run's needs; if a real gap surfaces during driving, capture it via the meta-loop and address it then.
