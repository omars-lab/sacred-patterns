# Iteration 54 — Hypothesis

```yaml
attempt: 54
date: 2026-06-11
stage: structure
target_wave: 12
gap_targeted: >
  Wave 12 — 10 real navy bell-shaped tiles in the middle ring, ONE
  per 36-deg repeat ON the dart axes (18 mod 36, rel jitter +-0.5 =
  registration noise), mean area ~644u^2 (5x the wave-11 bird),
  radial span ~138-173u — baseline 100.0% coverage / 46.2 iou on
  the iter-53 render. The baseline coverage is FULLY saturated by
  the field underlay, so wave-diff coverage has ZERO discrimination
  this wave and iou only weak; the load-bearing acceptance signals
  are the census, the eyeball gate, and the data-proven clearance.
  Pre-stated zoom expectation ("spiky crown") was PARTIALLY
  falsified by the look (ids 53/72): the tile is a smooth
  near-triangular BELL — apex outward on the axis (r ~170), flat
  slightly-notched base (r ~142-145), gently serrated flanks.
  Closing probe filled only 2.2% (618.5->632.2u^2 at 3u) — the
  serration and base nub are real but shallow; the 8-vert model
  cuts straight chords through them at IoU 0.961. Consensus was
  SYMMETRIZED by construction (each witness stacked with its
  mirror; max stack 20/20). DOF-penalized pick (IoU - 0.004n over
  symmetric eps seeds 2.0-6.0) chose the 5-row/8-vert model:
  fitted 0.961, snapped 0.959 on the USUAL g=0.5 (M=720) grid —
  the wave-11 g=0.25 escalation was tile-smallness-driven and does
  NOT recur here (g=0.25 probed anyway: 0.955, no better).
  Clearance data-proven (iterations/53/measure/clearance-wave12.py):
  10 snapped stamps overlap reference waves 1-11 AND unbuilt 13-22
  by ZERO px; 93.0% on-target (best yet), off-target 100%%
  attributed to near-white band px (7.0%, zero fragments, zero
  other). Model-vs-model gaps: >= 4.98u to OUR wave-10 teardrops
  (same dart axes, both members symmetric), >= 5.50u to OUR
  wave-11 birds (neighboring star-tip axes) — no face-split risk.
one_idea: >
  ONE rotated 8-vert cycle in layer 1, wave-8/9 axis-symmetric
  technique: five new blueprint rings C56-C60 (radii
  141.9/144.6/145.2/165.6/170.7; on-axis rings C56/C60 at M=20 so
  cpt1 is exactly 18 deg, pair rings C57-C59 at M=720) and the
  single cycle under rotate 10 around C0.mpt walking base-nub ->
  +side base -> +side flank -> apex -> -side flank -> -side base:
  [C56.cpt1 C57.cpt41 C58.cpt49 C59.cpt43 C60.cpt1 C59.cpt29
  C58.cpt23 C57.cpt31]. Fills navy via the existing layer == 1
  rule — and the reference color IS navy this wave, so wave 12
  needs NO Stage-2 color deferral (first since wave 2).
prediction: >
  Census 359 -> 374: +10 layer-1 eight-sided faces (sides==8
  bucket 10 -> 20) + 5 benign blueprint circles (circle bucket
  56 -> 61) — this is the PRIMARY gate. Wave-diff: coverage stays
  100.0 (saturated, zero signal) and iou rises into [47, 56] (from
  46.2; the bells add ~10300 on-target px of intersection in a
  window whose union is field-dominated). Waves 1-11 hold on the
  iter-53 baselines (w1 82.2/71.1, w2 87.1/59.0, w3 93.9/76.3, w4
  96.9/41.2, w5 98.0/53.1, w6 97.4/51.6, w7 96.0/25.1, w8
  84.2/32.9, w9 95.0/53.5, w10 94.4/25.4, w11 94.8/27.0); allow
  <= 2 iou down on middle-ring waves 7-11, with window-union dips
  (iter-52 precedent) most likely on w10/w11 whose crops contain
  wave-12 ink — if any dips beyond 2, attribute via the falsifier
  path before accepting.
falsifier: >
  If the census eight-sided count rises by less than 10, the cycle
  failed to close — Tier-0 witness (one bell, no field) before
  touching the composite. If the tiles render on star-tip axes or
  at the wrong ring, the dart-axis read is wrong — re-measure,
  don't nudge. If iou DROPS below 45, the new ink is landing off
  the wave-12 mask — re-check the M=20-vs-M=720 mixed-circle cpt
  arithmetic (an on-axis cpt error shows as a radial spike at 18
  deg, not a rotation). If waves 1-11 regress beyond the
  allowance, diff the gt census first (face-split signal, not
  paint) — the 4.98u/5.50u gaps say face-splits should NOT happen;
  a split here falsifies the min-distance check, not the wave
  model.
```

## Verdict (2026-06-11): WAVE 12 PASSES — iteration 54 FROZEN

- **Census (PRIMARY gate): 359 -> 374 EXACT** — +10 eight-sided faces
  (sides==8 bucket 10 -> 20) + 5 benign blueprint circles (C56-C60,
  56 -> 61). No face-splits: the 4.98u/5.50u min-distance proofs
  held. Known benign warning only (`_girih_hexagon_star`).
- **Wave-diff 12: coverage 100.0 (as predicted), iou 46.2 — the
  predicted rise to [47, 56] DID NOT HAPPEN; prediction mechanism
  falsified and attributed**: before/after crops of the iter-53 vs
  iter-54 renders at the same window are pixel-identical
  (zoom-ne18-render-BEFORE.png vs zoom-ne18-render.png) — the bell
  zone was ALREADY a navy `sides >= 6` field face in iter-53, so the
  wave-12 stamp is ink-over-ink: intersection AND union both
  unchanged. The falsifier threshold (iou < 45) did not fire. This
  is a THIRD baseline regime after saturated-coverage (w11):
  fully-saturated-window waves where wave-diff carries ZERO signal
  and census + clearance + eyeball are the entire acceptance.
- **Holds**: w1-w9, w11 bit-identical; w10 94.3/25.4 (coverage -0.1,
  within allowance). All within the <= 2 allowance.
- **Eyeball gate (Tenet 26, expectation written before viewing)**:
  zoom-ne18 + zoom-n90 (dart axes 18/90 deg, r 156u, crops saved in
  wave-diff/wave-12/) — the render's navy ink fills the reference
  bell outline at both axes, apex outward, wave-11 birds flanking in
  the correct arrangement. Matches the pre-stated expectation.
- **Structural honesty note**: the bell face exists in the gt with
  correct geometry (snapped IoU 0.959) but is pixel-invisible
  against the navy field underlay — the white-band separation that
  makes it read as a discrete tile in the reference is Stage-2
  strapwork/band-rerouting territory (joins the wave-8 rerouting
  backlog item).
- **No Stage-2 color entry for w12**: reference color is navy and
  the layer==1 fill rule already paints it navy — first wave since
  2 needing no color deferral.

Next: wave 13 per wave-plan.json — baseline from wave-diff's SVG
raster of THIS iteration's render.svg.
