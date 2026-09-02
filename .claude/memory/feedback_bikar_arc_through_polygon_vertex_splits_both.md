---
name: bikar-arc-through-polygon-vertex-splits-both
description: "When a lens arc passes through a polygon vertex (via shared construction circle), bikar's face-walker correctly splits both faces — even without declared shared topology — producing richer emission than naive expected-shape-count prediction"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When authoring Tier 1 polygon+lens fixtures that share a CONSTRUCTION CIRCLE (but declare neither shared edges nor shared vertices), MEASURE arc-through-polygon-vertex coincidences at design time. If the lens's intersection points (X01.cpt0/cpt1) straddle a polygon vertex angularly, that vertex IS on the lens's circular arc, and bikar's face-walker WILL split both faces at that point — producing rich topology (1 truncated N+1-sided polygon + multiple arc-bearing sub-faces) instead of the naive (1 polygon + 1 lens) emission.

**Why:** qiyas#132 Tick 67 (2026-05-27) authored `square-and-lens-shared-circle.bkr.tmpl` predicting 2-4 emitted faces. Construction: C0 origin r=100 ÷4 → square vertices, C1 center=(140,0) r=80 → intersection points X01 ≈ (82.857, ±55.99). The lens's C0-arc spans angles from +arctan(56/83)≈34° through 0° to -34° — passing through square vertex cpt0=(100, 0) at exactly y=0. Render outcome: 5 SVG faces emitted (1 truncated 5-sided square + 3 sides=3 arc-bearing sub-faces + 1 sides=3 lens remnant), 0 classified in gt.json because `sides==4` and `sides==2` rules don't match the actual emitted face categories. Template renamed FALSIFIED-* and preserved as hazard witness per Tenet 18.

**How to apply:** Before authoring any Tier 1 polygon+arc-on-shared-circle fixture, compute the lens's intersection-point angles on the shared circle AND the polygon's vertex angles on the same circle. If the lens-arc angular sweep CONTAINS any polygon vertex angle, the arc passes through that vertex and topology is richer than predicted. Either: (a) shift the second circle's center to avoid the coincidence, (b) accept the richer topology and write classify rules matching the actual carved face categories (e.g., `sides==5` for the truncated polygon), or (c) preserve as a hazard witness with FALSIFIED- prefix. Generalizes prior shared-vertex hazards (Ticks 9-25): those assumed shared-vertex topology requires explicit `intersect` or named-vertex `connect arc`; this lesson adds that ARC-THROUGH-POLYGON-VERTEX coincidence is ALSO a shared-topology-producer without declaration.

**Companion to:** [[feedback_cascade_primitive_semantic_composition]] (cascade plans composing ≥2 DSL primitives must validate semantics compose) and [[feedback_bikar_face_walker_polygon_edge_absorbed_by_coincident_arcs]] (related polygon/arc shared-boundary hazard from Tick 17). Together: bikar's face-walker has well-defined behavior at arc-polygon-vertex coincidences and arc-polygon-edge coincidences, but author-facing surface (DSL declaration shape) doesn't expose those coincidences — author must measure construction geometry before predicting emission.
