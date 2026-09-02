# Iteration 49 — Hypothesis

```yaml
attempt: 49
date: 2026-06-11
stage: structure
target_wave: 7
gap_targeted: >
  Wave 7 — 40 real deep_navy shapes at kind_r_frac 0.398, mean area
  142px^2 (~83.4u^2, the smallest gated so far), four per 36-deg
  repeat flanking the DART axes — sits at 71.1% coverage / 19.4 iou
  on the iter-48 render (field tiles + bands only). First multi-
  shape-per-axis wave. Visual identification (tinted crop + zooms of
  ids 92/107; pre-stated "free-standing 4-sided darts" was HALF-
  falsified — they are band-bounded interstice tiles, and the
  divergence located the true class before any DSL was written):
  two mirror-pairs per repeat, both pointing INWARD — an outer
  5-vertex teardrop/kite at rel +-6.8 deg (r 114.8-124.4) and an
  inner 4-vertex wedge at rel +-13.2 deg (r 97.2-112.6). Models fit
  by IoU coordinate-descent against 20-witness consensus masks
  (mirror-folded canonical frame): outer IoU 0.933 area 80.5u^2,
  inner IoU 0.951 area 80.8u^2 (measure/wave7-model-fit.json).
  Grid-snapped (measure/wave7-snap.json): outer IoU 0.888 / 80.9u^2,
  inner IoU 0.869 / 81.2u^2 on the rebuilt consensus — snapping costs
  ~nothing (fitted models score 0.880/0.866 on the same rebuilt
  masks). Clearance is data-proven: the 40 snapped polygons
  rasterized in reference px space overlap reference waves 1-6 by
  ZERO px; 84% of model ink lands on reference wave-7 pixels.
one_idea: >
  Two mirror-pair interstice rings in layer 1, same standalone-
  closed-cycle technique that passed waves 2-6: nine new blueprint
  rings — C23 r114.8/720, C24 r115.5/800, C25 r121.8/800 (the
  radial edge: both at cpt61 = 27.45 deg / cpt19 = 8.55), C26
  r124.4/400, C27 r122.5/400 (outer teardrop); C28 r97.2/720, C29
  r111.1/720, C30 r112.6/100, C31 r107.1/200 (inner wedge) — and
  FOUR rotated cycles (one per shape per repeat): outer+ [C23.cpt41
  C24.cpt61 C25.cpt61 C26.cpt28 C27.cpt27], outer- [C23.cpt31
  C24.cpt19 C25.cpt19 C26.cpt12 C27.cpt13], inner+ [C28.cpt58
  C29.cpt59 C30.cpt9 C31.cpt19], inner- [C28.cpt14 C29.cpt13
  C30.cpt1 C31.cpt1]. Zero quantization error (asserted in
  measure/snap-wave7.py: every cpt index times its grid step equals
  18+-rel exactly). Clearance vs our own rendered waves: wave-6
  shield max r 112.9 (axis peak) vs outer apex r 114.8 at rel 2.5
  (radial gap >= 3.6u at every shared ray); wave-5 arrowhead
  shoulder->apex edge sits >= 5u below the inner wedge along rel
  11..16.2; waves 3/4 radially distant. All four cycles standalone —
  no layer-1 edge crossings, no face splits.
prediction: >
  Wave-7 coverage >= 90% (from 71.1) and iou >= 45% (from 19.4; the
  shapes are the smallest yet — wave-5/6 at petal scale landed
  52.1-52.5, these are half that area, so band-edge erosion bites
  harder; the canonical-frame snap IoU 0.87-0.89 caps the ceiling).
  Census 226 -> 275: +40 layer-1 faces (+20 5-gons, +20 4-gons —
  counted as layer==1 sides==5 / sides==4 deltas, NOT raw sides
  counts, since the field already has pentagons and quads) and +9
  benign blueprint circles (C23-C31). Waves 1-6 hold in the eyeball;
  wave-5/6 iou may dip <= 2 points (metric interlock: adjacent-zone
  dilated envelopes), wave-1..4 unchanged.
falsifier: >
  If the four shapes render on the star-tip axes or the mirror pairs
  land on the wrong side, the rel-sign/axis read is wrong —
  re-measure, don't nudge. If layer-1 face count rises by less than
  40 (gt 5-gon/4-gon deltas short), a cycle failed to close — Tier-0
  witness (one teardrop, no field) before touching the composite.
  If coverage lands >= 90 but iou < 40, check WHERE: uniform thin
  ring of miss at the shape boundary = band-edge erosion (accepted,
  Stage-2 width work); a displaced blob = registration or a wrong
  radius — re-measure that vertex ring. If waves 1-6 regress beyond
  2 iou points, diff the gt shape census first (face-split signal,
  not paint signal).
```

