---
name: bikar-gt-emitter-drops-unclassified-polygons
description: "RESOLVED 2026-06-11 (bikar fae9509, Option E D2, gt schema 1.23) — and the original diagnosis was WRONG: the drop gate was never classify, it is the FILL gate (selectEligibleFaces requires a fill color; filled faces with face_class=null DO emit). An authored shape whose faces all lack fill is now surfaced loudly via gt.json `uncovered_shapes[]` + CLI stderr warning instead of vanishing silently. Authoring rule: every shape needs a matching FILL rule (not classify) to appear in gt.json."
metadata:
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

**RESOLVED 2026-06-11 + premise corrected** — bikar commit `fae9509` (line-primitive Option E, D2 slice, gt schema 1.23).

**The original diagnosis was wrong (tenet C1 case study).** This memory previously claimed the gt-emitter's "classify-dedup pass discards polygons with face_class=None." D1-slice investigation (2026-06-11) falsified that: filled faces with `face_class=null` DO emit. The real drop gate is **FILL eligibility** — `selectEligibleFaces` (gt-emitter.ts) excludes any face without a fill color from `shapes`. Tick 59's square vanished because no `fill` rule matched it, not because no `classify` rule did. The misdiagnosis arose because corpus convention pairs classify and fill rules (`classify .x where sides == N` + `fill void where sides == N color c`), so the missing-classify and missing-fill conditions always co-occurred.

**Current behavior (D2, schema 1.23):**
- The fill gate itself is unchanged and correct: gt.json mirrors what the rasterized PNG shows, and the detector cannot see unfilled regions.
- The *silence* is fixed: `collectUncoveredShapeIds` diffs named-shape tags in the evaluator's edge graph against every emitted shape's `source_primitives`; an authored shape with zero trace lands in gt.json top-level `uncovered_shapes[]` (omitted when empty — healthy gt.json byte-identical to 1.22, no corpus regen) and the CLI prints a stderr WARNING naming the shapes and the likely fix.
- Granularity is shape-level by design: per-face drop logging would flag the unfilled background segments every polygon-in-circle fixture has (6-pattern corpus sweep incl. medallion10-iter14/star10 = zero false positives; the unfilled-square witness = exactly one).

**Authoring rule that survives:** for a shape to appear in gt.json, at least one of its faces needs a matching **fill** rule. A non-empty `uncovered_shapes` in a corpus render or a CLI WARNING during regen means a missing fill/classify pair — fix the template, don't ignore it.

Witness: `bikar/packages/core/tests/render/gt-emitter-uncovered-shapes.test.ts` (Tick 59 reproduction, filled control, partially-filled line-cut polygon). Decision doc: `bikar/docs/decisions/2026-05-26-line-primitive-cascade-D1-D2-D3.md` (Shipped — D2 addendum). Companions: [[feedback_bikar_line_primitive_render_only]] (Tick 59's other defect, fixed in D1), [[feedback_bikar_gt_emitter_drops_same_class_faces]] (Ticks 54-58 — distinct mechanism, still live), [[feedback_bikar_gt_emitter_unions_same_class_chord_faces]] (Tick 60 — `line:`-tagged cut chords now exempt from the union; non-line chords still merge by design).
