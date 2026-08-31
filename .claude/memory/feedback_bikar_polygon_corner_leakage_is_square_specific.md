---
name: bikar-polygon-corner-leakage-is-square-specific
description: "REFINES the UNIVERSAL-LEAKAGE claim from Tick 82 (qiyas#132 Tick 87): pentagon (D_5, 108° interior at P) at deg-4 minimum + 1 lens + safe tangents produces a CLEAN ESCAPE fingerprint — 5 shapes (1 pentagon + 1 lens + 3 circles), pentagon face PURE (`.pentagon`×5 only), lens face PURE (`.lens_a`×2 only), ZERO leakage in either direction. FALSIFIES Tick 82's `polygon-corner sharing leaks tags universally regardless of polygon class' claim. Combined with Tick 83 (square clean-escape at deg-6) AND Tick 82 (square leaks at deg-4), the square is now multi-anomalous: WORST polygon at deg-4 (only polygon to leak), BEST polygon at deg-6 (only polygon to escape). Tentative unifying mechanism: square polygon-edge tangents (45°/135°) are exactly ±45° from the polygon-interior axis (+x→inside); the exact ±45° symmetry is the load-bearing variable for both anomalies."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When a polygon vertex P doubles as the corner of a single lens at safe-separation tangents (≥30° pairwise) at minimum-degree DCEL (degree-4 = 2 polygon edges + 2 lens arcs), the polygon-corner tag-leakage is NOT universal across polygon classes as Tick 82 claimed — it is SQUARE-SPECIFIC. The matrix at deg-4 + 1 lens + safe tangents:

- **Square (90° interior, D_4, Tick 82):** ASYMMETRIC LEAK. Polygon face polyclass-mixed with `.lens_a`; lens face stays pure.
- **Pentagon (108° interior, D_5, Tick 87):** CLEAN ESCAPE. Both polygon face AND lens face pure; zero leakage in either direction.

**Why:** qiyas#132 Tick 87 (2026-05-27) authored `pentagon-with-lens-at-vertex-separated-tangents.bkr.tmpl` to test the polygon-class-dependence of the Tick 82 universal-leakage claim at minimum degree. Tick 17 (simplest-first) applied: deg-6 + 3-lens packing at D_5 has no safe arrangement (pentagon edges 54°/126° leave only narrow safe windows; no 3-lens packing keeps ALL pairwise tangent differences ≥30° AND ≥30° from both pentagon edges). Deg-4 + 1 lens isolates the polygon-class effect at minimum degree before re-attempting deg-6 grading.

Geometry: C0=(0,0) r=100 ÷5 → pentagon inscribed; P=C0.cpt0=(100,0). CL_shared=(89.5811, 59.0885) r=60 (tangent 10° at P, center perpendicular to tangent in +y direction toward pentagon exterior). CL_a=(140, 0) r=40 (tangent 90° at P, center perpendicular to tangent in +x direction outside C0). Pentagon edges at P: P→cpt1 tangent 126°, P→cpt4 tangent 54°. Pairwise tangent differences (mod 180°): edge_54 vs edge_126 = 72° (exterior wedge), edge_54 vs CL_shared(10°) = 44°, edge_54 vs CL_a(90°) = 36°, edge_126 vs CL_shared(10°) = 64°, edge_126 vs CL_a(90°) = 36°, CL_shared vs CL_a = 80°. Minimum separation 36°, no co-tangent. Same hazard level as Ticks 82/83 (safe).

**Render verdict (PASS, Risk (i) D_5 ASYMMETRIC LEAK FALSIFIED, both faces clean):**
- shape[0]: type=pentagon, src=[`.pentagon`×5, `layer:0`×5, `pentagon_poly`×5] — CLEAN, NO `.lens_a` leak
- shape[1]: type=lens, src=[`.lens_a`×2, `C0:arc:#0`, `C0:arc:#1`, `layer:0`×2] — CLEAN, NO `.pentagon` leak
- shapes[2-4]: 3 circles

Total 5 shapes. Source primitives perfectly disjoint between polygon face and lens face.

**The refuted claim:** Tick 82's "polygon-corner sharing leaks tags universally regardless of polygon class, even at deg-4 minimum + safe tangents" is FALSE. The universal-leakage claim was square-specific, just like the absorption rule. Two square-specific defects now empirically identified:

1. **ABSORPTION exception at deg-6 + safe tangents (Tick 83):** square escapes while triangle/hexagon absorb (refined further by Tick 86: octagon partial-escapes).
2. **LEAKAGE exception at deg-4 + safe tangents (Tick 82):** square leaks while pentagon stays clean.

