# Iteration 57 — Hypothesis

```yaml
attempt: 57
date: 2026-06-11
stage: structure
target_wave: 15
gap_targeted: >
  Wave 15 — 10 real deep_navy five-pointed STAR tiles (pentagrams,
  apex pointing radially outward) at the outer edge, ONE per 36-deg
  repeat ON the dart axes (18 mod 36, rel jitter +-0.5 =
  registration noise), r 171-198u, mean area ~181u^2 — wave-4's
  shape class recurring at the outer ring. Baseline on the iter-56
  render: 100.0% coverage / 24.3 iou — SATURATED-COVERAGE regime
  (w11 precedent): the zone is already field ink, so coverage
  carries no signal and iou is weak; census + clearance + eyeball
  carry acceptance. Pre-stated zoom expectation ("narrow radial
  kite") was FALSIFIED by both witnesses (ids 30/58): the
  divergence — clean PENTAGRAMS — became the model (Tenet 26).
  Symmetrized consensus 20/20 stack, 164.1u^2; closing probe 6.3%/
  7.5% (concavities are the star valleys — real boundary, modeled
  raw). approxPolyDP's 6-row seed descended to a poor local optimum
  (0.916) while the DOF pick favored a noisy 8-row model with a
  split point-vertex — resolved by seeding descent from IDEAL
  PENTAGRAM GEOMETRY (star center r~184, outer ~12.5u, inner 0.382
  outer): the geo seed descended to 0.924 and the DOF pick then
  chose the topologically-correct 6-row/10-vert star. SNAP: g=0.5
  cost 0.028 > 0.01 — escalated to g=0.25 (M=1440), snapped 0.910
  (third escalation; driver = smallness, w11-style: 0.25 deg ~
  0.8u tangential at r 184 vs features +-1-3.25 deg). Clearance
  data-proven (iterations/56/measure/clearance-wave15.py): 10
  stamps overlap reference waves 1-14 AND unbuilt 16-22 by ZERO px;
  84.5% on-target (lowest yet — thin star points have high
  perimeter/area), off-target 100% attributed (14.0% near-white +
  1.5% w15-fragments, zero OTHER). Min distances: 6.47u to OUR w12
  bell (same dart axis, its apex r 170.7 vs our inner verts), 5.30u
  to each OUR w14 shield (angular neighbors across the dart line),
  34.3u to the w13 teardrops — all above the 4.79u precedent.
one_idea: >
  ONE rotated 10-vert cycle in layer 1, wave-12/13 axis-symmetric
  technique on DART axes: six new blueprint rings C70-C75 (radii
  177.6/175.2/181.0/187.5/186.8/194.3; on-axis rings C70/C75 at
  M=20 so cpt1 is exactly 18 deg, pair rings C71-C74 at M=1440 per
  the snap escalation) and the single cycle under rotate 10 around
  C0.mpt walking the star boundary valley/point alternately:
  [C70.cpt1 C71.cpt81 C72.cpt78 C73.cpt85 C74.cpt76 C75.cpt1
  C74.cpt68 C73.cpt59 C72.cpt66 C71.cpt63] (on-axis inner valley ->
  +bottom point 2.25 -> +valley 1.5 -> +side point 3.25 -> +valley
  1.0 -> on-axis apex -> mirror side back). Fills navy via the
  layer == 1 rule (reference deep_navy — Stage-2 deferral).
prediction: >
  Census 413 -> 429: +10 layer-1 ten-sided faces (decagon bucket
  11 -> 21 — wave-4 precedent: bikar types faces by side count,
  its pentagrams land in `decagon`) + 6 benign blueprint circles
  (circle bucket 70 -> 76) — PRIMARY gate. Wave-diff 15: coverage
  stays 100.0 (saturated), iou moves little ([22, 30] band — the
  stars stamp INTO existing field ink; only band-edge pixels
  change). Waves 1-14 hold on iter-56 baselines (w1 82.2/71.1, w2
  87.1/59.0, w3 93.9/76.3, w4 96.9/41.2, w5 98.0/53.1, w6
  97.4/51.6, w7 96.0/25.1, w8 84.2/32.9, w9 95.0/53.3, w10
  94.3/25.4, w11 94.8/25.8, w12 100.0/46.2, w13 98.6/51.8, w14
  93.3/46.8); allow <= 2 iou down on outer waves 12-14 whose crop
  windows contain wave-15 ink.
falsifier: >
  If the census decagon count rises by less than 10, the cycle
  failed to close — Tier-0 witness (one star, no field) before
  touching the composite. If any NON-decagon bucket moves, that is
  the face-split tell — the 5.30u w14-shield gaps (sides==6
  bucket) and the 6.47u w12-bell gap (sides==8 bucket) are the
  suspects; diff the gt face inventory before attributing. If the
  stars render on star-tip axes, the dart-axis cpt offset (+18 deg
  baked into kp/km — cpt1 on M=20, cpt72+4x on M=1440) is wrong.
  Since coverage is saturated, do NOT read coverage/iou as
  acceptance signals — the eyeball gate (star outlines visible in
  the render at the right spots) is decisive (w12 protocol).
```

