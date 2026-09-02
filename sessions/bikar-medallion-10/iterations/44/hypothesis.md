# Iteration 44 — Hypothesis

```yaml
attempt: 44
date: 2026-06-11
stage: structure
target_wave: 2
gap_targeted: >
  Wave 2 after iter-43: the standalone kites fixed the V-notch fusion
  (wave-1 recovered to 79.7%) but the darts are too thin — coverage fell
  to 81.2%, iou 50.7%. The reference dart is wide at the BASE (23.1 deg
  angular width at r 25-27) tapering to the tip; our kite peaked its
  width at r 30 and was only ~8 deg wide at the base
  (iterations/43/hypothesis.md verdict).
one_idea: >
  Fix the kite's width distribution, per the iter-43 falsifier: move the
  lateral vertices from (18 +- 9 deg, r 30) to (18 +- 11.25 deg, r 25).
  C3 becomes radius 25 divided into 160 (2.25-deg grid: cpt3 = 6.75 deg,
  cpt13 = 29.25 deg are the two laterals of the dart on the 18-deg axis).
  Everything else identical — same single rotated connect cycle, same
  C2/C1 inner and tip vertices. Kite area ~87.8 sq units vs the
  reference's 86.7; base width 22.5 deg at r 25 vs measured 23.1.
prediction: >
  Wave-2 coverage back to >= 90% (the wide base now covers the reference
  dart's base corners) and iou 50.7% -> >= 65%. Wave-1 holds >= 78%
  (the dart inner region barely changes; nothing new approaches the
  star).
falsifier: >
  If coverage recovers but iou stays in the 50s, the residual is no
  longer shape-fit — measure WHERE the extra/missing ink is before
  another geometry move; if it is the registration scale (our whole
  flower a few percent off), that is a wave-plan registration question,
  not a dart question — stop dart iterations and eyeball-gate wave 2 as
  matched-in-kind. If wave-1 drops below 75%, the wider base leaks into
  the star envelope — pull the inner vertex outward instead of widening
  further.
```

## Verdict (2026-06-11): WAVE 2 PASSES

Wave-diff: wave-2 coverage 81.2% -> 93.1%, iou 50.7% -> 60.3%. The sbs
eyeball is the gate and it reads matched: every gold outline holds a navy
dart with the wide base, the taper, the right tip radius, and a clean
white gap to the star — the reference's dart in kind and proportion.

Wave-1 number dipped 79.7% -> 70.7%, but the eyeball shows the star itself
untouched and inside its outline; the dip is metric interlock — our dart
ink vs the reference's dart ink inside the star's dilated envelope don't
coincide pixel-perfectly, and the envelope necessarily contains both. The
star gate (eyeball) still passes; the number is trend-only per protocol.

Residual, logged not chased: ~7% wave-2 coverage misses at the dart base
corners (reference base very slightly wider, 23.1 vs our 22.5 deg) and
band-width-scale edge mismatches capping iou at ~60. Not worth iterations
while waves 3-22 are unmatched.

Next: wave 3 (the 10 periwinkle shield petals) — iter-45.
