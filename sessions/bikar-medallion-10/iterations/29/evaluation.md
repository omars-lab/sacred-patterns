# iter-29 — Probe polygon-v0 verdict via concentric central circles

**Pattern:** iter-26 + 5 concentric inner circles (Cinner1..5 at r=10, 14, 18, 22, 26).
**Bikar HEAD:** 8c17615.
**Qiyas:** master.

## Why this run exists

Per iter-28's evaluation, cascade pivots from philosophy-blocked
v20/star verdicts to tractable polygon-v0 verdicts. iter-26 found
inner-star polygon-v0 PARTIAL 5/21 — closest A6 shape to a PASS.
Adding 16 more circles in the inner-star zone (centroid distance
< 0.3891 of pattern radius) would close it.

iter-29 adds 5 concentric circles inside C1 as a small probe to
confirm: (a) each `circle` declaration adds 1 to qiyas's encoded
polygon-v0 count, (b) all 5 pass the inner-star distance filter.

## Validation outcome — partial gain, only 2 of 5 circles counted

| Metric          | iter-26  | iter-29              |
|-----------------|---------:|---------------------:|
| A2 cv           | 0.0415   | 0.0406               |
| A4 / A5         | FULL / COMPLETE | FULL / COMPLETE |
| A6              | 0/18     | 0/18                 |
| inner-star polygon-v0 | PARTIAL 5/21 | **PARTIAL 7/21** |
| v0 in encoding  | 15       | 17 (+2)              |

Only 2 of the 5 added circles registered as new polygon-v0 in the
inner-star zone (5 → 7, +2). The other 3 must have either:
- Been deduplicated by qiyas's encoder (concentric circles too close in area)
- Been classified to a different zone (transition/rosette)
- Been dropped during `voids detect` cleanup

Inspecting `encode.json`: 17 v0 shapes total, with 10 at identical
area 7690.74 (Cmid2 clones), plus 7 distinct-radius circles. The
encoder appears to dedup OR the chord-crossing pattern fragments
the inner circles into chord-bounded arcs that don't re-form as
single-circle shapes.

## Conclusion

This verdict IS tractable but the gain-per-added-circle ratio is
poor (~40%). To reach 17+ (PASS threshold = 21-4 tolerance), I'd
need to add ~30+ inner circles, which would clutter the medallion.

Better alternative for future iters: stop adding tiny circles and
instead use larger circle subdivisions that survive the encoder
deduplication. OR accept that polygon-v0 stays PARTIAL and pivot
to rhombus-v4 (cand_in_zone=20 already exists; need to fix the
distance filter, which is geometric scaling not new construction).

## Cascade status

iter-29 holds A2/A4/A5 at ceiling. polygon-v0 advanced
5/21 → 7/21 (still PARTIAL). A6 score unchanged at 0/18 (PARTIAL
counts as 0 in score, only PASS counts).

Next iter pickup options:
1. iter-30: scale rhombus construction (existing 20 4-vertex
   shapes in inner-star zone exist but fail distance filter — need
   to relocate them closer to/farther from center to pass).
2. iter-30: add ~16 more concentric circles to push polygon-v0
   from PARTIAL 7/21 → potential PASS.
3. Pause cascade and pivot to other backlog work (per the loop's
   "address all our issues" directive — other tasks may have
   higher net cf_delta than further medallion iteration).

The cascade has hit a clear diminishing-returns slope. Iters 23-25
each shipped meaningful gains; iters 26-29 have each shipped
marginal-or-negative gains relative to the construction cost. Per
the cf_delta-cost-blind memory feedback, this is the signal to
pivot.
