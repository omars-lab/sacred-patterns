# iter-33 evaluation — gap-free girih field vs A6/A5 (Slice 3, decision-doc C″)

**Date:** 2026-05-28
**Construction:** `girih field decagonal 62 shells 2` + `voids detect` + classify/fill
**bikar engine:** Slice-2 DSL (commit ddb2e98, `girih field` statement)

## What was measured

Rendered iter-33 → SVG (9692 paths) + gt.json (2031 shapes) → `qiyas encode`
(2931 shapes, **dominant_fold=10 @ conf 0.76**) → `qiyas svg-audit --baseline
fixtures/bikar-medallion-10-iter11.baseline.json`.

## Results

| Audit | Status | Score | Reading |
|-------|--------|-------|---------|
| A1 (semantic census) | PASS | 100% | clean shape vocabulary, no degenerate faces |
| A2 (sector balance) | APPROXIMATE | 85 | 10-fold sectors balanced, CV 2.0% |
| A4 (coverage) | PARTIAL | 86.1% | field fills 86% of medallion bbox — gap-free as visual confirmed |
| A5 (band integrity) | BROKEN | 0.0 | 0 strapwork crossings (expected ~45 for n=10) |
| A6 (zone-band census) | — | 0/10 | every zone-band shape MISSING or EXCESS |

A6 per-shape: baseline expects v4 polygons (20 inner-star + 200 transition) and
v0 circles + v10/v20 stars; the field produces **0** of those in-zone and
**EXCESS** triangles (100 vs 10 inner; 580 vs 100 transition).

## Q1 answered (decision-doc 2026-05-28-medallion10-girih-ceiling.md)

> **Q1: does a real gap-free field clear the A6 zone bands, or is A5 still the right metric?**

**Answer: NO — the gap-free field does not clear A6, and A5 is also BROKEN — but
neither failure is about gaps.** The field IS gap-free (A4 86%, A1 PASS, A2 10-fold
balanced, visual confirmed). It fails A6/A5 because of a **vocabulary + metric
mismatch, not a construction gap:**

1. **A6 baseline is construction-specific.** `bikar-medallion-10-iter11.baseline.json`
   encodes the per-zone shape census of the *connect-on-circle* reference
   (circles from `divide`, v4 rhombi from `{10/k}` overlay intersections, v10/v20
   stars from `connect every k`). The girih field produces a *different but
   equally valid* tiling vocabulary (decagons + tile-decoration triangles +
   pentagons). Scoring a girih construction against a connect-on-circle baseline
   is an apples-to-oranges zone census — every band MISSES the baseline's expected
   class and shows EXCESS triangles.

2. **A5 measures strapwork band crossings.** The girih field's `voids detect`
   faces are *tile interiors*, not woven over/under bands, so there are 0
   crossings. A5 is the right metric *for a strapwork construction* but the field
   (as authored here, decoration-as-faces) isn't one — it's a tile mosaic.

**Implication for the cascade:** the girih field clears the *gap problem* that
capped iters 13–18 (A4 86% + A1/A2 clean is the best structural footing any
medallion-10 iter has had), but A6 cannot score it until the baseline is
re-derived from a girih construction, OR the field is styled to reproduce the
reference's strapwork bands (so A5 becomes the live metric). This is exactly the
fork the decision doc's Q1 posed; the data says **neither A6-as-is nor A5-as-is
fits — the baseline must move to the girih vocabulary first.**

## Recommendation (feeds decision-doc §8 + Slice 4 trigger)

- The field generator is validated end-to-end (DSL → SVG → encode → 10-fold @ 0.76).
- Before iter-34, the A6 baseline needs re-derivation from a girih reference
  (a new fixture), OR the medallion-10 acceptance metric for girih constructions
  switches to A4-coverage + A2-fold-balance (both strong here) until a strapwork
  overlay (Slice 4 bowtie/hexagon pocket-filling + band weaving) lands to make A5
  live. This is an owner-direction fork (which metric is canonical for the girih
  era) — surfaced, not pre-picked.

## Close (1) — A6 re-baselined to the girih vocabulary (2026-05-28, owner picked BOTH)

The owner resolved the fork BOTH ways. Close (1) re-derives the A6 baseline from a
girih-vocabulary reference and re-audits iter-33 against it.

**Mechanism:** `qiyas baseline emit render.svg --primitives-source svg -o
fixtures/bikar-medallion-10-girih.baseline.json` (same auto-emit path that produced
the iter-11 baseline), then `qiyas svg-audit render.encoding.json --baseline <new>`.

**Emit-time vs audit-time vocabulary drift (close-1 finding):** the first emit
produced 10 `expected_shapes`, 4 of which were generic `polygon` buckets with
`vertex_count=0`. These are shapes whose `vertex_count_for()` returned `None` at
emit time (params-based resolution in `svg_audit/_vocab.py`), but the A6 auditor
re-resolves vertex counts *geometrically* (A1 census shows clean 3/4/5/6/7/8/13/20-gons),
so a 0-vertex lookup can never match — they surfaced as spurious MISSING. The
resolved `-v3`/`-v5` buckets already census the same shapes. Dropping the 4 unresolvable
catch-all buckets leaves a baseline that scores the girih vocabulary fairly.

**Result — A6 went from 0/10 to 6/6 (1.0 PASS):**

| Audit | iter-11 (connect-on-circle) baseline | girih-vocabulary baseline |
|-------|--------------------------------------|---------------------------|
| A1 | PASS 100% | PASS 100% |
| A2 | 85 (10-fold, CV 2%) | 85 (unchanged) |
| A4 | 86.1% | 86.13% (unchanged) |
| A5 | BROKEN 0 | BROKEN 0 (strapwork deferred → Slice 4 / close-2) |
| **A6** | **0/10 (every band MISSING/EXCESS)** | **6/6 = 1.0 PASS** |

**Conclusion:** the fork's premise is confirmed empirically — scoring the girih field
against a connect-on-circle baseline was apples-to-oranges (A6=0); against a
vocabulary-matched baseline A6 is a clean 6/6. A5 remains 0 by design (no strapwork
yet — that is close-2's deferred Slice-4 half). The new baseline lives at
`fixtures/bikar-medallion-10-girih.baseline.json`.
