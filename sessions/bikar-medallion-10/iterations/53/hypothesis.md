# Iteration 53 — Hypothesis

```yaml
attempt: 53
date: 2026-06-11
stage: structure
target_wave: 11
gap_targeted: >
  Wave 11 — 20 real deep-navy 4-pronged spiky tiles ("birds") in
  the middle ring, TWO per 36-deg repeat in MIRROR PAIRS
  straddling the STAR-TIP axes (0 mod 36) at rel ~ +-7.9 deg,
  mean area ~135u^2, radial span ~142-164u — baseline 92.5%
  coverage / 26.9 iou on the iter-52 render. NOTE the baseline
  coverage is already near-saturated by the layer-0 girih field
  underlay (unlike waves 2-10 whose baselines were 30-50), so
  the wave-diff numbers have WEAK discrimination this wave; the
  load-bearing acceptance signals are the census, the eyeball
  gate, and the data-proven clearance. Pre-stated zoom
  expectation ("small kite/dart") was FALSIFIED by the look (ids
  59/60): the tile is a 4-pronged spiky star, and the pair
  members are mirror images — pair topology confirmed. Closing
  probe filled only 5% (133.2->139.9u^2 at 3u) — concavities are
  real boundary; modeled the raw consensus. Seeds from
  approxPolyDP at eps 2.5-5.0 refined by IoU coordinate descent,
  DOF-penalized pick (IoU - 0.004n) chose 6 verts: fitted 0.928.
  SNAP FINDING: the usual g=0.5 (M=720) snap cost 0.045 IoU on
  this small spiky tile (0.883); g=0.25 (M=1440) keeps 0.921 —
  probed both before accepting, area 135.5u^2 vs consensus 133.2
  (iterations/52/measure/wave11-fit.json). Clearance data-proven
  (iterations/52/measure/clearance-wave11.py): 20 snapped stamps
  overlap reference waves 1-10 AND unbuilt 12-22 by ZERO px;
  78.4% on-target, off-target fully attributed (20.6% near-white
  band px + 1.0% wave-11 fragments + 0.0% other). Model-vs-model
  gaps: >= 4.98u to OUR wave-9 16-gon (shares the star-tip
  axes), >= 6.85u to OUR wave-10 teardrop — no face-split risk.
one_idea: >
  TWO rotated 6-point cycles in layer 1, wave-7/10 mirror-pair
  technique on SHARED circles: six new blueprint rings C50-C55
  (radii 148.4/145.9/157.6/156.0/161.0/152.9, all M=1440 — first
  use of the 0.25-deg grid, forced by the snap finding above)
  and the pair of cycles under rotate 10 around C0.mpt:
  [C50.cpt15 C51.cpt37 C52.cpt45 C53.cpt33 C54.cpt27 C55.cpt25]
  (+ member) and
  [C50.cpt1425 C51.cpt1403 C52.cpt1395 C53.cpt1407 C54.cpt1413
  C55.cpt1415] (mirror member). Fills navy via the existing
  layer==1 rule (reference color deep_navy — Stage-2 deferral
  like waves 3-10).
prediction: >
  Census 333 -> 359: +20 layer-1 six-sided faces (sides==6
  bucket 50 -> 70) + 6 benign blueprint circles (C50-C55) — this
  is the PRIMARY gate this wave. Wave-diff: coverage >= 93 (from
  92.5; weak signal, saturated baseline) and iou in [26, 33]
  (from 26.9; the tiles add ~2900 render-px of intersection in a
  window whose union is field-dominated). Waves 1-10 hold on the
  iter-52 baselines (w1 82.2/71.1, w2 87.1/59.0, w3 93.9/76.3,
  w4 96.9/41.2, w5 98.0/53.1, w6 97.4/51.6, w7 96.0/25.1, w8
  84.2/32.9, w9 95.0/54.3, w10 94.4/25.4); allow <= 2 iou down
  on middle-ring waves 7-10, and w9 may dip via the window-union
  artifact (wave-8 precedent at iter-52) since wave-11 ink lands
  inside its crop — if w9 dips beyond 2, attribute via the
  iter-52 falsifier path before accepting.
falsifier: >
  If the census six-sided count rises by less than 20, a cycle
  failed to close — Tier-0 witness (one pair, no field) before
  touching the composite. If the tiles render on dart axes or at
  the wrong ring, the star-tip axis read is wrong — re-measure,
  don't nudge. If coverage DROPS below 92.5 or iou below 24, the
  new ink is landing off the wave-11 mask — re-check the M=1440
  cpt arithmetic (first use; an off-by-one in cpt indexing shows
  up as a ~0.25-deg rotation of every tile). If waves 1-10
  regress beyond the allowance, diff the gt census first
  (face-split signal, not paint) — the 4.98u/6.85u gaps say
  face-splits should NOT happen; a split here falsifies the
  min-distance check, not the wave model.
```

## Verdict (2026-06-11): WAVE 11 PASSES — iteration 53 FROZEN

- **Census (PRIMARY gate): 333 -> 359 EXACT** — +20 six-sided faces
  (`params.sides == 6` bucket 50 -> 70) + 6 benign blueprint circles
  (C50-C55, circle bucket 50 -> 56). No face-splits: the 4.98u/6.85u
  min-distance proofs held. Known benign warning only
  (`_girih_hexagon_star` leaves no gt trace — present since iter-33).
- **Wave-diff 11: coverage 94.8 (>= 93 ✓, from 92.5), iou 27.0
  (in [26, 33] ✓, from 26.9)** — weak-signal wave as predicted
  (saturated baseline); census + eyeball + clearance carried
  acceptance.
- **Holds**: w1 82.2/71.1, w2 87.1/59.0, w3 93.9/76.3, w4 96.9/41.2,
  w5 98.0/53.1, w6 97.4/51.6, w7 96.0/25.1, w8 84.2/32.9, w10
  94.4/25.4 — all bit-identical. w9 95.0/53.5 (iou -0.8, within the
  <= 2 allowance; wave-11 ink lands in its crop window as predicted —
  no attribution probe needed, dip inside allowance).
- **Eyeball gate (Tenet 26, expectation written before viewing)**:
  zoom-east + zoom-ne72 (axes 0/72 deg, r 153u, crops saved in
  wave-diff/wave-11/) — mirror-pair 4-pronged navy birds straddle
  each star-tip axis matching the reference pair topology and prong
  orientation; render ink sits inside the reference outline
  (snapped-model 0.921 territory); clear of the wave-9 16-gon and
  wave-10 teardrops. Matches the pre-stated expectation.
- **M=1440 first use validated**: no off-by-one rotation artifact
  (the falsifier's ~0.25-deg tell is absent — render ink centered in
  the reference outlines).
- **Stage-2 backlog addition**: w11 deep_navy (tiles currently fill
  navy via the layer == 1 rule; reference color is deep_navy —
  same deferral as waves 3-10).

Next: wave 12 per wave-plan.json — baseline from wave-diff's SVG
raster of THIS iteration's render.svg.
