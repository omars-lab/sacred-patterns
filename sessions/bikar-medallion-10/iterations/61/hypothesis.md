# Iteration 61 — Hypothesis

```yaml
attempt: 61
date: 2026-06-11
stage: structure
target_wave: 19
gap_targeted: >
  Wave 19 — 20 real small deep_navy TEARDROP-KITE tiles in the
  outer band (r 209-226u, mean area ~84u^2 — w15/w16 smallness
  class), ONE mirror pair per STAR-TIP axis (0 mod 36; wave-16
  off-axis topology): rel ~ +-7.6. Baseline on the iter-60 render:
  99.7 coverage / 20.7 iou — coverage saturated again: census +
  clearance + eyeball carry acceptance per the w12/w15/w17
  protocol. Pre-stated zoom expectation ("small compact convex
  4-6 sided wedge/diamond, radially elongated") was PARTIALLY
  falsified by the witnesses (ids 102/111): the tile is a
  TEARDROP elongated TANGENTIALLY — apex at rel ~9.8 pointing
  away from the axis, rounded base at rel ~6 (Tenet 26 divergence
  became the model; raw 5-8 mask vertex counts are grow-back
  strands). Fitted as ONE free 7-vert polygon via folded
  consensus (rel<0 mirrored into + frame, 20/20 stack, consensus
  82.1u^2 vs target 83.8; closing probes 5.6/6.1% — highest yet,
  consistent with a small tile's ragged raster boundary): fitted
  IoU 0.924, snapped 0.908 at g=0.25 — 8th escalation data point
  (driver: smallness, w15/w16 class; snapped IoU in-family with
  w15 0.910 / w16 outer 0.905). Fit overlay viewed: red boundary
  tracks the gray teardrop consensus tightly (divergence from
  expectation recorded above).
  Clearance data-proven (iterations/60/measure/clearance-wave19.py):
  20 stamps overlap reference waves 1-18 AND unbuilt 20-22 by ZERO
  px; 79.6% on-target, off-target 100% attributed (19.2%
  near-white + 1.2% w19-fragments + 0 OTHER — small tiles carry
  proportionally more band-boundary px). Min model distances:
  5.34u vs OUR w17 pentagon (dart-18 mirror member), 5.52u vs OUR
  w18 star (same axis), 7.16u vs w16 outer fin, 22.18u vs w16
  inner, 45.49u kite+ vs kite- — all above the 4.21u survival
  precedent set by wave 18.
one_idea: >
  TWO rotated free cycles in layer 1 (wave-16 mirror-pair
  technique on STAR-TIP axes): six new blueprint rings C107-C112,
  all M=1440 (Tenet 5 reuse checked: r=217.6 reuses EXISTING C95;
  the other six radii 214.1/212.1/217.8/220.1/221.1/221.2 have no
  matches — closest misses 216.3, 218.0). STAR-TIP cpt convention
  (cpt = rel/0.25, mirror = 1440 - cpt; wave-16 precedent):
  + member cycle
  [C95.cpt24 C107.cpt25 C108.cpt28 C109.cpt39 C110.cpt36
   C111.cpt28 C112.cpt26],
  mirror cycle
  [C95.cpt1416 C107.cpt1415 C108.cpt1412 C109.cpt1401 C110.cpt1404
   C111.cpt1412 C112.cpt1414].
  Both under rotate 10 around C0.mpt, appended after the wave-18
  cycle. Reference color is DEEP_NAVY; the layer == 1 rule fills
  navy — recorded in the Stage-2 color backlog (wave-19 entry).
prediction: >
  Census 530 -> 556: +20 seven-sided faces (unknown/7-vert bucket
  20 -> 40) + 6 benign blueprint circles (circle bucket 107 -> 113)
  — PRIMARY gate. Note the 7-vert bucket currently holds the w16
  outer fins (7.16u gap) — an exact +20 simultaneously proves the
  new cycles closed AND the fins survived. Wave-diff 19: coverage
  stays ~99.7 (saturated), iou moves little from 20.7 ([18, 35]
  band — tiles stamp INTO existing field ink). Waves 1-18 hold on
  iter-60 baselines (w1 82.2/71.1, w2 87.1/59.0, w3 93.8/76.3, w4
  96.9/41.2, w5 98.0/53.1, w6 97.4/51.6, w7 96.0/25.1, w8
  84.2/32.9, w9 95.0/53.3, w10 94.3/25.4, w11 94.8/25.8, w12
  100.0/46.2, w13 98.6/51.8, w14 93.3/46.2, w15 100.0/24.3, w16
  97.1/24.3, w17 100.0/45.1, w18 94.3/57.1); allow <= 2 iou down
  on outer waves whose crop windows contain wave-19 ink.
falsifier: >
  If the 7-vert bucket rises by other than 20, either a cycle
  failed to close (rise < 20) or a face-split fired (rise > 20, or
  any OTHER bucket moves) — the 5.34u w17-pentagon and 5.52u
  w18-star gaps are the prime suspects (their buckets: 6-vert 110,
  20-vert 12 — watch both). If tiles render on DART axes or at
  wrong rel sign, the star-tip cpt convention broke — Tier-0
  witness (one kite, no field) before touching the composite.
  Coverage/iou are NOT acceptance signals in the saturated regime
  — the eyeball gate (gt-outline overlay on the reference at >= 2
  star-tip axes) is decisive.
```

