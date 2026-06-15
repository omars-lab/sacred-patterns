# Iteration 60 — Hypothesis

```yaml
attempt: 60
date: 2026-06-11
stage: structure
target_wave: 18
gap_targeted: >
  Wave 18 — 10 real royal TEN-POINTED STAR medallions at the
  outermost band yet (r 192-239u, mean area ~992u^2), ONE
  axis-symmetric tile per STAR-TIP axis (0 mod 36; wave-13 on-axis
  topology — plan rel -0.3..+0.4). Baseline on the iter-59 render:
  58.1 coverage / 36.2 iou — NOT saturated: for the first time
  since wave 11, coverage/iou are LIVE acceptance signals alongside
  census + clearance + eyeball. Pre-stated zoom expectation
  ("elongated arrowhead/spearhead with concave flank notches") was
  FALSIFIED by the witnesses (ids 16/399): clean 10-pointed star
  medallions — rosette-center royal stars; the 28-34 raw mask
  vertex counts are rounded raster corners, not extra structure
  (Tenet 26 divergence became the model). Fitted as an 11-row /
  20-vert axis-symmetric polygon via the fit-wave13 machinery
  (symmetrized 20/20 stack, consensus 967.1u^2 vs target 991.8;
  closing probes 2.4/3.3% = concavities real): fitted IoU 0.969.
  SNAP: probed g=0.5 first (loss 0.017 > 0.01) -> escalated to
  g=0.25 (M=1440) — 7th escalation data point; driver is on-axis
  points + near-axis valleys (angular feature scale), same class
  as w17. Snapped IoU 0.962. Fit overlay viewed and matched the
  pre-stated expectation (red 20-vert boundary tracks the gray
  10-point consensus tightly).
  Clearance data-proven (iterations/59/measure/clearance-wave18.py):
  10 stamps overlap reference waves 1-17 AND unbuilt 19-22 by ZERO
  px; 92.9% on-target (best yet), off-target 100% attributed (7.1%
  near-white, zero fragments, zero OTHER). Min model distances:
  4.21u vs OUR w16 outer fin (same star-tip axes — BELOW the 4.78u
  survival precedent, tightest gap ever: PRIME face-split suspect),
  5.41u vs w16 inner, 9.80u vs w13 teardrop (same axis, on-axis
  radial neighbor: their apex 185.1 vs our inner point 194.9),
  10.08u vs w17 pentagons (dart axes), 10.29u vs w14 shields.
one_idea: >
  ONE rotated free cycle in layer 1 (wave-13 axis-symmetric
  technique on STAR-TIP axes): eleven new blueprint rings C96-C106
  (Tenet 5 reuse checked: NO existing radius matches any of
  194.9/200.2/199.5/207.0/209.2/216.3/222.6/224.6/232.2/229.9/235.0
  — closest misses 194.5 vs 194.9, 199.1 vs 199.5/200.2, 205.0 and
  208.0 vs 207.0, 217.6 vs 216.3). On-axis rows (inner point C96
  r=194.9, outer point C106 r=235.0) on M=20 per the w13/w15 rule
  (cpt0 exact 0 deg); the nine pair rows on M=1440 (g=0.25). Cycle
  walks the expand() order — on-axis inner, + side base->apex,
  on-axis outer, - side reversed:
  [C96.cpt0 C97.cpt5 C98.cpt14 C99.cpt14 C100.cpt21 C101.cpt17
   C102.cpt20 C103.cpt13 C104.cpt12 C105.cpt6 C106.cpt0
   C105.cpt1434 C104.cpt1428 C103.cpt1427 C102.cpt1420 C101.cpt1423
   C100.cpt1419 C99.cpt1426 C98.cpt1426 C97.cpt1435]
  under rotate 10 around C0.mpt, appended after the wave-17 cycles.
  Reference color is ROYAL; the layer == 1 rule fills navy —
  recorded in the Stage-2 color backlog (wave-18 entry).
prediction: >
  Census 509 -> 530: +10 twenty-sided faces (unknown/20-vert bucket
  2 -> 12 — a clean near-empty-bucket tell) + 11 benign blueprint
  circles (circle bucket 96 -> 107) — PRIMARY gate. Wave-diff 18
  RISES from 58.1/36.2 on BOTH numbers (not saturated; the 10 stars
  are ~37% of the wave-18 zone area). Waves 1-17 hold bit-identical
  on the iter-59 baselines (w1 82.2/71.1, w2 87.1/59.0, w3
  93.8/76.3, w4 96.9/41.2, w5 98.0/53.1, w6 97.4/51.6, w7
  96.0/25.1, w8 84.2/32.9, w9 95.0/53.3, w10 94.3/25.4, w11
  94.8/25.8, w12 100.0/46.2, w13 98.6/51.8, w14 93.3/46.2, w15
  100.0/24.3, w16 97.1/25.1, w17 100.0/45.1); allow <= 2 iou down
  on outer waves whose crop windows contain wave-18 ink.
falsifier: >
  If the 20-vert bucket rises by other than 10, either the cycle
  failed to close (rise < 10) or a face-split fired (rise > 10, or
  any OTHER bucket moves) — the 4.21u w16-outer-fin gap is the
  prime suspect (their buckets: unknown/7-vert 20, unknown/8-vert
  40 — watch both), w16 inner (5.41u) second. If tiles render on
  DART axes, the star-tip cpt convention broke — Tier-0 witness
  (one star, no field) before touching the composite. If w18
  coverage/iou do NOT rise, the stamps missed the zone — check the
  registration block before blaming the model.
```

