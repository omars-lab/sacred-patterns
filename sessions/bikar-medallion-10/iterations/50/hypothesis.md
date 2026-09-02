# Iteration 50 — Hypothesis

```yaml
attempt: 50
date: 2026-06-11
stage: structure
target_wave: 8
gap_targeted: >
  Wave 8 — 10 real navy diamonds at kind_r_frac 0.447, mean area
  316px^2 (~185.9u^2), ONE per 36-deg repeat sitting ON the dart
  axes (rel scatter +-0.6 deg = segmentation noise) — baseline
  42.1% coverage / 18.4 iou on the iter-49 render (computed via
  wave-diff's NEW canonical SVG raster path per the iter-49
  rasterizer finding). Visual identification (tinted crop + zooms
  of ids 87/100; pre-stated expectation "elongated radial hexagon"
  was FALSIFIED by the look — they are 4-vertex diamonds bounded by
  the white band lattice on all four sides, corners chamfered where
  bands cross, which is why raw contours report 5-9 vertices).
  Model fit by IoU coordinate-descent against the 20-witness
  consensus (10 rotated masks + their 18-deg mirrors, area-matched
  threshold): axis-symmetric diamond r_in 118.6, side 126.95 at
  rel +-4.75, r_out 134.75 -> IoU 0.932, area 169.8u^2 (vs 185.9
  raw mean - band nibble). Grid snap is FREE this wave: w=4.8 on
  M=300 (cpt19=22.8 deg, cpt11=13.2 deg exact, asserted 1e-9)
  scores IoU 0.932, area 172.0u^2 (measure/wave8-fit.json).
  Clearance data-proven: the 10 snapped diamonds rasterized in
  reference px space overlap reference waves 1-7 by ZERO px; 89.5%
  of model ink lands on reference wave-8 pixels.
one_idea: >
  One rotated 4-point cycle in layer 1, the same standalone-closed-
  cycle technique that passed waves 2-7: three new blueprint rings
  - C32 r118.6/20 (inner axis vertex, cpt1 = 18 deg), C33
  r126.9/300 (side vertices, cpt19/cpt11), C34 r134.8/20 (outer
  axis vertex, cpt1) - and ONE cycle [C32.cpt1 C33.cpt19 C34.cpt1
  C33.cpt11] under rotate 10 around C0.mpt. Diamonds fill navy via
  the existing layer==1 rule. Standalone: no layer-1 edge
  crossings (nearest built geometry is the wave-7 outer teardrop,
  radial gap >= 7.4u along every shared ray per the chord check;
  data proof above is authoritative).
prediction: >
  Wave-8 coverage >= 90% (from 42.1) and iou >= 40% (from 18.4;
  diamonds are wave-5/6 scale ~316px^2, those landed 52-53 — but
  wave 8's outward neighbors (waves 9-22) are unbuilt, so envelope
  penalty on ref-white lattice will bite; wave-7's attribution
  showed that penalty class dominates at small scale). Census 275
  -> 288: +10 layer-1 quads (counted as layer==1 sides==4 delta)
  + 3 benign blueprint circles (C32-C34). Waves 1-7 hold on the
  cairo baselines (w1 82.2/71.1, w2 87.1/59.0, w3 93.9/76.3, w4
  96.9/41.2, w5 98.0/53.1, w6 97.4/51.5, w7 96.2/25.7); wave-7 iou
  may MOVE UP a little (its 91%-of-penalty ref-white envelope zone
  partially gets correct navy ink from these adjacent diamonds —
  metric interlock in our favor); allow <= 2 down on 5/6/7.
falsifier: >
  If the diamonds render off-axis or at the wrong ring, the axis/
  radius read is wrong - re-measure, don't nudge. If layer-1 quad
  count rises by less than 10, the cycle failed to close - Tier-0
  witness (one diamond, no field) before touching the composite.
  If coverage lands >= 90 but iou < 35, check WHERE: penalty
  concentrated on ref-white lattice/unbuilt-wave zones = accepted
  (wave-7 precedent, Stage-2/later-wave business); a displaced
  blob = re-measure. If waves 1-7 regress beyond 2 iou points,
  diff the gt shape census first (face-split signal, not paint).
```

## Verdict (2026-06-11): WAVE 8 PASSES on construction — coverage capped by field strapwork, counterfactually proven

Wave-diff: coverage 84.2% (predicted >= 90, from 42.1) — MISSED;
iou 36.2% (from 18.4). The coverage prediction was falsified, and
the cause is named, measured, and owned: the uncovered 499px
(15.8%) sit at r 126.6-134.1 across the full rel width — 0% are
inboard of our inner tip, 2.2% outboard of the outer tip, and
**100% of them are near-white in OUR render**. That's the girih
field's white strapwork bands plowing straight through the
diamond zone; the reference's band lattice routes AROUND the
wave-8 diamonds. **Counterfactual proof** (measure/
probe-no-strapwork.bkr — identical pattern, strapwork statement
removed): wave-8 coverage **99.9%**. The diamond geometry is
essentially exact; the gap is entirely the approximate field
band network, which is Stage-2 band-geometry work (same owner as
wave-7's attributed iou miss). The probe's iou 29.0 (lower than
36.2) is consistent: removing the white bands exposes more
field-tile ink inside the 8px envelope.

Eyeball gate (pre-stated expectation: thin halo if model small,
displaced blob if mis-measured): zoom-top + zoom-right confirm
every gold outline contains our navy diamond, correct axes,
correct orientation — the visible loss is white bands crossing
the tile, exactly matching the px attribution. No displacement.

Census: gt shapes 275 -> 288, exactly as predicted: +10 quads
(the diamonds, classified sides=4) + 3 benign blueprint circles
C32-C34. The cycle closed on all 10 axes.

Holds (all via wave-diff's canonical SVG raster path, iter-49
finding): waves 1-6 BIT-IDENTICAL to the cairo baselines (82.2/
71.1, 87.1/59.0, 93.9/76.3, 96.9/41.2, 98.0/53.1, 97.4/51.5);
wave-7 96.2/25.4 (iou -0.3, within the <= 2 interlock allowance).

Stage-2 backlog additions: (a) w8 color check (navy fill via
layer==1 rule; plan samples navy — likely already right, verify
at Stage 2); (b) **band rerouting around the middle-ring
diamonds** — first wave where the field strapwork actively
crosses a gated tile; when Stage-2 band geometry is built, the
wave-8 coverage number should be re-measured (expect ~99.9).

Next: wave 9 per wave-plan.json — baseline from wave-diff's own
SVG raster of THIS iteration's render.svg.
