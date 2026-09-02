# Iteration 58 — Hypothesis

```yaml
attempt: 58
date: 2026-06-11
stage: structure
target_wave: 16
gap_targeted: >
  Wave 16 — 40 real deep_navy SAIL/FIN tiles at the outer edge
  (r 176-209u, mean area ~85.5u^2 — the SMALLEST tiles yet, vs
  w11's 135u^2), TWO mirror-pair families per STAR-TIP axis
  (wave-7's four-cycles-per-axis topology, star-tip variant):
  inner family at rel +-2.7 (r 179-195), outer family at rel
  +-6.7 (r 195-209). Baseline on the iter-57 render: 95.9%
  coverage / 25.3 iou — near-saturated regime (under-ink already
  covers most of the zone): census + clearance + eyeball carry
  acceptance. Pre-stated zoom expectation ("narrow kites") was
  FALSIFIED by the witnesses (ids 392/193): curved sail
  silhouettes with thin needle tails — the divergence became the
  model (Tenet 26). Both families fitted as free polygons via
  folded consensus (rel<0 mirrored into + frame, 20/20 stacks):
  inner 8-vert fitted IoU 0.938, outer 7-vert fitted 0.923.
  SNAP: both probed g=0.5 first (losses 0.093 / 0.018 > 0.01) and
  escalated to g=0.25 (M=1440) per the smallness driver — 4th and
  5th escalation data points; snapped 0.923 / 0.905. NOTE the
  fit-window lesson: the fold window's Y axis is TANGENTIAL
  DISTANCE IN UNITS, not degrees — the first fit run used a
  degree-sized window (Y 1-11) and produced loud garbage (0/20
  outer stack, threshold-zero consensus); fixed to Y 1-40u.
  Clearance data-proven (iterations/57/measure/
  clearance-wave16.py): 40 stamps overlap reference waves 1-15
  AND unbuilt 17-22 by ZERO px; 79.9% on-target (new low — needle
  tails have extreme perimeter/area), off-target 100% attributed
  (19.6% near-white + 0.5% w16-fragments, zero OTHER). Min model
  distances: 4.78u inner+ vs OUR w13 teardrop (ties the 4.79u
  precedent — prime face-split suspect), 4.93u outer vs OUR w14
  shield (same star-tip axes), 5.86u inner vs shield, 6.58u
  inner+ vs inner- across the axis, 7.03u inner vs outer family,
  21.5u+ to the w15 pentagrams (dart axes).
one_idea: >
  FOUR rotated free cycles in layer 1 (wave-7/14 mirror-pair
  technique on STAR-TIP axes): fifteen new blueprint rings
  C76-C90, all M=1440 (no existing radius matches — closest
  misses 191.8 vs 191.3, 188.3 vs 188.6; Tenet 5 reuse checked).
  Inner pair (8 verts, C76-C83 = radii 194.5/191.3/188.6/186.0/
  179.2/182.5/192.3/193.7): + member cpt [8 5 4 8 14 15 15 14],
  mirror cpt = 1440 - x. Outer pair (7 verts, C84-C90 = radii
  202.6/198.5/196.8/195.3/199.1/205.0/205.4): + member cpt
  [21 20 22 35 33 27 23], mirror cpt = 1440 - x. All four cycles
  under rotate 10 around C0.mpt, appended after the wave-15
  cycle. Fills navy via the layer == 1 rule (reference deep_navy
  — Stage-2 deferral, joining the backlog).
prediction: >
  Census 429 -> 484: +20 eight-sided faces (sides==8 bucket,
  gt type `unknown`/8-vert: 20 -> 40), +20 seven-sided faces
  (sides==7 bucket currently ABSENT: 0 -> 20 — a clean tell),
  +15 benign blueprint circles (circle bucket 76 -> 91) —
  PRIMARY gate. Wave-diff 16: coverage stays in the high-90s
  (near-saturated), iou moves little from 25.3 ([22, 32] band —
  tiles stamp largely INTO existing field ink). Waves 1-15 hold
  on iter-57 baselines (w1 82.2/71.1, w2 87.1/59.0, w3 93.9/76.3,
  w4 96.9/41.2, w5 98.0/53.1, w6 97.4/51.6, w7 96.0/25.1, w8
  84.2/32.9, w9 95.0/53.3, w10 94.3/25.4, w11 94.8/25.8, w12
  100.0/46.2, w13 98.6/51.8, w14 93.3/46.8, w15 100.0/24.3);
  allow <= 2 iou down on outer waves 12-15 whose crop windows
  contain wave-16 ink.
falsifier: >
  If the sides==7 bucket stays absent or rises by less than 20,
  one or both outer cycles failed to close — Tier-0 witness (one
  sail, no field) before touching the composite. If sides==8
  rises by other than 20, same for the inner pair. If any OTHER
  bucket moves, that is the face-split tell — the 4.78u w13
  teardrop gap and the 4.93/5.86u w14 shield gaps all live in the
  6-vert bucket (unknown/6-vert currently 90): diff the gt face
  inventory before attributing. If tiles render on dart axes,
  the star-tip cpt convention (cpt = rel/0.25 directly, no +72
  offset) broke. Coverage/iou are NOT acceptance signals in the
  near-saturated regime — the eyeball gate (gt-outline overlay on
  the reference at >= 2 axes, w15 protocol) is decisive.
```

