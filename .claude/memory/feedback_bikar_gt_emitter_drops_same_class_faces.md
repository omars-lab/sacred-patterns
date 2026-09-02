---
name: bikar-gt-emitter-drops-same-class-faces
description: "when bikar's evaluator emits multiple faces sharing the same boundary topology (i.e., spanning the same chord between the same named vertex pair, as in any shared-edge construction where both arcs CL1 and CL2 terminate at the same polygon-vertex pair), the gt-emitter drops some or all of them from gt.json entirely — even though the SVG renders all faces correctly. This is distinct from the face-walker absorption hazards: the bikar evaluator preserves the topology, but the gt-emitter does not propagate it. POLYGON-ORDER-INDEPENDENT and PLACEMENT-VARIANT-INDEPENDENT: confirmed at D_4 (Tick 54), D_6 (Tick 55), D_8 (Tick 56) across BOTH-CL-INSIDE and ONE-CL-INSIDE-ONE-OUTSIDE placement variants. CLASS-LABEL-INDEPENDENT (Tick 58): heterogeneous class tags (.lens_outer / .lens_inner) on the two arcs do NOT save the lens faces — drops BOTH lens faces (worse than Tick 50's homogeneous case which kept 1 of 2). DISAMBIGUATED via disjoint-witness (Tick 57): when ≥2 same-class faces do NOT share boundary topology (scalene-and-dual-asymmetric-lens: 2 lenses sharing no vertices with the polygon or each other), they survive cleanly with all 8 shapes in gt.json. So the trigger is shared boundary topology (same chord-vertex-pair), not the class multiplicity, and the class label is NOT a load-bearing dodge — both same and hetero classes fail."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When the bikar evaluator emits MULTIPLE distinct faces with the SAME `face_class` (e.g., two `.asymmetric_lens` faces from any shared-edge construction that produces both an "outer cap" and an "inner lens" region), the bikar gt-emitter drops some or all of them from gt.json. The SVG render is correct (all faces present with `data-face-class=asymmetric_lens` and distinct `data-face-index` values), but `gt.json["shapes"]` is missing at least one. **The hazard is polygon-order-independent AND placement-variant-independent: confirmed at D_4/D_6 both-CL-inside (Ticks 54/55, drops ALL same-class) and D_4/D_6/D_8 one-CL-inside-one-outside (Ticks 50/51/56, drops the SECOND same-class face).**

**Why:** Originally discovered 2026-05-26 by qiyas#132 Tick 54 (square-and-asymmetric-lens-shared-edge-both-inside, D_4 + L=141.42, where BOTH same-class faces dropped → 4 shapes vs expected 5). Generalized 2026-05-26 by Tick 55 (D_6 both-CL-inside, identical mechanism). Then REFRAMED 2026-05-26 by Tick 56 (D_8 one-CL-inside) which revealed the defect ALSO fires on the ONE-CL-INSIDE topology — drops 1 of 2 same-class faces (gt.json has 5 shapes total: 1 lens kept + 1 unknown polygon + 3 circles, but SVG has 2 lens faces). This retroactively reframes Ticks 50/51 (which I had thought "passed" with 5 shapes): they too were silently dropping the second `.asymmetric_lens` face. The defect is universal across any construction producing ≥2 faces with the same face_class.

*Tick 55 construction (both-CL-inside drops all):* D_6 hexagon (C0 r=100), chord cpt0=(100,0)→cpt1=(50, 86.6025), L=100. CL1 at M+20·perp = (57.68, 33.30), r=53.85 (h=20 inside, |center|=66.6). CL2 at M+40·perp = (40.36, 23.30), r=64.03 (h=40 inside, |center|=46.6, near origin). Both CL pass through {cpt0, cpt1} → shared-edge topology, both on interior side. bikar SVG inspection confirms 3 face paths: `grep -o 'data-face-class="[^"]*"'` → 1 hexagon + 2 asymmetric_lens. gt.json: 4 shapes (1 unknown-typed hexagon polygon + 3 circles). Both .asymmetric_lens faces dropped.

