# Iteration 48 — Hypothesis

```yaml
attempt: 48
date: 2026-06-11
stage: structure
target_wave: 6
gap_targeted: >
  Wave 6 — 10 navy (#253C64..#284067) shapes at kind_r_frac 0.348 on
  the DART axes (theta ~= 18 mod 36, centroid jitter 17.2-18.7) — sits
  at 39.1% coverage / 21.3 iou on the iter-47 render (girih field
  tiles only). Visual identification (tinted crop + mask zoom of id
  98; pre-stated "outward-pointing tile" was HALF-falsified — the
  divergence located the real orientation): a pentagon-shield pointing
  INWARD — sharp apex toward the medallion center, wide outer end
  whose edge carries a shallow center peak flanked by two dips.
  Measured model (3 shapes, vertex clusters consistent at tolerance
  1.0 and 2.0): apex_in (axis, 82.7u), side bends (+-6.75 deg, 91u),
  outer corners (+-9 deg, 111.2u), dips (+-2.5 deg, 109.7u), center
  peak (axis, 112.9u). Grid-snapped shoelace area 639.6u^2 vs measured
  mean 640.7u^2 (0.2% — tightest fit of any wave). The non-monotonic
  width profile around r 96-99 is attributed to EDT whisker artifacts
  (known issue), not a real waist vertex — finer-tolerance extraction
  produced no consistent vertex there.
one_idea: >
  An inward-shield ring in layer 1, same standalone-closed-cycle
  technique that passed waves 2-5: five new blueprint rings — C18
  r82.7/20 (apex, axis = cpt1), C19 r91/160 (2.25-deg grid, +-6.75 =
  cpt5/cpt11), C20 r111.2/40 (9-deg grid, +-9 = cpt1/cpt3), C21
  r109.7/720 (0.5-deg grid, +-2.5 = cpt31/cpt41), C22 r112.9/20
  (peak, axis = cpt1) — and one rotated 8-cycle walked CCW from the
  apex: connect cycle [C18.cpt1 C19.cpt11 C20.cpt3 C21.cpt41 C22.cpt1
  C21.cpt31 C20.cpt1 C19.cpt5]. Zero quantization error (each step
  divides gcd(18, delta)). Clearance: apex sits 7.2u above the wave-4
  pentagram's axis valley (75.5 -> 82.7, same axis) and the apex-bend
  edge passes 8.3u above the pentagram prongs; the wave-5 arrowheads
  occupy rel +-[9..18] deg at r <= 104.3 while our corner at rel +-9
  is at r 111.2 — 25u radial gap at the closest ray. The shape lives
  in the field zone — layer-1 paint covers field tiles and bands
  underneath, same accepted regime as waves 3-5.
prediction: >
  Wave-6 coverage >= 95% (from 39.1) and iou >= 50% (from 21.3; the
  shape is petal-sized — wave 5 at the same scale and radius landed
  52.3, and this model's area fit is tighter). Census 211 -> 226:
  +10 layer-1 8-gons (a vertex count no other wave uses — clean
  signal), +5 benign blueprint circles (C18-C22). Waves 1-5 hold in
  the eyeball; wave-4 and wave-5 iou may dip a few points (metric
  interlock: our apex/corner ink sits inside their dilated envelopes'
  neighborhoods on the same/adjacent axes).
falsifier: >
  If the shields render on the star-tip axes (rotated 18 deg), the
  axis read is wrong — re-measure, don't nudge. If a shield fails to
  close (gt layer-1 8-gon count does not rise by 10), the 8-cycle hit
  a snapping defect — Tier-0 witness (one shield, no field) before
  touching the composite. If coverage lands high but iou < 45, check
  WHERE: missing ink in rel +-[2.5..9] at r ~110 means the dips are
  band artifacts and the outer edge is really two straight
  corner-to-peak edges — drop C21 next iteration (single idea);
  extra ink past r 113 means peak/corner radii over-measured. If
  waves 1-5 visibly regress beyond metric interlock, diff the gt
  shape census first.
```

## Verdict (2026-06-11): WAVE 6 PASSES

Wave-diff: wave-6 coverage 98.5% (predicted >= 95, from 39.1
baseline), iou 52.5% (predicted >= 50, from 21.3) — the first wave to
meet BOTH numeric predictions. Pre-stated expectation: ten navy
inward-pointing pentagon-shields on the dart axes, sharp apex toward
the center just above each pentagram, wide outer edge with a subtle
center peak, filling the gold envelopes; iou loss as band-edge
mismatch plus the fine peak/dip outer-edge structure — not
misplacement or wrong orientation. The sbs + render-wave/ref-wave
crops match it: all ten envelopes contain a navy shield with the
apex inward and the wide edge outward, same axes and arrangement as
the reference; residual loss reads as slight over-fill at the
band-eaten envelope boundaries, exactly the predicted mechanism.

Waves hold: wave-1 89.7/70.7, wave-2 93.1/49.5, wave-3 96.0/72.7
(all unchanged), wave-4 98.3/38.6 (iou 39.2 -> 38.6) and wave-5
98.7/52.1 (52.3 -> 52.1) — both the predicted metric-interlock dips;
eyeball clean.

Census: gt shapes 211 -> 226, exactly as predicted: +10 layer-1
8-gons (theta 18 mod 36, identical areas — exact rotational
replication, Tenet 8), +5 benign blueprint circles C18-C22.

Measurement note for the record: the initial pre-stated visual
("outward-pointing tile") was half-falsified by the tinted crop —
the shape points INWARD; the divergence located the real
orientation before any DSL was written (Tenet 24 working as
designed). The model's grid-snapped shoelace area landed 0.2% from
the measured mean, the tightest fit of any wave.

Stage-2 note: shield fill is navy #132A61 via the layer==1 rule; the
wave plan samples these at #253C64..#284067 (its "navy"). Joins the
Stage-2 backlog (w3 periwinkle, w4 deep_navy, w5 cyan).

Next: wave 7 — 40 real deep_navy shapes at r_frac 0.398, mean area
just 142px^2 (~83u^2, the smallest gated so far), clustered at theta
{4.6, 11.2, 24.7, 31.2} mod 36 — four shapes per repeat unit flanking
the dart axes (18 +- 13.4 and 18 +- 6.9 approx). First multi-shape-
per-axis wave: expect ONE rotated group of 4 small cycles — iter-49.
