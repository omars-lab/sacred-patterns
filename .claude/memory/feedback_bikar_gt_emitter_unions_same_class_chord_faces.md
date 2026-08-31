---
name: bikar-gt-emitter-unions-same-class-chord-faces
description: "bikar gt-emitter MERGES (unions) two same-face_class polygons sharing a chord edge into a single shape — outline becomes the union perimeter (chord removed), face_count records the merged count. REFINED 2026-06-11 (bikar 3f79bc7, Option E D1): chords tagged `line:<id>` (pattern-scope cutting lines) are now EXEMPT from the union — author-declared line cuts are never re-merged at emit. The residual union fires only on shared chords WITHOUT line: provenance (hand-authored sub-polygon chords) and is BY DESIGN (gt mirrors the raster's painted regions). REQUIRES shared edge — disjoint same-color faces are NOT unioned (Tick 63 corrected 2026-05-26). Tick 60 (qiyas#132)."
metadata:
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

**REFINED 2026-06-11 (bikar `3f79bc7`, line-primitive Option E D1 + D3):** edges tagged `line:<id>` — i.e. chords produced by PATTERN-scope face-cutting `line`/`segment`/`bisector`/`tangent` declarations — are now **exempt** from `unionSameColorEdges` via `collectCutEdgeKeys` (gt-emitter.ts). An author-declared line cut is never re-merged at emit: `square-and-diagonal-line.bkr.tmpl` (qiyas `22e07ba`, split=train) emits 2 distinct `.triangle` shapes with the L0 chord intact. The hazard below remains live **only** for same-class chord-sharing faces whose shared chord lacks `line:` provenance (e.g. hand-authored explicit sub-polygon chords, as in Tick 60 itself) — and that residual merge is **by design**, not a bug: gt.json mirrors the raster's painted regions, and two same-color faces sharing an untagged chord paint as one region. Per the decision doc's D2 addendum (`bikar/docs/decisions/2026-05-26-line-primitive-cascade-D1-D2-D3.md`), the fix for an unwanted merge is authoring-side: route the split through a pattern-scope line (gets the exemption) or give the sub-faces distinct classes. Tick 60's FALSIFIED explicit-subpolygon template stays falsified — its chord carries no `line:` tag. The "corpus cannot ship any line-bearing Tier 1 fixture" conclusion at the bottom of this memory is OBSOLETE (D1+D2+D3 all shipped; see [[feedback_bikar_line_primitive_render_only]] and [[feedback_bikar_gt_emitter_drops_unclassified_polygons]]).

---

**Original hazard record (2026-05-26, pre-D1; the union mechanism below still applies to non-`line:` chords):**

When two polygons sharing a chord edge both carry the same `face_class` (e.g., both tagged `.triangle` via `classify .triangle where sides == 3`), the bikar gt-emitter **MERGES them into a single union-shape** in gt.json. The component triangles' boundaries are erased; only their union perimeter survives. The `face_count` field on the merged shape records the original count (2 in the canonical case), but the shape's `type` and `vertex_count` reflect the union geometry (e.g., `type=square, vertex_count=4` when two triangles fuse back into their parent square).

**Why:** Demonstrated 2026-05-26 by qiyas#132 Tick 60 (FALSIFIED-square-and-diagonal-line-explicit-subpolygons). Construction: D_4 square (C0 r=100), `polygon tri_upper [C0.cpt0 C0.cpt1 C0.cpt2]` + `polygon tri_lower [C0.cpt0 C0.cpt2 C0.cpt3]` + `line L0 from C0.cpt0 to C0.cpt2`, with `classify .triangle where sides == 3`. SVG correctly emitted 2 triangle face paths (both `data-face-class="triangle"`). gt.json contained ONLY 2 shapes:
1. `{id: gt_G0000, type: "square", vertex_count: 4, face_count: 2, face_class: ".triangle", source_primitives: [layer:0×4, tri_lower×2, tri_upper×2], outline: [(512,977), (977,512), (512,46), (46,512)]}` — the union shape, with the diagonal (chord cpt0-cpt2) absent from the outline.
2. `{id: gt_C000, type: "circle"}` — C0.

The line L0 itself was also absent from gt.json (separate concern — likely same line-primitive render-only issue from Tick 59, or lines are simply not gt-emitted as shapes).

**How to apply:** When authoring Tier 1 corpus fixtures that split a polygon into sub-polygons (whether via line/bisector/tangent + intersect+re-author, or via direct sub-polygon declarations), **same-class sub-polygons sharing a chord WILL merge in gt.json**. To preserve their separateness as distinct gt shapes, use **heterogeneous classes**:

```
classify .tri_top where face_class == ".tri_top"    # see note below
classify .tri_bot where ...
```

But beware — the Tick 58 hetero-class hazard (`feedback_bikar_gt_emitter_drops_same_class_faces`) shows that heterogeneous tags can make things WORSE (dropping both rather than merging). The combined hazard map: same-class sharing-chord → merge (Tick 60); same-class sharing-arc-chord → drop (Ticks 54/55/56); hetero-class sharing-arc-chord → drop both (Tick 58). All three are facets of the same gt-emitter classify-dedup/merge family, keyed on shared boundary topology.

**Stop rule before authoring any sub-polygon-bearing Tier 1 fixture:** if two sub-polygons share an edge (chord, arc, or otherwise), assume the gt-emitter will either merge them (same class) or drop one/both (hetero class), per the hazard family. The only known clean topology is:
- Distinct primitive types (e.g., one triangle + one lens) — NOT same-shape-class siblings
- Non-shared boundaries (sub-polygons that are entirely disjoint, e.g., separated by a third intervening face)

