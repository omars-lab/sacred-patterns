# Iteration 55 — Hypothesis

```yaml
attempt: 55
date: 2026-06-11
stage: structure
target_wave: 13
gap_targeted: >
  Wave 13 — 10 real turquoise teardrop/leaf tiles in the outer-middle
  ring, ONE per 36-deg repeat ON the star-tip axes (0 mod 36, rel
  jitter +-0.4 = registration noise), mean area ~591u^2, radial span
  ~148-188u — baseline 74.2% coverage / 40.7 iou on the iter-54
  render. UNLIKE waves 11/12 the baseline is NOT saturated: wave-diff
  regains real discrimination this wave, so coverage/iou rejoin the
  census + eyeball + clearance as acceptance signals. Pre-stated zoom
  expectation ("elongated kite/petal pointing outward, possibly with
  shallow band notches") was approximately CONFIRMED by both witnesses
  (ids 48/49): rounded-pentagon body, pointed apex outward on the
  axis (r ~185), on-axis base nub (r ~151). Closing probe filled only
  2.2% (570.9->583.6u^2 at 3u) — boundary concavities are real but
  shallow; modeled the raw consensus. Consensus SYMMETRIZED by
  construction (each witness stacked with its mirror; max stack
  20/20). DOF-penalized pick (IoU - 0.004n over symmetric eps seeds
  2.0-6.0) chose the 4-row/6-vert model: fitted 0.964. SNAP FINDING:
  g=0.5 (M=720) cost 0.013 IoU (0.951) — above the 0.01 escalation
  threshold — so g=0.25 (M=1440) applies: snapped 0.958. Second
  M=1440 wave after w11; here the escalation is driven by the tile's
  NARROW ANGULAR WIDTH (pair x ~4.25-4.5 deg), not smallness — the
  half-degree grid quantizes a 4.25-deg offset by ~6%, visible on a
  37u-long flank. Clearance data-proven
  (iterations/54/measure/clearance-wave13.py): 10 snapped stamps
  overlap reference waves 1-12 AND unbuilt 14-22 by ZERO px; 92.5%
  on-target, off-target 100% attributed (7.5% near-white band px,
  zero fragments, zero other). Model-vs-model min distances: 5.30u to
  OUR wave-9 16-gon (SAME star-tip axis, its on-axis apex r 146.1 vs
  our on-axis base r 151.4), 5.70u to each OUR wave-11 bird (same
  axes, flanking), 21.9u to OUR wave-12 bells (dart axes) — all above
  the 4.98u precedent that held; no face-split risk.
one_idea: >
  ONE rotated 6-vert cycle in layer 1, wave-12 axis-symmetric
  technique on star-tip axes: four new blueprint rings C61-C64
  (radii 151.4/156.1/168.5/185.1; on-axis rings C61/C64 at M=20 so
  cpt0 is exactly 0 deg, pair rings C62/C63 at M=1440 per the snap
  finding) and the single cycle under rotate 10 around C0.mpt walking
  base -> +side base -> +side flank -> apex -> -side flank -> -side
  base:
  [C61.cpt0 C62.cpt17 C63.cpt18 C64.cpt0 C63.cpt1422 C62.cpt1423].
  Fills navy via the existing layer == 1 rule (reference color
  turquoise — Stage-2 deferral like waves 3-11).
prediction: >
  Census 374 -> 388: +10 layer-1 six-sided faces (sides==6 bucket
  70 -> 80) + 4 benign blueprint circles (circle bucket 61 -> 65) —
  PRIMARY gate. Wave-diff 13: coverage rises from 74.2 into [88, 98]
  (the stamps cover ~94% of the reference wave mask and the zone's
  uncovered remainder is render-white today) and iou rises from 40.7
  into [45, 62] — wide band acknowledged: the wave-12 lesson says
  predict the PIXEL mechanism, and here the load-bearing claim is
  that the wave-13 zone is NOT already field ink (baseline coverage
  74.2 != 100 proves real white gap exists for new ink to fill).
  Waves 1-12 hold on the iter-54 baselines (w1 82.2/71.1, w2
  87.1/59.0, w3 93.9/76.3, w4 96.9/41.2, w5 98.0/53.1, w6 97.4/51.6,
  w7 96.0/25.1, w8 84.2/32.9, w9 95.0/53.5, w10 94.3/25.4, w11
  94.8/27.0, w12 100.0/46.2); allow <= 2 iou down on middle/outer
  waves 9-12 whose crop windows contain wave-13 ink — if any dips
  beyond 2, attribute via the falsifier path before accepting.
falsifier: >
  If the census six-sided count rises by less than 10, the cycle
  failed to close — Tier-0 witness (one teardrop, no field) before
  touching the composite. If the tiles render on dart axes or at the
  wrong ring, the star-tip axis read is wrong — re-measure, don't
  nudge. If coverage stays ~74 (no rise), the zone was already-inked
  after all — attribute via before/after crops (wave-12 protocol)
  before accepting, and re-examine the fill-rule path. If coverage
  rises but iou DROPS below 39, the new ink is landing off the
  wave-13 mask — re-check the M=20-vs-M=1440 mixed-circle cpt
  arithmetic (an off-by-one in M=1440 cpt indexing shows up as a
  ~0.25-deg rotation of every tile). If waves 1-12 regress beyond
  the allowance, diff the gt census first (face-split signal, not
  paint) — the 5.30u/5.70u gaps say face-splits should NOT happen; a
  split here (most likely vs the w9 16-gon, sides==16 bucket) would
  falsify the min-distance check, not the wave model.
```

