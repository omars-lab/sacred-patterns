---
name: bikar-line-primitive-render-only
description: "RESOLVED 2026-06-11 (bikar 3f79bc7, Option E D1): PATTERN-scope line-family primitives (`line`/`segment`/`bisector`/`tangent`) now ENROLL in the face-walker and genuinely cut faces, tagged `line:<id>`. BLUEPRINT-scope lines remain non-cutting derivation guides — that is the load-bearing authoring contract, not a residual bug. The old `intersect + re-author sub-polygons` workaround is obsolete for pattern-scope lines."
metadata:
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

**RESOLVED 2026-06-11** — bikar commit `3f79bc7` (line-primitive Option E, D1 slice) ended the render-only era for pattern-scope lines. Historical hazard + current contract below.

**Current behavior (Option E authoring contract):**
- **Pattern-scope** `line`/`segment`/`bisector`/`tangent` declarations push into `Environment.faceCuttingLines`; `buildLineCutEdges` (evaluator.ts) clips infinite lines to the geometry bbox (Liang-Barsky) and threads them into planar-graph extraction tagged `line:<id>`. A pattern-scope line genuinely cuts the faces it crosses.
- **Blueprint-scope** lines stay non-cutting guides. This is deliberate and load-bearing: enrolling blueprint guides would shatter blueprint-heavy patterns (e.g. Rosette-10's 10 guide lines) into construction slivers.
- Cut sub-faces keep their parent polygon's `shape_id` (`line:` is excluded from `isNamedShapeTag` in BOTH gt-emitter.ts and svg-renderer.ts twins); the gt-emitter's union-by-color walk exempts `line:`-tagged cut edges so same-class sub-faces are not merged back (the Tick 59/60 interaction).
- Companion D2 fix (bikar `fae9509`, schema 1.23): an authored shape that leaves zero trace in gt.json (fill gate dropped every face) is reported in gt.json `uncovered_shapes[]` + a CLI stderr warning — see [[feedback_bikar_gt_emitter_drops_unclassified_polygons]].

**Historical hazard (2026-05-26 → 2026-06-11, for reading old fixtures/ticks):** all four `env.lines.set` call sites (evalLine, evalBisector, evalTangent atPoint/fromPoint) were render-only — declared lines drew to SVG but `buildIntersectionGraph` never read `env.lines`, so crossed polygons emitted as single uncut faces (qiyas#132 Tick 59 witness, generalized by the Tick 62 audit). The era's workaround was `intersect L_id polygon_id` + re-author sub-polygons by name — obsolete now for pattern scope, but old corpus templates and ticks authored against it still reflect it.

**Corpus state:** Tick 59's entry is UN-FALSIFIED as `qiyas/calibration/i1-corpus/templates/square-and-diagonal-line.bkr.tmpl` (qiyas `22e07ba`, split=train) — the first line-cut fixture; the load-bearing change vs the falsified original is moving L0 to pattern scope. The falsified originals remain on disk as Tenet 18 witnesses (`FALSIFIED-square-and-diagonal-line.bkr.tmpl`; Tick 60's explicit-subpolygon variant stays FALSIFIED — its D3 union hazard for non-`line:`-tagged chords is still live, by design).

Witnesses: `bikar/packages/core/tests/dsl/line-face-cutting.test.ts` (D1, 5 tests incl. blueprint-guide control) + `bikar/packages/core/tests/render/gt-emitter-uncovered-shapes.test.ts` (D2). Decision doc: `bikar/docs/decisions/2026-05-26-line-primitive-cascade-D1-D2-D3.md` (Shipped addenda for both slices).
