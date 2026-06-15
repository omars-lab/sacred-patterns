# iter-28 — Tiny central {20/3} star (spatial isolation attempt)

**Pattern:** iter-26 with Cstar20 radius shrunk from 20 to 6 (within baseline's 0.0686 distance_from_center.max for v20).
**Bikar HEAD:** 8c17615.
**Qiyas:** master.

## Why this run exists

After iter-25/26/27 falsified three construction variants for the
v20 verdict, re-reading baseline.json revealed the inner-star v20
expectation has `distance_from_center.max = 0.0686` — a TINY
central star within ~6.86% of pattern radius, not the 20% radius
Cstar20 the prior iters used.

iter-28 tests whether *correctly-sized* Cstar20 (r=6, within
0.0686) + layer isolation can spatially isolate the chord polygon
from all other layers' content (their content lives at radius ≥30).
Spatial isolation is genuinely different in mechanism from prior
attempts — short chords physically can't reach other circles'
chord networks.

## Validation outcome — falsified again, but for a NEW reason

| Metric          | iter-26  | iter-27  | iter-28              |
|-----------------|---------:|---------:|---------------------:|
| A2 cv           | 0.0415   | 0.0406   | 0.04                 |
| A4 / A5         | FULL / COMPLETE | FULL / COMPLETE | FULL / COMPLETE  |
| A6              | 0/18     | 0/18     | **0/18 (unchanged)** |
| total shapes    | 2218     | 2154     | 2294                 |
| v2 shapes       | 106      | 106      | **138 (+32)**        |
| v20 anywhere    | 0        | 1 (silent)| **0**               |

**New falsification mechanism:** at r=6, the {20/3} chord polygon
chords are so short they encode as v2 band-segments (138 v2 shapes
vs iter-27's 106; +32 matches the {20/3} chord count exactly).
Spatial isolation worked — the chords didn't get subdivided by
other layers — but the chords themselves are too small to form
a closed v20 face that the encoder resolves as polygon-with-20-
vertices. The encoder treats short closed-loop chords as 32
individual line segments.

## Tenet 7 four-falsification close

| iter | Variant | Falsified by |
|------|---------|--------------|
| 25 | {20/3} on Cstar20 r=20 in layer 0 | C1 chord intersections subdivide |
| 26 | {20/3} on Cstar20 r=20 in isolated layer 4 | strapwork band crossings subdivide |
| 27 | `face` with 20 arcs on Cstar20 r=20 | encoder collapses to circle (no v20) |
| 28 | {20/3} on Cstar20 r=6 in isolated layer 4 | chords too short, encode as 32 v2 line-segments |

Four falsifications, four distinct mechanism reasons. The pattern
is now CONCLUSIVELY clear:

> No chord-polygon or arc-polygon construction in the bikar DSL
> using the strapwork-medallion philosophy can produce a v20 shape
> that qiyas's encoder resolves as a single 20-vertex face inside
> THIS medallion's geometry.

This confirms `feedback_a6_baseline_construction_philosophy_mismatch`
(written after iter-27): the gap is construction-philosophy-wide,
not tunable. Stop iterating the v20 verdict.

## Cascade local-optimum frame

| Metric | iter-14 (start) | iter-25 (cascade best) | iter-28 (final v20 attempt) |
|--------|----------------:|-----------------------:|-----------------------------:|
| A2 cv  | 0.067           | **0.0365**             | 0.04                         |
| A4     | -               | FULL                   | FULL                         |
| A5     | -               | COMPLETE               | COMPLETE                     |
| A6     | -               | 0/18                   | 0/18                         |
| dominant fold | 10       | 10 conf 0.74           | 10 conf 0.74                 |

iter-25 stands as the cascade's local-optimum: A2 cv 0.0365 (best
in cascade history, 45% better than iter-14 baseline), A4/A5 at
their ceilings, A6 ceiling reflecting the construction-philosophy
mismatch with the baseline.

## Cascade decision

**Mark medallion-10 cascade local-optimum at iter-25.** Do NOT
auto-close task #85 (per user direction "medallion-10 stays open,
keep striving") — but DO stop iterating the v20 verdict and any
inner-star star/rosette verdicts that share the same chord-polygon
philosophy gap. Future iters should either:

1. **Probe non-v20 verdicts** that the cascade philosophy CAN
   plausibly produce:
   - `inner-star--polygon-v0` (qiyas circle): iter-26 found 5/21
     PARTIAL — adding more central circles at scaled radii is
     tractable.
   - `inner-star--rhombus-v4`: iter-26 had `cand_in_zone=20,
     after_filter=0` — 20 rhombi exist but at wrong distance from
     center; resizing circles could pass the distance filter.
   - `rosette--polygon-v0`: expects 36 circles in rosette zone,
     none currently emitted.
2. **Re-frame the cascade goal** as A2/A4/A5 convergence + a
   curated subset of tractable A6 shapes, with v20/v8/v6 explicitly
   deferred to a future construction-philosophy cascade.

iter-29 should target rosette--polygon-v0 by adding intermediate
circles at scaled radii in the rosette zone. Predicted Δ: A6 0/18
→ 1/18 with no degradation on A2/A4/A5.