*Tick 56 construction (one-CL-inside drops second):* D_8 octagon (C0 r=100), chord cpt0=(100,0)→cpt1=(70.71, 70.71), L=76.54. CL1 at M-20·perp = (103.83, 43.01) r=43.18 (h=20 OUTSIDE, |center|=112.4). CL2 at M+40·perp = (48.40, 20.05) r=55.36 (h=40 INSIDE, |center|=52.4). Both CL pass through {cpt0, cpt1}. bikar SVG: 3 face paths (1 octagon + 2 asymmetric_lens). gt.json: 5 shapes (1 lens kept + 1 unknown polygon + 3 circles). The SECOND .asymmetric_lens face is silently dropped — same defect, less severe presentation. Construction: D_4 square + chord cpt0=(100,0)→cpt1=(0,100), L=141.42. CL1=(28.79, 28.79) r=76.81 + CL2=(7.57, 7.57) r=92.74, BOTH on polygon-INTERIOR side. bikar SVG output:
```
<path data-face-class="asymmetric_lens" data-face-index="0" data-sides="2" ... />  (outer cap, chord + CL2 short arc)
<path data-face-class="square" data-face-index="1" data-sides="4" ... />           (clean square, 4 line edges)
<path data-face-class="asymmetric_lens" data-face-index="3" data-sides="2" ... />  (inner asymmetric lens, CL1 arc + CL2 arc)
```
Three face paths emitted (face-index 0, 1, 3 — index 2 was probably an outer-face placeholder skipped). gt.json output:
```
shapes: [
  { type: square, class: .square },
  { type: circle }, { type: circle }, { type: circle }
]
```
Both `.asymmetric_lens`-classed faces missing. 4 shapes vs expected 5.

**Distinct from the face-walker absorption hazards** ([[feedback_bikar_face_walker_both_cl_outside_lens_absorption]], [[feedback_bikar_face_walker_short_chord_octagon_absorption]], [[feedback_bikar_face_walker_polygon_edge_absorbed_by_coincident_arcs]]): in those cases the face-walker itself fails to enroll all faces (the SVG is missing the absorbed face too). Here the face-walker is correct; the defect lives downstream in the gt-emitter's shape-extraction / classify-deduplication step.

**The hazard's discriminator (REFINED 2026-05-26 by Tick 57, then REFINED FURTHER by Tick 58):** any construction where ≥2 emitted faces share boundary topology — specifically: span the same chord between the same named vertex pair, as in shared-edge constructions where the two arcs CL1+CL2 both terminate at the same {cpt0, cpt1} polygon-vertex pair. **DISAMBIGUATING WITNESSES:**

- **Disjoint-witness (Tick 57):** `scalene-and-dual-asymmetric-lens` (Tier 1, already in corpus) has 2 disjoint asymmetric lenses both with `.asymmetric_lens` class but each on its own pair of CL circles with no shared vertices between the two lenses or with the polygon — gt.json has all 8 shapes (1 triangle + 2 lens + 5 circles), both same-class lens faces preserved. So **same-class alone is NOT the trigger**.

- **Hetero-class-witness (Tick 58, FALSIFIED):** `FALSIFIED-square-and-asymmetric-lens-shared-edge-hetero-class` — IDENTICAL geometry to Tick 50, only classify rules differ (`.lens_outer` on CL1, `.lens_inner` on CL2). SVG identical (3 face paths: 2 lens sides=2 + 1 square sides=4). gt.json: **4 shapes** (1 square + 3 circles, BOTH lens faces dropped). **WORSE than Tick 50's homogeneous case** which kept 1 of 2 lens faces. So **heterogeneous class labels do NOT dodge the hazard** — actually make it worse, likely because the gt-emitter's classify-dedup keys on something that collapses hetero classes to "unclassified" and discards them entirely.

The hazard's trigger is therefore **purely the boundary-topology coincidence (shared chord between same named vertex pair)**. Class labels are neither necessary nor sufficient: same-class faces that are topologically disjoint survive (Tick 57); hetero-class faces that share topology still get dropped, harder (Tick 58). The classify-by-predicate hazard ([[feedback_classify_by_predicate_cannot_witness_same_class_cross_refs]]) describes the inverse: the predicate matches multiple faces but tags them ambiguously. This one describes what happens AFTER classify succeeds with multiple same-class hits: the gt-emitter drops them.

**Detector still scored** the absorbed gt as canonical (because gt.json is itself the source of truth for the detector). The defect is invisible from qiyas's perspective; it's a bikar-pipeline correctness defect that compounds with the face-walker absorption hazard family.

