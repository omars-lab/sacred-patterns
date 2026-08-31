---
name: asymmetric-lens-intrudes-polygon-interior
description: "when an asymmetric lens shares a polygon edge with one CL inside the polygon interior, the face-walker emits the polygon face with a mixed line+arc boundary (not absorption — a valid alternate topology)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When an arc-polygon SHARED-EDGE construction uses an ASYMMETRIC lens (CL1 ≠ CL2 in radius) and one of the two construction circles sits on the **same side** of the chord as the polygon interior, the bikar face-walker emits the polygon face with `has_arcs=true` and a mixed boundary (polygon edges + one CL arc cutting across the chord-internal region). The output is still N face shapes (polygon + lens + circles), but the polygon face boundary is line+arc, not pure-line.

**Why:** Demonstrated 2026-05-26 by qiyas#132 Tick 50 (square-and-asymmetric-lens-shared-edge): CL1=(71.21, 71.21) r=76.81 sits OUTSIDE the square at +30·perp distance; CL2=(14.65, 14.65) r=86.60 sits INSIDE the square at −50·perp distance. CL2's arc, anchored at the cpt0/cpt1 shared-edge endpoints, sweeps through the square interior and the face-walker uses it as the polygon's boundary along the cpt0→cpt1 segment, dropping the chord polygon edge in favor of the arc. Output:
- 5 shapes total (matches expectation)
- 1 asymmetric_lens (sides=2, has_arcs=true) bounded by CL1 outer arc + CL2 inner arc (the "lens" is the slice between them, not a classical lens shape)
- 1 square face (sides=4, has_arcs=true) with 3 line edges (cpt1→cpt2→cpt3→cpt0) + 1 CL2 arc (replacing the cpt0→cpt1 line edge)

This is distinct from the bikar face-walker ABSORPTION hazard ([[feedback_bikar_face_walker_short_chord_octagon_absorption]] and [[feedback_bikar_face_walker_polygon_edge_absorbed_by_coincident_arcs]]): absorption produces FEWER shapes than expected (lens face missing). This produces the EXPECTED shape count, but the polygon face has a richer boundary type (line+arc) than the symmetric shared-edge case would predict. The qiyas detector handles both topologies correctly: Tick 50 scored ari_fused=1.0 with fused_lift=+0.556 (larger lift than D_4/D_6/D_8 shared-vertex entries' +0.260, reflecting that the detector's raw partition under-resolves the 3 classes more here but fusion still reaches ground truth).

**How to apply:** When authoring polygon + asymmetric-lens shared-edge entries in the I1 corpus, do not assume the polygon face will have `has_arcs=false`. Inspect `gt.json` evidence.outline_arcs: if one CL sits on the polygon-interior side of the chord, the polygon face's outline will include one `type=arc` segment. This is correct output, not a bug. The vocabulary `(polygon, has_arcs=true)` is a valid Tier 1 face_class that the detector + face-class fusion vocabulary expansion (post-#400/#490) can witness. For NEW asymmetric shared-edge entries: choose CL placement consciously — if you want clean (line-only polygon, arc-only lens), put both CL on the SAME side (the polygon exterior); if you want to test the mixed-boundary topology, put one CL on each side of the chord (Tick 50's choice).

**Companion to:** [[feedback_bikar_face_walker_short_chord_octagon_absorption]] (the absorption hazard this is NOT), [[feedback_bikar_face_walker_polygon_edge_absorbed_by_coincident_arcs]] (the broader hazard family this is also NOT), [[feedback_classify_by_predicate_cannot_witness_same_class_cross_refs]] (still applies — heterogeneous sides counts keep classify mutually exclusive even with mixed-arc boundary).
