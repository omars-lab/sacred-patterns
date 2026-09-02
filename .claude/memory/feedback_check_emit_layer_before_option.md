---
name: check-emit-layer-before-option
description: "Before authoring a complex new option for a partial-shape / DSL-as-source-of-truth cascade, verify the SVG renderer (or other emit layer) is actually emitting the data the proposed option assumes is missing"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When a cross-repo cascade involves a DSL-knows-fact → SVG-attribute → consumer-reads-fact pipeline (the Tenet 21 / 23 shape), and a downstream consumer (qiyas detector, scorer, matcher) appears to be missing information the producer (bikar evaluator) knows: **before authoring a new option that modifies the producer's evaluator semantics OR the consumer's heuristics, grep the SVG renderer for the attribute name.** The most common gap is not that the producer doesn't know the fact — it's that the producer knows but the SVG layer drops it.

**Why:** The 2026-05-25 cascade-#106 Option I empirical finding. The reopened decision doc recommended Option E (modify bikar `clip` semantic via CGAL Arrangement_2 pattern, 3-5 days of work, half-edge subdivision impl) on the hypothesis that bikar's clip drops boundary-incident inside fragments. The Tier 0/1 composition fixture (bikar 606bc7c) proved bikar's clip ALREADY preserves them via `partial: true` / `clippedAtBoundary` Face annotations — both ACCEPTED in evaluator-clip.test.ts:51-74 since the cascade was first authored. The actual gap was at the SVG layer: `svg-renderer.ts:buildFaceDataAttrs` emitted `data-face-class` and `data-symmetry-fold` but never emitted `data-partial` or `data-clipped-boundary`. Medallion-10 iter-21-probe render.svg had 722 face elements with zero partial attributes. The fix was a 9-line emit-site change + 2 vitest assertions (bikar 8c17615), not a 3-5 day half-edge subdivision rewrite.

**How to apply:**
1. When a partial-shape / metadata-cascade decision doc identifies a "qiyas can't see X" symptom, FIRST grep the producer's emit code for the attribute that would carry X to qiyas:
   ```
   grep -nE "data-X|emit.*X|push.*X" packages/core/src/render/svg-renderer.ts
   ```
2. Cross-check that the producer's *evaluator* already produces the in-memory fact (read the relevant `.test.ts` for the evaluator path; if a test asserts the property on the Face/Shape object, the producer side is done).
3. If (a) the evaluator produces it and (b) the renderer doesn't emit it: the entire option is a 1-day emit-site change + 2 tests + contract amendment. File it as a Phase 2 contract row, not a new decision doc.
4. If (a) and (b) both ship and the symptom persists: NOW the consumer-side wiring is the real bottleneck and a new option is justified.
5. This applies to ANY data-* attribute pipeline — `data-face-class`, `data-symmetry-fold`, `data-construction-source`, and the future `data-rotation-deg` / `data-class` candidates.

**Companion to:**
- [[feedback_cascade_primitive_semantic_composition]] (Tier 0 composition fixture surfaces emit-layer gaps that composite-only validation misses)
- [[feedback_consumer_audit_construction_contracts]] (audit both producer AND consumer surfaces — including emit-layer-as-producer)
- [[feedback_option_e_vertex_identity_wrong_layer]] (general lesson: locate the bug at the correct layer before choosing the option's mechanism)
- sacred-patterns Tenet 23 / bikar Tenet 21 (DSL-as-source-of-truth)
- DSL Metadata Contract at sacred-patterns/docs/dsl-metadata-contract.md

**Failure mode this prevents:** authorizing a multi-day architectural option (CGAL subdivision, intersect-primitive, qiyas detector rework) when the actual gap is a one-attribute emit-site addition in the renderer. The cost of running the grep before authoring Option E was ~10 seconds; the cost of NOT running it would have been 3-5 days of subdivision impl.

**Anti-pattern this names:** treating the SVG renderer as a transparent identity function between evaluator output and consumer input. Renderers are emit *projectors* — they choose what facts to carry forward and silently drop the rest. Every cascade that depends on "qiyas reads X from bikar SVG" implicitly depends on bikar's renderer emitting X, and that's a separate audit surface from "bikar evaluator computes X" or "qiyas detector consumes X."
