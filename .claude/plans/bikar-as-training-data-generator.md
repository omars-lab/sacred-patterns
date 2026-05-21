# Bikar-as-training-data-generator — the seam between Phase 1.B and B-AFF

## Context

This plan captures an architectural insight surfaced during the qiyas#161
spec-divergence resolution (2026-05-05). Owner read the
analysis at `qiyas/.claude/plans/i1-pass3-wiring-spec-divergence.md` —
which recommended Option C (defer #161, advance Phase 1.B as a bikar
gt-emitter regression test) — and pointed out:

> "I imagine ... we should be able to auto create a training pipeline
> given we have bkr generate a whole bunch of different patterns — we
> know the ground truth / what should be detected ... we can then see if
> things are being detected right in the right area, no?"

That observation is load-bearing. It transforms the cascade from
**linear** (C now → B-AFF eventually, hoping the corpus is enough) to
**explicitly seamed** (C now produces the asset B-AFF needs, on purpose,
so that switching from C to B-AFF later is just "press the button").

This doc names the seam, defines the asset C produces for B-AFF, and
specifies the discipline that keeps the seam clean.

## Pointers

- **Recommendation source:** `qiyas/.claude/plans/i1-pass3-wiring-spec-divergence.md` (commits `5d0f13a`, `ceb6187`, `d027ef8`, `1f125c2`)
- **Cascade plan being amended:** `.claude/plans/shape-identity-detection-cascade.md` (Phase 1.B section)
- **Iter-5 SHIP:** `qiyas/calibration/i1/iter-5-bidirectional-ari-ship.md` (F1.v3 → ARI=1.000 on Phase 1.A by construction)
- **B-AFF reference:** Asymmetric Feature Fusion, CVPR 2023 (arxiv 2403.00671) — gallery side has rich features, query side has lightweight; momentum-EMA classifier glues them.

## The seam

Bikar's gt-emitter already produces, for every construction it renders:

- `render.svg` / `render.png` — what the detector sees (the "query view")
- `pattern.gt.json` — the construction-grounded truth: per-shape
  `source_primitives`, polar position, area, bbox, fill_color (the
  "gallery view" — provenance + visual together)

For every shape in every pattern bikar can render, **we already have the
matched (visual, provenance) pair** that B-AFF training requires. Iter-5
proved that on Phase 1.A this pair is enough to fuse to ARI=1.000 by
construction. The training pipeline doesn't need to discover the pair —
bikar emits it.

This means:

- Today's deliverable from Phase 1.B (a corpus of medallion-6, -12,
  girih, mirror-only, scaled-concentric — bikar gt-emitter regression)
  **is structurally identical** to a B-AFF training set.
- The same corpus answers two questions:
  1. *Today:* does bikar's gt-emitter stay consistent across
     constructions? (regression test)
  2. *Later:* can a learned detector embedding be made cosine-compatible
     with a provenance-derived embedding? (B-AFF training)

The seam exists for free if we ship Phase 1.B with the right schema
discipline. It does not exist for free if we cut corners.

## What discipline preserves the seam

These are the rules that keep Phase 1.B an asset for B-AFF later, not
just a regression test that needs reformatting:

### Rule 1 — Render in deterministic, training-grade form

Each construction in Phase 1.B must render to:

- `render.png` at a **fixed canvas size** (default 1024×1024) with
  **fixed DPI** and **fixed anti-aliasing settings**. No per-construction
  tuning.
- A `metadata.json` recording the render parameters (canvas, DPI, AA,
  seed if any).

Why: B-AFF's query-side model trains on rasterized pixels. If renders
drift in resolution or AA between constructions, the visual embedding
sees scale-confounded inputs and the learned proxy generalizes badly.

### Rule 2 — `pattern.gt.json` includes per-shape `polygon_outline` in render-pixel coordinates

Iter-5's fusion uses `source_primitives` multisets (provenance side).
B-AFF training will additionally need each shape's *visual region* in
the render — the pixel mask or polygon outline that the gallery-side
model encodes.

