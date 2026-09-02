# iter-22 — Tenet 21 end-to-end validation (sacred-patterns#106 Option I)

**Pattern:** identical to iter-21-probe (extend+clip cascade with named satellites).
**Bikar HEAD:** 8c17615 (Slice 1 — emit data-partial + data-clipped-boundary).
**Qiyas HEAD:** da85fcc + svg_primitives._emit_path fix (Slice 5 — wire path branch).

## Why this run exists

iter-21-probe was rendered before bikar Slice 1 shipped, so its render.svg had
zero `data-partial` / `data-clipped-boundary` attributes. iter-22 re-renders
the same pattern with current bikar HEAD to validate the four-slice chain:

  bikar 8c17615 → svg → svg_primitives.py → Contour → classify_contour → Shape → a6_baseline

## Validation outcome

End-to-end Tenet 21 (DSL-as-source-of-truth) chain **confirmed working**:

| Layer                                       | Count    |
|---------------------------------------------|----------|
| SVG `data-partial="true"` attrs             | 140      |
| SVG `data-clipped-boundary` attrs           | 140      |
| Contours with `partial=True`                | 108*     |
| Shapes with `partial=True`                  | 108      |
| Shapes with `clipped_at_boundary="outline"` | 108      |
| A6 expected_shapes flipped MISSING→CLIPPED-MISSING via DSL-partial evidence | 2 |

*108 < 140 because some clipped fragments are sub-3-vertex or sub-pixel and get
filtered at the Contour stage (lens reductions, slivers).

## A6 verdict distribution (10 expected_shapes total)

  PASS:            3
  EXCESS:          2
  MISSING:         2  ← genuine misses (no DSL-partial in inner-star zone)
  CLIPPED-MISSING: 2  ← Slice 4 verdict flip with `dsl_partial_shape` evidence
  PARTIAL:         1

A6 score: 3/10 (0.30).

## Gap surfaced — `_emit_path` branch was missing partial threading

Initial run on iter-22 (with bikar Slice 1 emit) showed **zero Shape partials**
despite 140 SVG attrs. Investigation traced the gap to
`src/qiyas/stages/svg_primitives.py:_emit_path` — the SVG `<path>` branch did
not pass `partial` / `clipped_at_boundary` into Contour, only the `<polygon>`
branch did. Bikar emits clipped faces as `<path d="..."/>` elements (for arc
edges), so the wiring was effectively unreachable on real renders.

Fix: thread `meta.partial` + `meta.clipped_at_boundary` through both Contour
construction sites in `_emit_path`. New witness test
`test_data_partial_on_svg_path_carries_through_to_contour` pins the path
branch per Tenet 18.

## Score trajectory note (NOT the headline)

Composite scoring not run here; this iter exists to validate the wiring, not
to push the medallion-10 ceiling. Future iters (23+) can stack actual
construction improvements on a now-working detector path.
