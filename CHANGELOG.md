# Changelog

Archive of completed cross-repo tasks (sacred-patterns / qiyas / bikar).

The task list is for **in-flight** work; once a task completes, it moves here so
it stops consuming context. Per Tenet 6, this file is a **durable index into
decision docs, plans, and commits** — not a substitute for them. To understand
*why* a cascade was done a particular way, follow the decision-doc cross-references
in each section; the entries here only name the outcome.

When a cascade is closed, archive its tasks here and delete them via
`TaskUpdate status: "deleted"`. See `CLAUDE.md` § "Task hygiene" for the policy.

Format: `#NN [repo-prefix] subject — one-line outcome`. Repo prefix is one of
`[sp]` sacred-patterns, `[qiyas]`, `[bikar]`, or unprefixed when the task is
cross-repo orchestration owned by sacred-patterns.

---

## 2026-05-25 — #85 medallion-10 iter-24/25/26/27/28 cascade local-optimum at iter-25 (v20 verdict closed)

iter-24 composed #106 Option I (extend+clip silhouette) with #114 PR1 (strapwork): A2 cv 0.0406 (cascade best at the time), A4 FULL, A5 COMPLETE, A6 0/18 vs `input/baseline.json` (18-shape rich-inner-zone expectation). iter-25/26/27/28 probed four mechanism-distinct constructions for the inner-star v20 verdict (chord polygon shared layer / chord polygon isolated layer / direct `face` arc declaration / chord polygon at correct baseline scale r=6 spatially isolated) — all four falsified, each at a different pipeline stage. Pattern: this construction philosophy (chord-overlay + strapwork) fundamentally cannot produce a vertex-distinct v20 shape inside the medallion. iter-25 stands as cascade local-optimum at A2 cv 0.0365 (45% better than iter-14's 0.067), A4 FULL, A5 COMPLETE, A6 0/18 reflecting philosophy mismatch with baseline. Memory: `feedback_a6_baseline_construction_philosophy_mismatch.md`. Per user direction "medallion-10 stays open / keep striving," cascade #85 stays open but stops iterating v20 / star-v6 / star-v8 verdicts; next iters target polygon-v0 / rhombus-v4 verdicts the philosophy CAN plausibly produce.

