---
name: bikar-face-walker-short-chord-octagon-absorption
description: bikar face-walker absorbs the polygon edge AND drops the lens face when an arc-polygon shared-edge has a short chord on a high-order polygon (D_8 + L≈76 falsified Ticks 44/45 both passed)
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When an arc-polygon shared-edge construction uses `intersect XL CL1 CL2` + `connect arc XL.cpt0 -> XL.cpt1 on CL1` + reverse-arc on CL2 with BOTH lens endpoints coincident with polygon vertices, the bikar face-walker absorption hazard triggers selectively: short chord on a high-order polygon (D_8 + L≈76, qiyas#132 Tick 46) absorbs the lens entirely (one polyclass face with 7 polygon edges + 1 lens arc; lens face missing); longer chords (D_4 + L≈141 Tick 45, D_6 + L=100 Tick 44) emit two clean faces (polygon + lens).

**Why:** [[feedback_bikar_face_walker_polygon_edge_absorbed_by_coincident_arcs]] originally named the hazard as "polygon edge A→B whose endpoints both coincide with two arc-edges." Ticks 44/45/46 demonstrate the rule is narrower than that — the same incidence-topology produces zero-absorption (Ticks 44/45) or full-absorption (Tick 46). The differentiating factor across the three is chord length vs polygon edge-angle: the octagon's interior angle at a vertex (135°) leaves a smaller wedge for the incoming arc compared to the square (90°) or hexagon (120°), which appears to push the face-walker's incidence-ring traversal into the polyclass trap. Witness: qiyas#132 Tick 46 falsified 2026-05-26, template kept at `/Users/omareid/Workspace/git/qiyas/calibration/i1-corpus/templates/octagon-and-symmetric-lens-shared-edge.bkr.tmpl` (FALSIFIED header at top), render at `calibration/i1-corpus/renders/octagon-and-symmetric-lens-shared-edge/`. NOT enrolled in regenerate.py / splits.json / corpus.json to prevent calibrating the detector to absorb-shape verdicts.

**How to apply:** When authoring arc-polygon shared-edge entries in the I1 corpus, do not assume Ticks 44/45 passing → all polygon orders will pass. Test high-order polygons (D_8, D_10, D_12) with chord-length-to-polygon-circumference ratio matching the absorption trigger before enrolling. If the goal is to verify the absorption hazard (rather than dodge it), use this template as the explicit witness; otherwise prefer shared-vertex topology (Ticks 41/42/43) for high-order polygons until the bikar face-walker is patched.

**Companion to:** [[feedback_bikar_face_walker_polygon_edge_absorbed_by_coincident_arcs]] (the prior, broader claim this refines), [[feedback_bikar_face_walker_shared_edge_absorption_universal]] (Tick 21's universal-absorption diagnosis, since corrected), [[feedback_classify_by_predicate_cannot_witness_same_class_cross_refs]] (the polyclass trap this absorption produces).
