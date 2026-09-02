---
name: bikar-face-walker-both-cl-outside-lens-absorption
description: "when an arc-polygon SHARED-EDGE construction places BOTH lens circles on the polygon-EXTERIOR side of the shared chord (asymmetric or symmetric), the bikar face-walker absorbs the lens face entirely — uses the inner (smaller-distance-to-chord) CL arc as the polygon boundary, drops the outer CL arc, and emits a single polyclass face instead of 2 separate faces. POLYGON-ORDER-INDEPENDENT: confirmed at both D_4 (Tick 52) and D_6 (Tick 53)."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When an arc-polygon SHARED-EDGE construction (both CL endpoints coincident with polygon edge endpoints) places BOTH construction circles on the polygon-EXTERIOR side of the shared chord, the bikar face-walker emits a SINGLE absorbed face with `(N-1) polygon edges + 1 inner CL arc` and DROPS the lens face entirely. The outer CL arc is unused; the lens region between CL1 and CL2 never emits as its own face. **The hazard is polygon-order-independent: confirmed at D_4 (Tick 52) and D_6 (Tick 53), with the same mechanism each time.**

**Why:** Demonstrated 2026-05-26 by qiyas#132 Tick 52 (square-and-asymmetric-lens-shared-edge-both-outside, D_4 + L=141.42) and CONFIRMED 2026-05-26 by Tick 53 (hexagon-and-asymmetric-lens-shared-edge-both-outside, D_6 + L=100).

*Tick 52 construction:* D_4 square (C0 r=100), chord cpt0=(100,0)→cpt1=(0,100), L=141.42. CL1 at M+30·perp = (71.21, 71.21), r=76.81 (h=30 outside, |center|=100.71). CL2 at M+60·perp = (92.43, 92.43), r=92.74 (h=60 outside, |center|=130.71). Both CL pass through {cpt0, cpt1} → shared-edge topology, both on exterior side → asymmetric lens entirely outside the square.

*Tick 53 construction:* D_6 hexagon (C0 r=100), chord cpt0=(100,0)→cpt1=(50, 86.6025), L=100. CL1 at M+20·perp = (92.32, 53.30), r=53.85 (h=20 outside, |center|=106.60). CL2 at M+40·perp = (109.64, 63.30), r=64.03 (h=40 outside, |center|=126.60). Same topology as Tick 52 at a different polygon order + shorter chord. Same absorption pattern: 4 shapes emit (1 polyclass face with 5 hexagon_poly line edges + 1 absorbed CL1 arc + 3 circles); lens face missing entirely. source_primitives signature: `[.asymmetric_lens, C0:arc:#0, hexagon_poly×5, layer:0×6]` (the orphan `.asymmetric_lens` tag survives but the lens face never emits, matching Tick 52's signature).

Expected output: 5 shapes (square line-only + asymmetric lens + 3 circles). Actual output: 4 shapes:
- 1 polyclass face: 3 line edges (cpt1→cpt2→cpt3→cpt0) + 1 CL1 arc (sweep cpt1→cpt0 on CL1, the smaller exterior circle) replacing the cpt0→cpt1 polygon edge. source_primitives=[.asymmetric_lens, C0:arc:#0, layer:0×4, square_poly×3] — note: one .asymmetric_lens tag survives but the lens face never emits.
- 3 circles (C0, CL1, CL2)
- 0 lens face

The face-walker's choice of CL1 (inner) over CL2 (outer) as the polygon boundary: the polygon's exterior on this chord-side already contains BOTH CL arcs; the walker picks the closer-to-chord arc (CL1) as the boundary because that's the first arc it encounters when walking outward from cpt0. The region between CL1 and CL2 (the asymmetric lens) and the region between CL1 and the chord both become "outside" topologically equivalent to the same face-walker traversal.

Detector still scored `ari_a_vs_b=1.0` and `ari_fused_vs_b=1.0` because the gt.json only contains 4 shapes (the lens isn't in ground truth either — bikar's face extractor is the source of ground truth, not an external oracle). The defect is invisible from qiyas's perspective; it's a bikar-pipeline correctness defect.

**Companion to / contrast with:**
- [[feedback_asymmetric_lens_intrudes_polygon_interior]] (Tick 50, the ONE-CL-INSIDE topology where the polygon face emits with mixed line+arc boundary but the lens DOES emit as its own face). The contrast pair (Tick 50 + Tick 52, same square + same asymmetric construction modulo CL2 placement) localizes the absorption hazard: it's not "asymmetric placement" or "shared-edge topology" alone — it's specifically "both CL on the polygon-exterior side." When one CL is inside, both faces emit.
- [[feedback_bikar_face_walker_short_chord_octagon_absorption]] (Tick 46, D_8 short-chord). Distinct trigger: that hazard requires a high-order polygon + short chord; Tick 52 fires at D_4 + L=141 (NOT short). The two absorption families are independent.
- [[feedback_bikar_face_walker_polygon_edge_absorbed_by_coincident_arcs]] (Tick 17, two arcs spanning the same chord with same polygon edge endpoints). Tick 17 produces a polyclass face but with sides=(4,4,5) — different absorption arithmetic; Tick 52 produces sides=4 (looks like a "clean" square) but with one arc edge silently replacing a line edge.

**How to apply:** When authoring asymmetric (or symmetric) shared-edge entries in the I1 corpus, REJECT both-CL-on-same-side-of-chord constructions for any polygon order. **Confirmed polygon-order-independent at D_4 (Tick 52) and D_6 (Tick 53); do not waste a slot probing D_8 — the generalization is established.** The minimum viable shared-edge asymmetric layout is "one CL inside, one CL outside" (Tick 50 pattern) — that produces the mixed-boundary topology correctly. If you specifically want to test a clean line-only polygon boundary with asymmetric lens, use the SHARED-VERTEX topology (Ticks 47/48/49), not shared-edge with both-CL-outside.

For the bikar repo: this is the same family of face-walker absorption bugs that Tick 46 and Tick 17 surfaced. A fix would generalize across all three (and the broader hazard family memory `feedback_bikar_face_walker_polygon_edge_absorbed_by_coincident_arcs`). The DSL spec contract for arc-polygon shared-edge topologies needs a documented invariant: "if N arcs share the same chord endpoints with a polygon edge, the face-walker must emit one face per arc + the polygon face (N+1 total)." Current behavior absorbs them.

Falsified artifacts retained as Tenet 18 witnesses; NOT in splits.json or corpus.json:
- `qiyas/calibration/i1-corpus/templates/FALSIFIED-square-and-asymmetric-lens-shared-edge-both-outside.bkr.tmpl` + `renders/FALSIFIED-square-and-asymmetric-lens-shared-edge-both-outside/` (Tick 52, D_4)
- `qiyas/calibration/i1-corpus/templates/FALSIFIED-hexagon-and-asymmetric-lens-shared-edge-both-outside.bkr.tmpl` + `renders/FALSIFIED-hexagon-and-asymmetric-lens-shared-edge-both-outside/` (Tick 53, D_6)
