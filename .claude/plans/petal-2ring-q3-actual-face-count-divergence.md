---
status: RESOLVED 2026-05-06
discovered: 2026-05-06
resolved: 2026-05-06
resolution: Option I (per-face class resolver via bikar schema 1.15 face_class) — shipped via cascade slices #210, #211, #212, then refined-A C3 contract step (qiyas#226) made face_class the load-bearing class-selector while preserving the legacy multiset path for face_class-null corpora as `derive_fused_partition_v2_multiset`.
discovered_by: claude during /loop work on task #207 (Option D parametric template authoring)
related:
  - decision: qiyas/docs/decisions/2026-05-05-petal-n-2ring-class-partition.md
  - cascade-plan: sacred-patterns/.claude/plans/shape-identity-detection-cascade.md
  - prior-iter: qiyas/calibration/i1/iter-8-multiclass-fusion-delta.md
  - smoke-artifact: /tmp/petal-2ring-2class/pattern.gt.json
---

# Spec divergence — Petal-2-Ring emits 6 lens faces (with mixed class tags), not 24 partitionable faces

## What the decision doc claimed (Option D premise)

`qiyas/docs/decisions/2026-05-05-petal-n-2ring-class-partition.md` selected **Option D — parametric K-class variant** with K ∈ {2, 3, 4, 6} and these partition rules (decision doc lines 282-285):

> partition rules per K: K=2 (X-class vs Y-class, 18/6); K=3 (Option B partition, 6/12/6); K=4 (X-inner / X-outer-A / X-outer-B / Y, 6/6/6/6, same selector problem as Option C); K=6 (per-sector grouping, 4/4/4/4/4/4).

These partitions assume Petal-2-Ring emits **24 face shapes** that can be partitioned into K classes. The doc's "Layman summary" makes this premise explicit (lines 19-22):

> The pattern we're starting from (Petal-2-Ring) currently paints all 24 of its arc-bounded faces the same color, so the algorithm has nothing to discriminate against.

## What the empirical smoke test reveals

