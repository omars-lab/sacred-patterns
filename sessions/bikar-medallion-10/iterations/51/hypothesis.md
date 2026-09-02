# Iteration 51 — Hypothesis

```yaml
attempt: 51
date: 2026-06-11
stage: structure
target_wave: 9
gap_targeted: >
  Wave 9 — 10 real cyan interstice blobs at kind_r_frac 0.463, ONE
  per 36-deg repeat centered ON the star-tip axes (0 mod 36; first
  wave on star-tip axes after waves 2-8 on dart axes), mean area
  1486px^2 (~872.6u^2), radial span ~113-146u — baseline 51.3%
  coverage / 30.0 iou on the iter-50 render (wave-diff canonical
  SVG raster path). Visual identification (zooms of ids 71/82;
  pre-stated expectation "large elongated polygon" was FALSIFIED
  by the look — they are spiky ~16-vertex interstice blobs whose
  outline is defined by the surrounding white band lattice, raw
  contours 21-26 verts at eps 1.2). Envelope probe (fit-wave9b,
  morphological closing at 3/4/5u band scale) filled <2% area —
  proving the concavities are REAL tile boundary, not band-carve
  noise like wave-8's chamfers; the model must include them.
  Model: symmetrized 16-gon — 2 on-axis tips + 7 mirrored (r,+-x)
  pairs — IoU coordinate-descent against the 20-witness consensus
  (10 rotated masks + 18-deg mirrors, area-matched threshold,
  unanimous 20/20 core): fitted IoU 0.970; snapped (r->0.1u,
  x->0.5deg on M=720, asserted 1e-9) IoU 0.963, area 842.3u^2 vs
  consensus 848.1 (measure/wave9-fit.json). Star-tip-axis snap
  rule is FREER than dart axes: vertex at +-x needs only x*M/360
  integer; on-axis verts are cpt0 on M=20. Clearance data-proven:
  the 10 snapped 16-gons rasterized in reference px space overlap
  reference waves 1-8 by ZERO px; 93.7% of stamp ink lands on
  reference wave-9 pixels (measure/clearance-wave9.py).
one_idea: >
  One rotated 16-point cycle in layer 1, same standalone-closed-
  cycle technique as waves 2-8: nine new blueprint rings C35-C43
  (radii 113.5/118.3/117.0/124.9/128.1/134.2/139.2/141.1/146.1;
  axis tips on M=20 cpt0, paired verts on M=720) and ONE cycle
  [C35.cpt0 C36.cpt5 C37.cpt11 C38.cpt12 C39.cpt17 C40.cpt14
  C41.cpt15 C42.cpt15 C43.cpt0 C42.cpt705 C41.cpt705 C40.cpt706
  C39.cpt703 C38.cpt708 C37.cpt709 C36.cpt715] under rotate 10
  around C0.mpt. Fills navy via the existing layer==1 rule (wave
  color is CYAN in the reference — color correctness is Stage-2
  business like waves 3-8; the gate counts any non-near-white
  ink). Standalone: angular gap to the wave-8 diamonds is 4.55 deg
  (18 - 8.65 - 4.8) and the inner tip r 113.5 clears the wave-7
  ring's outermost circle C30 r 112.6; data proof above is
  authoritative.
prediction: >
  Wave-9 coverage >= 85% (from 51.3; wave-8 precedent: white
  strapwork plows through this zone too — its crossings are
  ALREADY part of the measured spiky outline where they coincide
  with the reference lattice, but our straight-through bands
  deviate from the reference's routed bands mid-tile, so expect
  some near-white carving inside the mask) and iou >= 40% (from
  30.0). Census 288 -> 307: +10 layer-1 16-gons (sides==16) + 9
  benign blueprint circles (C35-C43). Waves 1-8 hold on the
  cairo baselines (w1 82.2/71.1, w2 87.1/59.0, w3 93.9/76.3, w4
  96.9/41.2, w5 98.0/53.1, w6 97.4/51.5, w7 96.2/25.4, w8
  84.2/36.2); wave-8 iou may move up (adjacent correct ink in its
  envelope ring, same interlock as wave-7 at iter-50); allow <= 2
  down on waves 5-8.
falsifier: >
  If the blobs render off-axis or at the wrong ring, the star-tip
  axis read (0 mod 36 vs dart 18 mod 36) is wrong — re-measure,
  don't nudge. If layer-1 16-gon count rises by less than 10, the
  cycle failed to close — Tier-0 witness (one blob, no field)
  before touching the composite. If coverage lands >= 85 but iou
  < 35, attribute WHERE: penalty on ref-white lattice / unbuilt
  outer waves = accepted (waves 7-8 precedent); a displaced blob
  = re-measure. If coverage < 85, run the no-strapwork
  counterfactual probe BEFORE any geometry change (wave-8
  precedent: construction was exact, bands cost 15.8 points). If
  waves 1-8 regress beyond 2 iou, diff the gt census first
  (face-split signal, not paint).
```

## Verdict (2026-06-11): WAVE 9 PASSES — both predictions cleared, best middle-ring iou yet

Wave-diff: coverage 95.0% (predicted >= 85, from 51.3) PASSED;
iou 54.6% (predicted >= 40, from 30.0) PASSED — the highest iou
of any middle-ring wave (w4 41.2, w5 53.1, w6 51.6, w7 25.2, w8
36.2). The 5% uncovered is white band-carving inside the mask,
the same Stage-2 band-geometry business as waves 7-8; no
counterfactual probe needed since both predictions cleared.

Eyeball gate (pre-stated expectation: navy spiky 16-gon inside
each gold ref outline, star-tip axes, notches oriented
correctly): zoom-east confirms — our 16-gon fills the reference
blob, the left-side concave notches match, orientation exact;
zoom-north straddles the 72/108-deg blobs, both filled. The
visible in-mask loss is white bands crossing, matching the px
attribution. No displacement.

Census: gt shapes 288 -> 307 exactly as predicted: +10
sixteen-sided faces (type 'unknown' — no classify rule names
16-gons; counted by sides) + 9 benign blueprint circles C35-C43.
The 16-point cycle closed on all 10 star-tip axes.

Holds: waves 1-6 and 8 BIT-IDENTICAL to the iter-50 baselines;
wave 7 96.0/25.2 (-0.2/-0.2, within the <= 2 allowance).

Stage-2 backlog addition: w9 color — reference is CYAN, our fill
is navy via the layer==1 rule (same deferral as waves 3-8).

Next: wave 10 per wave-plan.json — baseline from wave-diff's SVG
raster of THIS iteration's render.svg.
