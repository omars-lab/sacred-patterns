# iter-34 evaluation — Slice-4 strapwork overlay makes A5 live (bikar#653)

**Date:** 2026-06-07
**Construction:** iter-33's `girih field decagonal 62 shells 2` + `voids detect`
+ classify/fill, **+ a `strapwork width 6 / crossing alternating / color
#FFFFFF` overlay** (the only DELTA from iter-33).
**bikar engine:** deco-only strapwork weaving (this session's kernel change —
girih tiles now tag outline edges vs decoration lines distinctly; the band
weaver runs over the decoration network alone).

## Plain-English what & why

iter-33 converged the gap-free decagonal girih field but rendered it as flat blue
filled faces — A5 band-integrity scored **0 BY DESIGN** because nothing was woven
into over/under bands. The reference (`input/reference.jpg`) is defined by **white
interlacing strapwork bands** weaving around blue 10-point stars. iter-34 is the
deferred Slice-4 half: a render-style overlay that draws the field's existing
decoration centerlines as woven white bands, recovering the reference look and
making A5 a live metric (decision-doc close-2).

## The kernel change (render-style, not geometry)

First render of iter-34 (strapwork over the field as-authored) produced a **dense
white mesh, not the reference's bold sparse straps** — 5640 band strands. Root
cause (located via probe, not guessed): `girihTileSegments(tile, true)` pushes
BOTH the tile polygon OUTLINE edges and the decoration lines into the segment
set, and the weaver wove all of them. The tile boundaries are erasable
scaffolding (Hankin/Kaplan: "remove the original tiling"); only the decoration
lines are the visible interlacing.

**Fix:** tag outline edges (`_girih_outline`) vs decoration lines
(`_girih_decoration`) distinctly in the kernel; build the strapwork edge graph
from the decoration-tagged segments alone. Non-girih patterns (no decoration tag)
weave the full graph exactly as before — backward compatible. This is a
render-style change (which lines become bands), consistent with memory
`feedback_girih_strapwork_is_render_style_not_geometry`. Strand count dropped
**5640 → 2790**, and the weave became the clean rosette star-lattice.

Witness frozen as tests (Tenet 18): `packages/core/tests/kernel/girih-tiles.test.ts`
("girih segment role tags") + `packages/core/tests/dsl/evaluator.test.ts` ("girih
field + strapwork weaves the decoration network only").

## Results — A5 goes live

| Audit | iter-33 | iter-34 | Reading |
|-------|---------|---------|---------|
| A1 (semantic census)  | PASS 100% | PASS 100% | clean vocabulary, no degenerate faces |
| A2 (sector balance)   | 85 | 85 | 10-fold balanced, CV ~2% |
| A4 (coverage)         | 86.13% | **100%** | bands + fills cover the medallion bbox |
| **A5 (band integrity)** | **BROKEN 0** | **COMPLETE 100** | **1054 band crossings woven (was 0)** |
| A6 (zone-band census) | 6/6 (1.0) | 5/6 (0.833) | one strapwork-induced EXCESS — see below |

- `qiyas encode`: 5391 shapes, **dominant_fold=10 @ conf 0.78** (iter-33: 0.76).
- `qiyas svg-audit --baseline fixtures/bikar-medallion-10-girih.baseline.json`:
  **3/5** umbrella (A1, A4, A5 PASS; A2 APPROXIMATE; A6 5/6).
- `qiyas pixel-diff` vs reference: **similarity 70.4%** (iter-33: 65.5%) — a ~5pt
  improvement attributable to the recovered white lattice. Asymmetric-channel
  warning (r=85.7 vs b=63.8) reflects the palette being bluer than the
  reference's lighter tones, not a structural defect.

## A6 5/6 — the one EXCESS is the baseline predating strapwork (NOT a defect, NOT re-baselined-to-self)

A6 dropped from 6/6 to 5/6: `transition--pentagon-v5` is EXCESS (found 40,
expected 20). The girih baseline (`bikar-medallion-10-girih.baseline.json`) was
emitted from **iter-33, before any strapwork**. The woven bands legitimately
subdivide some transition-zone regions into additional pentagon faces — a real,
expected consequence of weaving, exactly the drift close-2 anticipated ("when
#653 ships, A5 becomes live and the bar tightens"). The other 5 zone-bands
(inner-star pentagon + v3, outer v3, rosette v3, transition v3) all PASS cleanly.

**I deliberately did NOT re-emit the baseline from iter-34** to force 6/6 — that
would be scoring the render against itself (Tenet 7, tune-to-fit) and prove
nothing about fidelity. The honest reading: the strapwork overlay preserves 5/6
zone-bands and adds the bands A5 measures; the single EXCESS is the price of the
new (correct) bands the baseline doesn't yet model. Re-baselining-to-strapwork is
a follow-up the owner can elect; it is not done here.

## Definition-of-done check (handoff)

> "The medallion-10 render visually matches reference.jpg — white interlacing
> bands + legible star tiles — AND A5 band-integrity goes live."

- ✓ **White interlacing bands**: present, woven over/under (1054 crossings),
  forming the rosette star-lattice — the reference's defining feature.
- ✓ **Legible star tiles**: central 10-point star + ring rosette stars read
  clearly (see `render.png`, `diff/diff-overlay.png`).
- ✓ **A5 live**: COMPLETE 100 (was BROKEN 0 by design).

## Honest remaining gaps (deferred, out of render-style scope)

1. **Pocket small-stars absent.** The reference's small turquoise/cobalt
   pocket-stars come from bowtie/hexagon tile decoration lines. The field is
   **decagons-only** (69 decagons, 0 bowtie/hexagon) — the Slice-1 spillover the
   decision doc flagged: bowtie/hexagon pocket-filling is deferred geometric
   Slice-4 work, owner-gated (new tile geometry, the 3-way B-H-D chooser). The
   dominant white rosette lattice is recovered WITHOUT them.
2. **Fill regions more fragmented** than the reference's flat zones (faces come
   from the full field's `voids detect`, not from between-band regions).
3. **Boundary** is a scalloped decagon edge vs the reference's rounded rosette
   perimeter (the red ring in `diff/diff-visual.png`).

These are refinements beyond "make A5 live + recover the white lattice"; none
block the close-2 deliverable.

## Artifacts

- `pattern.bkr` — iter-33 field + strapwork overlay block
- `render.svg` (2790 strands) / `render.png` — final render
- `render.encoding.json` — fold-10 @ 0.78
- `svg-audit.json` — 3/5, A5 COMPLETE 100
- `diff/` — pixel-diff vs reference (70.4% similarity)
- `visual-verdict.md` — Tenet-24 expectation-first + the decisive deco-only probe