## Verdict (2026-06-11): WAVE 18 PASSES — iteration 60 FROZEN

- **Census (PRIMARY gate): 509 -> 530 EXACT** — +10 twenty-sided faces
  (unknown/20-vert bucket 2 -> 12, the clean near-empty-bucket tell) +
  11 benign blueprint circles (C96-C106, 96 -> 107). Every other
  bucket unchanged — NO face-split: the 4.21u w16-outer-fin gap
  (below the 4.78u survival precedent — flagged as prime suspect)
  SURVIVED; the w16 buckets (7-vert 20, 8-vert 40) untouched. New
  survival precedent: 4.21u. Known benign warning only
  (`_girih_hexagon_star`).
- **gt placement check**: exactly 10 new 20-vert faces in the px band
  330-420 (iter-59 had only the 2 unrelated near-center 20v faces at
  r 0.5), ON the star-tip axes (rel -0.08..+0.08 deg), uniform
  3024.7 px^2 = 990.0u^2 vs model shoelace 983.8.
- **Wave-diff gates**: waves 1-15 + 17 bit-identical to the iter-59
  baselines. w16 iou 25.1 -> 24.3 (-0.8, within the pre-stated <= 2
  allowance — its crop window contains the new wave-18 ink at 4.21u;
  coverage unchanged 97.1). **w18: 58.1/36.2 -> 94.3/57.1** — first
  live (non-saturated) coverage/iou acceptance since wave 11, both
  numbers rose strongly as predicted.
- **Eyeball gate (Tenet 26, expectation written before viewing)**:
  gt-outline overlay on the reference at star-tip axes 0 and 72
  (wave-diff/wave-18/overlay-zoom-{axis0,axis72}.png + full
  overlay-w18-on-ref.png): one red 20-vert ten-pointed-star outline
  per axis riding the royal star-medallion tile at the rosette
  center, 10 points sharp, mirror-symmetric about the star-tip
  line, silhouette tracked. Divergence recorded: a uniform ~2-3 px
  translation-like offset (red overruns the white bands upper-right,
  royal under-covered lower-left, SAME screen direction at both
  axes) — consistent with a small wave-diff registration-center
  mismatch plus snapped 0.962, NOT a rotation/convention error (the
  clearance proof in the plan-center frame showed 92.9% on-target,
  and the zoom centroids sat 1.18/1.41 deg off-axis only in the
  registration frame while gt thetas are rel <= 0.08).
- **Snap taxonomy data point 7**: g=0.5 loss 0.017 > 0.01 on a LARGE
  tile (992u^2) -> g=0.25; driver = on-axis points + near-axis
  valleys — second witness for the angular-feature-scale
  discriminator at the large end of the area range.
- **Stage-2 note**: reference color is ROYAL; the layer == 1 rule
  fills navy — wave-18 added to the Stage-2 color backlog (with the
  w15 navy-on-navy priority witness still first).

Next: wave 19 per wave-plan.json — baseline from wave-diff's SVG
raster of THIS iteration's render.svg. Routing-doc entry for the
17/18/19 batch comes due when wave 19 closes.
