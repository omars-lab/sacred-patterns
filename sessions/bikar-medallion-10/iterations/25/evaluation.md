# iter-25 — Add central 20-pointed star (inner-star zone construction probe)

**Pattern:** iter-24 + `circle Cstar20 center(0,0) radius 20; divide Cstar20 into 20; connect every 3 on Cstar20` in layer 0.
**Bikar HEAD:** 8c17615.
**Qiyas:** master.

## Why this run exists

iter-24 closed the partial-shape + strapwork composition cleanly but A6
against `input/baseline.json` is 0/18 — the real reference target
expects much richer inner shapes (1 inner-star 20-vertex star, 6
8-vertex stars, 2 6-vertex stars, 10 rhombi, 28 rosette 6-vertex stars,
etc.).

iter-25 attacks the topologically simplest missing shape:
`inner-star--star-v20` (expected 1, found 0). Construction: a {20/3}
star polygon on a new central circle Cstar20 (radius 20).

## Validation outcome

| Metric          | iter-24                | iter-25                |
|-----------------|-----------------------:|-----------------------:|
| A1              | PASS                   | PASS                   |
| A2 status       | APPROXIMATE            | APPROXIMATE            |
| A2 cv           | 0.0406                 | **0.0365** (new best)  |
| A4              | FULL                   | FULL                   |
| A5 status       | COMPLETE               | COMPLETE               |
| A6 score        | 0/18                   | **0/18 (unchanged)**   |
| inner-star v20  | MISSING (0 / 1)        | **MISSING (0 / 1)**    |
| inner-star v0   | MISSING (0 / 21)       | PARTIAL (5 / 21)       |
| inner-star band-segment-v2 | MISSING (0 / 3) | EXCESS (66 / 3)    |
| dominant_fold   | 10 conf 0.73           | 10 conf 0.74           |
| total shapes    | 2153                   | 2578                   |

## Hypothesis falsified — central 20-star didn't materialize as a single face

The DSL `connect every 3 on Cstar20` was emitted (raw chord count
increased by 425 shapes, A2 cv improved, fold confidence ticked up),
but the central 20-pointed star DIDN'T appear as a single closed
20-vertex face. Instead its edges were subdivided by intersections
with C1's existing chord patterns (radius 20 vs 30 are too close —
{20/3} chords pass through the C1 disk and cross `connect every K on C1`
chords from layer 0).

## What this teaches

For the medallion-10 inner zone, multi-circle chord patterns in
the SAME layer subdivide each other into many small polygon faces
instead of preserving the "star polygon" identity. The detector
correctly sees what's drawn (lots of v3/v4/v5/v6 faces);
the construction side dropped the v20 identity at the planar-face
extraction step.

**Resolution paths (deferring choice to user / next iter):**

1. **Move Cstar20 outside the C1 disk** — e.g., radius 35 (between C1=30
   and Cmid2=50). The {20/3} chords no longer cross C1's chord network,
   so the 20-star face is preserved. But it lands in a different zone
   ("transition") which mis-maps against the baseline's zone
   expectations.
2. **Layer isolation** — put `connect every 3 on Cstar20` in its own
   layer (say layer 4). Layers don't share chord intersections in
   bikar's planar-face extraction, so the 20-star survives. This is
   the lowest-risk option.
3. **Replace C1's chord patterns with the Cstar20 patterns** — i.e.,
   the central decagrams on C1 ARE the visual "central star," and
   the v20 baseline expectation is a mis-read of the reference image.
   Requires re-inspection of reference.jpg.
4. **Larger Cstar20 radius (e.g., r=29) + remove `connect every 2 on C1`** —
   `every 2 on C1` is the densest chord pattern in the inner zone;
   removing it leaves more chord-free area for Cstar20.

## Composite ceiling preserved

Even with A6 unchanged, A2 cv 0.0365 is the new best in the cascade
and A5/A4 stay at their iter-24 ceiling. The new chord network
doesn't degrade anything; it just doesn't yet emit the topologically
distinct 20-star face A6 expects.

Next iter pickup: try resolution path #2 (layer isolation) — lowest
risk, simplest DSL change, most likely to deliver A6 0/18 → 1/18.
