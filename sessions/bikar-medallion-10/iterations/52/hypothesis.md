# Iteration 52 — Hypothesis

```yaml
attempt: 52
date: 2026-06-11
stage: structure
target_wave: 10
gap_targeted: >
  Wave 10 — 20 real deep-navy teardrop tiles in the middle ring,
  TWO per 36-deg repeat in MIRROR PAIRS straddling the dart axes
  (18 mod 36) at rel ~ +-6.1 deg, mean area ~83.7u^2, radial span
  ~128-144u — baseline 37.1% coverage / 10.6 iou on the iter-51
  render (wave-diff canonical SVG raster path). Same pair-member
  topology as wave 7: the tile is NOT self-symmetric, so the
  consensus (20 witnesses folded to the + side: rel<0 members
  mirrored about the 18-deg axis; area-matched threshold; max
  stack 20/20) models ONE member and the .bkr stamps it plus its
  mirror. Closing probe (0/3/4u disks -> 80.5/84.9/85.3u^2)
  shows modest fill — the notches are mostly real boundary;
  modeled the raw consensus. DOF-penalized seed sweep (5/6/7
  verts, IoU - 0.004n) picked the 6-vert model: fitted IoU
  0.917; snapped (r->0.1u, rel->0.5deg on M=720, asserted 1e-9)
  IoU 0.908, area 80.7u^2 vs consensus 80.5
  (iterations/51/measure/wave10-fit.json). Dart-axis snap rule:
  vertex at rel x -> cpt(36+2x) for the + member, cpt(36-2x) for
  the mirror. Clearance data-proven: the 20 snapped teardrops
  rasterized in reference px space overlap reference waves 1-9 by
  ZERO px AND unbuilt waves 11-22 by ZERO px; 77.6% of stamp ink
  lands on reference wave-10 px, and the 22.4% off-target is
  fully attributed (21.0% near-white band px + 1.4% wave-10
  fragments) — acceptable band-boundary noise on small ~84u^2
  tiles (iterations/51/measure/clearance-wave10.py).
one_idea: >
  TWO rotated 6-point cycles in layer 1, wave-7 mirror-pair
  technique on SHARED circles: six new blueprint rings C44-C49
  (radii 137.7/131.4/131.8/137.2/139.8/139.9, all M=720) and the
  pair of cycles under rotate 10 around C0.mpt:
  [C44.cpt41 C45.cpt48 C46.cpt52 C47.cpt53 C48.cpt51 C49.cpt46]
  (+ member) and
  [C44.cpt31 C45.cpt24 C46.cpt20 C47.cpt19 C48.cpt21 C49.cpt26]
  (mirror member). Fills navy via the existing layer==1 rule
  (reference color is deep_navy — Stage-2 business like waves
  3-9; the gate counts any non-near-white ink). Standalone:
  clearance proof above is authoritative (zero px on every other
  wave, built and unbuilt).
prediction: >
  Wave-10 coverage >= 80% (from 37.1; wave-7 small-mirror-pair
  precedent reached 96) and iou >= 20% (from 10.6; small tiles +
  21% of stamp ink on ref-white band px suppress iou the same
  way wave-7's 25.2 was suppressed). Census 307 -> 333: +20
  layer-1 six-sided faces (type 'unknown', counted by sides) + 6
  benign blueprint circles (C44-C49). Waves 1-9 hold on the
  iter-51 cairo baselines (w1 82.2/71.1, w2 87.1/59.0, w3
  93.9/76.3, w4 96.9/41.2, w5 98.0/53.1, w6 97.4/51.6, w7
  96.0/25.2, w8 84.2/36.2, w9 95.0/54.6); allow <= 2 iou down on
  adjacent middle-ring waves (7-9).
falsifier: >
  If the teardrops render on star-tip axes or only 10 faces
  appear, the mirror-pair stamping is wrong — re-measure, don't
  nudge. If layer-1 six-sided count rises by less than 20, a
  cycle failed to close — Tier-0 witness (one pair, no field)
  before touching the composite. If coverage lands >= 80 but iou
  < 18, attribute WHERE: penalty on ref-white lattice = accepted
  (waves 7-9 precedent); displaced tiles = re-measure. If
  coverage < 80, run the no-strapwork counterfactual probe
  BEFORE any geometry change (wave-8 precedent: construction was
  exact, bands cost the points). If waves 1-9 regress beyond 2
  iou, diff the gt census first (face-split signal, not paint).
```

## Verdict (2026-06-11): WAVE 10 PASSES — both predictions cleared; w8 dip attributed to window-union artifact

Wave-diff: coverage 94.4% (predicted >= 80, from 37.1) PASSED;
iou 25.4% (predicted >= 20, from 10.6) PASSED — in line with the
wave-7 small-mirror-pair precedent (25.1), where the iou ceiling
is set by ref-white band px inside the small tiles' masks.

Census: gt shapes 307 -> 333 exactly as predicted: +20 six-sided
faces (type 'unknown', counted via params.sides; bucket 30 -> 50)
+ 6 benign blueprint circles C44-C49. Both cycles closed on all
10 dart axes.

Holds: waves 1-6 BIT-IDENTICAL to the iter-51 baselines; w7
96.0/25.1 (-0.1), w9 95.0/54.3 (-0.3) — within allowance. Wave 8
84.2/32.9: iou -3.3 EXCEEDS the <= 2 allowance, so the falsifier
path was followed: (1) gt census diff is clean — only the
predicted +20/+6, no face-split; (2) wave-8 coverage is
bit-identical (84.17 vs 84.2) and registration identical, so the
intersection is unchanged — the union grew ~10%, which is the
ink volume of the 20 new teardrops landing inside wave-8's broad
crop window [192,158,580,561]; (3) the clearance proof
(iterations/51/measure/clearance-wave10.py) shows ZERO px of the
new ink on reference wave-8 px. Verdict: measurement-window
union inflation from CORRECT adjacent wave-10 ink — the same
interlock that suppressed wave-7's iou — not a wave-8 geometry
regression. New wave-8 hold baseline going forward: 84.2/32.9.

Eyeball gate (pre-stated expectation: 20 navy teardrops in
mirror pairs flanking each dart axis, slightly chunkier than
ref, white bands crossing): zoom-east decisive — both pair
members filled at the ref positions, mirror orientation exact;
zoom-north confirms across axes. In-mask loss is white
band-crossing, matching the px attribution. No displacement.

Stage-2 backlog addition: w10 color — reference is DEEP_NAVY,
our fill is navy via the layer==1 rule (same deferral as waves
3-9).

Next: wave 11 per wave-plan.json — baseline from wave-diff's SVG
raster of THIS iteration's render.svg.