**Companion to / contrast with:**
- [[feedback_bikar_gt_emitter_drops_same_class_faces]] (Ticks 54-58 — DROP hazard for same-class arc-chord-sharing faces). The drop vs merge distinction may be a function of whether the shared boundary is an arc (drop) or a line/chord (merge); Tick 60 is the first witness with a straight-line shared boundary and it merged rather than dropped, suggesting boundary geometry is load-bearing.
- [[feedback_bikar_gt_emitter_drops_unclassified_polygons]] (Tick 59 — DROP hazard for face_class=None polygons). Tick 60's classified triangles avoided D2 but hit D3.
- [[feedback_bikar_line_primitive_render_only]] (Tick 59 — D1; declared line doesn't cut polygons). Tick 60 worked around D1 by explicit sub-polygons; D3 then fired at the gt-emitter layer.

**Implications for the I1 corpus:** the entire "sub-polygon" construction strategy in bikar DSL is hostile to qiyas detector ingestion when sub-polygons share boundaries. The corpus needs either:
1. A bikar-side fix that preserves sub-polygon identity in gt.json (don't merge, don't drop — emit each as a distinct shape with its own component-level outline)
2. A DSL convention shift away from sub-polygons toward primitive-level composition (each "sub-polygon" emitted as a fully independent polygon with its own classify class — but then Tick 58's hetero-class drop hazard fires)
3. Documented acceptance that this entire topology class is uncoverable by the current bikar pipeline (file as a known gap in the cross-repo dependencies doc)

Tick 60 closes the line-primitive probe arc that opened with Tick 59. Two ticks, three foundational defects (D1 + D2 + D3). The bikar `line` primitive + sub-polygon authoring pattern is structurally incompatible with the gt-emitter at three independent layers; the corpus cannot ship any line-bearing Tier 1 fixture until one or more of these defects is resolved.

Falsified artifact retained as Tenet 18 witness; NOT in splits.json or corpus.json:
- `qiyas/calibration/i1-corpus/templates/FALSIFIED-square-and-diagonal-line-explicit-subpolygons.bkr.tmpl` + `renders/FALSIFIED-square-and-diagonal-line-explicit-subpolygons/` (Tick 60, D_4)

**CORRECTION 2026-05-26 (qiyas#132 Tick 63 re-diagnosis):** the earlier REFINEMENT below was WRONG about the mechanism. Re-inspecting the FALSIFIED-mirror-scalene-pair artifacts on 2026-05-26:
- SVG `render.svg` contains exactly ONE `class="scalene_tri"` path (NOT two). The earlier `grep -c 'class="scalene_tri"'` was misleading because it also matched `data-face-class="scalene_tri"` as a substring.
- gt.json has `face_count=1` (NOT 2 unioned) — the gt-emitter faithfully reported the single face that existed in the SVG.
- Therefore the gt-emitter is INNOCENT on Tick 63. The defect lives upstream in the bikar **evaluator's evalMirror path** (or the face-walker downstream of it): the `mirror around` block did not produce a reflected polygon face in the FaceGraph at all. Only the original triangle was emitted.
- The degenerate gt.json outline spanning both triangles' bbox (612px wide for a 200px triangle) is a separate symptom — the single emitted face's vertex set or outline metrics computation is grabbing coordinates from the mirror-block's residual primitives somehow, but the face_count of 1 is the load-bearing signal.

**Implication:** Tick 63 does NOT extend the Tick 60 union hazard to disjoint faces. The gt-emitter `unionSameColorEdges` (gt-emitter.ts:686) only unions when `occs.length === 2` (a shared edge exists) — disjoint faces cannot trigger it. The mechanism described in the earlier REFINEMENT ("union by color identity alone") is contradicted by the code.

**Real Tick 63 defect (re-filed):** bikar `mirror` DSL primitive evaluator emits SVG/face-walker geometry for only the original polygon, not its reflected copy. Probably a missing call to add the reflected polygon to the polygon registry or to the face-walker input graph. Filed as bikar follow-up (see task graph).

**RESOLVED 2026-05-27 (bikar 3ae578c, #597):** evalMirror now snapshots `env.polygons` keys before body evaluation and registers reflected copies under derived name `${baseId}__mirror` per docs/design/derived-shape-naming.md (Option A, #607). Templates that want the mirrored polygon's edges emitted into the face-walker opt in by adding `edges from <id>__mirror`. The mirror-scalene-pair template re-renders to 4 gt.json shapes (2 triangles + 2 circles), confirming the original face_count=1 falsification is dissolved. Tier 1 mirror compositional dimension is now covered.

Falsified artifact retained for reproduction:
- `qiyas/calibration/i1-corpus/templates/FALSIFIED-mirror-scalene-pair.bkr.tmpl` + `renders/FALSIFIED-mirror-scalene-pair/` (Tick 63)

**Original (now-superseded) REFINEMENT statement preserved below for audit trail:**

~~The union path fires on geometrically-disjoint same-color faces too, not only on chord-sharing pairs.~~ — FALSE per 2026-05-26 re-inspection. Tick 63 was the proposed witness; it doesn't hold. Tick 60 (chord-sharing same-class) remains the only confirmed gt-emitter union hazard documented above.
