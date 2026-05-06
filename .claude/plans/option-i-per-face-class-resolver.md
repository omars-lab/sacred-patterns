---
status: APPROVED — implementation in progress (owner overrode wait-for-decision 2026-05-06)
discovered: 2026-05-06
owner: omar (override of /loop hard-stop wait)
parent-escalation: petal-2ring-q3-actual-face-count-divergence.md
related:
  - decision: qiyas/docs/decisions/2026-05-05-petal-n-2ring-class-partition.md
  - cascade-plan: sacred-patterns/.claude/plans/shape-identity-detection-cascade.md
  - cgal-references: see Option I body in parent escalation doc
---

# Option I implementation plan — per-face class resolver in bikar gt-emitter

## What this plan implements

Plain-English: today the bikar gt-emitter records every class tag from a face's
boundary edges as a multiset (`source_primitives = [".x_petal", ".x_petal",
".y_petal", ".y_petal", ...]`). That works fine when all the boundary edges
agree, but on a Petal-2-Ring lens face — where `.x_petal` arcs and `.y_petal`
arcs share the same boundary — the multiset gives downstream consumers no
single per-face label they can partition on. CGAL's Arrangement_2 library
solves this by parameterizing per-face data directly (`Arr_extended_dcel<…,
FData>`) and using a combiner functor (`Arr_face_overlay_traits<…,
OvlFaceData>`) to compute the per-face label from edge-side data. We're adding
the same layer to bikar.

