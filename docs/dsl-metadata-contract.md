# DSL Metadata Contract

**Version:** v1.3 (v1 ACCEPTED + Slice 1a/1b ACCEPTED + `data-partial` / `data-clipped-boundary` ACCEPTED for #106 Option I + `data-shape-id` **producer-side ACCEPTED, F2-oracle use-case FALSIFIED** 2026-05-29 + gt.json `params.sides` ACCEPTED 2026-06-10)
**Status:** ACCEPTED 2026-05-20 → v1.1 amendment 2026-05-25 (#106 partial-shape provenance, bikar commit 8c17615) → v1.2 amendment 2026-05-29 (#663 `data-shape-id` PROPOSED → emit shipped (bikar #664) + qiyas consumer threaded (#665/#666) → F2-oracle use-case **falsified at Step 5** — see qiyas/docs/decisions/2026-05-29-f2-face-class-is-wrong-retrieval-label.md REOPENED. The attribute and its producer/consumer plumbing remain valid for future consumers; the F2 retrieval-gate use-case is the falsified piece.) → v1.3 amendment 2026-06-10 (gt.json `params.sides` — authoritative geometric corner count, bikar gt-emitter schema 1.21 → 1.22; engine-restraint audit, medallion-10 iter-38)
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

## See also

- sacred-patterns CLAUDE.md Tenet 23 — the principle.
- sacred-patterns/docs/decisions/2026-05-20-universal-dsl-tagging.md — the decision doc for the v1→Phase-1 cascade.
- bikar/.claude/plans/is-there-an-actionalble-logical-cascade.md — the implementation plan (6 slices).
- qiyas/docs/decisions/2026-05-20-qiyas-anti-symmetry-floor-breach.md — the symptom this cascade dissolves at root.
- qiyas/docs/ci-report-standard.md — the cross-repo CI report doc this contract is structurally modeled on.
