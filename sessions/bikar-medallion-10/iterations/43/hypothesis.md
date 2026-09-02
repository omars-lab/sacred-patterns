# Iteration 43 — Hypothesis

```yaml
attempt: 43
date: 2026-06-11
stage: structure
target_wave: 2
gap_targeted: >
  Wave 2 after iter-42: coverage 98.2% (darts placed and sized right) but
  iou 40.7%, and wave 1 collapsed 83.1% -> 50.7%, because the iter-42 dart
  kites shared the star's outer edges and filled the V-notches between
  star points with navy — where the reference keeps white bands
  (iterations/42/hypothesis.md verdict).
one_idea: >
  Standalone dart kites that never touch the star. Each dart is its own
  closed 4-cycle with all vertices on blueprint rings: inner (18 deg,
  r 23 — measured ink base 22.8), two lateral (18+-9 deg, r 30), outer
  tip (18 deg, r 41 — measured ink tip). Blueprint gains C2 r23 /20 and
  C3 r30 /40 (C1 r41 /20 stays from iter-42); the zigzag connects are
  replaced by one rotated `connect cycle [C2.cpt1 C3.cpt1 C1.cpt1
  C3.cpt3]`. Kite area 84.5 sq units vs the reference's 86.7 — matched.
  The gap between star edges and dart inner vertex renders as canvas
  white = the reference's band, free of charge.
prediction: >
  Wave-2 iou 40.7% -> >= 65% (the V-notch extra ink is gone; remaining
  mismatch is the kite's straight flanks vs the reference dart's slightly
  wider base, ~18 vs ~23 deg). Coverage stays >= 90% (our kite is very
  slightly narrower than the reference dart, so a sliver of reference ink
  at the base corners may go uncovered). Wave-1 iou recovers to >= 78%
  (near its 83.1% solo value; only the dart inner vertex region sits
  within 8px of the star's edges).
falsifier: >
  If wave-2 coverage drops materially below 90%, the kite is too narrow —
  widen the lateral vertices (C3 ring radius or angle), not the tip. If
  wave-1 iou does not recover above ~70%, the dart still pollutes the
  star envelope — pull the inner vertex outward (r 23 -> 26). If the
  cycle fails to close as a face (gt face count unchanged), the rotated
  connect-cycle endpoint snapping across three circles is broken — build
  a Tier-0 witness (one kite, no star, no field) before touching the
  composite.
```

## Verdict (2026-06-11): FALSIFIER FIRES (too-narrow branch) — widen the base

Wave-diff: wave-2 coverage 98.2% -> 81.2%, iou 40.7% -> 50.7%; wave-1
recovered 50.7% -> 79.7% (predicted >= 78 — the standalone-kite separation
worked, the white star-dart gap is back and the star silhouette is clean).

The sbs eyeball: every gold outline contains a navy kite on the right axis
with the right tip, but ours are visibly thinner — the reference dart has a
WIDE base (measured 23.1 deg angular width at r 25-27) tapering to the
point, while our kite peaks its width at r 30 (lateral vertices +-9 deg)
and is only ~8 deg wide down at the base. Wrong width distribution: too
much area high, too little low.

Routing per the falsifier (widen the lateral vertices, not the tip):
iter-44 moves the laterals to (18 +- 11.25 deg, r 25) — on a 160-division
grid (2.25-deg steps: cpt3 = 6.75 deg, cpt13 = 29.25 deg). Kite area
~87.8 sq units vs reference 86.7; base width 22.5 deg at r 25 vs measured
23.1. Same single-cycle construction, only C3 changes (r 30/40 -> r 25/160).
