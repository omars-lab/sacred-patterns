# Iteration 37 — visual verdict (2026-06-10)

## Numbers

| metric | iter-36 | iter-37 | predicted |
|---|---|---|---|
| pixel similarity | 72.9% | **74.2%** (+1.3, session high) | +2–6 |
| color match | 65.2% | 66.8% | — |
| channel-drift spread (r−b) | 30.3 | 26.7 | "should shrink" ✓ |
| gt.json shapes | 2031 | **844** | "fewer, larger faces" ✓ |

## Predicted vs actual — honest read

The structural hypothesis was RIGHT and the lift prediction was again too
optimistic (+1.3 actual vs +2–6 predicted; third consecutive over-prediction —
future hypotheses should halve their gut number). Expectation written before
viewing, then confirmed in the render and the ref/36/37 zoom triptych
(/tmp/zoom-ref-36-37.png):

- **Confirmed:** between-rosette zones lost the fractured white micro-mesh;
  large simple faces now sit where the lens hexagons are; face count dropped
  2031 → 844; rosette {10/3} stars survive outside the lenses with chords
  trimmed at the rims; no rim slivers spotted; channel drift narrowed,
  consistent with iter-36's diagnosis that the drift was a structural-density
  symptom.
- **Predicted residual, now the top gap:** the new large lens faces wear the
  WRONG fill family. Measured from gt.json: 531/844 faces (63%) are 3-sided
  and wear pale #BBC5D5 (.turquoise), while the reference shows saturated
  cyan (#32B0CA) and royal/navy pocket-stars in exactly those zones. The
  shape is right; the color role is wrong. This is a fill-class mapping
  problem, not a construction problem.

Engine note (shipped with this iteration, bikar task #23): the field dedup
fix (negative-zero key) removed 5 silently-duplicated decagons present in
every shells-2 render since iter-33, so this A/B is pockets + dedup, not
pockets alone.

## Next-gap routing

1. **Pocket/triangle color-role mapping (top).** Don't guess the remap:
   sample the reference's color at OUR face centroids per class (a measured
   role-transfer, the same discipline as iter-36's palette histograms), then
   re-map the classify/fill rules — possibly classifying lens faces directly
   via their `_girih_hexagon` source tag rather than side-counts. 63% of
   faces are currently in the palest family; the reference's same zones are
   mid/dark.
2. **Per-role color via portal Q7 annotations** (carried — same theme as #1;
   the expert look adjudicates once the 80% gate clears; we are at 74.2%).
3. **Boundary ring: scalloped vs rounded** (carried from iter-36).