## Verdict (2026-06-11): WAVE 7 PASSES — coverage met, iou miss fully attributed

Wave-diff: wave-7 coverage 96.2% (predicted >= 90, from 71.3
baseline) — met. iou 25.7% (predicted >= 45, from 19.2) — MISSED,
and the falsifier's "check WHERE" branch fired. The attribution
(measure/ penalty-breakdown run, reproduces iou 0.2568 exactly):
the iou denominator charges all render ink in an 8px envelope
around the tiles; for these smallest-yet shapes the penalty zone
(16037px) is 2.7x the tiles' own area (5839px). **91.0% of the
penalty sits where the REFERENCE itself is white band-lattice** —
zones our render still fills with field-tile ink because waves
8-22 and the Stage-2 band geometry aren't built; only 9.0% is true
neighbor-tile mismatch. Counterfactual iou with the ref-white
envelope zones whitened: **0.771**. The miss is the unbuilt
surroundings, not this wave's geometry — the >= 45 prediction was
mis-calibrated for an interstice wave whose envelope is owned by
later waves.

Eyeball gate (pre-stated expectation: orange reference outlines
land ON our navy tiles, loss as boundary halo; displaced blob =
falsified): the zoomed sbs confirms every outline contains our
tile, correct axes, correct mirror-pair arrangement, both rings —
no displaced blobs, no wrong-axis tiles.

Census: gt shapes 226 -> 275, exactly as predicted: +20 layer-1
pentagons (outer teardrops), +20 layer-1 quads (inner wedges), +9
benign blueprint circles C23-C31. All 40 cycles closed.

Waves hold — BUT only after unifying the rasterizer (the
load-bearing finding of this iteration): the iter-48 render.png on
disk was rasterized by a softer path; comparing my cairosvg
1024-height raster of iter-49 against it produced phantom drift
(w1 coverage -7.5, w2 iou +9.5) at ALL radii. Re-rasterizing
iter-48's SVG through the SAME cairosvg call collapsed the drift:
waves 1-4 hold BIT-IDENTICAL (82.2/71.1, 87.1/59.0, 93.9/76.3,
96.9/41.2), wave-5 98.0/52.9 -> 98.0/53.1, wave-6 97.5/52.5 ->
97.4/51.5 (within the predicted <= 2 interlock). Tenet-11 at the
rasterizer layer: wave-diff comparisons are only valid when both
renders go through one rasterization path. Canonical from now on:
cairosvg, output_height=1024. The cairo-path baselines above
REPLACE the iter-48 verdict's numbers for all future hold checks.

Stage-2 note: tiles fill navy #132A61 via the layer==1 rule; the
wave plan samples wave-7 at deep_navy. Joins the Stage-2 backlog
(w3 periwinkle, w4 deep_navy, w5 cyan, w6 navy, w7 deep_navy).

Next: wave 8 per wave-plan.json — and per the rasterizer finding,
compute its baseline from a cairosvg re-raster of THIS iteration's
render.svg, not from any pre-existing PNG.
