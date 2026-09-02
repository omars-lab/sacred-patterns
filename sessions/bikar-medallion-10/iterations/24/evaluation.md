# iter-24 — Composition of strapwork (iter-23) with extend+clip (iter-22)

**Pattern:** iter-22's named-satellite extend+clip silhouette + iter-23's `crossing over` strapwork (width 5).
**Bikar HEAD:** 8c17615 (data-partial emit, canonicalEdgeOrder, all current cascades shipped).
**Qiyas:** master (svg_primitives.py Slice 5 fix for path-branch partials).

## Why this run exists

iter-22 (sacred-patterns#106 Option I) and iter-23 (bikar#114 PR1) each validated one half of the medallion-10 cascade independently:

- iter-22: extend+clip silhouette works; A2 cv 0.087, A5 BROKEN (no strapwork).
- iter-23: `crossing over` strapwork works; A2 cv 0.0526, A5 COMPLETE (no extend+clip).

iter-24 is the **composition test**: do the two cascades' fixes compose
cleanly, or does combining them resurface either bug?

## Validation outcome — composition is a net win

| Metric          | iter-22 | iter-23  | iter-24 (compose)     |
|-----------------|--------:|---------:|----------------------:|
| A1 status       | PASS    | PASS     | PASS                  |
| A2 status       | UNEVEN  | UNEVEN   | **APPROXIMATE**       |
| A2 cv           | 0.087   | 0.0526   | **0.0406** (best yet) |
| A4 coverage     | -       | -        | **FULL** (100%)       |
| A5 status       | BROKEN  | COMPLETE | **COMPLETE**          |
| A5 band count   | -       | 33       | 34                    |
| A5 crossings    | -       | 302      | 310                   |
| dominant_fold   | 10      | 10       | 10 (conf 0.73)        |
| total shapes    | 741     | 1463     | 2153                  |
| svg-audit score | 2/5     | 3/4      | **3/4**               |

**iter-24 has the best A2 cv of the entire medallion-10 cascade so
far (0.0406, even below iter-14's 0.067 strapwork-free baseline)**
AND keeps A5=COMPLETE AND A4=FULL. The two cascades compose cleanly
with no resurgent bugs — composition is a net win, not a neutral
combination.

## Three hypotheses tested

1. ✓ **A5 stays COMPLETE** — strapwork mode unchanged from iter-23; 34
   bands vs 33 (one more band fragment due to extra clipped boundary
   strands), 310 crossings vs 302.
2. ✓ **A2 cv stays low** — 0.0406 actually *improves* on iter-23's
   0.0526. Hypothesis was 0.06–0.09; reality is better. Why: the
   extend+clip mechanism redistributes per-sector shape totals more
   evenly than naive `repeat at C0 depth 1`.
3. ✓ **A4 = FULL** — silhouette coverage 100%; the union(C0, S0..S9)
   boundary captures every emitted shape.

## A2 status: APPROXIMATE (not UNEVEN)

A2 transitioned from UNEVEN (iter-23) → APPROXIMATE (iter-24) at the
same fold detection. This is a real status improvement, not a noise
artifact: APPROXIMATE means cv is below the audit's
near-uniform threshold but mismatch count is non-zero. iter-23's cv
of 0.0526 was above that threshold; iter-24's 0.0406 is below it.

## Composite score not run

Requires iter-14 baseline.json comparison. The A2 cv + A4 + A5 deltas
are the load-bearing evidence that composition is clean.

## What this unlocks for #85

The medallion-10 cascade now has, simultaneously:
- Extend+clip silhouette working (#106 Option I)
- Strapwork bands working with rotation-invariant strand assignment (#114 PR1)
- A5 COMPLETE (best verdict in cascade history)
- A2 cv 0.0406 (best cv in cascade history)
- A4 FULL coverage

Remaining ceiling: A6 verdict (requires baseline) and structural
diversity in the inner-star zone (2 true MISSING shapes from iter-22's
analysis attributed to upstream construction gaps in inner-star, not
detector blind spots).

Next iter focus options:
- **(P1)** Add an inner-star construction layer to close the 2 MISSING
  inner-star shapes from iter-22 (predicted composite ceiling lift).
- **(P2)** Capture a new iter-14-class baseline.json so future iters
  get A6 verdicts and composite scores.