The technical name for the addition: a **per-face class resolver** that runs
once per face after the perimeter walk, takes the face's per-edge class tags
(weighted by arc length), and emits a single canonical per-face class label.
The label lands on `gt_G####.params.face_class` (and is also surfaced in
`evidence.face_class`) alongside the existing `source_primitives` multiset
(which we keep — it's strictly more information than the per-face label).

## Slice 0 — smallest mergeable slice (this plan)

The goal of slice 0 is a one-shot end-to-end demonstration that the resolver
works on the very face that surfaced the divergence. Constraints:

- **Hard-coded combiner choice.** No DSL surface in slice 0. The combiner is
  always `dominant_arc` (longest-arc-length wins; ties broken by lex order).
- **No new style-block syntax.** No parser changes. No
  `face_class_resolver` directive yet.
- **Default-on.** Every face gets `face_class` populated; if the multiset is
  uniform, `face_class = that single tag`; if mixed, the resolver picks.
- **Backwards-compatible.** `source_primitives` is unchanged; `face_class` is
  a new optional field, additive on the schema.

Acceptance for slice 0:

1. Build bikar locally; render `/tmp/petal-2ring-2class/Petal-2-Ring-2class.bkr`.
2. The resulting `pattern.gt.json` has 6 lens shapes (unchanged) but each one
   carries a non-empty `params.face_class` ∈ {`.x_petal`, `.y_petal`}.
3. Distribution of per-face labels: 3 X-faces and 3 Y-faces (the geometry of
   Petal-2-Ring's 6 lens regions: alternating X/Y around the ring).
4. **Correctness check:** the X-classified faces are the ones whose boundary
   X-arcs are longer in total than Y-arcs (verified by reading
   `outline_arcs` and summing arc lengths per class).
5. Bikar's existing test suite stays green (the resolver is additive; no
   existing field changes).

### Files touched in slice 0

**bikar:**
- `packages/core/src/render/gt-emitter.ts` — add `resolveFaceClass()` function
  near line 595 (just before the `sourcesMultiset` block); call it; populate
  `params.face_class` and `evidence.face_class` on the GtShape literal at
  lines 609-628.
- `packages/core/src/render/gt-emitter.test.ts` (or sibling — confirm
  bikar's test layout) — unit test for `resolveFaceClass`:
  - all-uniform → returns the single class
  - mixed with X-arcs longer → returns X
  - mixed with Y-arcs longer → returns Y
  - tie → returns lex-first
  - empty (no class tags, only positional `:arc:#` and `layer:` tags) →
    returns `null`
- (no DSL parser changes in slice 0)

**qiyas (zero-touch in slice 0):**
- The qiyas-side iter-8 driver still reads `source_primitives` for B-partition
  derivation. The new `face_class` field is informational on slice 0; the
  iter-8 re-run that proves Option D's K=2 partition works with the resolver
  is **slice 2**, not slice 0.

### Out of scope for slice 0

- DSL surface (`face_class_resolver dominant_arc`) — slice 1
- Other combiners (`majority`, `first_match`) — slice 1
- Re-authoring Petal-2-Ring as the parametric K ∈ {2,3,4,6} template — slice 2
- iter-8 re-run with `face_class`-aware B-partition — slice 2
- Updating the decision doc Q3 PASS verdict — slice 3 (after iter-8 ships)

## Slice 1 — DSL surface + combiner library (planned, not started)

**Adds:** `face_class_resolver dominant_arc | majority | first_match` directive
inside the `style` block. Default remains `dominant_arc` (so slice 0
behavior is the new default).

**bikar files:** parser change in `packages/core/src/dsl/parser.ts`,
evaluator threading in `packages/core/src/dsl/evaluator.ts`, additional
combiner implementations alongside `resolveFaceClass`.

**Acceptance:** unit tests cover all 3 combiners; integration test renders
Petal-2-Ring-2class.bkr with each combiner explicitly set and verifies the
expected per-face classifications.

## Slice 2 — qiyas-side iter-8 re-run (planned, not started)

**Adds:** Petal-N-2ring parametric template authored against `face_class`
(not against `source_primitives`); iter-8 driver re-derives B-partition from
`face_class`; per-K SHIP verdicts measured.

**Files:** new `qiyas/calibration/phase-1b-corpus/templates/petal-N-2ring.bkr.tmpl`,
extension to `regenerate.py` for K ∈ {2,3,4,6}, rewrite of
`qiyas/calibration/i1/iter-8-multiclass-fusion-delta.py` to read `face_class`,
new iter-8 record at `qiyas/calibration/i1/iter-8-multiclass-fusion-delta.md`
(replacing the HARD STOP record).

**Acceptance:** at least one K-instance achieves fused_v3 ARI = 1.000
(cascade-plan SHIP target). If none do, that's a separate finding documented
in the new iter-8 record (would not retroactively invalidate slice 0/1, but
would re-open the parent escalation's E vs F decision).

## Slice 3 — decision doc + escalation closure (planned, not started)

**Adds:** update
`qiyas/docs/decisions/2026-05-05-petal-n-2ring-class-partition.md` to record
that Option D is now testable (with a footnote pointing at slice 0/1/2).
Update `petal-2ring-q3-actual-face-count-divergence.md` parent escalation to
mark the divergence RESOLVED with the resolver that landed.

## Cost estimate

- Slice 0: ~half a day (single function + 5 unit tests + smoke verification)
- Slice 1: ~half a day (parser + evaluator threading + 2 more combiners +
  integration test)
- Slice 2: ~1 day (template re-author + iter-8 driver rewrite + corpus regen +
  per-K analysis writeup)
- Slice 3: ~half an hour (doc updates)

Total: 2-3 days of focused work, matching the original Option I estimate.

## Why a hard-coded `dominant_arc` is the right slice-0 default

Three reasons:

1. **Geometrically grounded.** Arc length is a real per-edge scalar that
   varies smoothly with template geometry; counting arcs by ID would be
   purely positional. Dominant arc length is the closest analog to "majority
   class" that makes sense when the boundary is a continuous curve.
2. **Matches CGAL convention.** CGAL's standard combiners for face overlay
   (when the user provides no functor) are weighted-area/length-based; the
   library's documented examples use area-weighted majority for face data.
3. **Doesn't lose Y-only or X-only faces.** A face whose boundary is 100% X
   arcs returns `.x_petal` regardless of arc lengths; the combiner reduces
   to "the single tag" in that degenerate case. Only mixed faces consult the
   weight.

## Tenet alignment check

Tenet 1 (smallest slice that ships value): slice 0 ships a working resolver
on the originating face only. Tenet 2 (root-cause, no fallback): the
divergence is fixed at its source, not papered over qiyas-side. Tenet 4
(verify before claiming done): slice 0 acceptance step 4 explicitly checks
the per-face classifications against arc-length math, not against "we got
some X and some Y." Tenet 5 (read existing shape): the resolver lives next
to the existing `sourcesMultiset` block in `gt-emitter.ts`, not in a new
file. Tenet 8 (general not specific): the combiner works on any face,
single-class or multi-class; the same code path runs whether the boundary
has 0, 2, or 100 class tags. Tenet 9 (intent header): the resolver function
gets a 3-line header naming the question — "What single class label does
this face carry, when its boundary edges may carry conflicting tags? Per CGAL
Arr_face_overlay_traits, the answer is a user-supplied combiner; default to
arc-length-weighted majority."
