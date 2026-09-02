# iter-26 — Layer-isolated {20/3} central star (Resolution Path #2 from iter-25)

**Pattern:** iter-25 with `connect every 3 on Cstar20` moved from layer 0 to a new layer 4.
**Bikar HEAD:** 8c17615.
**Qiyas:** master.

## Why this run exists

iter-25 falsified the "central 20-star via {20/3} on Cstar20 r=20"
hypothesis: the chords got subdivided by C1's chord network (also at
r=30, same layer 0). iter-25's evaluation.md recommended Resolution
Path #2 (layer isolation) as lowest risk.

iter-26 ships exactly that change — Cstar20 chords in their own
layer 4. Bikar's planar-face extractor runs per-layer (see
bikar/docs/lessons.md "Multi-layer extraction"), so layer 4's
chords don't see layer 0's intersection set.

## Validation outcome — also falsified

| Metric          | iter-25                | iter-26                |
|-----------------|-----------------------:|-----------------------:|
| A1              | PASS                   | PASS                   |
| A2 status       | APPROXIMATE            | APPROXIMATE            |
| A2 cv           | 0.0365 (cascade best)  | 0.0415                 |
| A4              | FULL                   | FULL                   |
| A5 status       | COMPLETE               | COMPLETE               |
| A6 score        | 0/18                   | **0/18 (unchanged)**   |
| inner-star v20  | MISSING (cand_in_zone=0) | **MISSING (cand_in_zone=0)** |
| total shapes    | 2578                   | 2218                   |
| v20 anywhere    | 0                      | **0**                  |

## Hypothesis falsified — layer isolation insufficient under strapwork

The {20/3} face never materializes anywhere in the encoding
(`shapes_by_vertex_count` has keys 0,2,3,4,5,6,8,10 — no 20).

**Root cause (revised understanding from iter-25 + iter-26):** even
with layer isolation at the planar-face-extraction step, the
`strapwork width 5 crossing over` pass operates on the FULL set of
chords across all layers when generating bands. Strapwork band-edges
crossing through the {20/3} chord network subdivide the 20-star face
into many small bands and band-internal voids — the v20 identity
gets dropped during strapwork synthesis, not planar-face extraction.

This means the chosen construction (a {20/k} star polygon embedded
inside a strapwork medallion) is **structurally incompatible** with
single-face v20 emergence regardless of which layer the chords sit
in. Stopping per Tenet 7.

## Two falsifications of the same construction (Tenet 7 stop rule)

| iter | Variant of "central 20-star via {20/3}" | Falsified by |
|------|------------------------------------------|--------------|
| 25   | {20/3} on Cstar20 r=20 in layer 0       | C1 chord intersections at r=30 in layer 0 |
| 26   | Same chords moved to layer 4 (isolated) | Strapwork band crossings still subdivide |

Per the `handle-falsification` skill's Tenet 7 stop rule: two
variants of "central 20-star as {20/3} chord polygon" have falsified
for the same root reason (chord-network subdivision under strapwork).
Do NOT author variant 3 of this construction.

## What to try instead — fundamentally different sources for the v20 face

The remaining resolution paths from iter-25 that move OFF the "{20/3}
chord polygon" approach:

1. **`face` statement — direct declaration.** bikar's DSL supports
   `face` statements that declare a face by listing its boundary
   edges directly (see bikar/docs/language-reference.md). A 20-vertex
   star face can be declared explicitly without relying on chord-pair
   intersections to define it. This decouples from strapwork's
   subdivision entirely because the face is asserted at evaluation
   time, not derived from intersections. **Recommended.**

2. **Move strapwork OFF the central zone.** Restrict strapwork to
   layer 1+ (the rosette/transition zones) and leave layer 0 + the
   central-star layer untouched. The v20 face would emerge cleanly
   but the medallion loses its strapwork-everywhere visual
   coherence. **Tradeoff: aesthetic vs. A6.**

3. **Reframe the v20 expectation as a baseline-misread.** The
   reference image's "central 20-pointed star" may visually be the
   {10/3}+{10/4}+{10/2} chord superposition on C1, which the
   detector counts as v3/v4/v5/v6 faces. A6 expects v20 because the
   baseline encoder counted the visual outer envelope as a polygon
   with 20 vertices. **Requires re-inspecting reference.jpg.**

4. **Accept the A6 ceiling at 0/18 and pivot.** With A2=0.0406
   (cascade best, iter-24) and A4/A5 at their ceilings, the cascade
   has converged on every audit dimension except A6. A6's "rich
   inner constructions" expectation (18 distinct shape classes)
   may require a fundamentally different medallion design than the
   one this cascade has been iterating. **The wedge-and-rotate
   iteration may have hit its natural ceiling.**

## Composite ceiling preserved (mostly)

A2 cv 0.0415 is slightly above iter-25's 0.0365 (the cascade best)
but still well below iter-23's 0.0526 and iter-14's 0.067. A4/A5
remain at their ceilings. The construction probe didn't regress
anything load-bearing.

## Next iter pickup — recommendation

Resolution Path #1 (`face` statement direct declaration) is the
cheapest construction-side fix and most likely to bypass the
strapwork-subdivision problem. iter-27 should try it.

If Path #1 also falsifies (variant 3 — also Tenet 7-eligible to
stop), the cascade should pivot to Path #4 (accept ceiling) and
re-frame the medallion-10 deliverable around the A2/A4/A5 wins
this cascade has already achieved, deferring the rich-inner-shapes
expectation to a follow-on cascade with a different construction
philosophy.