**How to apply:** When authoring DSL `.classN` tags in the I1 corpus, REJECT shared-edge constructions where ≥2 emitted face regions share boundary topology (same chord between same named vertex pair, as in any shared-edge with both CLs emitting through the same {cpt0, cpt1}) — regardless of class label. **Heterogeneous class tags do NOT dodge the hazard** (Tick 58 falsified this hope). Disjoint same-class faces (separate CL pairs, no shared vertices) are FINE — see `scalene-and-dual-asymmetric-lens` as the in-corpus topologically-disjoint baseline. **For a workable shared-arc topology in the corpus**, the only escape is changing the GEOMETRY so the two arcs don't span the same chord: e.g., shared-vertex (one arc endpoint on a polygon vertex, the other elsewhere) or fully-disjoint placement. **Confirmed polygon-order-independent AND placement-variant-independent across D_4/D_6/D_8 and both-CL-inside vs one-CL-inside; no further probes needed to establish the generalization.** If the topology genuinely produces multiple same-class regions (e.g., shared-edge lens, any nested/concentric construction, any sub-region split that yields ≥2 same-class faces), either (a) use heterogeneous class tags (`.lens_outer`, `.lens_inner` instead of two `.asymmetric_lens`), or (b) accept that gt.json will under-represent the topology and treat the construction as a known FALSIFIED witness. **Retroactive note:** any "passing" shared-edge asymmetric-lens entry in the I1 corpus (Ticks 50/51 + their kin) is silently exhibiting this defect — they look right because they have ≥1 lens shape, but the SVG always has 2 lens faces. If you're auditing the corpus for hidden defect signatures, grep render.svg for `data-face-class` counts and compare against gt.json shape types.

**For the bikar repo:** the gt-emitter's shape-extraction step (likely in `face-extractor.ts` or `gt-emitter.ts`) needs to enroll one shape per distinct face, NOT one shape per distinct `face_class`. A fix would generalize across all "same-class multiplicity" constructions and may also resolve some of the absorption-family hazards' downstream impact (where the absorbed polyclass face's source_primitives multiset is currently the only signal of what was absorbed).

**Companion to / contrast with:**
- [[feedback_bikar_face_walker_both_cl_outside_lens_absorption]] (Ticks 52+53): face-walker absorption — SVG itself is missing the face. Here SVG is intact, gt drops it.
- [[feedback_classify_by_predicate_cannot_witness_same_class_cross_refs]] (Tick 9, 15): classify-by-`sides==N` predicates tag ambiguously. Adjacent failure mode in the classify pipeline; this entry is the downstream emit-side consequence.
- [[feedback_asymmetric_lens_intrudes_polygon_interior]] (Tick 50): the one-CL-inside variant where the polygon face has mixed line+arc boundary but the lens still emits. Tick 54 changes only the second CL's side (outside → inside) and gets a completely different defect.

Falsified artifacts retained as Tenet 18 witnesses; NOT in splits.json or corpus.json:
- `qiyas/calibration/i1-corpus/templates/FALSIFIED-square-and-asymmetric-lens-shared-edge-both-inside.bkr.tmpl` + `renders/FALSIFIED-square-and-asymmetric-lens-shared-edge-both-inside/` (Tick 54, D_4, both-CL-inside)
- `qiyas/calibration/i1-corpus/templates/FALSIFIED-hexagon-and-asymmetric-lens-shared-edge-both-inside.bkr.tmpl` + `renders/FALSIFIED-hexagon-and-asymmetric-lens-shared-edge-both-inside/` (Tick 55, D_6, both-CL-inside)
- `qiyas/calibration/i1-corpus/templates/FALSIFIED-octagon-and-asymmetric-lens-shared-edge.bkr.tmpl` + `renders/FALSIFIED-octagon-and-asymmetric-lens-shared-edge/` (Tick 56, D_8, one-CL-inside — partial-drop witness)

**Already-enrolled silently-defective entries (do NOT remove from corpus to preserve historical detector calibration baseline; flag in audit):**
- `square-and-asymmetric-lens-shared-edge` (Tick 50, D_4, one-CL-inside)
- `hexagon-and-asymmetric-lens-shared-edge` (Tick 51, D_6, one-CL-inside)
