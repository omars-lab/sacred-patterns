# Phase 1.B corpus execution plan

## Context

- Owner approved Option C (qiyas#161 resolution, `1f125c2`).
- Owner approved the architectural seam (`bikar-as-training-data-generator.md`, `7355530`).
- Owner gave "go" 2026-05-05.

This doc is the execution plan for actually building Phase 1.B. It
turns the five authoring rules into a sequence of concrete PRs across
three repos (bikar, qiyas, sacred-patterns).

## Inventory — what already exists

Surveyed bikar `patterns/` 2026-05-05:

**Already authored as `.bkr`:**
- `patterns/Stars/Star-{7,10,14,16}.bkr`
- `patterns/Star-8.bkr`, `patterns/Hexagram.bkr`
- `patterns/Rosettes/Rosette-{10,10-Ring,10-Tiled,12,12r}.bkr`
- `patterns/Rosette-12.bkr`
- `patterns/Weave/Weave-{6,8,12}.bkr`
- `patterns/Tiled Patterns/Moroccan-12.bkr`, `Star-8-Tiled.bkr`
- `patterns/Sq-Oct.bkr`

**Phase 1.A corpus:** `Star-7`, `Star-10`, medallion10-iter14 — all done.

**What Phase 1.B needs that doesn't exist yet:**
1. `medallion-6` — n-fold scaling check (lower N).
2. `medallion-12` — n-fold scaling check (higher N).
3. Girih tiling — translation-tile arrangement.
4. Mirror-only-symmetry pattern — reflection-only critical case.
5. Scaled-concentric stress case — three concentric rosettes.

The Star-N and Rosette-N families *might* serve some of these slots
without new authoring — needs verification (are existing Star-14 /
Rosette-12r close enough to "medallion-12" for the regression test, or
do we need a true medallion-12 with satellites + interlace?).

## In-flight bikar work — coordination

Bikar working tree at 2026-05-05 has uncommitted changes (parser.ts,
tokens.ts, strapwork.ts, render/index.ts, ~52 lines) implementing the
**symmetry-preserving strapwork crossing modes** (qiyas#108 PR2,
qiyas#113-#114 — `over` and `under` keywords joining `alternating`).

Inspection shows this is **backward-compatible**: existing `.bkr` files
that use `crossing alternating` (or omit it) continue to parse and
render identically. The change only *adds* new tokens.

**Coordination decision:** Phase 1.B authoring **does not block on
landing the in-flight strapwork work**. New `.bkr` templates for
medallion-6, -12, etc. can be authored against the current working tree
because they don't use `over` / `under`. If we author against committed
HEAD instead, no behavior changes.

**However:** the *gt-emitter schema extension* (Rule 2 — per-shape
`polygon_outline` in render-pixel coordinates) IS a bikar-side change
and should land **after** the in-flight strapwork work commits cleanly,
to keep diffs attributable.

## Execution sequence

Five PRs in three repos, sequenced for minimal coordination cost.

### PR 1 (bikar, can start now) — Phase 1.B `.bkr` templates

Author the missing five constructions as parametric `.bkr` files where
possible. Each renders cleanly via `bun render`.

**Deliverables:**
- `patterns/medallion/medallion-6.bkr` (parametric on N where bikar DSL
  supports it; otherwise concrete).
- `patterns/medallion/medallion-12.bkr`.
- `patterns/girih/girih-5tile.bkr` (decagon + bowtie + hexagon +
  pentagon + thin-rhombus).
- `patterns/mirror-only/mirror-strap.bkr` (single horizontal axis
  reflection, no rotation).
- `patterns/concentric/concentric-3level.bkr`.

**Validation per file:**
1. `bun run render <pattern>.bkr <pattern>.png --width 1024 --height 1024`
   produces a 1024×1024 PNG without errors.
2. Visual eyeball — does it look like the construction it claims to be?
3. `pattern.gt.json` emitted alongside has at least one shape per
   visible region (no empty truth artifacts).

**Commits:** one per construction (5 commits), so any later regression
points at a single file.

**Out of scope for PR 1:** the new schema extension (PR 3). PR 1 ships
with whatever `pattern.gt.json` schema bikar emits today — adding
`polygon_outline` is a separate concern.

### PR 2 (qiyas, can start now) — `corpus.json` index + driver

The index format is the API. Authoring it before the schema extension
forces clean separation between "list of constructions" and "what each
construction's truth contains."

**Deliverables:**
- `qiyas/calibration/phase-1b-corpus/corpus.json` listing the 5
  Phase 1.B constructions + 3 Phase 1.A constructions, each with:
  - `id` (e.g., `medallion-6-default`)
  - `bkr_path` (path to source `.bkr` in bikar repo)
  - `render_path` (path to PNG output)
  - `gt_path` (path to `pattern.gt.json`)
  - `parameters` (rendering parameters: canvas, AA, seed if any)
  - `split` (`train` / `val` / `test`)
- `qiyas/calibration/phase-1b-corpus/splits.json` with explicit holdouts:
  - test: girih, mirror-only (out-of-distribution checks)
  - val: medallion-6, concentric-3level
  - train: medallion-12, plus all Phase 1.A
- `qiyas/calibration/phase-1b-corpus/regenerate.sh` — driver script
  that walks `corpus.json`, calls bikar render for each entry with
  fixed parameters, writes outputs to `renders/<id>/`. Idempotent.
- `qiyas/calibration/phase-1b-corpus/README.md` — consumer contract
  (one section per consumer: validate-detector regression today, B-AFF
  trainer hypothetical).

**Validation:** `regenerate.sh` runs to completion; emits 8 render
directories; `qiyas validate-detector --corpus calibration/phase-1b-corpus`
runs and produces a per-construction report (existing detector, expect
identity-fidelity below the eventual convergence bar — that's fine, the
gate is "report runs," not "detector passes").

**Commits:** one (this is a single coherent unit).

### PR 3 (bikar, after in-flight strapwork lands) — `polygon_outline` schema extension

Extends `pattern.gt.json` shapes with per-shape polygon outline in
render-pixel coordinates.

**Deliverables:**
- gt-emitter walks each shape's polygon, transforms vertices from
  bikar's intrinsic coordinate frame to render-pixel coordinates using
  the same canvas-size logic the renderer uses.
- Schema bump: `pattern.gt.json` schema_version 2 → 3.
- Migration: emitting both old fields (compatibility) plus new
  `polygon_outline_px` field for one bikar release; add deprecation
  comment on old fields.
- `pattern.gt.json` schema doc updated.

**Validation:**
- Existing tests on Phase 1.A patterns continue to pass.
- New unit test: render medallion-10-iter14 at 1024×1024 → walk each
  shape's `polygon_outline_px` → render outline as overlay → diff
  against the actual shape mask. Per-shape IoU ≥ 0.99.

**Commits:** one (schema + emitter + tests + doc together — a single
schema bump should be atomic).

### PR 4 (sacred-patterns, after PR 1 lands) — wire `corpus.json` consumption

Sacred-patterns side updates so the iteration loop can consume Phase 1.B
results.

**Deliverables:**
- `tools/iteration-validate.sh` learns a `--corpus <path>` flag that
  forwards to `qiyas validate-detector`.
- `validation.json` envelope grows a `corpus.* ` section when
  `--corpus` is provided, surfacing per-construction identity-fidelity
  rows.
- `docs/validation-overall.md` updated with the new section.

**Validation:** `iteration-validate.sh` against any Phase 1.A session
with `--corpus` works; `validation.json` is well-formed.

**Commits:** one.

### PR 5 (qiyas, after PRs 1-3 land) — re-run F1.v3 ARI cross-check on Phase 1.B

This is the *test* the cascade was originally trying to enable. With
the parametric corpus in place:

**Deliverables:**
- Run `derive_fused_partition_v2` on each Phase 1.B construction's
  `pattern.gt.json`.
- Compute ARI(A_fused_v3, B_truth) per construction.
- Expected outcome (per iter-5's algebraic-identity argument): ARI =
  1.000 on every construction *if and only if* bikar's gt-emitter is
  internally consistent.
- Any construction returning < 1.000 = a bikar gt-emitter bug.
- New file: `qiyas/calibration/i1/iter-6-phase-1b-ari.md` ship/escalate
  report.

**Validation:** ship if every Phase 1.B construction passes ARI ≥ 0.95;
otherwise escalate the construction(s) with the bug as bikar tickets.

**Commits:** one (ship report + cross-check script).

## Schedule (rough)

- PR 1 (5 .bkr files): days. Authorable now. Independent commits.
- PR 2 (corpus.json + driver): hours after PR 1 starts (can prototype
  index against existing files, then point at PR 1 outputs).
- PR 3 (schema extension): waits for in-flight strapwork to land. ~1–2
  days authoring + tests once unblocked.
- PR 4 (sacred-patterns wiring): hours. Mechanical.
- PR 5 (ARI cross-check): hours. The interesting part is reading the
  outcome — if any construction ARI < 1.000, we've found a bikar bug.

## Hard stops (per loop directive)

- **Spec divergence** during PR 1 (a construction can't be authored
  cleanly because the DSL is missing a primitive): STOP, file as a
  bikar issue.
- **Cross-construction validation failure** in PR 5 (any construction
  ARI < 0.95 on its own gt-emitter): STOP, escalate as a bikar bug.
  This is the Phase 1.B regression test catching exactly what it was
  designed to catch.
- **Two persistent test failures** in any PR: STOP, document.
- **Bikar in-flight work breaks** while authoring PR 1 against current
  working tree: STOP, ask owner whether to checkout HEAD or wait.

## What this plan does NOT do

- Build B-AFF. The corpus is the asset; the trainer is a future PR.
- Modify `iter-14` detector tuning. Phase 1.B exposes detector gaps via
  `validate-detector`; closing those gaps is per-construction follow-up
  work in #152.
- Touch the qiyas-medallion10 convergence loop (#85 / #123). Those run
  in parallel.

## Pointers

- Authoring rules: `.claude/plans/bikar-as-training-data-generator.md`
- Cascade plan: `.claude/plans/shape-identity-detection-cascade.md`
- #161 resolution: `qiyas/.claude/plans/i1-pass3-wiring-spec-divergence.md`
- iter-5 SHIP: `qiyas/calibration/i1/iter-5-bidirectional-ari-ship.md`