**Verified satisfied 2026-05-05** (during #190 implementation): bikar's
`gt-emitter.ts` already emits `evidence.outline` in render-pixel
coordinates (line 464: "Build pixel-space outline"; vertices passed
through `geomToPixel(v, bbox, scaleX, scaleY)`). Same coordinate frame
as `render.png`. `outline_arcs.source/target` are also pixel-space.
**No schema change needed** — `outline` IS the polygon_outline this rule
required. No 1.13 → 1.14 bump.

Why this matters: a B-AFF gallery-side model takes (image patch +
provenance tags) → embedding. The cropping data already exists.

### Rule 3 — Parametric variation, not hand-authored one-offs

Each construction template should be a **bikar `.bkr` file** that takes
parameters (e.g., `medallion-N` with N ∈ {6, 8, 10, 12, 14, 16}). Phase
1.B authors **the templates**, not the renders. A driver script
enumerates parameter combinations and emits the render+gt pair for each.

Why: B-AFF needs *augmentation density*. 6 medallion-N values × 8 stroke
widths × 5 rotations is 240 training samples from one template. 6
hand-authored medallion-N files is 6 samples and a maintenance burden.
Parametric templates are how the training corpus scales without human
labor scaling with it.

### Rule 4 — Train/val/test split lives in the corpus, not the trainer

The corpus directory layout includes `splits.json` that fixes which
parameter combinations are in train vs val vs test. The split is
authored once, with explicit out-of-distribution holdouts (e.g., "all
girih constructions are test-only").

Why: the moment a B-AFF training run picks splits dynamically, every
re-run has different held-out sets and progress can't be compared. The
split is part of the corpus, not the trainer. (This also catches over-
fits in the "today" use case — if a detector improvement only helps on
medallion-10 because we accidentally trained on it, the held-out girih
test row exposes it immediately.)

### Rule 5 — One `corpus.json` index that both consumers read

The corpus directory has a single `corpus.json` listing every render+gt
pair, parameters used, and split assignment. Both consumers — today's
`qiyas validate-detector` regression run and tomorrow's B-AFF trainer —
read this index. Neither walks the directory tree directly.

Why: the index is the **API**. As long as the index format is stable,
the two consumers stay decoupled, and the seam holds.

## Proposed corpus directory layout

```
qiyas/calibration/phase-1b-corpus/
├── corpus.json                          # ← the API
├── splits.json                          # train/val/test assignments
├── templates/                           # bikar .bkr parametric templates
│   ├── medallion-N.bkr                  # parameter: N
│   ├── girih-tile.bkr                   # parameters: tile-set, scale
│   ├── mirror-only.bkr                  # parameters: axis-count
│   ├── scaled-concentric.bkr            # parameters: ratio, levels
│   └── strapwork.bkr                    # parameters: N, crossing-mode
├── renders/                             # generated; not git-tracked beyond samples
│   └── <template>-<param-hash>/
│       ├── render.png                   # 1024×1024, fixed AA
│       ├── render.svg                   # for symbolic regression
│       ├── pattern.gt.json              # provenance + per-shape polygon_outline
│       └── metadata.json                # render parameters
└── README.md                            # how to regenerate; consumer contract
```

## Two-consumer contract

**Consumer A — today's `qiyas validate-detector` regression run:**
- Reads `corpus.json`, picks the test split.
- For each (render, gt) pair, runs the detector on render.png, computes
  identity-fidelity against pattern.gt.json.
- Emits per-construction pass/fail rows.

**Consumer B — tomorrow's B-AFF training run (when triggered):**
- Reads `corpus.json` + `splits.json`.
- Trains gallery-side mixer on (render patch, provenance multiset)
  pairs from train split.
- Trains query-side lightweight model on (render patch only) from train
  split, with momentum-EMA constraint to gallery's classifier.
- Validates on val split, holds out test split for final eval.
- Emits a learned embedding model that the detector can use as a per-
  pair identity gate at runtime.

Consumer A exists; Consumer B is hypothetical. The contract is what
makes the hypothetical consumer cheap to build later.

## Scope cuts — what this plan is NOT

- **Not building B-AFF now.** Building B-AFF is months of work and only
  worth it when there's a concrete consumer of detector-time identity
  (e.g., sacred-patterns iteration loop's A6 baseline match on novel
  patterns where bikar truth is unavailable). This plan only ensures the
  ground exists for B-AFF when the trigger comes.
- **Not blocking Phase 1.B on training-pipeline ergonomics.** Phase 1.B
  ships when the corpus exists, the index is stable, and the regression
  test runs green. B-AFF-readiness is a side-effect of doing those
  things with discipline, not an additional Phase.
- **Not committing to B-AFF as the eventual path.** If by the time we
  need detector-time identity, a different architecture (e.g., learned
  retrieval embeddings, neural shape descriptors, foundation-model
  features) has matured, we use that. The corpus is the asset; the
  trainer is the swap-in.

## Cascade impact

Adds a paragraph to `shape-identity-detection-cascade.md` Phase 1.B
section pointing at this doc, plus the five rules as Phase 1.B
acceptance criteria. Phase 1.B's existing description ("expand to
8-construction corpus to catch over-fits") becomes ("expand to
parameter-driven corpus per `bikar-as-training-data-generator.md`,
which doubles as a B-AFF training-corpus when we need it").

No new tasks for Phase 1.B beyond what's already in the cascade plan;
this doc just specifies *how* Phase 1.B should be authored so the seam
is preserved.

## Why this matters now (not when B-AFF is being built)

Three reasons to lock the discipline now, not later:

1. **Corpus authoring is the expensive part.** Authoring 5 parametric
   bikar templates is days of work. Reformatting 5 hand-authored
   one-offs into parametric templates later is days of work *plus* the
   risk that the originals encode tacit assumptions that don't survive
   parametrization. Do it right once.

2. **Schema decisions compound.** If `pattern.gt.json` lacks
   per-shape polygon_outline at Phase 1.B time, every consumer walks
   around it. By the time we need B-AFF, three other consumers have
   built workarounds and the schema is harder to extend.

3. **The seam is the value.** The recommendation in the divergence doc
   was Option C *because* C unblocks B-AFF later. That argument
   collapses if C ships in a form B-AFF can't consume. Naming the seam
   makes the recommendation auditable.

## Owner sign-off needed

Before Phase 1.B authoring starts, owner approves:

- [x] These five rules become Phase 1.B acceptance criteria.
- [x] `pattern.gt.json` schema gets `polygon_outline` extension
      (bikar-side change; coordinates with bikar's in-flight strapwork
      work at `421e943`+).
- [x] Training/val/test splits are authored as part of corpus
      construction, not deferred.
- [x] `corpus.json` index format is the API; both consumers read it.

**Signed off 2026-05-05 by Omar.** Phase 1.B authoring begins under
these five rules. First parametric template: petal-N-ring (the arc-bearing
template named in `qiyas/calibration/i1/iter-6-arc-aware-tf-smoke.md` as
the load-bearing arc-path coverage gap from PR3's polygon-only smoke
test). Tracked under sacred-patterns task #187 and its slices #189–#193.
