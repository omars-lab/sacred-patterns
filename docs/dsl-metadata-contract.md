# DSL Metadata Contract

**Version:** v1.5 (v1 ACCEPTED + Slice 1a/1b ACCEPTED + `data-partial` / `data-clipped-boundary` ACCEPTED for #106 Option I + `data-shape-id` **producer-side ACCEPTED, F2-oracle use-case FALSIFIED** 2026-05-29 + gt.json `params.sides` ACCEPTED 2026-06-10 + orb-view provenance ACCEPTED 2026-08-02 + `data-authored-region` **producer-side ACCEPTED, consumer pending** 2026-08-02 + ribbon-view provenance ACCEPTED 2026-08-16)
**Status:** ACCEPTED 2026-05-20 → v1.1 amendment 2026-05-25 (#106 partial-shape provenance, bikar commit 8c17615) → v1.2 amendment 2026-05-29 (#663 `data-shape-id` PROPOSED → emit shipped (bikar #664) + qiyas consumer threaded (#665/#666) → F2-oracle use-case **falsified at Step 5** — see qiyas/docs/decisions/2026-05-29-f2-face-class-is-wrong-retrieval-label.md REOPENED. The attribute and its producer/consumer plumbing remain valid for future consumers; the F2 retrieval-gate use-case is the falsified piece.) → v1.3 amendment 2026-06-10 (gt.json `params.sides` — authoritative geometric corner count, bikar gt-emitter schema 1.21 → 1.22; engine-restraint audit, medallion-10 iter-38) → v1.4 amendment 2026-08-02 (owner approval of the two amendments both mirrors had been carrying as PROPOSED-pending-owner: orb-view provenance, both halves shipped and witnessed; `data-authored-region`, producer half shipped and frozen, named consumer not built) → v1.5 amendment 2026-08-16 (ribbon-view provenance — the six rows both mirrors had been carrying as PROPOSED since 2026-08-15, with **both** halves now shipped and witnessed: bikar#96 `fdc82ef` GT schema 1.27, qiyas#12 `6c60187` SCHEMA 1.24. Includes the first row whose content is an **omission** — `data-orb-base-face` is specified absent on ribbon views — and closes a defect rather than adding a capability: before `ribbon_pass` existed, ribbon views scored composite 1.000 with every shape in them misnamed)
**Owner:** sacred-patterns (canonical); mirrors live in bikar + qiyas
**Tenet:** sacred-patterns CLAUDE.md Tenet 23 — DSL-as-source-of-truth.

## What this contract is

When bikar's DSL knows a fact at authoring time (the user wrote `square A B C D`, or wrapped a layer in `rotate 8`), that fact must propagate through the SVG `data-*` attribute layer as **authoritative**, so qiyas reads it directly instead of re-deriving it from rasterized geometry.

This file is the **versioned table** of every `data-*` attribute the contract covers. Each row names:
- The attribute name on the SVG element.
- The DSL surface (statement or construct) that produces it.
- The bikar emit site (file + identifier).
- The qiyas consumer (schema field + read site).
- The fallback when the attribute is absent (vtracer-traced SVG, photos, pre-#333 bikar).

**Versioning rule:** any addition or semantic change to this table is a contract bump (v1 → v2 → …). Removals require a deprecation window of at least one minor release across both repos.

**Round-trip contract:** for every row, a CI gate (`qiyas validate-dsl-contract --strict`, qiyas#496) must render a bikar fixture, parse the SVG through qiyas, and assert the value round-trips byte-faithful through the named schema field. Silent drops by a refactor on either side are a contract violation.

## Scope

In scope: attributes that bikar's DSL knows authoritatively at authoring time.

Out of scope:
- Photo / I2 cascade: the producer is the camera + tracer, which does not know face identity. Qiyas's detector becomes the producer-of-record there; its tags carry detector-confidence, not authoring-confidence.
- vtracer-traced SVG of bikar output (round-trip-through-raster): authoritative attributes are lost in rasterization by design.
- Pre-#333 bikar SVG: this contract was authored 2026-05-20; older fixtures don't carry it. Fallback is the geometric path.

## Attributes — v1 ACCEPTED (currently emitted)

These three are live on every face path bikar's renderer emits (since bikar#333 + qiyas#400 Slice 2, commit 59f5beb).

| Attribute | Producer (DSL → emit) | Consumer (qiyas) | Fallback when absent |
|---|---|---|---|
| `data-sides` | `square`/`pentagon`/`hexagon`/`regular_polygon` DSL statements, or any closed `connect` cycle whose face the evaluator can count vertices on → `packages/core/src/render/svg-renderer.ts:219` (`emitFaceAttrs`) | `Contour.authoritative_sides: int \| None` in `src/qiyas/schema.py:257`, read by `_read_bikar_metadata` in `src/qiyas/stages/svg_primitives.py:71` | polygon classifier runs the geometric vertex-count path (lossy for N=4,5,6 at jitter-prone rasters; qiyas#400) |
| `data-face-index` | Renderer assigns a stable per-pattern face ordinal → `svg-renderer.ts:223` | `Contour.face_index: int \| None` in schema; same `_read_bikar_metadata` site | None — qiyas can't recover a stable pattern-scoped face index from raster alone (used only for identity-aware matching when present) |
| `data-layer` | DSL `layer N { … }` block; blueprint layer is -1 → `svg-renderer.ts:228` | `Contour.layer: int \| None` | None — qiyas falls back to "all faces at layer 0" |

## Attributes — Phase 1 PROPOSED (Slice 1 of universal-dsl-tagging cascade)

These three are the Phase-1 additions; Slice 1 (bikar) ships emit, Slice 2 (qiyas) ships consume, Slice 3 (qiyas) wires them through matcher + scorer.

| Attribute | Producer (DSL → emit) | Consumer (qiyas) | Fallback when absent |
|---|---|---|---|
| `data-face-class` | **ACCEPTED 2026-05-20** (Slice 1a, bikar commit 4fee484). The `.className` attached to faces by `classify .name where …` rules. Renderer copies the SVG `class=` value into `data-face-class` so qiyas reads a single value instead of parsing a class list. Emit site: `packages/core/src/render/svg-renderer.ts:215-220` (`buildFaceDataAttrs`). | `Contour.face_class: str \| None` (new field, SCHEMA 1.14 → 1.15, Slice 2 / qiyas#493 — pending). Matcher: when both sides carry `face_class`, mismatched-class pairs add `CLASS_MISMATCH_COST` to the Hungarian cost (per DETR canonical pattern). | matcher falls back to geometric + sides-based scoring (today's path) |
| `data-symmetry-fold` | **ACCEPTED 2026-05-20** (Slice 1b, bikar commit d6f3014). DSL `rotate N { … }` block — `evalRotate` post-processes its emitted segments/arcs/faces to stamp a `rotate:N` source tag (via `appendTag`/`appendFaceSource`), face-extractor unions tags into `face.sources`, renderer reads in `buildFaceDataAttrs`. Emit site: `packages/core/src/dsl/evaluator.ts:evalRotate` (post-replication) + `packages/core/src/render/svg-renderer.ts:buildFaceDataAttrs`. **Scope note:** `repeat N { … }` is NOT in scope for Slice 1b — repeat is a loop over division points (each iteration runs body afresh), not a rotational transform; fold-from-repeat is a separate Slice 4 candidate. **Plan-premise correction (2026-05-20):** the original plan said `face.sources` already carries `repeat:N`/`rotate:N`; investigation showed only `layer:`, `extend:`, `.className` are present — the plumbing is net-new. | `Contour.symmetry_fold: int \| None` (Slice 2b, qiyas — pending). Scorer: `_check_dominant_fold` consults this first; geometric rotational-orders derivation is the fallback. | `_check_dominant_fold` runs today's rotational-orders derivation (correctly classifies fold-12 cases; mis-classifies fold-6 vs fold-8 as DIVISOR via shared factor 2 — see qiyas#490) |
| `data-wave` | **ACCEPTED 2026-06-15** (wave-provenance engine, bikar — see `bikar/.claude/prompts/wave-provenance-engine.md`). DSL `wave N` statement stamps a `wave:N` source tag on every face emitted under it (central reading-pass = 1, inner ring = 2, …); funnels through `environment.ts:tagSegments` like `layer:N`, so the global girih field gets tagged for free. **Min wave wins** when edges from several waves meet a face (matches `data-layer`'s min-layer rule). Orthogonal to `data-layer` — a wave spans multiple layers. Emit sites: `packages/core/src/dsl/evaluator.ts:evalWave` (sets `currentWave`) + `packages/core/src/dsl/environment.ts:tagSegments` (tag) + `packages/core/src/render/svg-renderer.ts:buildFaceDataAttrs` (`resolveWaveValue`, min). Queryable via `wave == N` (`fill-resolver.ts:resolveWaveAttribute`). Backward compatible: absent when no `wave` statement is used. | **Build-portal consumer, not qiyas.** `sacred-patterns` build-wave-ghosts: render the full medallion-10 recipe once, then for wave N draw faces with `data-wave <= N` in color and the rest greyed — a true cumulative "our build, grown through wave N". (sacred-patterns#26/#27/#29/#31.) | portal falls back to recipe-slicing, which over-colors the whole field (PROBE-wave1-slice-overcolors.png witness) — the gap this attribute closes |
| `data-construction-source` | (Slice 4, deferred) Per-face segment-source tags: `circle_arc:<index>`, `line_segment:<index>`, `bisector:<index>`, etc. Already in `face.sources` per Explore; renderer drops them today. Emit site: `svg-renderer.ts:219-236` (extend). | `Contour.construction_source: list[str] \| None`. Matcher gets identity-aware alignment (faces sharing construction provenance bias toward matching). | matcher falls back to geometric + sides-based scoring |

## Attributes — Phase 2 ACCEPTED (partial-shape provenance, sacred-patterns#106 Option I)

The Tier 0/1 composition fixture for cascade #106 (bikar 606bc7c) confirmed that `clip pattern to <boundary>` already annotates boundary-incident inside fragments with `partial: true` + `clippedAtBoundary: <name>` on Face objects, and gt-emitter promotes both to JSON. The SVG renderer was the missing link: medallion-10 iter-21-probe render.svg had 722 face elements with **zero** `data-partial` attributes despite the cascade plan relying on qiyas reading them. Bikar 8c17615 closes the gap.

| Attribute | Producer (DSL → emit) | Consumer (qiyas) | Fallback when absent |
|---|---|---|---|
| `data-partial` | **ACCEPTED 2026-05-25** (bikar commit 8c17615). DSL `clip pattern to <boundary>` evaluator stamps `partial: true` on faces whose original geometry straddled the boundary (the kept inside portion); renderer reads `face.partial` in `buildFaceDataAttrs`. Emit site: `packages/core/src/render/svg-renderer.ts:249-252`. Value: literal string `"true"` when present; attribute omitted entirely when false. | (pending qiyas-side wiring) `Contour.partial: bool \| None` for the CLIPPED-MISSING detector to consult instead of inferring partialness from boundary-distance heuristics. | qiyas detector falls back to current path (treat all faces as fully-inside; partial-shape gap accepted as ceiling). |
| `data-clipped-boundary` | **ACCEPTED 2026-05-25** (bikar commit 8c17615). DSL `clip pattern to <boundary>` evaluator stamps `clippedAtBoundary: <boundary-name>` on the same partial faces; renderer reads `face.clippedAtBoundary` in `buildFaceDataAttrs`. Emit site: `packages/core/src/render/svg-renderer.ts:249-252`. Value: the literal DSL boundary identifier (e.g., `outline`, `outer_b`). | (pending qiyas-side wiring) `Contour.clipped_at_boundary: str \| None`. Matcher can use the boundary name to group co-clipped partials when scoring composite identity. | None — qiyas cannot recover which boundary clipped a face from raster alone; absence means "no provenance signal." |

## Attributes — v1.2 producer-side ACCEPTED, F2-oracle use-case FALSIFIED (`data-shape-id`, qiyas#661 Option C)

**Status (2026-05-29):** The attribute is **emitted by bikar** (#664, schema-1.21) and **read by qiyas** (`evidence.shape_id`, #665; F2 `F2Shape.shape_id`, #666). The plumbing works and the contract row stands. What was falsified is the **use-case** the row was authored for: gating F2 cross-construction retrieval on `shape_id` as the answer-key. On the regenerated i1-corpus, retrieval scored under `shape_id` gave mAP=0.296 / CMC@1=0.273 / EER=0.305 — **worse** than the original `face_class` baseline (mAP=0.607), and far worse than the detector's geometric `type` (`geom_label`: mAP=0.892, CMC@1=1.0, EER=0.035). Root cause: bikar template authors reuse author-chosen `polygon <id>` names (e.g. `scalene_tri_poly`) across geometrically distinct triangles — the name is a generic label, not a canonical-geometry identity. The synthetic _MIXED_CORPUS test that passed Option C hand-assigned `tri_poly`/`sq_poly` per geometric kind; real `.bkr` templates don't follow that discipline. See qiyas/docs/decisions/2026-05-29-f2-face-class-is-wrong-retrieval-label.md (REOPENED 2026-05-29) for the full falsification log, Options E (gate on `geom_label`) / F (owner handback), and the cross-repo memory entry `feedback_synthetic_test_cant_validate_unenforced_producer_discipline`.

**What this means for the contract:** `data-shape-id` remains a valid producer-side fact bikar knows and emits authoritatively — future consumers that want "the author's name for the shape this face came from" (e.g., a styling pass that targets a specific authored polygon) can read it. Future consumers MUST NOT assume `shape_id` denotes geometric-identity equivalence unless they also enforce producer-side discipline (every distinct geometry gets a distinct `polygon <id>`), which today's `.bkr` corpus does not guarantee.

**Why this row exists (original framing, retained for audit):** qiyas's F2 cross-construction signature (spec #144) needs an *answer key* — a label saying "this shape in pattern A is the same kind as that shape in pattern B." The first F2 retrieval run (qiyas commit 7323223) scored mAP=0.61 against `data-face-class`, and the falsification (`qiyas/docs/decisions/2026-05-29-f2-face-class-is-wrong-retrieval-label.md`) proved the cause: `face_class` is a *fill/role* label (`.royal` spans 4/8/12/20-sided shapes), not a shape-identity label. The owner picked Option C: bikar emits an **authoritative shape-identity** the F2 harness labels by — an independent authored oracle, not a label derived from the descriptor under test. The Option-C-as-F2-oracle premise was the falsified part; see status block above.

**What bikar actually knows (investigation, 2026-05-29, qiyas#663):** bikar has **no** generic `square`/`pentagon`/`regular_polygon N` named-shape statement that stamps a shape-kind onto faces (verified: `packages/core/src/dsl/ast.ts` has `PolygonNode` (ordered point list) + `GirihNode` (tileType) + `FaceStatementNode`, none carrying a shape-kind name). The author-chosen identity bikar *does* know flows today into the face's source tags (`face.sources`) and out to qiyas's `source_primitives`:
- `polygon <id> points(...)` → the author's `<id>` appears as a source tag (e.g. `hexagon_poly`, `octagon_poly` — verified in i1-corpus gt.json `source_primitives`).
- `girih <tileType> ...` → `decagon`/`pentagon`/`hexagon`/`rhombus`/`bowtie`.
- arc primitives → `lens` / `circle` (the detector's geometric `type`, which already scores mAP=1.0 as a coarse label per the falsification doc).

So `data-shape-id`'s value is the **author-chosen geometry-source identifier**, deliberately distinct from `data-face-class` (the fill/role label) and finer than the detector's coarse `type`.

| Attribute | Producer (DSL → emit) | Consumer (qiyas) | Fallback when absent |
|---|---|---|---|
| `data-shape-id` | **Producer-side ACCEPTED 2026-05-29** (qiyas#663 contract bump → #664 bikar emit → #665 qiyas consumer → #666 F2 read site). **F2-oracle use-case FALSIFIED 2026-05-29** — see status block above and qiyas/docs/decisions/2026-05-29-f2-face-class-is-wrong-retrieval-label.md REOPENED. The author-chosen shape-identity of the face's *dominant geometry source*: the `polygon <id>` identifier for polygon faces, the `girih` `tileType` for girih-tile faces, or `lens`/`circle` for single-arc-primitive faces. Value grammar: a bare DSL identifier string (e.g. `hexagon_poly`, `decagon`, `lens`). Emit site (planned): `packages/core/src/render/svg-renderer.ts` `buildFaceDataAttrs`, reading the dominant non-class, non-`layer:`, non-`boundary:` source tag from `face.sources`. **Authorability constraint (the documented gap):** when a face carries *multiple* distinct polygon-source tags (absorbed / mixed faces — `type:unknown` in gt.json, e.g. the #132 shared-edge constructions where the face-walker merged two polygons), there is **no single authoritative shape** — the attribute is **omitted** for those faces, not guessed. This is the precise condition under which the F2 cascade's documented **Option-B fallback** (signature-derived label) carries those faces instead. | (planned, #665) `evidence.shape_id: str \| None` in the qiyas gt-emitter → F2 `F2Shape.shape_id` (#666); `build_query_cases` default label becomes `lambda s: s.shape_id`. | F2 falls back to the signature-derived label (Option B) for faces with no `shape_id`; the photo/I2 cascade (no authoring producer) always uses the derived label. |

## gt.json fields — v1.3 ACCEPTED (`params.sides`, authoritative geometric corner count)

**Why this row exists (plain English first):** a face the DSL classifies as a triangle (`sides == 3`) can export `vertex_count: 4` in gt.json, because the two numbers count different things. The DSL `sides` predicate counts *geometric* corners — collinear runs and continuous same-arc spans merge into one side (`countGeometricVertices`, `packages/core/src/graph/geometric-vertices.ts`). gt.json `vertex_count` is the raw stitched-ring outline length: a triangle whose edge was split by a tessellation neighbor exports 4 outline points. Downstream (qiyas) could not tell what the classifier actually matched — a fact the DSL knew at evaluator time was being re-derived (wrongly) from the outline. Surfaced by the medallion-10 iter-38 session (faces classed `sides == 3` exporting `vertex_count: 4`).

| Field | Producer (bikar → emit) | Consumer (qiyas) | Fallback when absent |
|---|---|---|---|
| gt.json `params.sides` | **ACCEPTED 2026-06-10** (engine-restraint audit, Gap 3). Geometric corner count of the shape's outer ring, computed by `countGeometricVertices` — the *same* function the DSL `sides` fill/classify predicate uses, guaranteeing `params.sides` always equals what `sides == N` matched. Emit site: `buildComponentShape` in `packages/core/src/render/gt-emitter.ts`; GT_SCHEMA_VERSION `1.21` → `1.22`. `vertex_count` is unchanged (raw outline length, back-compat). | gt.json readers (qiyas detector / F-stages) treat `params.sides` as the authoritative side count for schema ≥ 1.22; `vertex_count` remains the raw-outline measure. | Pre-1.22 gt.json: consumers fall back to `vertex_count` (lossy — over-counts on tessellation-split edges and multi-arc continuous spans). |

**Recorded discrepancy, explicitly out of scope for v1.3:** the SVG `data-sides` attribute (v1 ACCEPTED row above) emits raw `face.edgeCount` (`svg-renderer.ts` `buildFaceDataAttrs`) — a *third* notion that matches neither the DSL predicate nor `vertex_count` in general. Changing it would be a semantic change to an ACCEPTED row and needs its own amendment + qiyas-consumer review (`Contour.authoritative_sides` currently expects the v1 semantics). Flagged here so the next amendment doesn't rediscover it.

## Attributes — v1.4 ACCEPTED (orb-view provenance: `data-orb-view`, `data-projection`, `data-orb-base-face`, gt.json `orb_view`)

**Status (2026-08-02):** ACCEPTED. These rows sat as PROPOSED in the bikar and qiyas
mirrors from 2026-07-25 while both halves were built; this amendment is the owner
approval the mirrors were waiting on, granted after — not before — the producer, the
consumer and the witnesses existed. Producer: bikar `--format views`, GT_SCHEMA_VERSION
1.24 (`packages/core/src/render/gt-emitter.ts:343`). Consumer: qiyas SCHEMA_VERSION 1.22
(`src/qiyas/schema.py:25`) and `src/qiyas/orb_validate.py`. Decision doc:
`bikar/docs/decisions/2026-07-25-orb-view-orthographic-validation.md`.

**What a view is.** An orthographic projection of an orb's *inscribed 2D pattern* —
the bounded faces, lifted per base-polyhedron face onto the orb's mid-surface
(spherical or faceted, by the same rule the solidifiers use) — taken along one
symmetry axis of the base solid. The axis set is not enumerated by hand: it is derived
generically from base-solid element 0 by `symmetryViewAxes(base)` in
`packages/core/src/kernel3d/orb-views.ts:39`, which is why this doc names the function
rather than listing axes per solid. A whole-face front cap (every vertex direction ·
axis ≥ 0.3) keeps only unbroken front-hemisphere faces.

**Why the 2D contract transfers to a 3D artifact (the transfer condition).** An orb
view is not a new artifact kind. It is an SVG of closed 2D outlines, emitted by bikar's
renderer and parsed by exactly the same qiyas pipeline stage (`_read_bikar_metadata` in
`src/qiyas/stages/svg_primitives.py`) that reads a flat pattern. The front cap is what
makes that true: because no face is split at the rim, qiyas's standing 2D assumptions —
closed outlines, one shape per path, no occlusion — still hold. **Where the transfer
stops:** projection scrambles 2D adjacency, so per-view gt deliberately does *not*
colour-union neighbouring faces, and `shape_id` / `authored_region` are 2D-pattern
identities that are not threaded through the lift. Per-view gt emits those as `null` —
following the omission discipline the `data-shape-id` row establishes, rather than
guessing a value the lift cannot justify.

**Conditional emission, and what that costs the strict gate.** Like `data-symmetry-fold`
(emitted only under `rotate N`), these attributes appear only on orb-view renders; every
2D pattern render legitimately lacks all four. A strict `validate-dsl-contract` run over
2D fixtures must therefore exempt them with `--allow-absent`, which the Slice 5c ratchet
gate in the qiyas Makefile does; the stale-exemption guard fires if a 2D fixture ever
starts carrying them.

**What the witnesses actually prove, and what they do not (read with the "Round-trip
contract" clause above).** Three qiyas witnesses — `test_data_orb_view_carries_through_to_contour`,
`test_data_projection_carries_through_to_contour`, `test_data_orb_base_face_carries_through_to_contour`
in `tests/test_svg_primitives_bikar_metadata.py` — pass as of 2026-08-02 and are held to
these rows by the contract-coverage gate `tests/test_dsl_metadata_contract.py` (25 tests
green together). They prove the **SVG → `Contour` field** half. They do **not** satisfy
this doc's "Round-trip contract" requirement, which asks for a CI gate that renders a
bikar fixture and asserts the value survives end to end; that is Slice 5b/5c, it needs
cross-repo CI wiring, and it remains unbuilt for these rows exactly as it remains unbuilt
for every row above. Accepting these rows does not close that gap and must not be read
as closing it.

| Attribute | Producer (DSL → emit) | Consumer (qiyas) | Fallback when absent |
|---|---|---|---|
| `data-orb-view` | **ACCEPTED 2026-08-02** (PROPOSED 2026-07-25, M3). Which symmetry-axis view this render is: `<kind>-<fold>` (e.g. `vertex-5`, `face-3`, `edge-2`), from `symmetryViewAxes(base)`. Emitted on the root `<svg>` **and** every face `<path>`, by `buildViewFaceAttrs` / `renderOrbViewSVG` in `packages/core/src/render/orb-view-renderer.ts`. Present only on `--format views` output. | `Contour.orb_view: str \| None` (qiyas SCHEMA 1.22), read by `_read_bikar_metadata` in `src/qiyas/stages/svg_primitives.py`. Its presence is the discriminator `qiyas orb-validate` uses to enter orb-view mode. | None, and this one is not recoverable: which axis a projection was taken along is not derivable from the projected outlines. Absence means "not an orb view", which is the correct reading for every 2D render. |
| `data-projection` | **ACCEPTED 2026-08-02** (PROPOSED 2026-07-25, M3). `spherical` \| `faceted` — the orb mid-surface the pattern was lifted onto before orthographic projection, the same rule the solidifiers apply. Same emit site as above. Mirrored in gt.json as `orb_view.projection`. | `Contour.orb_projection: "spherical" \| "faceted" \| None` (SCHEMA 1.22), same read site. | qiyas cannot tell a spherical lift from a faceted one by outline shape alone at the tolerances it scores at; absent ⇒ the view is scored without a projection assumption rather than under a guessed one. |
| `data-orb-base-face` | **ACCEPTED 2026-08-02** (PROPOSED 2026-07-25, M3). Index of the base-polyhedron face this projected pattern face was lifted through — the 3D provenance needed to regroup per-tile faces after projection destroys 2D adjacency. Emitted on face `<path>` by `buildViewFaceAttrs`; in gt.json as `params.orb_base_face` via `buildOrbViewShape` in `gt-emitter.ts`. | `Contour.orb_base_face: int \| None` (SCHEMA 1.22), same read site. | qiyas falls back to ungrouped per-face scoring. Re-deriving the grouping from the projection is precisely the re-derivation Tenet 23 exists to prevent — two faces from different base tiles can land adjacent and indistinguishable. |
| gt.json `orb_view` | **ACCEPTED 2026-08-02** (PROPOSED 2026-07-25, M3). Optional envelope field `{view, kind, fold, axis, projection, radius_mm, front_cap_min_dot}`, emitted by `emitOrbViewGroundTruth` in `gt-emitter.ts` at GT_SCHEMA_VERSION 1.23 → 1.24. Present exactly on per-view orb gt and absent on 2D pattern gt, so the addition is additive and contract-conformance safe. Per-view gt is one shape per projected face (no colour-union), straight-chord outlines, `shape_id`/`authored_region` null, declared symmetry = the axis fold at confidence 1.0. | `qiyas orb-validate` (`src/qiyas/orb_validate.py`) scores each view's encoding against this envelope and emits `OrbValidateWarning` (`source: "orb-validate"`, qiyas `diff.json` schema) on shape-count, type-histogram, declared-fold or view-set-completeness disagreement. | `orb-validate` fires `gt-missing-orb-view` and declines to score. It does not fall back to a 2D comparison — a view scored as a flat pattern would be scored against the wrong ground truth, which is worse than not scoring it. |

## Attributes — v1.5 ACCEPTED (ribbon-view provenance: `data-strand`, `data-ribbon-depth`, `data-ribbon-trimmed`, `data-orb-base-face`'s absence, gt.json `ribbon_pass` / `orb_view.representation`)

**Status (2026-08-16):** ACCEPTED. These six rows sat as PROPOSED in the bikar and qiyas
mirrors from 2026-08-15 while both halves were built; this amendment is the owner
approval the mirrors were waiting on, granted after — not before — the producer, the
consumer and the witnesses existed, on the same footing as v1.4. Producer: bikar
`--format views` → `<out>/ribbons/`, GT_SCHEMA_VERSION 1.26 → 1.27
(`packages/core/src/kernel3d/orb-ribbons.ts`, `renderOrbRibbonViewSVG` and
`emitRibbonViewGroundTruth`), merged as bikar#96 `fdc82ef`. Consumer: qiyas
SCHEMA_VERSION 1.24, `RibbonPassShape` + `_drift_ribbon_pass`
(`src/qiyas/diff/scorer.py`), merged as qiyas#12 `6c60187`. Decision docs:
`qiyas/docs/decisions/2026-08-15-ribbon-pass-shape-type.md` and §3 of
`bikar/docs/decisions/2026-07-25-orb-view-orthographic-validation.md`.

**Two drawings of one orb, not two orbs.** A cell view and a ribbon view along the same
axis of the same preset are the same solid with different ink: cells draw the surface the
strands divide, ribbons draw the strands themselves. They are not alternative renderings
to be diffed against each other and they do not superimpose. That is what makes
`orb_view.representation` **required on both emitters rather than optional-defaulting-to-cells** —
the two put comparable shape counts on the same disc for the same axis, and nothing else in
the envelope tells them apart, so a gt scored against the wrong one reports a bad render
rather than a mismatched pair.

**Why the ribbon representation exists at all, and why it is not a fallback.** The
`overlap` preset has **no** cell view: its bands cross rather than tile, so there is no
face decomposition to draw, and bikar refuses to emit one rather than lifting a flat
preview that would picture a different solid. For that preset the ribbon views are the
complete view set. For the woven presets both exist. A consumer must therefore treat an
absent cell view as a legitimate geometry answer, not as a missing file.

**Where the v1.4 transfer condition still holds, and the one place it changes.** A ribbon
view is still an SVG of closed 2D outlines read by the same `_read_bikar_metadata` stage —
bands are *filled*, not stroked, precisely so each is a shape with a centroid, an area and
a vertex count rather than a stroke a detector must infer one from. The front-cap argument
carries unchanged. **What changes is occlusion:** bands genuinely overlap each other, so
unlike a cell view the drawing is depth-ordered, and document order — a total back-to-front
sort on true depth — is the only correct occlusion answer. `data-ribbon-depth` is parity,
not paint order, and the two disagree; see its row.

**What the witnesses prove, and what they do not.** Three qiyas witnesses —
`test_data_strand_carries_through_to_contour`,
`test_data_ribbon_depth_carries_through_to_contour`,
`test_data_ribbon_trimmed_false_carries_through_as_false_not_none` in
`tests/test_svg_primitives_bikar_metadata.py` — are held to these rows by the
contract-coverage gate `tests/test_dsl_metadata_contract.py`. They prove the
**SVG → `Contour` field** half. As with every row in this file, the "Round-trip contract"
clause above — render a bikar fixture, assert the value survives end to end — remains
**unbuilt**, and accepting these rows does not close that gap. What *is* new since v1.4 is
adjacent but is not the same thing: bikar's `.github/workflows/orb-validate.yml` (bikar#100,
`5349a80`) now renders all 14 orbs through the pinned `ghcr.io/naqshcoffee/qiyas:v0.2.0`
image and pins each view set's composite **and its shape-type histogram**, so a silent
retyping of every band is caught. That gates the *scores and types*, not this table's
attribute round-trip.

| Attribute | Producer (DSL → emit) | Consumer (qiyas) | Fallback when absent |
|---|---|---|---|
| `data-strand` | **ACCEPTED 2026-08-16** (PROPOSED 2026-08-15, Q2). Which woven strand this band belongs to — the closed-loop id from the global parity solve (`orbWeave.passes[].strandId`), carried from the solid rather than re-derived, so a view can never disagree with the mesh about who crosses over whom. Emitted on every band `<path>` by `renderOrbRibbonViewSVG` (`packages/core/src/render/orb-view-renderer.ts`); in gt.json as `params.strand` via `buildRibbonShape` in `gt-emitter.ts`. Present only on ribbon views. | `Contour.ribbon_strand: int \| None` (qiyas SCHEMA 1.24), read by `_read_bikar_metadata`. **Deliberately unscored by `_drift_ribbon_pass`**: a strand id is a label from the solve, not a measurement, and two correct encodings may number the same loop differently. Whether a view shows the strands the gt declares is a question about the whole view, not about a matched pair. | qiyas cannot recover loop membership from a single band's outline — a pass looks the same whichever loop it belongs to. Absent ⇒ bands are scored individually, which is what the drift function already does. |
| `data-ribbon-depth` | **ACCEPTED 2026-08-16** (PROPOSED 2026-08-15, Q2). `over` \| `under` — which side of the weave this pass sits on at its node. **Parity, not paint order**, and the distinction is measured: of the 249 mixed-parity overlapping band pairs on `Maclado-9-Overlap.vertex-3`, painting every `over` band last puts the wrong one on top in **3**, each by 0.50–0.58 mm of real depth — not a rounding tie — and **zero** on the other five views across both woven presets. Five views out of six let the wrong rule pass, which is why it is written down rather than left to be discovered. Same emit site; gt.json `params.over`. | `RibbonPassShape.over: bool` (SCHEMA 1.24). `_drift_ribbon_pass` weights it a **full unit** — in a weave the parity *is* the design, so an inverted crossing is not a small error. | Not recoverable: which of two overlapping bands is physically on top is exactly what the projection destroys. A consumer that reads this attribute to decide *occlusion* re-introduces the bug above — document order already answers that question. |
| `data-ribbon-trimmed` | **ACCEPTED 2026-08-16** (PROPOSED 2026-08-15, Q2). `true` \| `false` — whether this element is one half of an under pass cut back from its crossing (the gap the over band spans). Declared rather than inferred because it is **not recoverable from the outline**: a trimmed half and a short straight pass trace the same quadrilateral. Same emit site; gt.json `params.trimmed`. | `RibbonPassShape.trimmed: bool` (SCHEMA 1.24), parsed **tri-state** (`true` / `false` / absent) for exactly the reason above — `false` must survive as `false` rather than collapsing into "not stated", which its witness test pins by name. Weighted a full unit in `_drift_ribbon_pass`. | Not recoverable; see the producer column. Absent ⇒ the band is scored without a trim claim rather than under a guessed one. |
| `data-orb-base-face` **absent on ribbon views** | **ACCEPTED 2026-08-16** (PROPOSED 2026-08-15, Q2). **The omission is the claim.** `data-orb-base-face` names the generative unit a drawn element came from; a strand crosses many wheels and many fillers on its way around the sphere, so every candidate index would be one arbitrary choice among equally true ones. `renderOrbRibbonViewSVG` omits the attribute and `buildRibbonShape` omits the `params.orb_base_face` key — **not** `-1` and **not** `null`, either of which a consumer reads as data. This follows the omission discipline `data-shape-id` established. | Consumer obligation, and it is a real one: qiyas's base-face round-trip gate must stay **quiet** when neither side declares a base face, rather than reporting the empty set as a mismatch. Pinned by the D-g gate's companion case. | n/a — absence is the specified state, so there is no fallback to describe. A consumer that synthesizes an index here is inventing provenance. |
| gt.json shape type `ribbon_pass` | **ACCEPTED 2026-08-16** (PROPOSED 2026-08-15, Q2). One drawn band: a through-pass (edge-midpoint → node → edge-midpoint) or one trimmed half of one. `GtShapeType` + `buildRibbonShape` in `gt-emitter.ts`, GT_SCHEMA_VERSION 1.26 → 1.27. Carries `strand` / `over` / `trimmed` from the weave solve plus `width` / `spine_length` / `bend_deg` / `rotation_deg`, which a reader **re-derives from the outline** by pairing vertex `i` with vertex `n-1-i` — the two sides of one cross-section. That pairing needs the authored vertex order, which the SVG-direct encode path preserves and a raster trace would not. **Why a new type rather than a reused polygon name is measured, not asserted,** on `Maclado-9-Weave.vertex-3` (456 bands): qiyas's classifier returned 426 `regular_polygon` + 24 `rhombus` + 6 `girih_rhombus`, and bikar's own `classifyFace` would say 276 `square` + 180 `unknown`. Every band mismatches, 30 land in a family a 1.2 × 10 mm strip does not belong to, and **no such name carries width, length, bend or parity**. | `ShapeType.ribbon_pass` + the `RibbonPassShape` variant + `_drift_ribbon_pass` (rotation on a **180°** period — a spine is an axis, not a ray), qiyas SCHEMA 1.24. | The geometric classifier types the band as whatever polygon family it best fits, which the measurement above shows is wrong for every band. This is the row that closes a defect rather than adding a capability: before it, ribbon views scored composite 1.000 while every shape in them was misnamed, because the gt scorer is type-agnostic by design. |
| gt.json `orb_view.representation` | **ACCEPTED 2026-08-16** (PROPOSED 2026-08-15, Q2). `'cells'` \| `'ribbons'` — which of the two drawings of the orb this per-view gt describes. `GtOrbView` in `gt-emitter.ts`, set by `emitOrbViewGroundTruth` (`'cells'`) and `emitRibbonViewGroundTruth` (`'ribbons'`). **Required on both, not optional-defaulting-to-cells** — see the prose above. `ribbon_width_mm` rides alongside on ribbon views only. Ribbon views are written to `<out>/ribbons/`; the subdirectory rather than a stem infix is itself a contract choice, so every stem still matches qiyas's `_VIEW_STEM_RE` and `orb-validate <out>/ribbons` works with no change to the naming contract. | `qiyas orb-validate` reads it to pair an encoding with the right gt. | A gt with no `representation` predates 1.27. Because the two representations put comparable shape counts on the same disc, guessing a default is the failure mode this field exists to prevent — the honest reading of an absent value is "this producer predates the distinction", not "cells". |

## Attributes — v1.4 producer-side ACCEPTED, consumer pending (`data-authored-region`, sacred-patterns#53)

**Status (2026-08-02):** **Producer-side ACCEPTED; the named consumer does not exist yet.**
This row is deliberately not a full ACCEPTED, and the shape is the one `data-shape-id`
already established: the fact is emitted, deterministic and frozen by tests, and the
use-case it was authored for has not been built. The row is admitted now because the
producer half is finished and would otherwise drift unrecorded, not because the cascade
is complete.

**What it is.** A stable id, unique per authored decoration-region *instance*, shared by
every face fragment that geometry split out of that one authored region — so a consumer
can fuse the shards back into the shape a person actually sees. Distinct from
`data-shape-id`, which is the shape *kind* (`decagon`, uniform across every placement);
this is the *instance* ("decoration region R of placed tile T").

**How this doc's own gating principle is satisfied.** §"Attributes — v2+ candidates"
requires that a fact enter the contract only when a downstream consumer would otherwise
re-derive it. The consumer is named and the re-derivation is measured: sacred-patterns
`/simplify` clusters faces into a shape vocabulary, and without this id it lists the 2–3
construction-line triangles each petal was split into instead of the petal — the "there
are no triangles there" finding of 2026-06-15. What is missing is the code, not the
justification. Until that code lands, this row buys nothing at runtime and should not be
counted as if it did.

**Producer half, and the finding that constrains any consumer.** Threaded
`girih-tiles.ts:girihTileSegments(instanceId)` → the evaluator's field/pocket/subdivide
emit sites → `face.sources` → `resolveAuthoredRegion` in both `svg-renderer.ts` (per-face)
and `gt-emitter.ts` (per-multiset). Frozen by `packages/core/tests/render/authored-region-id.test.ts`
(6 tests). The witness is a 1-shell decagonal field of 11 tiles: 101 fragment faces fuse
to 11 distinct ids (centre tile = 21 fragments, each ring tile = 8). **Load-bearing:** the
gt.json path unions same-*colour* adjacent faces into one shape *before* resolving the id,
so per-region distinct ids are observable only on the per-face SVG `data-authored-region`.
That attribute — not gt.json — is the authoritative fuse surface a consumer must read.
The gt.json `evidence.authored_region` carries the resolver's output for the
possibly-colour-unioned component and is null when that component straddles more than one
region. A consumer written against gt.json would silently see fewer regions than exist.

**Omission rule.** When a face's bounding edges carry more than one distinct region id — a
face genuinely straddling two authored regions — the attribute is absent and
`authored_region` is `null`. Never guessed, exactly as `data-shape-id` omits on
mixed-source faces. Deterministic (bikar Tenet 8): the id is a pure function of
construction order.

**Architecture note (extends an ACCEPTED decision, not a new mechanism).** The id flows as
a face-attribute Map consumed by the gt-emitter, following
`bikar/docs/decisions/2026-05-18-region-identity-class-emission-4-layer-fix.md` Option D
(face attributes live on faces, not re-derived from edge tags). Option B's competing
edge-tag mechanism was explicitly rejected there.

| Attribute | Producer (DSL → emit) | Consumer | Fallback when absent |
|---|---|---|---|
| `data-authored-region` | **Producer-side ACCEPTED 2026-08-02** (PROPOSED 2026-06-15, sacred-patterns#53). Per-tile-instance + per-decoration-region suffix on the girih segment tags (`_girih_decoration:<tileIdx>.<regionIdx>`). SVG: `buildFaceDataAttrs` → `resolveAuthoredRegion` (per-face — the authoritative surface). gt.json: `buildComponentShape` in `gt-emitter.ts` → `evidence.authored_region` (per-component, after colour-union). Value grammar: an opaque stable string; consumers compare it for equality and must not parse it. | **Not built.** Planned: sacred-patterns `/simplify` fuses faces sharing this id before clustering. No qiyas `Contour` field, no qiyas witness test, and therefore no row in the qiyas mirror's "Currently covered" table — adding one before the consumer exists would make the coverage gate assert a witness that has nothing to witness. | `/simplify` clusters unfused, and reports construction-line fragments as if they were authored shapes. That is today's behaviour and stays today's behaviour until the consumer lands. |

## Attributes — v2+ candidates (not yet proposed)

These are anticipated but not committed. Each would need (a) a named qiyas consumer call site, (b) a contract-doc PR, (c) a bikar emit-site PR, (d) a CI round-trip witness.

- `data-class` on blueprint circles/lines (when the DSL supplied a className) — needed once Phase 3 lifts `.className` slots onto LineNode/BisectorNode/TangentNode/OffsetArcNode/FilletNode.
- `data-construction-class` on faces — coarser-grained-than-`data-face-class` rollups (e.g., `star`, `band`, `infill`) the user might style as a group.
- `data-rotation-deg` on faces — the per-face rotational offset within a `repeat`/`rotate` block, so qiyas can recover the rotational generator group without a Fourier pass.

The gating principle (sacred-patterns Tenet 23, "How to apply" point 4): **a fact enters the contract only when a downstream consumer would otherwise re-derive it.** Wishful tagging — "we might need this someday" — is not the contract's job.

## Decay and stewardship

This file is the **source of truth** when the producer side and the consumer side disagree. If bikar emits an attribute not in this table, qiyas must ignore it. If qiyas reads an attribute not in this table, bikar must not be expected to emit it.

When a contract bump lands:
1. Edit this file with the new row.
2. Mirror the row into bikar's `docs/dsl-metadata-contract.md` (one-line cross-reference to this canonical doc + the new row's specifics).
3. Mirror into qiyas's `docs/dsl-metadata-contract.md` (same pattern).
4. Bump SCHEMA_VERSION on the qiyas Contour if the consumer field is new.
5. Add a witness test in `qiyas/tests/test_svg_primitives_bikar_metadata.py` (extend the existing Tier 0 suite at qiyas/tests/test_svg_primitives_bikar_metadata.py).
6. Add a witness in `qiyas/tests/test_polygon_authoritative_sides_hint.py`-style for consumption (extend the Tier 0 + medallion-witness pattern).
7. A row whose producer half is finished but whose named consumer is not built lands as
   **producer-side ACCEPTED, consumer pending** — steps 4–6 are skipped on purpose, and
   the row must say so in the Consumer column rather than leave it blank. `data-shape-id`
   (v1.2) and `data-authored-region` (v1.4) are the two instances. The mirrors must not
   list such a row in their "Currently covered" table: the qiyas contract-coverage gate
   (`tests/test_dsl_metadata_contract.py`) requires a witness test per covered row, and a
   row with no consumer has nothing to witness.

## See also

- sacred-patterns CLAUDE.md Tenet 23 — the principle.
- sacred-patterns/docs/decisions/2026-05-20-universal-dsl-tagging.md — the decision doc for the v1→Phase-1 cascade.
- bikar/.claude/plans/is-there-an-actionalble-logical-cascade.md — the implementation plan (6 slices).
- qiyas/docs/decisions/2026-05-20-qiyas-anti-symmetry-floor-breach.md — the symptom this cascade dissolves at root.
- qiyas/docs/ci-report-standard.md — the cross-repo CI report doc this contract is structurally modeled on.
