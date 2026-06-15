# Iteration 40 — Hypothesis

```yaml
attempt: 40
date: 2026-06-11
stage: structure
target_wave: 1
gap_targeted: >
  First wave-driven iteration under the agreed wave plan (gate passed
  2026-06-11, studio agree button). Wave 1 — the single navy center star,
  the heart of the middle flower (waves 1-3) — FAILS its gate against
  iter-39: wave-diff coverage 60.4%, iou 42.2%, and the sbs.png shows our
  center star visibly undersized. Measured: our star is 807 px2 in the
  registered frame vs the reference's 1687 px2 — 2.09x too small by area,
  1.45x linear. Star diameter is 4.8% of the medallion; the reference's is
  ~7%.
one_idea: >
  shells 2 -> shells 1. The girih decoration's star size is fixed relative
  to its host decagon (historical {10/3} vocabulary — no scale knob), so
  the only parameter lever on the star/medallion RATIO is the field extent.
  Dropping one growth ring shrinks the medallion relative to the central
  decagon; after registration (render scaled so medallion diameters match)
  the center star should grow by roughly the field-radius ratio, expected
  ~1.5x linear vs the needed 1.45x.
prediction: >
  Wave-1 coverage rises from 60.4% toward >= 85% and iou from 42.2% toward
  >= 60%; the sbs shows our star points reaching the gold reference
  outline. The whole-image similarity will likely DROP (the outer flower
  ring vanishes with shell 2) — that is expected and out of scope: the
  whole-image number is trend-only under the wave protocol; waves 2+ own
  the rest, and the outer ring returns in later iterations (possibly via a
  composed construction: bigger central rosette + explicit outer ring).
falsifier: >
  If wave-1 coverage/iou do NOT improve materially under shells 1, the
  star/medallion ratio is not governed by shell count the way the packing
  estimate says — route to the construction-philosophy fork (explicit
  central rosette construction sized from the reference, layered with or
  replacing the field center).
```

## Verdict (2026-06-11): FALSIFIER FIRES — route to the construction fork

Wave-diff: coverage 60.4% → 100.0%, iou 42.2% → 48.4%. The coverage jump is
vacuous: the center is now a large solid navy face that happens to cover the
reference star's footprint; iou barely moved because most of that ink lies
OUTSIDE the star.

What the center actually is (a false engine-bug alarm, resolved by Tier-0
witnesses — edges-only and strapwork renders of a bare
`girih field decagonal 62 shells 1 pockets star`): the {10/3} decoration's
own central decagon, rendered exactly as designed. The gt.json face that
looked seed-sized (R=103.4) is in the 1024-px image frame; ÷1.753 it is 59
pattern units — the decoration center. The kernel keeps all 10 seed chords
at shells 1 (and clips them fully at shells 2, where the center is instead
covered by lens pocket-star motifs — that was iter-39's small center star).

So the real shape of the failure: **neither shell setting can match wave 1.**

| | center shape | size (% of medallion dia) | reference |
|---|---|---|---|
| shells 2 (iter-39) | pointed star (lens motif) | 4.8% — 1.45× too small | 10-pointed star, ~7% |
| shells 1 (iter-40) | flat-sided decagon ({10/3} chords) | 20.3% — ~2.9× too big | |

Shell count is not a wave-1 lever. Per the falsifier: iter-41 keeps the
shells-1 field (its center + 10 bold rosettes matches the reference's
middle-flower + inner-flowers layout far better than shells 2's fine mesh)
and overlays an EXPLICIT central 10-pointed star sized from the reference
(~7% of medallion diameter) in its own layer inside the field's empty
central decagon. Waves 2–3 (the middle flower's petals) fill the remaining
annulus in later iterations.
