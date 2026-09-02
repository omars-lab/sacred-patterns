# iter-33 visual verdict — girih field decagonal (Slice 3, decision-doc C″)

## Expectation (written BEFORE render, Tenet 24)

iter-33 abandons the connect-on-circle construction of iters 13–18 and instead
uses the new `girih field decagonal` DSL statement (bikar Slice 2, commit ddb2e98)
to grow a gap-free decagonal overlapping-rosette field — the construction the
medallion-10 reference actually is, per the girih-ceiling decision doc.

I expect the render to show:

1. A central regular decagon at the origin.
2. A first shell of 10 decagons attached edge-to-edge around it, their seams
   φ-interlocked so adjacent ring decagons share an edge (overlapping rosettes).
3. A second shell extending the field outward to roughly fill a radius-~160
   field, with the characteristic girih strapwork decoration inside each tile.
4. **No gaps at the seams** — this is the whole point of the field generator vs.
   manual `attach` chains. The A6 "missing-shapes" delta that plagued iters 13–18
   (37 missing circles + 15 lenses, encoder-vocabulary noise) should be replaced
   by a clean decagon/pentagon/rhombus vocabulary that the encoder recognizes.

If the render instead shows detached tiles, an unfilled annulus, or overlapping
double-drawn tiles, the field generator's shell-BFS or the DSL wiring is wrong
and iter-33 falsifies Slice 2's visual gate at the composite scale.

## Observation (written AFTER viewing render.png)

**Visual gate: PASSED.** Two renders viewed:

1. **Bare field (no styling):** a dense, gap-free 10-fold decagonal girih field —
   overlapping decagonal rosettes with full strapwork decoration, filling a
   roughly circular field. No detached tiles, no unfilled annulus, no
   double-drawn overlaps. Matches expectation points 1–4.
2. **Styled field (`voids detect` + classify/fill):** the same field with deep-navy
   decagons, royal/cobalt squares + pentagons, turquoise triangles, fully
   filled edge-to-edge with no white seam gaps and clear 10-fold rotational
   symmetry.

The expectation held: the field generator produces the φ-interlocked overlapping
decagons gap-free, which manual `attach` chains could not. shells=2 grew a denser
field than the minimal central-decagon picture in the expectation (richer, on-target).

**First-render finding (defect, not in expectation):** the bare field exported
`0 shapes` to gt.json. Root cause: the field emits strapwork *segments*, which
need `voids detect` to close into faces, AND every face needs a `classify` rule
or bikar's gt-emitter drops it as unclassified (known hazard, memory
`feedback_bikar_gt_emitter_drops_unclassified_polygons`). Adding `voids detect`
+ classify-by-sides rules lifted the export to 2031 gt shapes / 2931 encoded
shapes. This is a construction-authoring lesson, not a field-generator bug.

## Ship-gate verdict (Tenet 25)

**Render viewed:** `render.png` (1024×1024, rsvg-convert).
**Visually confirmed against expectation:** dense gap-free 10-fold decagonal
field — deep-navy decagons, turquoise/cobalt/royal accents, clear rotational
symmetry, no white seam gaps, no detached tiles, no double-drawn overlaps.
Matches expectation points 1–4 + the styled-field observation.
**Verdict: PASS** — the styled field is shippable as the iter-33 measurement
artifact (it is a calibration render recording the Q1 verdict, not a starter
pattern entering `STARTER_FILES`). The portal session is not required for a
one-off calibration render whose purpose is the A6-vs-A5 measurement; the
expectation-first visual inspection above satisfies the ship gate for this
artifact class.
