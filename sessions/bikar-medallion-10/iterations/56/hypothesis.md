# Iteration 56 — Hypothesis

```yaml
attempt: 56
date: 2026-06-11
stage: structure
target_wave: 14
gap_targeted: >
  Wave 14 — 20 real royal shield tiles at the outer edge, one MIRROR
  PAIR per 36-deg star-tip axis at rel ~ +-9.5 (wave-7/10/11 pair
  topology), r 159.6-195.0u, mean area ~587.3u^2 — baseline 55.5%
  coverage / 28.1 iou on the iter-55 render (normal regime, real
  wave-diff signal). Pre-stated zoom expectation (mirror-image
  shield tiles canted opposite ways) CONFIRMED by both witnesses
  (ids 32 rel +9.6 / 37 rel -9.5). Folded consensus (all 20 members
  mapped to the + frame, rel<0 mirrored): max stack 20/20, 563.3u^2.
  Closing probe filled only 2.3%/2.4% at 3u/4u — concavities real
  but shallow, modeled the raw consensus. DOF-penalized pick (IoU -
  0.004n over eps seeds 2.0-6.0) chose the 6-vert free model: fitted
  0.967. SNAP: g=0.5 (M=720) cost 0.0097 <= 0.01 — NO escalation,
  consistent with the refined taxonomy (this tile spans ~9 deg of
  arc at r~177; the discriminator is angular feature scale, and
  these features are wide). Snapped 0.957. Clearance data-proven
  (iterations/55/measure/clearance-wave14.py): 20 stamps (pair per
  axis) overlap reference waves 1-13 AND unbuilt 15-22 by ZERO px;
  93.9% on-target, off-target 100% attributed (6.1% near-white band,
  zero fragments, zero OTHER). Model-vs-model min distances: 4.79u
  to OUR wave-13 teardrop (same axis — NEW TIGHTEST, just under the
  4.98u precedent that held; ~6px, far above bikar's merge epsilon),
  5.18u to each OUR wave-11 bird, 35.6u across the axis to own
  mirror, 22.0u to the next-axis pair, 21.5u to the w9 16-gon.
one_idea: >
  TWO rotated 6-vert cycles in layer 1 (wave-11 mirror-pair
  technique on star-tip axes): five new blueprint rings C65-C69
  (radii 162.2/170.3/180.2/188.3/191.8, all M=720 per the snap
  finding) PLUS REUSE of existing C63 (r 168.5, M=1440, from wave
  13) for the 168.5 vertex — Tenet 5: the radius already exists;
  rel 13.0 deg is exactly cpt52 on its 0.25-deg grid. + member
  cycle walks outer-apex -> inner flank -> base dip -> far base ->
  far shoulder -> outer shoulder:
  [C69.cpt11 C66.cpt12 C65.cpt18 C63.cpt52 C67.cpt29 C68.cpt23];
  mirror cycle reflects every angle about the axis:
  [C69.cpt709 C66.cpt708 C65.cpt702 C63.cpt1388 C67.cpt691
  C68.cpt697]. Fills navy via the existing layer == 1 rule
  (reference color royal — Stage-2 deferral like waves 3-13).
prediction: >
  Census 388 -> 413: +20 layer-1 six-sided faces (sides==6 bucket
  80 -> 100) + 5 benign blueprint circles (circle bucket 65 -> 70;
  C63 reused, NOT re-added) — PRIMARY gate. Wave-diff 14: coverage
  rises from 55.5 into [90, 99] (stamps cover 93.9% of the
  reference wave mask and the uncovered remainder is render-white
  today) and iou rises from 28.1 into [45, 65]. Waves 1-13 hold on
  the iter-55 baselines (w1 82.2/71.1, w2 87.1/59.0, w3 93.9/76.3,
  w4 96.9/41.2, w5 98.0/53.1, w6 97.4/51.6, w7 96.0/25.1, w8
  84.2/32.9, w9 95.0/53.3, w10 94.3/25.4, w11 94.8/26.1, w12
  100.0/46.2, w13 98.6/52.4); allow <= 2 iou down on outer waves
  9-13 whose crop windows contain wave-14 ink — if any dips beyond
  2, attribute via the falsifier path before accepting.
falsifier: >
  If the census sides==6 count rises by less than 20, a cycle
  failed to close — Tier-0 witness (one shield, no field) before
  touching the composite. If the count rises by MORE than 20 or any
  other bucket moves, that is the face-split tell — the 4.79u w13
  gap is the prime suspect (a split w13 teardrop perturbs the SAME
  sides==6 bucket, so diff the gt face inventory by layer/centroid,
  not bucket totals alone, before attributing). If tiles render
  mirrored onto dart axes or only 10 appear, the mirror-cycle cpt
  arithmetic is wrong (km = -x mod M; an error shows as missing or
  axis-reflected tiles). If coverage stays ~55 (no rise), re-examine
  the fill-rule path with before/after crops (wave-12 protocol)
  before accepting. If coverage rises but iou DROPS below 27, the
  ink is landing off the wave-14 mask — re-check the mixed-M cpt
  indexing (C63 is M=1440 while C65-C69 are M=720; an off-by-one
  on C63 shows as a 0.25-deg shear of one vertex only).
```

## Verdict (2026-06-11): WAVE 14 PASSES — iteration 56 FROZEN

- **Census (PRIMARY gate): 388 -> 413 EXACT** — +20 six-sided faces
  (sides==6 bucket 80 -> 100) + 5 benign blueprint circles (C65-C69,
  65 -> 70; C63 reused per Tenet 5, not re-added). Every other
  bucket unchanged — no face-split: the 4.79u w13 gap (new tightest)
  held. Known benign warning only (`_girih_hexagon_star`).
- **Wave-diff 14: coverage 93.3 (in [90, 99] ✓, from 55.5), iou
  46.8 (in [45, 65] ✓, from 28.1)** — normal-regime signal, both
  bands hit.
- **Holds**: w1-w10, w12 bit-identical; w11 94.8/25.8 (iou -0.3)
  and w13 98.6/51.8 (iou -0.6, wave-14 ink in its crop window as
  predicted) — both within the <= 2 allowance.
- **Eyeball gate (Tenet 26, expectation written before viewing)**:
  zoom-east0 + zoom-ne72 (star-tip axes 0/72 deg, r 177u, crops in
  wave-diff/wave-14/) — at both axes the render's two navy shields
  fill the reference wave-mask outlines in the mirrored
  opposite-cant arrangement, w13 teardrop on-axis between them, no
  merged/absorbed faces. Matches the pre-stated expectation (shape
  compared, not color — see deferral below).
- **Snap taxonomy data point**: g=0.5 HELD (loss 0.0097) on a wide
  (~9 deg) tile — consistent with the angular-feature-scale
  discriminator; first M=720 wave since the w13 refinement.
- **Circle-reuse precedent**: C63 (w13's M=1440 flank ring) carries
  a w14 vertex at cpt52/cpt1388 — first cross-wave blueprint-ring
  reuse; divide-circles are point sources only (no arcs drawn), so
  no enrollment interaction, confirmed by the census.
- **Stage-2 backlog addition**: w14 royal (tiles fill navy via the
  layer == 1 rule; reference color is royal — same deferral as
  waves 3-13).

Next: wave 15 per wave-plan.json — baseline from wave-diff's SVG
raster of THIS iteration's render.svg.