Evaluations: `~/Dropbox/Data/sacred-patterns/bikar-medallion-10/iterations/{24,25,26,27,28}/evaluation.md`. No tasks closed (cascade continues at #85).

---

## 2026-05-25 — #114 bikar strapwork rotation-canonicalization (Slice 2 closeout)

PR1 (bikar `8bc6735`, 2026-05-18) shipped `canonicalEdgeOrder` — polar-angle seed ordering in `assignStrands` outer loop to root-fix bikar#115 rotation non-invariance. Slice 2 end-to-end validated 2026-05-25 via medallion-10 iter-23 (re-render of iter-16's broken `crossing over` DSL through patched bikar): A2 cv 0.2671 (BROKEN) → 0.0526 (UNEVEN, **below** iter-14's 0.067 strapwork-free baseline); A5 status BROKEN → COMPLETE (10 lenses, 33 estimated bands, 292 band-crossings, dominant_fold 10 conf 0.76). PR2 (orbit detection per approach B) not triggered. PR3 (Hankin face-walk per Kaplan 2005) remains deferred.

- #114 [bikar] [#85 strapwork blocker] Implement strapwork rotation-canonicalization (3 PRs planned, PR1 sufficient)

Plan: `sacred-patterns/.claude/plans/bikar-strapwork-rotation-canonicalization.md`. Evaluation: `~/Dropbox/Data/sacred-patterns/bikar-medallion-10/iterations/23/evaluation.md`. Unblocks #85 strapwork iteration.

---

## 2026-05-23→25 batch — #362 Phase 1 D4 cutover + #363 Phase 2 producer cutover + #138 closeout + drain queue

12-task batch closing the typed-wire-format cutover (qiyas #525 → #531 → #532 → #534 → #535 → #536, end-to-end), the #138 detector under-recall thread, and three drain-queue picks (#391 import-linter, #434 bikar merge policy, #138 baseline schema). Cascade closed 2026-05-25 with commit qiyas `8bfe319` (slice 4c). Net cascade outcome: `Shape` legacy class deleted, `Encoding.shapes: list[ShapeUnion]` typed-wire-format live, `Arrangement.params: dict` bag-typed anti-pattern eliminated, `_LEGACY_FIXTURE_DEFAULTS` 16-shape fallback dict + `from_legacy*` helpers + `to_legacy*` bridges + `@property params` shim all deleted (−1327 LOC).

### #362 Phase 1 D4 — Encoding.shapes typed-wire-format cutover

D4 ships in three slices: D4a (#525) cutover `Encoding.shapes` field type, D4b (#531) SCHEMA bump 1.17→1.18, D4c (#532) delete legacy `Shape` class + bridges. Producer-side cascade follows in #534 (Phase 2 ArrangementUnion ctor) → #535 (slice 4b consumer migration to typed dispatch + bridge deletion) → #536 (slice 4c `_LEGACY_FIXTURE_DEFAULTS` + dict-flattening validator deletion + medallion-10 fixture in-place migration).

- #525 [qiyas] [#362 Phase 1 Slice D4] Cutover Encoding.shapes to list[ShapeUnion]; delete legacy Shape; bump SCHEMA 1.17→1.18
- #531 [qiyas] [#525 D4b] SCHEMA_VERSION bump 1.17 → 1.18 for typed-wire-format cutover
- #532 [qiyas] [#525 D4c] Delete legacy Shape, from_legacy, to_legacy, _LEGACY_FIXTURE_DEFAULTS, @property params bridge
- #534 [qiyas] [#363 Phase 2 follow-on] Cut producer over to typed ArrangementUnion ctor
- #535 [qiyas] [#532 slice 4b] Migrate .params consumers to typed dispatch; delete bridge
- #536 [qiyas] [#535 slice 4c] Delete _LEGACY_FIXTURE_DEFAULTS + dict-flattening validator + regen medallion-10-strapwork on x86_64

Decision doc: `qiyas/docs/decisions/2026-05-23-362-phase-1-d4-cutover-serialization.md` (ACCEPTED Option B — clean break + SCHEMA bump + regen). Memory: `feedback_legacy_removal_ordering.md` (producers-before-consumers deletion ordering — falsified once in slice 4a).

### #138 cascade closeout — detector under-recall

#138 parent + Slice 2 (#516) closed via Option G (baseline schema notes-as-discriminator fix, archived earlier) + #529 drain-queue + #530 status commit + #533 pre-existing rosette EXCESS/PARTIAL triage (root-caused to unrelated emit→audit round-trip drift; not slice 4c regression).

- #138 [qiyas] [#129 PR1 follow-on] qiyas: detector under-recall + over-unknown on rendered patterns
- #516 [qiyas] [#138 Slice 2 — Option B] Render iter-18 + re-measure against iter-11 baseline
- #529 [qiyas] [drain queue] Ship #138 — baseline schema notes-as-discriminator fix (Option G)
- #530 [qiyas] Commit qiyas #138 decision doc ACCEPTED status (Option G)
- #533 [qiyas] [#138 follow-on] Diagnose pre-existing test_emit_audit_round_trip_is_clean rosette EXCESS/PARTIAL

Decision doc: `qiyas/docs/decisions/2026-05-22-138-rescope-after-empirical-delta.md` (ACCEPTED Option G).

### Drain queue — typed parameters + layering gate

Three older PROPOSED docs picked up under 2026-05-24 decision authority: bikar merge policy (#434/#527 Option B), qiyas+bikar import-linter (#391/#528 Option A), Phase 2 ArrangementUnion (#363) + Phase 3 Warning union (#364) + helper cleanup (#365) ship as part of the cascade since their consumers all migrated in #535/#536.

- #363 [qiyas] [#339 PIVOT] Migration: Arrangement → discriminated union (Phase 2)
- #364 [qiyas] [#339 PIVOT] Migration: Warning → per-source discriminated union (Phase 3)
- #365 [qiyas] [#339 PIVOT] Cleanup: delete _param_int / _param_float helpers
- #391 [cross-repo] [#349 follow-on] Import-linter contract-based layering gate (qiyas + bikar)
- #434 [bikar] Decision doc: make merge policy a typed parameter on buildIntersectionGraph (vs magic constant)
- #527 [qiyas] [drain queue] Ship #434 — bikar merge policy as typed param on buildIntersectionGraph (Option B)
- #528 [cross-repo] [drain queue] Ship #391 — import-linter contract gate (Option A)

Decision docs: `bikar/docs/decisions/2026-05-18-buildintersectiongraph-merge-policy-as-parameter.md` (ACCEPTED Option B), `qiyas/docs/decisions/2026-05-18-import-linter-layer-contracts.md` (ACCEPTED Option A), `sacred-patterns/CLAUDE.md` Tenet 24 (no backwards compatibility — pre-authorizes breaking-change ordering used in slice 4a→4c).

### Sacred-patterns

- #111 [sp] [qiyas] Plan: hierarchical/quadtree pixel-diff with per-region localization — plan filed at `sacred-patterns/.claude/plans/hierarchical-pixel-diff.md`; implementation tracked in #112 (still pending, deferred).

---

## 2026-05-22→23 batch — #138 cascade + #362 Phase 1 + Universal DSL Tagging closeout + Tier 1 corpus

26-task batch closing five sub-cascades whose tasks all reached terminal
status in the 2026-05-19 → 2026-05-23 window. Archived together because the
cascades closed in overlapping commits and the task-list hygiene policy
fired (≥20 completed + cascade closure both trigger). Each section below is
self-contained; see decision-doc / commit cross-references for the *why*.

### #138 cascade — detector under-recall + over-unknown on rendered patterns

Started as "detector finds 0 circles vs baseline expects 12" (qiyas#138
parent). Slice 1 (circle producer) shipped, then on 2026-05-22 a pipeline
re-run falsified the parent's framing: detector already finds 14 circles
via existing `circle_to_shape` adapter; the 12 baseline "circles" were
stored as `type=polygon, vertex_count=0, notes="qiyas type: circle"`.
Re-scope to Options F/G/H captured in
`qiyas/docs/decisions/2026-05-22-138-rescope-after-empirical-delta.md`
(REOPENED). Slice 2 (#516) pending owner pick.

- #510 [qiyas] [#138 Path A] Refresh A6 baseline from SVG-direct path on iter-11
- #511 [qiyas] [#311 follow-on] present-options decision doc for star7 missed-red-shapes
- #514 [qiyas] [#138 Path B+C] Inspect detector-vs-baseline delta + implementation plan
- #515 [qiyas] [#138 Slice 1 — Option A] Circle-contour producer + single-circle.bkr Tier 0 + tests
- #517 [qiyas] [#138 conditional] Revive Option C classifier elevators (superseded by falsification)
- #518 [qiyas] [#138 Tenet 18 witness] Codify end-to-end histogram comparison test honoring `notes` discriminator

Decision doc (REOPENED + falsification log): `qiyas/docs/decisions/2026-05-22-138-rescope-after-empirical-delta.md`.
Memory: `feedback_run_pipeline_before_authoring_rescope.md`.

### #362 Phase 1 — Shape → Pydantic discriminated union migration

Slices A → D3 shipped (scaffold → typed subclasses → adapter shim →
detectors emit-side → consumers). D4 (cutover Encoding.shapes to
list[ShapeUnion] + delete legacy Shape) pending owner pick on serialization
shape — present-options doc filed 2026-05-23 with 4 options A/B/C/D
(recommendation B: clean break + SCHEMA 1.17→1.18 + regen 1 strict-pinned
fixture). Phase 2 (#363) + Phase 3 (#364) + cleanup (#365) blocked on D4.

- #473 [qiyas] [#362 PR-B] Migrate Shape per-subclass models onto Polygon/ArcShape bases
- #519 [qiyas] [Slice A] Scaffold ShapeUnion module + CircleShape (simplest variant)
- #520 [qiyas] [Slice B] Typed subclasses for elevator-promoted polygons (Square/Pentagon/Decagon)
- #521 [qiyas] [Slice C] Triangle family + remaining typed subclasses
- #522 [qiyas] [Slice D1] Adapter shim: legacy Shape ↔ ShapeUnion bidirectional + tests
- #523 [qiyas] [Slice D2] Migrate detectors emit-side to typed ShapeUnion
- #524 [qiyas] [Slice D3] Migrate consumers (matcher/scorer/report/debug) to read ShapeUnion fields

Decision docs: `qiyas/docs/decisions/2026-05-16-typed-shape-params-vs-object-bag.md`,
`qiyas/docs/decisions/2026-05-23-362-phase-1-d4-cutover-serialization.md` (PROPOSED).

### Universal DSL Tagging cascade — final closeout

Slice 5c (cross-repo GHA wiring for `validate-dsl-contract`) shipped,
closing the cascade originally archived in the section below (see
"Universal DSL Tagging cascade — Tenet 23 / qiyas#491-#503").

- #504 [cross-repo] Slice 5c — wire `qiyas validate-dsl-contract` into qiyas + bikar GHA
- #526 [qiyas] [#504 follow-on] Investigate petal-N-ring-0e6e3fa6 missing data-face-class
- #507 [qiyas] [#371 conditional] Re-measure iter-14 residue after B1 lands

### Tier 1 corpus + bikar multi-polygon edges-from fix

Square-and-scalene shipped as the first Tier 1 corpus entry (square +
scalene triangle, no shared geometry); discovered bikar `markOuterFace`
multi-component bug (#513) — see "bikar face-extractor per-component
outer-marking" section below for the cross-repo cascade.

- #512 [qiyas] Ship square-and-scalene as first Tier 1 corpus entry
- #513 [bikar] Multi-polygon edges-from: gt-emitter drops second polygon, renderer doubles it
- #311 [qiyas] [detector] Red shapes in star7 are undetected (closed by feedback-classes B3)
- #317 [qiyas] [feedback-classes B3] acceptance.yaml: same_color_neighbor_max_delta_rgb + corpus-wide impact

### Other closeouts in this window

- #371 [qiyas] [#256 follow-on] partial-polygon detector starved by fragmented residue on raster-traced inputs
- #398 [sp] [B1 Option A] Implement render.svg-direct path in sacred-patterns iteration loop
- #399 [qiyas] [B1 follow-on] Calibrate validate-detector count-fidelity for SVG-direct over-count
- #471 [qiyas] [CI-platform-portability] Re-measure all pinned baselines on Linux CI runner
- #472 [bikar] Fix CI auth — deploy.yml + sync-patterns.yml fail at npm ci (@naqshcoffee/ui 401)
- #489 [qiyas] [#400 Slice 3 follow-on] Lens detector — authoritative hint for non-polygon shapes

---

## bikar#424 multi-arc origin-coincidence (face-extractor / DCEL linkage)

Face extractor produced sliver/malformed faces on petal-N-ring at N ∈ {4, 8, 12}
(any N where 4 satellite circles pass through the shared origin vertex). Phase 1
probes located the bug at the DCEL linkage step (`buildHalfEdges`), not at the
angular sort. Cascade ran through 7 falsifications across Options B/C/D/E/G;
Option F (arc-identity-aware linkage — same-circle continuation overrides CCW
sibling at pass-through vertices) authored as the surviving plan. Freeze-accept
path also authored for N=4/8/12 as permanent corpus limitation pending owner
pick between Option F shipment and freeze.

- #423 [bikar] Tier 0 / template: single-rhombus template — 4 collinear points
- #424 [bikar #333 Rung-2 root cause] face-extractor multi-arc origin-coincidence
- #425 [bikar] Phase 1 — instrument `buildHalfEdges`, falsify angular-sort hypothesis
- #426 [bikar] Phase 2 — decision doc + impl for origin-coincidence fix
- #427 [bikar] Phase 3 — regen corpus + audit dict + close cascade
- #428 [bikar] Option C slice 1 — consumer audit (EdgeGraph downstream)
- #430 [bikar] Geometry pipeline architecture doc — stages + contracts + vertex-identity policy
- #431 [bikar] Promote probe-script views to first-class debug methods on EdgeGraph / PlanarGraph
- #438 [bikar] Apply handle-falsification skill to Option C+D narrative (retroactive)
- #439 [bikar] Option E — author implementation plan (DSL vertex-identity caller-supplied)
- #440 [bikar] Option E Slice 0 — DSL arc-emit primitives + named-point identity mapping audit
- #441 [bikar] Option E Slice 1 — EdgeGraph typed `endpointIdentity` field (no behavior change)
- #442 [bikar] Option E Slice 2 — DSL evaluator wires named-point ID through to edge metadata
- #443 [bikar] Option E Slice 3 — kernel `getNodeIndex` consumes `endpointIdentity` as primary merge key
- #447 [bikar] Option B — chord-bisector sort key plan for `compareOutgoing`
- #448 [bikar] Freeze-accept path — document N=4/8/12 as permanent corpus limitation
- #449 [bikar] Option F — decision doc for arc-identity-aware linkage rule
- #450 [bikar] Option F Slice 1 — author `findSameArcContinuation` helper + unit test
- #456 [bikar] ESCALATION — owner decision needed after 7 falsifications

Decision docs: `bikar/docs/decisions/2026-05-19-face-extractor-origin-coincidence-fix.md`
(Phase 1f probe data + Option F mechanism). Plan:
`bikar/.claude/plans/option-f-arc-identity-aware-linkage.md`. Falsification
log: `bikar/.claude/plans/option-b-chord-bisector-sort.md` (FALSIFIED).
Skills authored alongside: sacred-patterns `handle-falsification` (#436) +
`debug-kernel-change` (#432) + cross-refs in `present-options` / `decision-doc` (#437).

## Cross-repo skills + tenets (sacred-patterns)

Verification ladder + falsification feedback loop authored as standalone
skills after the bikar#424 cascade demanded both. Tenets 21 (full-suite
acceptance) + 22 (promote-probes-to-methods) added to bikar CLAUDE.md to
codify the lessons from 7 falsifications.

- #432 [sp] debug-kernel-change skill — verification ladder for kernel/intersection/face-extractor edits
- #433 [bikar] Tenets 21 + 22 to CLAUDE.md — full-suite acceptance + promote-probes-to-methods
- #436 [sp] handle-falsification skill — feed falsification back into decision docs
- #437 [sp] present-options + decision-doc skills cross-reference handle-falsification

## bikar 4-layer region-identity fix — gt-emitter Map consumption (Option D)

bikar#333 Rung-1 fix: `connect arc … .petal` was not flowing class through
the 4-layer chain to SVG fill emission. Option D (gt-emitter Map consumption)
shipped corpus-wide, closing `face_class=null` on petal-N-ring N ∈ {4,6,8,10}.

- #333 [bikar] Region-identity class doesn't reach SVG fill emission (parent issue)
- #421 [bikar] Option D — gt-emitter Map consumption + corpus sweep
- #422 [bikar] §B6 — decision doc for `fill-void-where` Map population gap

Decision: `bikar/docs/decisions/2026-05-18-region-identity-class-emission-4-layer-fix.md`.

## qiyas mypy strict mode (qiyas#335 / #339)

Cross-repo tenet 16 (no `Any` to silence strict typing) enforced for qiyas:
mypy `--strict` enabled in `pyproject.toml`, ~140 errors fixed, CI gate added,
pre-commit hook re-enabled. Slice 1 was already in CHANGELOG as #338; closing
slices 2 + 3 + follow-on here.

- #335 [qiyas] Add mypy strict to pyproject + CI gate (parent)
- #339 [qiyas] Slice 2 — fix ~140 strict mypy errors in src/qiyas
- #340 [qiyas] Slice 3 — verify strict-mode green + CI gate
- #387 [qiyas] Follow-on — re-enable mypy --strict block in `.githooks/pre-commit`

PIVOT to typed Shape variants (qiyas#362) still open as next-step.

## qiyas telemetry + fixture gate restoration (qiyas#457-#464)

Wave that surfaced when CI silence (#461 root) was investigated: telemetry
byte-equality on 15-digit floats (#457), CLI-reference freshness gate not
running in CI (#459), full pytest suite too slow for CI (#460), 1 red test
on master under CI silence (#461). Closed via `_assert_telemetry_close`
helper (#464), Makefile `ci-local` target (#462), Stop hook (#463). Most
were absorbed by qiyas#474 (meaning-level invariants superseded the
byte-strict noise floor); residual ones closed here.

- #457 [qiyas] Telemetry snapshot tests use byte-equality on 15-digit floats
- #458 [qiyas] `test_fixtures_no_drift` failing on master — root-cause investigation
- #459 [qiyas] CLI-reference freshness gate doesn't run in CI / pre-commit on `cli.py` changes
- #460 [qiyas] Full pytest suite takes 22min uninstrumented, 60min+ under coverage
- #461 [qiyas] CI doesn't run pytest on master — silence is the bug
- #462 [qiyas] [#461 Option A] Makefile `ci-local` target — simulate CI pipeline locally
- #463 [qiyas] [#461 Option A] Stop hook to run CI simulation on task completion
- #464 [qiyas] [#457 Option B Slice 1] `_assert_telemetry_close` helper in test_telemetry_snapshots

## CI platform portability — Linux runner failures (qiyas#468 / #469 / #470)

Pinned baselines measured on macOS dev box; CI runs `ubuntu-latest` and
native libs produce slightly different outputs. Encoder-drift half (#468/#469)
absorbed by qiyas#474's meaning-level invariants (band-tolerant); robustness
floor half (#470) remains tracked as scope-reduced #471.

- #468 [qiyas] CI Linux: encoder drops 1/18 shapes (test_emit_audit_round_trip)
- #469 [qiyas] CI Linux: bikar-medallion-10-strapwork shape count 555→554 drift
- #470 [qiyas] CI Linux: robustness floors miss on Moroccan-12 jpeg=90, Topkapi-Star crop=0.85

Memory: `feedback_ci_platform_portability.md`. Follow-on: #471 (scope-reduced
to robustness-floors-only after #474 absorption).

## bikar deps — Vite 8 + ws security upgrade

- #388 [bikar] Vite v8 upgrade — clear esbuild dev-server vuln chain (4 moderate)
- #435 [bikar] ws@8.20.0 uninitialized memory disclosure via @supabase/realtime-js

## qiyas#400 Slice 2 — bikar `data-sides` carry-through (parser-side)

Bikar's `render.svg` emits `data-sides="N"` + `data-face-index` + `data-layer`
on every face path. Pre-Slice-2 the qiyas parser discarded those attributes
and the polygon classifier re-derived sides from raster-jittered vertices —
failing on squares (4), pentagons (5), hexagons (6). Slice 2 carries the
metadata onto `Contour` (`source_tag`, `authoritative_sides`, `face_index`,
`layer`); bumps SCHEMA_VERSION 1.13 → 1.14. Slice 3 (consumption side)
shipped as commit fa7e836 — pending CI green to close as #488.

- #487 [qiyas] Slice 2 — thread `data-sides` / `source_tag` through `svg_primitives.py` onto Contour

Source: qiyas commit 59f5beb. Issue: `qiyas/docs/issues/2026-05-18-svg-direct-discards-bikar-data-sides.md`.
Decision: `qiyas/docs/decisions/2026-05-18-shape-vocabulary-vs-detector-tolerances.md`.

## Misc shipped

- #329 [qiyas] [#290 RESCOPE] Petal-N-ring template — drop `where sides == 2`, regen corpus, verify N=4/N=8 classify

---

## CI report standard — meaning-level fixture gate + visual report duo (qiyas#474)

Replaced qiyas's byte-strict fixture-drift comparator with a meaning-level
Pydantic invariants model and pinned the cross-repo CI report standard
(`actions/upload-artifact@v4` + `$GITHUB_STEP_SUMMARY`). Originated in qiyas
#469 → #474 (same fixture, 2 byte-drift failures in 24h driven by mypy-strict /
Pydantic typing refactors); resolved as decision-doc Option D (replace the
contract, not patch it). Standard now realized end-to-end in qiyas; bikar and
sacred-patterns hold pointer docs that activate when their first CI
report-emitting job lands.

- #475 [qiyas] Slice 0 — pin `docs/ci-report-standard.md` + ACCEPT Option D
- #476 [qiyas] Slice 1 — `FixtureInvariants` Pydantic model + first `invariants.yaml`
- #477 [qiyas] Slice 2 — meaning-level comparator + `--strict` byte-strict escape hatch
- #478 [qiyas] Slice 3 — `qiyas fixtures report` + `report-index` CLI subcommands
- #479 [qiyas] Slice 4 — wire artifact + step summary into `.github/workflows/ci.yml`
- #480 [qiyas] Slice 5 — sweep (one fixture in corpus; pre-migrated in Slice 1)
- #481 [qiyas] Slice 6 — `tools/ci-report-validate.py` for inspection skills
- #482 [qiyas] Slice 7 — cross-repo pointer docs + memory entry
- #483 [qiyas] Slice 8 — close cascade, file adoption follow-ups, this entry

Source: qiyas `d5f5a6c`, `059f125`, `699f8ea`, `71d48ae`; bikar `928e05c`;
sacred-patterns `6b27504`. Decision: `qiyas/docs/decisions/2026-05-20-byte-strict-fixture-comparator-decay.md`.
Plan: `qiyas/.claude/plans/2026-05-20-meaning-invariants-and-default-ci-visual-reports.md`.
Standard: `qiyas/docs/ci-report-standard.md`. Memory: `reference_ci_report_standard.md`.

---

## Validation orchestrator — Phase 2 / Phase 3 (`qiyas` as the single analytical pipeline)

Replaced sacred-patterns' parallel analytical tooling (svg-diff, zone-audit,
arch-audit) with `qiyas` sub-commands. Each phase shipped as one bundled
swap PR per the move-not-copy policy in `docs/image-validation-design.md` §5.

- #13 [qiyas] Phase 2: Implement `qiyas pixel-diff` upstream
- #14 [qiyas] Phase 2: Implement `qiyas zone-audit` upstream
- #15 Phase 2: Pre-swap parity validation (3 sessions)
- #16 [sp] Phase 2: Sacred-patterns swap PR — delete svg-diff.sh and zone-audit.py
- #17 [qiyas] Phase 3: Implement `qiyas svg-audit` (A1/A2/A4/A5/A6)
- #18 Phase 3: Pre-swap parity validation for svg-audit (3 sessions)
- #19 [sp] Phase 3: Sacred-patterns swap PR — delete arch-audit.py
- #20 [qiyas] Implement `qiyas score` (unified similarity score + warnings)
- #21 [sp] Wire qiyas score into iteration-validate.sh and weights/sacred-patterns.json
- #22 [bikar] Phase 2: Migrate BIKAR scripts/svg-diff.sh into qiyas in same shipment
- #23 Decide long-running invocation surface for qiyas — Docker CLI selected
- #24 [sp] Update qiyas-diff.sh wrapper to use Python click context
- #26 [qiyas] Build calibration corpus: tag converged iterations across completed sessions
- #27 [qiyas] Implement `qiyas score replay` sub-command
- #28 [qiyas] Implement `qiyas score explain` sub-command
- #29 Split validation.json schema: envelope to qiyas, overall rollup stays in sacred-patterns
- #30 [qiyas] Phase 2 prep: Inventory BIKAR analytical scripts overlapping with qiyas/sacred-patterns
- #31 [qiyas] Phase 2 follow-on: Implement `qiyas raster-diff` thin orchestrator
- #32 [qiyas] A6 baseline-vocab adapter — apply design-new-detector skill
- #33 [qiyas] Consolidated owner-review doc for all open qiyas decisions
- #34 [qiyas] Apply owner decisions to source plans (10 decisions)
- #35 [qiyas] Create qiyas skill for expanding detector and score scope
- #36 [qiyas] Write qiyas svg-audit umbrella design doc
- #37 [qiyas] Establish unit + integration test coverage policy for qiyas Phase 2/3 commands
- #48 [qiyas] [#17 slice 1] A1 semantic census audit
- #49 [qiyas] [#17 slice 2] A2 sector symmetry audit
- #50 [qiyas] [#17] Update qiyas mental-model docs for svg-audit
- #51 [qiyas] Add doc-update prompt to qiyas detector/audit skills
- #52 [qiyas] [#17 slice 3] A4 coverage completeness audit
- #57 [qiyas] [#17 slice 4] A6 baseline-vocab adapter audit
- #58 [qiyas] [#25 slice 1] A5 closed-form-only audit (count-based)
- #61 [qiyas] [#25 slice 4] A5 parity report (validates slice 2 needed)
- #63 [qiyas] Add band_crossing shape type to qiyas + count in A5
- #70 [qiyas] qiyas score: wire svg-audit warnings into composite + warnings array

Decision docs: `docs/image-validation-design.md`, `docs/validation-overall.md`,
`qiyas/docs/validation-envelope.md`.

## Warnings-driven iteration (qiyas warnings + counterfactuals)

Replaced "scores guide iteration" with "warnings guide iteration." Every
detector emits a warnings array with `counterfactual_score_delta`; the
iteration agent reads `validation.json` → `overall.warnings[0]` and translates
the named delta into a code edit.

- #38 [qiyas] Symmetry comparison detector — compare two images' symmetry structure
- #39 [qiyas] Rich warnings across qiyas detectors — drive iteration loop, not just scores
- #40-#47 [qiyas] [#39 slices 1-8] pixel-diff, zone-audit, validate, counterfactual transformers, score thin rollup, sp orchestrator integration, calibration smoke
- #66 [sp] Refactor sacred-patterns iteration skill to consume qiyas warnings + counterfactuals
- #71-#73 [qiyas] [#38 slices 1-3] symmetry-diff fold-only, reflection-axes, per-sector-totals
- #105 [qiyas] Fix symmetry detector for thin-stroke flat-color renders (dilate before MSE)

## I1 shape-identity cascade (qiyas detector capability proof)

Multi-iteration cascade proving detector capability for identity + arrangement
across bikar constructions. Iter-1 through iter-15 covered F1 within-construction
signatures (turning function + provenance fusion), F3 arrangement classifier
(canonical-fit residuals), and corpus expansion (Phase 1.A → Phase 1.B with
arc-bearing templates).

- #142-#156 [qiyas] Cascade spec + corpus + detector implementation (F1/F2/F3 + validate-detector + hint)
- #157 [qiyas] Audit qiyas test suite for fixture-overindexed tests beyond F3
- #159-#161 [qiyas] iter-2: turning_function.py + TF rescue + medallion10 calibration
- #162-#167 [qiyas] iter-3 Option C: ARI cross-check (truth-class rederivation A/B/C)
- #168-#170 [qiyas] iter-3 owner decisions: B-partition granularity, Path 4 multi-view kernel combination
- #171-#177 [qiyas] iter-4/5: provenance distance + fused signature + bidirectional fusion + ARI validation
- #178 [bikar] Phase 1.A corpus addition: Star-10.bkr (decagram {10/3})
- #179-#186 [bikar] Arc-aware face emission (5 spikes + 3 PRs + S2 follow-ups)
- #187-#194 [qiyas] Phase 1.B scaffold + Petal-N-Ring + Petal-N-2ring templates + iter-5/8 validation
- #195 [bikar] DSL `for i in 0..N` loop construct
- #196-#200 [bikar] Lens-emission Option A (edgeKey + arc center/sweep) — Petal-Full +7-vs-+12 discrepancy resolved
- #201-#214 [qiyas] iter-7/8 re-runs + Option I face_class resolver + closeout
- #215 [qiyas] Delete multiset class-matching branch; face_class is sole class-selector path
- #220 Hook: widen decision-doc-watch regex
- #221-#233 [qiyas+bikar] Refined-A face_class-vs-multiset divergence cascade (Phases 0-3 with C3 contract slice)
- #234-#238 [qiyas] iter-11/12 SMI + AMI small-N bias pre-check + γ closeout-as-noop
- #239-#246 [qiyas+bikar] iter-13 Option β asymmetric Wallace + α resolver source_primitives population
- #252 [qiyas] γ-narrow ship record in tally.json
- #253 [bikar] File issue: dominant_arc resolver populates source_primitives for arc-faces
- #268 [qiyas] (deferred) TF scalene_triangle combined-transforms regression — DEFERRED, kept open as #268
- #275-#279 [bikar] α resolver decision doc + impl (edge-tag union) + ARI gate
- #280-#289 [qiyas] I1 entries 1-5 + Phase 0 pipeline unification (Tenet 11)
- #294-#298 [qiyas] I1 closeout: CLI report + dashboard + acceptance.yaml + visual proof
- #300-#310 [bikar+qiyas] α-resolver per-edge sources leak — Option A (TF + clustering handle 2-vertex lens-faces)
- #312-#326 [qiyas+bikar] feedback-classes A1-E1 + same-color-neighbor merge filing + degenerate arc-path fix
- #395 [qiyas] test_v2_face_class_petal_n_2ring_corpus_K4 unpinned to schema 1.18

Decision docs: `qiyas/docs/decisions/` (face_class-vs-multiset, refined-A
parity-scope, K=3 ARI saturation, asymmetric Wallace, gt-emitter width_px).
Calibration log: `qiyas/calibration/i1/tally.json`.

## Region-identity 4-layer chain (bikar#333 cascade)

`connect arc … .petal` did not flow class through to SVG fill emission across
petal-N-ring N ∈ {4,6,8,10}. Diagnosed as 4-layer chain: (1) silent-skip in
applyArcRegionClasses, (2) selector-path stamps faceClasses Map but
(3) gt-emitter reads only edge tags, (4) sides predicate read tessellated
polyline length instead of geometric corner count.

- #290 [bikar] α-resolver per-edge sources leak — fix outerRing.sources for arc-faces
- #327-#332 [bikar#333] Corpus sweep + Option B impl + petal-N-ring template fix + DSL spec doc + silent-emission filter issue
- #406-#408 [bikar] Decision doc (Options E/F/G) + Option E edge-identity probe + Option G geometric-vertex count
- #413 [bikar] Tier 0 unit test — petal-N-ring class-count invariant (per Tenet 17)
- #414 [bikar] Decision doc addendum — source-tag path interaction (2026-05-18)
- #418 [bikar] Option E edge-identity probe matches zero faces on every corpus template
- #419 [bikar] Pre-existing evaluator.test.ts provenance-tagging failures — enriched tag scheme per qiyas#169
- #420 [bikar] Option E silently skipped — selector-path stamps Map but gt-emitter reads only edge tags

Decision docs: `bikar/docs/decisions/2026-05-17-arc-region-class-precision.md`,
`bikar/docs/decisions/2026-05-18-region-identity-class-emission-4-layer-fix.md`.

## Partial-shape rendering cascade (sacred-patterns#106)

Closes medallion-10 ~74% ceiling: extended-then-clipped construction shapes
needed qiyas CLIPPED-MISSING verdict + bikar boundary/extend/clip/intersect
DSL primitives.

- #254 [sp] Decision doc — partial-shape rendering scope & sequencing
- #255-#256 [qiyas] Spec + implement partial-polygon detection + CLIPPED-MISSING
- #259-#260 [sp] CLIPPED-MISSING translation row + iter-14 re-validation
- #261-#267 [qiyas] [#256 slices 1-7] OpenPolyline + partial_polygon detector + pipeline wire + A6 verdict + counterfactual + tests
- #269-#278 [bikar] [#258 PR1+PR2] boundary union(...) + extend modifier + gt-emitter schema 1.16/1.17 + virtual-radius decision
- #367-#370 [bikar] [#258 PR3] clip pattern to <boundary> + arrangement-walk clip + schema 1.19

Decision docs: `sacred-patterns/docs/decisions/` (partial-shape scope),
`bikar/docs/decisions/2026-XX virtual-radius mechanism`.

## Cross-repo engineering tenets (codified to all three CLAUDE.md files)

- #154 Adopt sacred-patterns CLAUDE.md tenets 7 & 8
- #334 [cross-repo] FP-first tenet with language-specific sub-rules
- #336-#337 [cross-repo] Simple-shapes-first tenet (Tier 0 single-primitive corpus) + mirror to qiyas + bikar
- #353-#359 [cross-repo] No `Any`/`any` strict-mode silencer + enforcement (ruff ANN401, mypy disallow_any_explicit, make local.typecheck)
- #373 [cross-repo] Tenet 14: docstring I/O examples for important functions
- #375-#376 [cross-repo phase 2] Mirror Tenet 14 + Tenet 16 to qiyas + bikar
- #377-#380 [cross-repo] TIERS.md canonical definitions + bikar Tier 0 templates + unified pipeline + closeout
- #411 [cross-repo] Tenet 18: codify debug witness as a unit test before shipping fix
- #416 TIERS.md — add asymmetric-witness design contract for Tier 1 entries

## Build-time code validation cascade (5-tier gate stack)

- #341 [cross-repo] Docstring coverage enforcement — ruff D rules + CI gate
- #342 PARENT — Build-time code validation cascade
- #344 [cross-repo] Pre-commit hooks — qiyas/bikar/sacred-patterns
- #345 [cross-repo] Secret scanning — gitleaks
- #346 [cross-repo] Dependency vulnerability scanning — pip-audit + npm audit
- #347 [cross-repo] SAST — semgrep + bandit (qiyas)
- #348 [cross-repo] Dead code + complexity gates (vulture, ruff C901, knip)
- #349 [cross-repo] Import-graph + spell-check (import-linter, madge, codespell)
- #350 [cross-repo Tier 4] Property-based testing for geometry — hypothesis + fast-check
- #382-#386 Drain qiyas/bikar/sacred-patterns docstring grace lists
- #389-#390 Drain qiyas C901 + bikar complexity grace lists
- #392-#394 [bikar+sp] fast-check property tests + qiyas add-new-detector skill update

## Typed-Shape PIVOT (qiyas mypy strict — #339)

Replacing `dict[str, object]` fig-leaf with Pydantic discriminated union per
decision doc `qiyas/docs/decisions/2026-05-16-typed-shape-params-vs-object-bag.md`.

- #338 [qiyas] [#335 slice 1] Add [tool.mypy] strict=true + ignore-missing-imports
- #360-#361 [qiyas] Decision doc + plan: geometric class system
- #366 [qiyas] Type-enrichment cleanup: schema.py + detectors
- #374 [qiyas] Commit #366 type-enrichment cleanup

## auto-iterate cascade

- #101-#104 [sp] auto-iterate Phase 0/1/1.5/2 — manual dry run → driver harness → autonomous Agent → post-iteration capture

## qiyas detector calibration (sub-cascade in I1)

- #107-#108 [qiyas+bikar] Encoder partial-shape detection + symmetry-preserving strapwork crossing modes plan
- #117-#126 [qiyas+sp] #109 Tax A + Tax B fragmentation cost + counterfactual_adjusted_score_delta wiring
- #119-#122 [qiyas+sp] Tax B Docker rebuild + sp orchestrator pointed at Tax-B image
- #124-#126 [qiyas+sp] Score rollup honors negative adjusted_delta + iter-14 re-validation + iter-18 design

## Mental-model upkeep (qiyas#247-#251)

- #247-#251 [qiyas] Audit dev-mental-model.md + extract 6 decision-derived principles + post-ACCEPT skill update + staleness hook

## qiyas product / bundle commits

- #82 Document qiyas product vision (mission, value-add, use cases, impact)
- #83 Rebuild & push qiyas v0.1.1 Docker image (score/baseline/fixtures groups)
- #86 Commit qiyas bundle 1: shipped CLI features
- #93 Commit qiyas bundle 2: docs, plans, skills, mental-model, roadmap rewrite
- #94 Commit sacred-patterns interpret-pattern skill + tools
- #95 Commit sacred-patterns iteration-validate.sh + qiyas-diff.py + validate-svg.sh + analysis tools
- #96 Commit sacred-patterns learn-new-pattern + generate-drawing skill updates + learnings + plans
- #97 Commit sacred-patterns docs/image-validation-design.md + docs/cross-repo-dependencies.md + REFERENCES.md
- #98 [sp] [learn-new-pattern] Resurrect session-1 on qiyas-orchestrator path
- #99 [sp] Write sacred-patterns iteration practice hand-off doc

## Critical-path tool (qiyas#402)

- #401 [audit] Phase 0 — Grade last 5 cascades on production-input-distribution coverage
- #402 [qiyas] viz deps CLI + hook for goal-anchored task graph
- #403 [qiyas] TaskUpdate hook — regenerate viz on task changes + drift warn
- #404 Routing plan §F — mechanical critical-path check replaces §A Class 5
- #405 Drift audit — backfill last 30 loop pickups against critical path

## SVG-direct path (sacred-patterns#396-#397)

- #396 [sp] Decision doc — eliminate rasterize→trace round-trip vs preserve as defense-in-depth
- #397 [sp] Q1 gt-fidelity audit gate for Option A

## Other shipped work

- #64 [qiyas] CLI help/man-page generation with staleness hooks
- #65 [qiyas] Hook: capture pattern-analysis edge cases as text fixtures
- #67 [qiyas] qiyas trace --show unknown — visual triage for unknown classifications
- #68 [qiyas] make regen-baselines target — ergonomics for detector-addition test-baseline updates
- #69 Cross-repo task linkage convention — sacred-patterns ↔ qiyas ↔ bikar
- #76 [qiyas] [V2.D] Construction hints — design spike (FOLDED into #151)
- #79 [qiyas] qiyas score backfill — re-run scoring against historical iterations
- #81 [qiyas] qiyas baseline emit IMAGE — auto-generate baseline.json from qiyas encode
- #84 Make qiyas-score unavailability a loud blocker (revised: no synth fallback)
- #110 [sp] Iter-17: drive next iteration from iter-14 warnings[0]
- #125 [sp] [#123] Re-validate iter-14 with Tax-B image
- #126 [sp] [#123] Read iter-14 Tax-B warnings[0] and design iter-18 edit
- #130-#137 [bikar+qiyas] #129 PR1 gt-emitter + validate-detector + over-segmentation/symmetry fixes + truth-overlay tool
- #139-#141 [qiyas] [#138] K-sweep diagnostic + findings appended + count-fidelity metric
- #294 [qiyas] [#284] Diagnose pinwheel render: chiral arms invisible
- #295 [qiyas] [#284] Run validate-detector on pinwheel + sunflower
- #305 [qiyas] [#300 RESCOPED] Option A impl — extend TF + A-clustering for 2-vertex lens-faces
- #381 [bikar] [#358 follow-on] Type-augment packages/web/src/main.ts DOM monkey-patches
- #409 [qiyas] [#311] Owner pick — detector capability gap on color-derived classes
- #410 [sp] [#398 BLOCKER] Owner clarify Option A mechanism: gt.json as geometry vs label oracle
- #412 [debugging-tooling] Investigate code-graph visualization for impl/dep/test-coverage tracking
- #417 [qiyas] [#311 Q1] star7 gt.json has face_class=None + fill=None for all 30 shapes

## Counterfactual fragmentation tax (qiyas#109 / #118)

Bounded the cf_delta upside-only bias surfaced by iter-15/16/17 of bikar-medallion-10 (per `feedback_cf_delta_cost_blind` memory). Plan named 5 fix archetypes; Tax B subtracts predicted fragmentation cost from raw composite_delta.

- #109 [qiyas] Plan: counterfactual fragmentation/interaction tax
- #118 [qiyas] Implement #109 PR2 — Tax B fragmentation cost (fix-archetype classifier)

## Strapwork rotation canonicalisation (bikar#113 / #115)

Root-caused iter-16 medallion-10's 247 sector-fragmenting band extras to `assignStrands` outer-loop non-invariance. Audit confirmed medallion-10 is NOT Hankin-PIC, so the fix is the seed-order canonicalisation in #114 PR1 (commit bikar 8bc6735), not a new strapwork mode. `data-strand` IDs are renderer-internal — verified label-agnostic. #114 stays in-flight (PR1 slice 2 — orchestrator re-render validation — is owner-gated).

- #113 [bikar] Plan: rotation-canonicalize strapwork strand assignment — see `sacred-patterns/.claude/plans/bikar-strapwork-rotation-canonicalization.md`
- #115 [bikar/research] Audit: medallion-10 is NOT Hankin-PIC; strapwork kernel correctly input-agnostic — see `bikar/docs/issues/2026-05-18-medallion-10-is-not-hankin-pic-audit.md` (commit bikar 8096047)

## Universal DSL Tagging cascade (Tenet 23 / qiyas#491-#503)

DSL-as-source-of-truth: when bikar authors a fact (face class, symmetry
fold, side count), that fact propagates through SVG `data-*` as
authoritative; qiyas reads instead of re-deriving from geometry. Cascade
codified the principle as a cross-repo tenet, shipped the contract doc,
wired producer + consumer + matcher + scorer in 5 slices, then added a
runtime `qiyas validate-dsl-contract --strict` CLI + Slice 5a "every
contract row has a witness test" CI gate. Dissolved qiyas#490 anti-symmetry
breach at root (Hexagram vs Star-8 score 0.560 → below 0.55 floor); also
closed half of qiyas#400 type-vocabulary lumping.

- #491 [cross-repo] Slice 0 — Tenet 23 (sp/bikar/qiyas mirrors) + DSL Metadata Contract v1 + decision doc
- #492/#497 [bikar] Slice 1a/1b — emit `data-face-class` + `data-symmetry-fold` from svg-renderer
- #493/#498 [qiyas] Slice 2a/2b — Contour consumes `face_class` + `symmetry_fold` via SCHEMA 1.14→1.15
- #494 [qiyas] Slice 3 — matcher + scorer use the new fields; close #490
- #499 [qiyas] Slice 3a — plumb face_class + symmetry_fold from Contour onto Shape
- #500 [qiyas] Slice 3b — Hungarian cost adds CLASS_MISMATCH_COST on mismatch
- #501 [qiyas] Slice 3c — `_check_dominant_fold` consults Shape.symmetry_fold before re-derivation
- #496 [qiyas] Slice 5a — `tests/test_dsl_metadata_contract.py` gate (every contract row → witness test)
- #503 [qiyas] Slice 5b — `qiyas validate-dsl-contract --strict` runtime CLI subcommand
- #488 [qiyas] #400 Slice 3 — polygon classifier consumes Contour.authoritative_sides as hint
- #490 [qiyas] Anti-symmetry breach dissolved (Star-8 svg vs Hexagram raster, 0.560 → < floor)
- #400 [qiyas] Type-vocabulary lumping closed (squares/pentagons/lenses no longer → unknown via SVG path)

Decision docs: `sacred-patterns/docs/decisions/2026-05-20-universal-dsl-tagging.md`,
`qiyas/docs/decisions/2026-05-20-qiyas-anti-symmetry-floor-breach.md`.
Pending: #504 Slice 5c (cross-repo GHA wiring), #495 Slice 4 (construction provenance, trigger-gated).

## CI hygiene — make-target-mirrors-CI policy (qiyas#502 / #505)

Establishes that every CI job has a `make local.*` equivalent so dev box can
reproduce CI failures; `ci-local-fast` runs the 5 sub-30s gates as the pre-push
hook the Tenet-19 "log + ship" rule depends on. The timeout-minutes:30 fix
backfired on actual ~100min CI pytest runtime; raised to 90min in 3c1fedc;
#506 filed to investigate the 3.4x dev-box vs CI gap.

- #502 [qiyas] make target for sample CI artifact report (per ci-report-standard.md)
- #505 [qiyas] `timeout-minutes: 90` on pytest step (replaces the GHA 6h job default)

## Test discipline — taxonomy + divergence enforcement (qiyas#158 / sp#78)

Closed two strategic doc/skill gaps that the I1 cascade kept tripping over: (a) ALGORITHM vs INTEGRATION test intent was unnamed, letting per-fixture ARI scores stand in for algorithm correctness across 13 iterations (Tenet 7/8 failure pattern); (b) the divergence policy in `qiyas/docs/sacred-patterns-integration.md` was documented but unenforced (strategic gap #6), letting workarounds land without filed qiyas issues.

- #158 [qiyas] Test taxonomy — ALGORITHM (synthetic, pin invariants) vs INTEGRATION (real fixture, pin pipeline well-formedness) — see `qiyas/docs/test-taxonomy.md`; cross-linked from dev-mental-model §12 and the four add-* skills (commit qiyas ec9af06)
- #78 [sp] `escalate-qiyas-divergence` skill — capture fixture / file qiyas issue / cross-link / decide wait-vs-workaround with deletion deadline; iteration-guide §C0 cross-references it (commit sp 6cea752)

## bikar face-extractor per-component outer-marking (qiyas#513 / #512)

bikar's `markOuterFace` picked the single largest-|area| face globally — correct
for single-component planar graphs, but lost K-1 outer cycles when the graph had
K disjoint components, surfacing downstream as ghost bounded faces with reversed
winding. Discovered while authoring the Tier 1 corpus entry `square-and-scalene`
(square + scalene triangle, no shared geometry): gt.json emitted 3 shapes instead
of 4, dropping the scalene triangle. Fix uses union-find on twin half-edges to
identify components, then per-component largest-|area| with positive-signedArea
tie-break for polygon-only components. Cross-repo cascade: bikar commit 36a4886
+ qiyas commit 06067ea ship together; `qiyas validate-detector` now reports
`macro_ari_fused_vs_b = 1.000` across **20/20** corpus entries (was 12/12;
admits 7 Tier 0 single-primitive + 1 Tier 1 composition).

- #513 [bikar] face-extractor: mark one outer cycle per connected component
- #512 [qiyas] Ship square-and-scalene as first Tier 1 corpus entry

Witnesses filed with the fix (Tenet 18):
- `packages/core/tests/graph/face-extractor-disjoint-components.test.ts` (3 tests: 2 squares, square+scalene, 3 triangles)
- Updated `packages/core/tests/render/gt-emitter-extension-factor.test.ts` from "every face = 1.5" (relied on master's accidental gt-emitter self-cancellation when both octagon cycles stayed bounded) to "dominant-vote: at least one face = 1.5"
