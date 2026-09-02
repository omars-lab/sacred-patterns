# Iteration 41 — Hypothesis

```yaml
attempt: 41
date: 2026-06-11
stage: structure
target_wave: 1
gap_targeted: >
  Wave 1 (the navy center star) still fails its gate after iter-40's
  falsifier fired: neither girih shell setting can produce it (shells 2
  gives a lens-motif star 1.45x too small; shells 1 gives a flat-sided
  decoration decagon ~2.9x too big — iterations/40/hypothesis.md verdict).
  Iter-40 wave-1 numbers: coverage 100% (vacuous — solid navy decagon
  floods the envelope), iou 48.4%.
one_idea: >
  Per the iter-40 falsifier route: keep the shells-1 field and overlay an
  EXPLICIT central 10-pointed star, sized from the reference, in its own
  DSL layer inside the field's empty central decagon — and blank that
  decagon to white so it becomes the star's canvas instead of a navy slab.
  Star: blueprint circle radius 22.6 pattern units (= measured reference
  tip radius 29.5px / 739px medallion, scaled to our 565.75-unit
  medallion), divide into 10, connect every 4 ({10/4} = two superimposed
  pentagrams; Tier-0 witness /tmp/star-witness rendered a solid 10-point
  star, 31 faces, all filled navy). Orientation measured: reference tips
  at 3.6 deg mod 36, ours at 0.0 — a 1.9px tip offset, ignored.
  Engine prerequisite shipped first (bikar c0aa77e, task #52): the
  cross-layer face dedup key gains area, so the star's central decagon
  (0,0 / 10 edges) no longer collides with the field's decoration decagon
  (0,0 / 10 edges) — without the fix the star renders with a hole.
prediction: >
  The sbs shows a navy 10-pointed star on a white central canvas, tips
  reaching the gold reference outline; iou rises materially from 48.4%
  toward >= 60% (our star's area is ~13% under the reference's at matched
  tip radius — slightly thinner points — so a perfect-overlap iou is not
  expected). Coverage drops from the vacuous 100% to roughly the star's
  true overlap; that drop is healthy, not a regression.
falsifier: >
  If the star renders broken (hole, missing faces, white slivers), the
  dedup fix or the layer composition is wrong — debug at Tier 0 before
  touching the composite. If the star renders clean but iou does NOT
  improve, the star SHAPE family is wrong (reference points fatter /
  rounder than {10/4} chords give) — route to a different star
  construction (e.g. Hankin-angle star or explicit 20-gon outline) rather
  than scale tuning.
```

## Verdict (2026-06-11): WAVE 1 PASSES

Wave-diff: coverage 100%→89.7% (now real, not vacuous), iou 48.4% → 83.1%.
The sbs eyeball confirms the prediction: a solid navy 10-pointed star on the
white central canvas, tips reaching the gold reference outline, orientation
aligned (3.4 deg phase offset invisible at this scale), no hole — the dedup
fix (bikar c0aa77e) held in the composite. Whole-render check: the field is
byte-identical in character to iter-40 outside the center; the central navy
slab is gone.

Residual, logged not chased: our {10/4} chords give slightly thinner points
than the reference (~13% less area at matched tip radius) — visible as small
gold slivers at the tip notches. If a later whole-flower pass wants it, the
falsifier route (Hankin-angle star) is the named alternative; not worth an
iteration while waves 2-22 are unmatched.

Next: wave 2 (middle-flower petals) — iter-42.
