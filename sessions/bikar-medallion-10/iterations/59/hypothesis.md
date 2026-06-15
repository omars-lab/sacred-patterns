# Iteration 59 — Hypothesis

```yaml
attempt: 59
date: 2026-06-11
stage: structure
target_wave: 17
gap_targeted: >
  Wave 17 — 20 real navy HOUSE-PENTAGON tiles at the outermost band
  yet (r 187-225u, mean area ~595u^2), ONE mirror pair per DART axis
  (wave-10 topology at the outer edge): rel ~ +-4.6 about the 18 mod
  36 axes. Baseline on the iter-58 render: 100.0 coverage / 45.1 iou
  — FULLY saturated coverage (under-ink already covers the zone):
  census + clearance + eyeball carry acceptance per the w12/w15
  protocol. Pre-stated zoom expectation ("lobed/scalloped rim
  silhouette") was FALSIFIED by the witnesses (ids 149/288): large
  house/kite PENTAGONS with a short pointed tail; the noisy 8-17
  mask vertex counts are segmentation grow-back strands the
  area-matched consensus threshold washes out (Tenet 26 divergence
  became the model). Fitted as ONE free 6-vert polygon via folded
  consensus (rel<0 mirrored into + frame, 20/20 stack, consensus
  588.4u^2 vs target 594.8; closing probes 1.7/1.8% = concavities
  real): fitted IoU 0.972 — best fit of any wave. SNAP: probed
  g=0.5 first (loss 0.017 > 0.01) -> escalated to g=0.25 (M=1440)
  — 6th escalation data point with a NEW driver: not smallness
  (595u^2 is large) but NEAR-AXIS VERTEX PRECISION — the rel-0.66
  nose vertex needs the fine grid. Snapped IoU 0.962.
  Clearance data-proven (iterations/58/measure/clearance-wave17.py):
  20 stamps overlap reference waves 1-16 AND unbuilt 18-22 by ZERO
  px; 91.7% on-target (best yet — large convex tile), off-target
  100% attributed (8.3% near-white, zero fragments, zero OTHER).
  Min model distances: 5.08u vs OUR w14 shield (axis-0/36
  star-tip neighbors), 5.21u vs OUR w16 outer fin (same), 5.36u
  vs OUR w15 pentagram (SAME dart axis, apex r 194.3), 5.37u
  pent+ vs pent- across the dart line, 21.25u vs w16 inner,
  23.09u vs w12 bell — all above the 4.78u survival precedent.
one_idea: >
  TWO rotated free cycles in layer 1 (wave-10/15 mirror-pair
  technique on DART axes): five new blueprint rings C91-C95, all
  M=1440 (Tenet 5 reuse checked: r=205.0 reuses EXISTING C89; the
  other five radii 192.9/193.1/208.0/218.0/217.6 have no matches —
  closest misses 192.3, 193.7). DART-axis cpt convention bakes in
  the +18-deg offset (cpt = (18+rel)/0.25, mirror = (18-rel)/0.25;
  wave-15 precedent): + member cycle
  [C89.cpt75 C91.cpt80 C92.cpt96 C93.cpt112 C94.cpt93 C95.cpt80],
  mirror cycle
  [C89.cpt69 C91.cpt64 C92.cpt48 C93.cpt32 C94.cpt51 C95.cpt64].
  Both under rotate 10 around C0.mpt, appended after the wave-16
  cycles. Fills navy via the layer == 1 rule (reference color IS
  navy this time — still recorded in the Stage-2 backlog for the
  final color pass).
prediction: >
  Census 484 -> 509: +20 six-sided faces (unknown/6-vert bucket
  90 -> 110) + 5 benign blueprint circles (circle bucket 91 -> 96)
  — PRIMARY gate. Note the 6-vert bucket is ALSO where the w13
  teardrop (4.78u gap) and w14 shields (4.93/5.86u gaps) live: an
  exact +20 simultaneously proves the new tiles closed AND the old
  tight gaps survived. Wave-diff 17: coverage stays 100.0
  (saturated), iou moves little from 45.1 ([42, 55] band — tiles
  stamp INTO existing field ink). Waves 1-16 hold on iter-58
  baselines (w1 82.2/71.1, w2 87.1/59.0, w3 93.8/76.3, w4
  96.9/41.2, w5 98.0/53.1, w6 97.4/51.6, w7 96.0/25.1, w8
  84.2/32.9, w9 95.0/53.3, w10 94.3/25.4, w11 94.8/25.8, w12
  100.0/46.2, w13 98.6/51.8, w14 93.3/46.2, w15 100.0/24.3, w16
  97.1/25.1); allow <= 2 iou down on outer waves 12-16 whose crop
  windows contain wave-17 ink.
falsifier: >
  If the 6-vert bucket rises by other than 20, either a cycle
  failed to close (rise < 20) or a face-split fired (rise > 20, or
  any OTHER bucket moves) — diff the gt face inventory per shape
  before attributing; the 5.08u w14-shield and 5.21u w16-fin gaps
  are the prime suspects. If tiles render on STAR-TIP axes, the
  dart cpt convention (+18-deg baked into cpt = (18+rel)/g) broke
  — Tier-0 witness (one pentagon, no field) before touching the
  composite. Coverage/iou are NOT acceptance signals in the
  saturated regime — the eyeball gate (gt-outline overlay on the
  reference at >= 2 dart axes, w15 protocol) is decisive.
```