## Verdict (2026-06-11): WAVE 16 PASSES — iteration 58 FROZEN

- **Census (PRIMARY gate): 429 -> 484 EXACT** — +20 seven-sided faces
  (sides==7 bucket 0 -> 20, the clean tell: bucket was absent), +20
  eight-sided faces (sides==8 bucket 20 -> 40) + 15 benign blueprint
  circles (C76-C90, 76 -> 91). Every other bucket unchanged — no
  face-split: the 4.78u w13-teardrop gap and the 4.93u/5.86u
  w14-shield gaps (all in the 6-vert bucket, held at 90) survived.
  Known benign warning only (`_girih_hexagon_star`).
- **gt placement check**: 20 fins (7-vert) at rel +-6.37..6.54 about
  the star-tip axes (plan +-6.7), uniform 248.0 px^2; 20 sails
  (8-vert, px-band r 300-350) at rel +-2.49..2.68 (plan +-2.7),
  uniform 254.8 px^2 = 83.4u^2 vs model 82.9. (First placement query
  filtered polar.r in UNITS by mistake — polar.r is RENDER PX; the
  10 faces it caught at rel +-18 were pre-existing dart-axis tiles,
  not wave-16. Divergence written down, query fixed.)
- **Wave-diff gates**: w16 97.1/25.1 (baseline 95.9/25.3 — coverage
  +1.2 as the stamps add zone ink, iou in the predicted [22,32]
  band; near-saturated regime, metric not the acceptance signal).
  Waves 1-13 + 15 hold bit-identical (w3 -0.1 cov = rounding);
  w14 iou -0.6, within the allowed <= 2 on outer waves whose crop
  windows contain wave-16 ink.
- **Eyeball gate (Tenet 26, expectation written before viewing)**:
  gt-outline overlay on the reference at axes 0 and 90
  (wave-diff/wave-16/overlay-zoom-{tip0,tip90}.png + full
  overlay-w16-on-ref.png): four red outlines per axis — two sails
  hugging the axis, two fins farther out — each riding a deep_navy
  sail/fin sliver between the white bands, mirror-symmetric about
  the axis, silhouettes tracking the curved-sail-with-needle-tail
  ink. Divergence recorded: needle tails graze the white band edges
  by ~1-2 ref px (consistent with the 19.6% near-white off-target
  attribution and snapped IoU 0.923/0.905). Shape class,
  orientation, axis placement, size confirmed.
- **Snap taxonomy data points 4+5**: both families escalated g=0.5
  -> g=0.25 (losses 0.093/0.018 > 0.01); driver = smallness
  (~83/81u^2, smallest tiles yet) — consistent with the
  angular-feature-scale discriminator.
- **Fit-window lesson codified in the script** (measure/
  fit-wave16.py header + window comment): the fold window's Y axis
  is TANGENTIAL u, not degrees — a degree-sized window produced
  loud garbage (0/20 stack, threshold-zero consensus) before the
  fix.
- **Stage-2 backlog addition**: w16 deep_navy (fills navy via the
  layer == 1 rule; reference color is deep_navy — same deferral as
  waves 3-15).

Next: wave 17 per wave-plan.json — baseline from wave-diff's SVG
raster of THIS iteration's render.svg.
