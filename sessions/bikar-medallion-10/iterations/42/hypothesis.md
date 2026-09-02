# Iteration 42 — Hypothesis

```yaml
attempt: 42
date: 2026-06-11
stage: structure
target_wave: 2
gap_targeted: >
  Wave 2 — the 10 small deep-navy darts of the middle flower — scores
  coverage 0.0% / iou 0.0% against iter-41 (nothing of ours renders
  there). Measured from the reference segmentation (exemplar id 213):
  darts are outward-pointing kites on the 18-degrees-offset axes (between
  adjacent star tips), ink spanning r 29.8..53.5px = 22.8..41.0 pattern
  units, angular width ~23 deg at the base tapering to a point. The
  tinted-flower eyeball (flower-tinted.png) confirms: 10 red kites wedged
  in the notches between the center star's points and the petal bases.
one_idea: >
  A dart ring in layer 1: blueprint circle C1 radius 41 (the measured
  dart-tip radius) divided into 20 (odd points land on the 18-deg dart
  axes), plus one rotated zigzag — rotate 10 around C0.mpt { connect
  C0.cpt0 -> C1.cpt1, connect C1.cpt1 -> C0.cpt1 }. Each dart face closes
  automatically against the star's two outer edges (tip -> concave vertex
  -> tip) already in layer 1, so no new primitive and no hand-placed
  vertex list: 1 circle + 2 connects inside a rotate. The existing
  `fill void where layer == 1 color navy` inks the darts.
prediction: >
  Wave-2 coverage 0% -> >= 85% (the reference dart ink sits inside our
  kite footprint) and iou 0% -> >= 50%. Known extra-ink residual, accepted
  up front: our kite includes the V-notch down to the star's concave
  vertex (r ~12 units) while the reference's white bands eat that notch
  (its dart ink starts at ~23 units) — some extra ink lands in the wave-2
  envelope and caps iou below the wave-1-style 80s. Wave-1 re-check may
  dip a few iou points from dart-base ink inside the star's dilated
  envelope — interlock effect, not a regression; the star itself is
  untouched (zigzag meets it only at tip vertices, no new crossings).
falsifier: >
  If the darts render misplaced (on the tip axes instead of between them)
  the divide-phase assumption (cpt0 at angle 0) is wrong — fix the phase,
  don't move the radius. If coverage is high but iou lands well under 50%
  because the V-notch extra ink dominates, switch the dart inner boundary
  from the star's edges to the tip-to-tip chord (triangle darts) in
  iter-43. If layer-1 faces break (star hole returns, darts not closing),
  debug at Tier 0 with a star+zigzag witness before touching the
  composite.
```

## Verdict (2026-06-11): FALSIFIER FIRES (extra-ink branch) — route to standalone kites

Wave-diff: wave-2 coverage 0% → 98.2% (darts placed and sized right — the
sbs gold outlines sit exactly on our dart tips; axis check: reference dart
axes mean 18.05 deg mod 36 vs our 18.0), but iou 40.7% — under the >= 50%
prediction. Wave-1 re-check: iou 83.1% → 50.7%, far beyond the predicted
"few points" dip.

The sbs names the mechanism: our dart kites share the star's outer edges,
so they fill the V-notches between star points with navy — exactly where
the reference keeps white bands — fusing star + darts into one solid
20-pointed blob. The extra notch ink pollutes BOTH envelopes.

Routing per the falsifier, upgraded by the eyeball: NOT chord-triangle
darts (the tip-to-tip chord still encloses the notch as a layer-1 face that
the `layer == 1` fill would ink navy). Instead, standalone dart kites that
never touch the star: 4 own vertices per dart — inner (18 deg, r 23), two
lateral (18±9 deg, r 30), outer tip (18 deg, r 41) — one rotated
`connect cycle`, three blueprint rings (C2 r23 /20, C3 r30 /40, C1 r41
/20). Kite area d1*d2/2 = 18 * 9.39 / 2 = 84.5 sq units vs the reference's
86.7 (148 px²) — matches; the white gap between star edges and dart is the
reference's band, free of charge. Iter-43.