## Verdict (2026-06-11): WAVE 17 PASSES — iteration 59 FROZEN

- **Census (PRIMARY gate): 484 -> 509 EXACT** — +20 six-sided faces
  (unknown/6-vert bucket 90 -> 110) + 5 benign blueprint circles
  (C91-C95, 91 -> 96). Every other bucket unchanged — no face-split:
  the 5.08u w14-shield, 5.21u w16-fin, and 5.36u w15-pentagram gaps
  all survived, and the exact +20 in the 6-vert bucket simultaneously
  proves both cycles closed AND the old 6-vert residents (w13
  teardrops, w14 shields) were untouched. Known benign warning only
  (`_girih_hexagon_star`).
- **gt placement check**: exactly 20 new 6-vert faces in the px band
  330-390 (0 in iter-58's), at rel +-4.26..4.42 about the DART axes
  (fit centroid ~4.3), uniform 1774.8 px^2 = 580.8u^2 vs model
  shoelace 577.3. Ring reuse confirmed: r=205.0 via existing C89.
- **Wave-diff gates**: ALL 17 waves bit-identical to the iter-58
  baselines (max delta 0.0/0.0) — w17 stays 100.0/45.1: the tiles
  stamped INTO existing field ink exactly as predicted (saturated
  regime; census + clearance + eyeball carried acceptance).
- **Eyeball gate (Tenet 26, expectation written before viewing)**:
  gt-outline overlay on the reference at dart axes 18 and 90
  (wave-diff/wave-17/overlay-zoom-{dart18,dart90}.png + full
  overlay-w17-on-ref.png): two red house-pentagon outlines per axis,
  mirror-symmetric about the dart line, each riding a large navy
  house-pentagon tile in the outermost band, nose toward the axis,
  roof out at ~r218 — silhouettes tracked tightly. Divergence
  recorded: edges graze the white band borders ~1-3 px in places
  (dart-18 lower member pokes slightly past the tile's right
  corner), consistent with snapped 0.962 + the 8.3% near-white
  attribution. Shape class, orientation, axis placement, size,
  mirror symmetry confirmed.
- **Snap taxonomy data point 6 (NEW driver)**: escalated g=0.5 ->
  g=0.25 with loss 0.017 > 0.01 on a LARGE tile (595u^2) — driver is
  near-axis vertex precision (the rel-0.75 nose), not smallness;
  the discriminator is angular feature scale, now witnessed from
  both ends of the area range.
- **Stage-2 note**: reference color IS navy — the layer == 1 rule
  already paints wave-17 correctly; listed in the backlog only for
  the final color-pass audit.

Next: wave 18 per wave-plan.json — baseline from wave-diff's SVG
raster of THIS iteration's render.svg.
