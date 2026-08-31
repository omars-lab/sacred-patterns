---
name: bikar-gt-emitter-sliver-filter-dissolves-polygon-corner-leakage
description: "qiyas#132 polygon-corner-leakage cascade (Ticks 82-93) ROOT-CAUSE FIXED at bikar gt-emitter via Polsby-Popper isoperimetric gate; previously-recorded \"polygon-corner leakage\" feedback memories describe the SYMPTOM, not a persistent hazard"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

The qiyas#132 polygon-corner-leakage cascade (Ticks 82, 83, 84, 85, 86, 87, 88, 91, 92, 93 — eight prior feedback memories under `feedback_bikar_polygon_corner_leakage_*`, `feedback_bikar_polygon_anchored_escape_*`, `feedback_bikar_polygon_corner_sharing_universal_tag_leakage`) is RESOLVED at the producer (bikar). The pattern those memories described — `.hexagon` source_primitives multiplicity inflated to 2 at lens-anchored polygon-corner vertices, square/pentagon/octagon emitting unexplained extra polyclass faces, parity-rule fits and counterexamples across D_3..D_8 — was a **single root cause**: bikar's face-walker emits a degenerate "lasso" cycle (4 vertices, all-arc, area ~0.02 px², Polsby-Popper ratio ~7.5e-7) at any lens-anchored polygon-corner DCEL vertex. The polygon-class-dependence and tangent-dependence patterns the cascade probed for were artifacts of that single sliver being *almost* invisible — its shape was geometry-dependent so probes saw different fingerprints, but the bug was always the same.

**Fix** (bikar commit 61c207b, 2026-05-27): gt-emitter rejects outlines with Polsby-Popper isoperimetric ratio < 1e-4 (n≥3 vertices, lens n=2/arcs=2 exempt). Filter at gt-emitter (consumer) not face-extractor (producer) because kernel tests pin documented topology (arc-region-identity buggy over-stamp counts, two-crossing-segments open faces). Tier 0 witness `packages/core/tests/render/gt-emitter-polygon-corner-leakage.test.ts` codifies the Tick 88 hex_lens fixture as regression gate.

**Why:** all 791 bikar tests green; the hex_lens Tick 88 fixture (the polygon-corner-leakage cascade's canonical baseline) no longer emits the 0.02 px² sliver; .hexagon face count drops from 2 to 1. The cascade's downstream qiyas-side measurements (HUNGARIAN matcher class-mismatch costs, signature pillars, anti-symmetry floor breaches that motivated qiyas#490) should now reflect the cleaner emit.

**How to apply:**

1. When reading any of the eight `feedback_bikar_polygon_corner_*` / `feedback_bikar_polygon_anchored_escape_*` memories, treat them as **historical investigation records**, not active hazards. The mechanism they documented (face-walker absorbs polygon corner at lens-shared vertex; tangent / degree / interior-angle / parity discriminators emerge from probing different fixture geometries) is fixed.

2. Before invoking the polygon-corner-leakage cascade's parity/degree/tangent matrix for any new investigation, regenerate the qiyas i1 corpus baselines (every fixture in `qiyas/calibration/i1-corpus/renders/`) against bikar core post-commit 61c207b — the existing baselines may bake in the sliver, and any qiyas anti-symmetry / matcher tolerances calibrated against those will measure differently now.

3. The Tick 23 "degree-6 all-arc tangent-sort breaks" hazard (`feedback_bikar_degree_6_all_arc_tangent_sort_breaks`) is **separately mechanistically distinct** — that's tangled cross-class lens faces at high-degree all-arc vertices, not the polygon-corner sliver. Tick 23 remains an open hazard for compositions like medallion-10 where 3+ lens circles converge.

4. If a new investigation surfaces a similar all-arc degenerate cycle (lasso, area < 1 px², Polsby-Popper < 1e-4) that the gt-emitter filter doesn't catch, the threshold may need refinement — check whether the new sliver has arcs and whether the lens exemption is too broad.

**Companion to** [[feedback_bikar_polygon_corner_leakage_deg4_non_monotonic]], [[feedback_bikar_polygon_corner_sharing_universal_tag_leakage]], [[feedback_bikar_polygon_corner_leakage_is_square_specific]], [[feedback_bikar_polygon_anchored_escape_is_square_specific]], [[feedback_bikar_polygon_anchored_escape_is_graded_non_monotonic]], [[feedback_bikar_polygon_corner_degree_orthogonal_to_tangent]], [[feedback_bikar_polygon_interior_angle_compounds_with_degree]], [[feedback_bikar_polygon_anchored_escape_hatch_boundary_collapse]] — those eight memories are SYMPTOM-LEVEL traces of the bug this memory marks resolved.
