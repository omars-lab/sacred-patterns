# Iteration 45 — Hypothesis

```yaml
attempt: 45
date: 2026-06-11
stage: structure
target_wave: 3
gap_targeted: >
  Wave 3 — the 10 periwinkle shield petals of the middle flower — has
  nothing of ours (iter-41 baseline: coverage 2.1%, iou 1.9%; the field's
  faces incidentally graze the envelope). Contour extraction on three
  reference petals (skimage find_contours + approximate_polygon, eps 2px)
  gives a consistent 6-vertex shield on each star-tip axis: base
  (0 deg, ~30.5u), hips (+-14.5 deg, ~50u), shoulders (+-11.2 deg, ~62u),
  tip (0 deg, ~65.5u). Shoelace area of that hexagon: 576 sq units vs the
  reference petal's 578 (986 px^2) — the vertex model matches.
one_idea: >
  A petal ring in layer 1, same standalone-closed-cycle technique that
  passed wave 2: four new blueprint rings — C4 r30.5/10 (base), C5
  r50/100 (hips: 3.6-deg grid, +-14.4 deg = cpt4/cpt96), C6 r62/100
  (shoulders: +-10.8 deg = cpt3/cpt97), C7 r65.5/10 (tip) — and one
  rotated 6-cycle: connect cycle [C4.cpt0 C5.cpt4 C6.cpt3 C7.cpt0
  C6.cpt97 C5.cpt96]. Analytic check: petal edges cross neither the dart
  edges (in the 6.75..14.4 deg overlap zone the petal edge runs at r ~41
  vs dart edge r ~28) nor the star. Petal tips (65.5u) poke past the
  white canvas decagon (59u) into the field — layer-1 paint covers the
  field faces there, accepted structural noise at this stage.
prediction: >
  Wave-3 coverage >= 90% and iou >= 60% (same regime as the dart pass;
  the petal is larger so band-edge mismatch weighs proportionally less —
  iou may land higher). Waves 1-2 hold (nothing new approaches them:
  petal base r 30.5 vs dart laterals r 25, white gaps preserved). The
  whole middle flower (waves 1-3) reads as the reference's rosette in
  the sbs.
falsifier: >
  If the petals render misplaced or rotated 18 deg, the axis assumption
  (petals ON star-tip axes) is wrong — re-measure, don't nudge. If
  coverage is high but iou < 50%, check WHERE: if extra ink rings the
  petal tips, the field-overlap noise is larger than expected — consider
  blanking the first field ring inside r ~66 to white (canvas extension)
  as the NEXT iteration's single idea. If the petal faces fail to close
  (gt shape count does not rise by ~10), the 6-cycle across four rings
  hit a snapping defect — Tier-0 witness (one petal, no field) before
  touching the composite.
```

## Verdict (2026-06-11): FALSIFIER FIRES (new branch: band-overlay slicing) — engine task

Wave-diff: wave-3 coverage 58.2%, iou 48.0% (predicted >= 90 / >= 60);
wave-2 dipped 60.3% -> 49.5%; wave-1 held 70.7%.

The sbs eyeball names a mechanism none of the falsifier branches
anticipated: the petals are PRESENT, correctly shaped and placed inside
the gold outlines — but the field's white strapwork bands render on top
of all face layers and slice through the layer-1 petals (the bands were
invisible until now because everything under them was white canvas or
field ink; a navy petal under a white band shows the band). The reference
routes its band network AROUND the flower — the flower paints over the
field, bands included.

Routing: this is a render-ORDER defect, not a construction defect — no
.bkr edit can fix it (strapwork is a flat top overlay in svg-renderer).
Engine task (bikar): when multiple face layers exist, emit the strapwork
band group BETWEEN the layer-0 face group and higher-layer face groups —
bands belong to the layer whose segments they weave (girih deco = layer
0); higher layers paint over them. Tier-0 witness + red->green regression
per Tenets 17/18, then re-render iter-45 unchanged (the .bkr is already
right) and re-gate wave 3.

## Re-gate verdict (2026-06-11, after engine fix): WAVE 3 PASSES

Engine fix shipped as bikar 87c8a20 (task #53): renderSVG now emits
base (layer<=0) face groups -> blueprint -> strapwork bands -> overlay
(layer>0) face groups, with a red->green regression in
svg-renderer.test.ts. The fix also surfaced that compileDSL and the CLI
--emit-truth path dropped faceLayers entirely — both now pass it through
(without that, the CLI renderer never saw layering and the reorder could
not activate). pattern.bkr re-rendered UNCHANGED.

Wave-diff after re-render: wave-3 coverage 58.2% -> 96.0%, iou 48.0% ->
75.3% (the best iou of any wave so far — the predicted "larger shape,
band mismatch weighs less" regime). Pre-stated expectation: 10 solid
shield petals, unsliced, inside their gold outlines, tips poking outward.
The sbs eyeball matches it exactly — the band slicing is gone and the
middle flower reads as the reference rosette in structure. Petal COLOR is
periwinkle vs the reference navy: Stage-2 material, not a structure-gate
concern.

Waves hold: wave-1 89.7/70.7 (star untouched, inside its outline);
wave-2 93.1/49.5 — iou dipped 60.3 -> 49.5, same metric interlock as the
iter-44 wave-1 dip (our petal ink vs reference petal ink inside the
darts' dilated envelope don't pixel-coincide); the eyeball shows every
dart matched, gate still passes.

Middle flower (waves 1-3) complete. Next: wave 4 — the 20 deep-navy
shapes at r_frac 0.248 (NOT part of the flower) — iter-46.