## Verdict (2026-06-11): WAVE 19 PASSES — iteration 61 FROZEN

- **Census (PRIMARY gate): 530 -> 556 EXACT** — +20 seven-sided faces
  (unknown/7-vert bucket 20 -> 40) + 6 benign blueprint circles
  (C107-C112, 107 -> 113). Every other bucket unchanged — NO
  face-split: the 5.34u w17-pentagon gap (6-vert bucket held at 110),
  the 5.52u w18-star gap (20-vert held at 12), and the 7.16u
  w16-outer-fin gap all SURVIVED; the exact +20 in the fins' own
  bucket simultaneously proves the new cycles closed AND the fins
  survived, as the prediction framed it. Survival precedent stays
  4.21u (no tighter gap this wave). Known benign warning only
  (`_girih_hexagon_star`).
- **gt placement check**: exactly 20 new 7-vert faces, mirror pairs
  flanking every star-tip axis (centroid rel -8.47..-6.25 / +6.26..
  +8.45 deg), centroid r 214.1-222.5u, uniform 243.8 px^2 = 79.8u^2
  vs model shoelace ~80 — clean uniform stamping at all 10 axes.
- **Wave-diff gates**: waves 1-18 hold bit-identical to the iter-60
  baselines (no <= 2 iou allowance consumed anywhere). w19 stays
  99.7/20.7 — coverage saturated as pre-stated; iou inside the
  predicted [18, 35] band (the kites stamp INTO existing field ink,
  so the binary ink mask is unchanged). Coverage/iou were declared
  non-acceptance signals for this wave; census + clearance + eyeball
  carried it.
- **Eyeball gate (Tenet 26, expectation written before viewing)**:
  gt-outline overlay on the reference at star-tip axes 0 and 72
  (wave-diff/wave-19/overlay-zoom-{axis0,axis72}.png + full
  overlay-w19-on-ref.png, filtered to the 20 new kites by centroid
  r > 211u to exclude the 7-vert w16 fins): one red teardrop outline
  per SIDE of the star-tip line, mirror pair, riding the small
  deep_navy slivers that flank the w18 rosette, apex pointing
  tangentially away from the axis exactly as the falsified-then-
  corrected model says. Divergence recorded: the same ~2-3 px
  translation-like registration offset seen at w18 (red overruns the
  white band on the same screen side at both axes) — registration-
  frame artifact, not a convention error (gt placement check above
  is in the render frame and is exact).
- **Snap taxonomy data point 8**: smallness driver (84u^2, w15/w16
  class), snapped 0.908 at g=0.25 — in-family with w15 0.910 / w16
  outer 0.905; the smallness end of the discriminator now has four
  witnesses.
- **Stage-2 note**: reference color is DEEP_NAVY; the layer == 1
  rule fills navy — wave-19 added to the Stage-2 color backlog.

Next: wave 20 per wave-plan.json — baseline from wave-diff's SVG
raster of THIS iteration's render.svg. The routing-doc entry for the
17/18/19 batch is due NOW (per the iter-60 verdict's closing line).
