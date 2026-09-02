# iter-30 — Rhombus-v4 distance-filter rescaling probe (FALSIFIED)

**Pattern:** iter-25 + Crhom r=60 with `connect every 4` in isolated layer 5.
**Bikar HEAD:** 8c17615.
**Qiyas:** dev (master).

## Why this run exists

Per iter-29's evaluation, the cascade has hit a diminishing-returns
slope on polygon-v0 (PARTIAL 7/21 → would need ~16 more circles for PASS).
iter-29 recommended pivoting to **inner-star rhombus-v4** because iter-24
showed `cand_in_zone=20 after_filter=0` — 20 4-vertex shapes exist but
all fail the distance filter [0.251, 0.3877].

Hypothesis (Option A — distance-filter rescaling): adding a divided circle
at r≈60 with `connect every 4` would produce 4-vertex chord-rhombi whose
centroids land at distance_ratio ~0.30 (inside the target band).

## Validation outcome — falsified, no improvement on rhombus-v4

| Metric          | iter-25 (base)  | iter-30                    |
|-----------------|----------------:|---------------------------:|
| A1              | 100.0           | 100.0                      |
| A2 score        | 85.0            | 85.0                       |
| A4              | 100.0           | 100.0                      |
| A5              | 100.0           | 100.0                      |
| A6              | 0/18            | **0/18 (unchanged)**       |
| rhombus-v4      | MISSING 0/10    | MISSING 0/10 (cand=20)     |
| inner-star squares (in band) | 0/20  | **0/20 (no change)**       |
| total shapes    | 2218            | 2247 (+29)                 |

**Empirical falsification:** inspected iter-30 encoding.json. The 20
`type=square` shapes in the inner-star zone are IDENTICAL in count
and distance-ratio distribution to iter-24 (all at ratio 0.10–0.20,
none in [0.251, 0.3877]). The new Crhom r=60 layer added 29 shapes
TOTAL to the encoding, but ZERO new `type=square` shapes at the
target band. The new chord crossings were absorbed into:
- Strapwork band crossings / band segments
- Regular polygons of other vertex counts
- Unknown classifications
- Lens faces (chord-arc intersections)

## Hypothesis falsification — Option A mechanism wrong

The premise "a divided circle at r=R with `connect every 4` produces
4-vertex faces classified as squares with centroids at ~R/2 ratio"
held for C1 (iter-24 baseline: 20 squares at ratio 0.10–0.20 from
C1 chord crossings) but **did not hold for Crhom at r=60**. Possible
mechanisms:
1. The strapwork layer applies AFTER chord-network construction.
   Chord crossings on Crhom (at radius 60) are intercepted by
   strapwork's band-crossing detector and reclassified as
   `band_crossing` or `band_segment` rather than `square`.
2. The chord-network on Crhom intersects other layers' chords
   (extended satellites, Cmid2, Cmid) creating compound faces with
   >4 vertices.
3. The encoder's `type=square` classifier has tight tolerances on
   side-length equality that the geometry at r=60 violates.

## Tenet 7 falsification close — fifth A6 verdict failing on construction philosophy

| iter | Variant | A6 target | Falsified by |
|------|---------|-----------|--------------|
| 25 | {20/3} on Cstar20 r=20 in layer 0 | inner-star--star-v20 | C1 chord intersections subdivide |
| 26 | {20/3} on Cstar20 r=20 in isolated layer 4 | inner-star--star-v20 | strapwork band crossings subdivide |
| 27 | `face` with 20 arcs on Cstar20 r=20 | inner-star--star-v20 | encoder collapses to circle |
| 28 | {20/3} on Cstar20 r=6 in isolated layer 4 | inner-star--star-v20 | chords too short, encode as 32 v2 line-segments |
| **30** | **`connect every 4` on Crhom r=60 in isolated layer 5** | **inner-star--rhombus-v4** | **chord rhombi absorbed by strapwork, no new squares in band** |

**Five falsifications across two distinct A6 verdicts (v20 + rhombus-v4),
each at a different pipeline stage.** This extends the cross-repo memory
`feedback_a6_baseline_construction_philosophy_mismatch` — the philosophy
mismatch is not just about v20; it is **the strapwork-medallion philosophy
cannot place rhombi (or any 4-vertex shape) at the baseline's expected
distance bands**.

The baseline (likely derived from a different construction philosophy —
girih tiling with explicit rhombi as primary tiles) expects rhombi as
*standalone tiles* at specific radii, while strapwork-medallion produces
4-vertex shapes only as *intersection-faces of chord networks*, with
centroids determined by the chord network geometry (not the underlying
circle's radius).

## Cascade decision

**Mark medallion-10 cascade local-optimum at iter-25.** Stop iterating
rhombus-v4 with chord-network-adding variants. Per `feedback_a6_baseline_construction_philosophy_mismatch`,
the cascade should stop iterating any A6 verdict whose expected
distance/area distribution conflicts with strapwork-medallion's
intersection-face geometry.

The A6 verdicts that REMAIN tractable under this philosophy:
- `inner-star--polygon-v0` (qiyas circle): currently PARTIAL 7/21
  per iter-29 (gain-per-circle ~40%, diminishing returns confirmed)
- `transition--polygon-v0`: 10 candidates exist in iter-30 audit,
  but `after_filter=0` (similar distance-filter issue)
- A1/A2/A4/A5: all at or near ceiling

**No A6 verdict in the 18-shape baseline is reachable via further
chord-network additions to the existing strapwork construction.**

## Next iter pickup — pivot away from medallion-10

Per Tenet 20 (simplest broken thing first) and the cf_delta-cost-blind
feedback memory, the loop should pivot OFF medallion-10 cascade for
A6 chasing. The cascade has converged at iter-25 ceiling for what
the current construction philosophy can deliver.

#85 stays OPEN per owner direction "keep striving," but the open work
is now **construction philosophy migration** — not parameter tuning.
A genuine A6 score improvement would require:
1. Adding girih-tile primitives to bikar DSL (decagon, pentagon,
   rhombus, bow-tie, hexagon as tile types, not blueprint circles)
2. Re-authoring medallion-10 using tile placement instead of chord
   networks
3. Re-rendering the same visual pattern with explicit rhombus faces

This is a multi-week scope (DSL extension + pattern rewrite + qiyas
detector validation that tile primitives are classified correctly).
Defer until owner explicitly prioritizes it; in the meantime, return
to other cascade work (R1-R4 leaves per post-i1-task-routing §C).