## Verdict (2026-06-11): WAVE 13 PASSES — iteration 55 FROZEN

- **Census (PRIMARY gate): 374 -> 388 EXACT** — +10 six-sided faces
  (sides==6 bucket 70 -> 80) + 4 benign blueprint circles (C61-C64,
  61 -> 65). No face-splits: the sides==16 bucket (w9 16-gons, the
  5.30u nearest neighbor) is untouched; all other buckets unchanged.
  Known benign warning only (`_girih_hexagon_star`).
- **Wave-diff 13: coverage 98.6 (predicted [88, 98] — 0.6 above the
  band top; the mechanism was right, the band conservative), iou
  52.4 (in [45, 62] ✓, from 40.7)** — first wave since 10 where
  wave-diff carried real signal again, and it confirmed: the zone's
  uncovered 25.8% was render-white and the new ink filled it.
- **Holds**: w1-w10, w12 bit-identical; w9 95.0/53.3 (iou -0.2) and
  w11 94.8/26.1 (iou -0.9, wave-13 ink in its crop window as
  predicted) — both within the <= 2 allowance, no attribution probe
  needed.
- **Eyeball gate (Tenet 26, expectation written before viewing)**:
  zoom-east0 + zoom-ne72 (star-tip axes 0/72 deg, r 168u, crops
  saved in wave-diff/wave-13/) — the render's navy teardrop fills
  the reference outline at both axes: apex outward on the axis,
  rounded body, on-axis base clear of the w9 16-gon apex, w11 birds
  flanking in the correct arrangement. Matches the pre-stated
  expectation (shape compared, not color — see deferral below).
- **Snap-escalation taxonomy refined**: the g=0.25 (M=1440)
  escalation has TWO drivers now — tile smallness (w11, 135u^2) and
  narrow angular width (w13, x ~4.25-4.5 deg on 37u flanks). The
  g=0.5-first probe rule stays; the rule's prediction "big tiles
  hold g=0.5" is FALSIFIED as stated — the correct discriminator is
  angular feature scale, not area.
- **Stage-2 backlog addition**: w13 turquoise (tiles currently fill
  navy via the layer == 1 rule; reference color is turquoise — same
  deferral as waves 3-11).

Next: wave 14 per wave-plan.json — baseline from wave-diff's SVG
raster of THIS iteration's render.svg.
