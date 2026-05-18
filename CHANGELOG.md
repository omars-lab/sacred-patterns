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