## Verdict (2026-06-11): WAVE 15 PASSES — iteration 57 FROZEN

- **Census (PRIMARY gate): 413 -> 429 EXACT** — +10 ten-sided faces
  (decagon bucket 11 -> 21, wave-4 precedent confirmed: bikar types
  by side count) + 6 benign blueprint circles (C70-C75, 70 -> 76).
  Every other bucket unchanged — no face-split: the 5.30u w14-shield
  gaps (sides==6 held at 100) and the 6.47u w12-bell gap (sides==8
  held at 20) both survived. Known benign warning only
  (`_girih_hexagon_star`).
- **gt placement check**: all 10 new decagons at polar theta 18.09/
  54.09/90.06/126.01/161.95/197.91/233.91/269.94/305.99/342.05 —
  dart axes to within 0.1 deg; uniform area 509 render-px^2
  (= 165.6u^2, the model area); 10 outline verts each.
- **Wave-diff 15: 100.0/24.3 — unchanged from baseline, iou in the
  [22, 30] band** ✓. As predicted for the saturated regime the
  metric carried no signal: the stars stamp navy INTO existing
  field ink, so the binarized wave-mask comparison cannot move.
  Waves 1-14 hold bit-identical to their iter-56 baselines (zero
  iou delta on all 14).
- **Raster before/after (w12 protocol)**: iter-56 vs iter-57 cairo
  diff = 7339 px. Pentagram-shaped clusters exactly where predicted
  on dart axes (d90/d270: on-axis apex clusters at r~335 render px
  ~ 194u, side-point pairs at +-3.7 deg); the remaining fragments
  (incl. clusters near star-tip axes at the w13-apex radius) were
  eyeballed before/after at tip0 — thin strapwork hatch-line
  redistribution inside EXISTING faces from voids re-tessellation,
  zero geometry change (census exactness is the topology witness).
- **Eyeball gate (Tenet 26, expectation written before viewing)**:
  the render-zoom expectation ("matching navy pentagram visible")
  was PARTIALLY met — the stars are nearly invisible navy-on-navy
  in the render because the fill rule paints layer-1 navy and the
  under-ink at the wave-15 zone is already navy (divergence
  recorded; render-style matter, Stage-2 color work, not geometry).
  DECISIVE eyeball ran on the gt-outline overlay instead
  (wave-diff/wave-15/overlay-zoom-{d18,d90}.png + full
  overlay-w15-on-ref.png): at both checked axes the red gt outline
  is a five-pointed star, apex outward, riding the reference's
  deep_navy pentagram tile. Divergence recorded: sub-tile offset
  ~1-3 ref px (direction varies by axis) and slightly smaller than
  the ink star — consistent with snapped IoU 0.910 on a 20-witness
  consensus with +-0.5 deg per-tile jitter. Shape class,
  orientation, axis placement, size confirmed.
- **Snap taxonomy data point**: third g=0.25 escalation (g=0.5 cost
  0.028 > 0.01); driver = smallness (164u^2), w11-style —
  consistent with the angular-feature-scale discriminator.
- **Stage-2 backlog addition**: w15 deep_navy (tiles fill navy via
  the layer == 1 rule; reference color is deep_navy — same deferral
  as waves 3-14; note the navy-on-navy invisibility above makes
  w15 a priority witness for the Stage-2 color pass).

Next: wave 16 per wave-plan.json — baseline from wave-diff's SVG
raster of THIS iteration's render.svg.