Built `/tmp/petal-2ring-2class/Petal-2-Ring-2class.bkr` per the K=2 spec — 18 arcs tagged `.x_petal`, 12 arcs tagged `.y_petal`, distinct palette colors, no `classify` rules (per Q3 finding constraint #2). Rendered against the post-lens-fix bikar dist (with `bikar` commit `10702b7` lens-face emission fix landed).

**Result:**
- `pattern.gt.json` has **6 lens faces total**, not 24.
- **Every** lens face's `source_primitives` array contains BOTH `.x_petal` AND `.y_petal` (verbatim: `[".x_petal", ".x_petal", ".y_petal", ".y_petal", ":arc:#15", ":arc:#26", ":arc:#29", ":arc:#6", "layer:0", "layer:0"]` — 4 arcs per face, 2 X-tagged + 2 Y-tagged).

This means:
- The 24 `connect arc` invocations in Petal-2-Ring create 24 *edges* in the planar graph — but those edges bound only 6 distinct *faces*.
- The X-class vs Y-class partition (the K=2 case) does not exist at the face level — every face has both X and Y arcs on its boundary.
- The remaining K-instances (K=3, K=4, K=6) inherit the same problem: they all assume the partition operates on 24 faces, when only 6 exist.

## Why iter-8's "lens fix unlocks petal-2-ring" hypothesis was incomplete

iter-8's recommended next-step #1 (lines 158-162) said:

> **Bikar fix (preferred):** patch `gt-emitter.ts` to handle 2-vertex lens faces (e.g., key edges by `(vertices, arcCenter, sweepCCW)` tuple instead of vertex-pair only). Then `Petal-2-Ring.bkr` emits 6 X-petal + 6 Y-petal faces with distinct `:arc:#0` (X-base) vs `:arc:#1` (Y-base) tags — clean 2-class arc-bearing corpus, 6 instances each.

The bikar lens-emission fix did land (bikar commit `10702b7`, qiyas#196-#200), and Petal-2-Ring did go from 0 → 6 face shapes. But the iter-8 recommendation predicted **6 X + 6 Y = 12 distinct faces** with **distinct class tags per face**. The actual outcome is **6 mixed-class faces**.

The mismatch is at the planar-graph level, not the gt-emitter level: Petal-2-Ring's geometry produces 6 physical lens regions where X-arcs and Y-arcs share boundaries on the same face. The lens fix made the perimeter walk find these faces; it did not (and could not) split a single physical face into two by coloring its bounding arcs differently.

## What this implies for the cascade

The Option D parametric corpus cannot be authored as the decision doc specified. Three structural facts force the issue:

1. **Petal-2-Ring's geometry yields 6 faces, not 24.** No template-authoring-side change can synthesize partitionable faces that aren't there.
2. **Source tag union, not partition.** A face adjacent to both `.x_petal` and `.y_petal` arcs gets both tags. The `source_primitives` array is a multiset over its boundary edges, not a partition selector.
3. **Q3's earlier "PASS with constraints"** verdict (decision-doc §"Q3 smoke test results") was made on the prior session's smoke artifact at a higher level of abstraction — it confirmed `connect arc .className` syntax propagates to `source_primitives`, but did not check whether per-arc tagging produced per-class faces. It does not.

## Options the owner should consider

### Option E — Switch to a construction that genuinely emits K partitionable faces

Use a different bikar pattern as the parametric base — one whose planar graph naturally has K · m faces (m faces per class) for the K values we want to test. Candidates from the bikar pattern library:

- `Petal-Full.bkr` already emits 14 face shapes with non-trivial multi-class structure (per iter-8 result: 4 A-clusters / 10 B-classes). It just doesn't reach fused_v3 = 1.000 because its B-classes are singleton-heavy, not because the faces aren't partitionable.
- Hexagram or rosette templates may give cleaner per-class face counts.

This requires repeating the Option-A-through-D analysis for the new construction.

### Option F — Drop the "fused_v3 = 1.000 on 4 K-instances" SHIP target

If no construction in the bikar library naturally yields the partition shape needed, soften the cascade plan stop rule. Per Tenet 7, this requires a separate write-up — a metric-side change to accommodate structural reality, not a tuning win.

### Option G — Ship the cascade slice as Q3-blocked, defer iter-8 indefinitely

iter-8's existing HARD STOP record stands. Mark task #194 as blocked, mark tasks #207-#210 as deleted, and document that multi-class arc-bearing fusion-delta validation requires either Option E (different construction) or Option F (different metric) — both of which are owner decisions, not implementation work.

### Option H — Bikar feature: `face .className` with explicit class tag

Per iter-8 next-step #2 (line 163-166), add a bikar primitive that lets a template author declare "this face belongs to class X" directly, bypassing the per-edge tag-union. Then Petal-2-Ring could be re-authored with 6 face declarations per class instead of 24 arc declarations. This is the most invasive option but the most general — it would fix the same problem for any future multi-class arc-bearing template.

### Option I — Bikar refactor: per-face data with combiner callback (CGAL-canonical pattern)

Web-search of the canonical literature (CGAL Arrangement_2 docs, May 2026) confirms this is *not* a "weird local choice" we made — it's a layer the bikar gt-emitter skipped. The canonical practice in computational-geometry libraries is:

- **Labels live on faces, not on edges.** CGAL's `Arr_extended_dcel<Traits, VData, HData, FData, ...>` parameterizes face data directly via `FData`, separately from per-half-edge data via `HData`.
- **Per-edge tags are convenience for the template author; the construction-time DSL must compute a per-face label from those tags.** CGAL's `Arr_face_overlay_traits<Arr_A, Arr_B, Arr_R, OvlFaceData>` takes an `OvlFaceData` *functor* that combines face data from two input arrangements (e.g., dominant class, weighted vote, geometric area). The same pattern applies to a single arrangement with multi-edge boundaries.
- **Multi-edge-shared faces are normal, not a bug.** "Two arrangement faces may share more than a single edge on their boundary" — Petal-2-Ring's 6 faces with 4 boundary arcs each is geometrically correct; what's missing is the combiner that turns those 4 per-edge tags into 1 per-face label.

What this looks like in bikar: extend `gt-emitter.ts` so that when a face's boundary half-edges carry conflicting `.className` tags, a user-supplied combiner (in the template's `style` block, e.g. `face_class_resolver dominant_arc | majority | first_match`) decides the per-face class — instead of defaulting to "paste all tags into source_primitives as a multiset." Default combiner could be "majority by arc-length" to preserve current behavior on single-class faces while making multi-class faces well-defined.

This is strictly more general than Option H (`face .className`): Option H requires the template author to enumerate every face by name; Option I infers per-face class from per-arc tags using a combiner the author picks once per template. Option I also brings bikar into alignment with the canonical CGAL pattern, which makes future qiyas/bikar interop on planar-graph face attributes cheaper (CGAL's BGL bridge, overlay traits, etc., all assume per-face data).

**Cost estimate:** 2-3 days (new bikar primitive + 3-5 combiner implementations + Petal-2-Ring re-author + corpus regen + iter-8 re-run).

## What changed between Q3 PASS and this discovery

- Q3 smoke (recorded 2026-05-05 in decision doc §"Q3 smoke test results"): verified `source_primitives` contains the class tag per arc. PASS.
- This discovery (2026-05-06): verified what `source_primitives` contains is a *union* over the face's boundary arcs, not a *single* class per face. The per-arc tag does propagate, but the resulting per-face tag is a multiset, and the K-class partition described in Option D operates on per-face tags.

Q3's PASS verdict was technically correct but didn't go deep enough. This finding is the next-question-deeper. Tenet 6 (verify inherited claims) caught it on the second pass; Tenet 4 (verify before claiming done) is what this doc is now executing.

## Recommendation

This is an owner call. My read:

- **Option G (defer)** is the cheapest and the most honest: we don't have a construction that supports the K-class test, the existing iter-8 HARD STOP already records the structural reason, and adding 4 K-instances against a wrong premise would be the kind of "ship something to look like progress" failure mode the cascade plan was designed to prevent.
- **Option E (different construction)** is the right *next* move if the cascade owner wants to validate F1.v3 fusion-delta on multi-class arc geometry at all. It re-opens a research question (which template?) but doesn't require any code.
- **Option H (bikar feature)** is the right *eventual* move if multi-class arc-bearing patterns are common enough in the real bikar pattern library to justify the DSL extension. That's a question I can't answer from here.

Cascade tasks #207, #208, #209, #210 should pause until the owner picks E, F, G, or H.

## Hard-stop trigger reference

Per the autonomous-loop input verbatim (in the cascade plan):

> Hard stops (do not proceed past these):
> - Spec divergence: if implementation reveals a spec is wrong, STOP. Surface the divergence as a doc edit proposal under .claude/plans/ and wait.

This doc is the surface. Task #207 is paused with the marker below; #208-#210 stay pending.

## Resolution outcome (2026-05-06)

Owner picked **Option I** (per-face data with combiner callback —
CGAL-canonical pattern). Shipped as a 4-slice cascade:

- **Slice 0 (#210, bikar):** schema 1.15 — gt-emitter walks face
  primitives and resolves a per-face `face_class` via dominant-arc
  class fold.
- **Slice 1 (#211, qiyas):** F1.v3 ingests `face_class`, makes it the
  load-bearing class-selector in `derive_fused_partition_v2`.
- **Slice 2 (#212, qiyas):** parametric Petal-N-2ring × {K=2,3,4,6}
  corpus authored with per-arc `.className` directives.
- **Slice 3 (this slice, doc closeout):** record resolution on the
  parent decision doc (qiyas) + flip this plan to RESOLVED.

Subsequent refined-A Phase 3 (qiyas#226) contracted
`derive_fused_partition_v2` to require `face_class_for` (sub-decision
C3, scoped contract: legacy multiset preserved as
`_v2_multiset` for face_class-null corpora). That contract is what
locked Option I in as the long-term spec.

**Calibration outcome (iter-8 re-run, 2026-05-06):**
- petal-2-ring K=2: fused_v3=1.000 (delta +0.508)
- petal-2-ring K=3: fused_v3=0.756 (delta +0.012, partial — class-skew)
- petal-2-ring K=4: fused_v3=1.000 (delta +0.508)
- petal-2-ring K=6: fused_v3=1.000 (delta +0.371)

3 of 4 K-instances ship at the SHIP threshold; K=3 stays partial for
the structural reason §"Q3 smoke test results" predicted (no template
authoring change can fix it without renaming the partition itself).

The original cascade tasks all complete: #207, #208, #209, #210
(superseded by the Option I cascade), #211, #212. Decision doc
parent (`qiyas/docs/decisions/2026-05-05-petal-n-2ring-class-partition.md`)
gained a §"Resolution (2026-05-06)" section pointing back at this plan
and the slice cascade.