**These point in OPPOSITE directions:** the square is the WORST polygon at deg-4 (leaks tags into the polygon face when no other polygon does) AND the BEST polygon at deg-6 (cleanly escapes absorption when no other polygon does). The square is multi-anomalous across the polygon-anchored-vertex matrix.

**Tentative unifying mechanism (NOT closed-form yet):** bikar's tangent-sort tie-break behavior at degree-N all-arc/mixed DCEL vertices interacts with the polygon's internal-bisector alignment. The square's polygon-edge tangents (45°/135°) are exactly ±45° from the polygon-interior axis (+x→inside). Pentagon's are 54°/126° (±36° from polygon-interior axis on inscribed-in-C0-at-cpt0 setup). The exact ±45° symmetry may be the load-bearing variable for both anomalies:
- **At deg-4** (Tick 82): the exact ±45° polygon-edge tangents make the face-walker assign one lens tangent to the polygon cycle (leakage). Pentagon's ±36° avoids the tie-break and assigns cleanly.
- **At deg-6** (Tick 83): the exact ±45° polygon-edge tangents create the symmetric tangent-sort that resolves the 6-way ordering cleanly (escape). Triangle (±30°), hexagon (±60°), octagon (±67.5°) all break the symmetry that the square uniquely satisfies.

Without bikar face-walker source-read, this is a tentative mechanism explanation. The closed-form rule has NOT emerged yet — requires either source-level audit of the tangent-sort tie-break OR further witness ticks (heptagon 128.57°/D_7 at deg-4+1 lens; hexagon D_6 at deg-4+1 lens; pentagon D_5 at carefully-engineered deg-6) to fully characterize.

**How to apply:** (a) **Refined leakage matrix** (replaces Tick 82's universal-leakage claim): polygon-corner-shared lens vertex at deg-4 minimum + safe tangents leaks tags ONLY when polygon is square (D_4); pentagon (D_5) stays clean; D_3/D_6/D_7/D_8 unknown — likely some additional anomalies among them; (b) **For cascade authoring:** the polygon-anchored escape hatch's safety claim at deg-4 + 1 lens + safe tangents is now POSITIVE for non-square polygons (pentagon witness empirically supports cross-polygon use without leakage), but witness count is N=1 — extend to D_3/D_6/D_7 before relying universally; (c) **For downstream consumers:** dominant-tag voting remains universally safe; treating "pure polygon face with no lens leakage" as a polygon-face witness at HIGH confidence is appropriate for D_5 topologies; (d) **Open follow-up witness candidates:** heptagon (128.57°/D_7) — between hexagon and octagon, tests if leakage extends to D_7; hexagon (D_6) at deg-4+1 lens — tests if hexagon's deg-6 absorption (Tick 85) carries down to deg-4 leakage like square does; pentagon at deg-6 with 3-lens packing (requires non-safe-tangent compromise) — tests if D_5 escapes deg-6 too; (e) **The witness IS the limitation:** bikar's face-walker behavior at deg-4 + 1 lens + safe tangents is now documented across 2 ticks (82 D_4 leak, 87 D_5 clean); empirical taxonomy at this matrix cell is partial — needs at least 1 more witness at D_6 or D_7 to discriminate between "square-only leakage" and "low-D_N leakage with monotone transition."

**Companion to:** [[feedback_bikar_polygon_anchored_escape_is_graded_non_monotonic]] (Tick 86 — octagon D_8 partial escape at deg-6; the deg-6 matrix matrix being graded), [[feedback_bikar_polygon_anchored_escape_is_square_specific]] (Tick 85 — original square-only claim at deg-6 NOW REFINED to D_4 + D_8 escape variants; this entry is the deg-4 equivalent), [[feedback_bikar_polygon_interior_angle_compounds_with_degree]] (Tick 84 — interior-angle monotonicity refuted at deg-6), [[feedback_bikar_polygon_corner_degree_orthogonal_to_tangent]] (Tick 83 — original deg-6 escape claim, narrowed by Ticks 84/85), [[feedback_bikar_polygon_corner_sharing_universal_tag_leakage]] (Tick 82 — universal-leakage claim NOW REFUTED by this entry; leakage is square-specific), [[feedback_bikar_polygon_anchored_escape_hatch_boundary_collapse]] (Tick 81 — square + co-tangent absorption), [[feedback_bikar_homogeneous_radius_degree_4_tangent_contamination]] (Ticks 77/79 — underlying tangent-sort tie-break defect that likely powers all polygon-class anomalies).
