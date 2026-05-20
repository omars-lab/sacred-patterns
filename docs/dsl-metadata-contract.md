# DSL Metadata Contract

**Version:** v1 (current emissions + Slice 1a `data-face-class`); Phase 1b `data-symmetry-fold` PROPOSED
**Status:** ACCEPTED 2026-05-20 — v1 ACCEPTED rows live (Slice 1a landed bikar 4fee484); Slice 1b PROPOSED (#497)
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
| `data-symmetry-fold` | **PROPOSED** (Slice 1b, #497). DSL `repeat N { … }` or `rotate N { … }` construction needs new evaluator plumbing in `evalRotate`/`evalRepeat`/`replicateArcsRadially`/`replicateFacesRadially` to propagate the fold count as a `rotate:N` face source tag. Renderer then reads it in `buildFaceDataAttrs`. **Plan-premise correction (2026-05-20):** the original plan said `face.sources` already carries `repeat:N`/`rotate:N`; investigation showed only `layer:`, `extend:`, `.className` are present — the plumbing is net-new. | `Contour.symmetry_fold: int \| None`. Scorer: `_check_dominant_fold` consults this first; geometric rotational-orders derivation is the fallback. | `_check_dominant_fold` runs today's rotational-orders derivation (correctly classifies fold-12 cases; mis-classifies fold-6 vs fold-8 as DIVISOR via shared factor 2 — see qiyas#490) |
| `data-construction-source` | (Slice 4, deferred) Per-face segment-source tags: `circle_arc:<index>`, `line_segment:<index>`, `bisector:<index>`, etc. Already in `face.sources` per Explore; renderer drops them today. Emit site: `svg-renderer.ts:219-236` (extend). | `Contour.construction_source: list[str] \| None`. Matcher gets identity-aware alignment (faces sharing construction provenance bias toward matching). | matcher falls back to geometric + sides-based scoring |

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
