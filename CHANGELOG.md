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

## 2026-06-11 — review-portal aesthetic feedback cascade (#2–#12)

The portal grew from a topology checker into the owner's full feedback surface:
plain-language guided review (grandma bar, Tenet 27), aesthetic annotation
kinds, and a readiness gate so expert eyes are only asked for when machine
metrics say the render is worth their time. Decision trail: qiyas
review-portal docs + bikar 403f670.

- #2  [bikar] Deco-only strapwork kernel fix (bikar#653) — shipped 403f670 (girih fields weave the decoration network only)
- #3  [qiyas] Annotation schema for aesthetic feedback — Q9 color / Q10 shape / Q11 style kinds in state.py
- #4  [qiyas] Review-pass iter-34, pick canonical render — SUPERSEDED, never executed: the wave-based gate flow (#37/#50) replaced the canonical-render pick; closing stale
- #5  [qiyas] Portal UI for Q9/Q10/Q11 aesthetic kinds — shipped
- #6  [qiyas] Grandma-mode review page — no-jargon guided review shipped
- #7  [qiyas] Spot-the-difference structural review — bidirectional mirror + mismatch datapoint
- #8  [qiyas] Replay ranking fix — structural stubs ranked before colour/style
- #9  [qiyas] One-command review launch + server-origin URL fix
- #10 [qiyas] Web compare upgrades — lens, flip/blink, hints, resume, saved dots
- #11 [qiyas] End-to-end verify upgraded portal on iter-34 — visual check passed
- #12 [qiyas] Review-readiness gate — CLI refuses expert review when metrics say not-converged

## 2026-06-11 — annotations → hypothesis handoff cascade (#13–#19)

Owner clicks in the portal now land as a seeded `hypothesis.md` in the next
iteration directory — the loop's feedback wiring.

- #13 Plan: automate annotations → hypothesis.md handoff
- #14 [qiyas] review-verdict module + emitter (verdict.py) with tests
- #15 [qiyas] CLI --emit hypothesis + review-path command
- #16 [sp] portal-handoff.py + seed-hypothesis.py + tests
- #17 [sp] auto-iterate terminal_state + SKILL seed integration
- #18 End-to-end witness on medallion-10 + decision note
- #19 [sp] auto-iterate render_bkr fix — require() fails on bikar's ESM dist

## 2026-06-11 — medallion-10 iters 35–38 + engine-gap cascade (#20–#26, #28–#31)

The pre-wave iteration era (bold straps → measured palette → pocket density →
color-role transfer) and the engine-restraint audit that fed four bikar engine
gaps. Outcome docs: iterations/35–38 hypothesis.md; bikar engine commits per gap.

- #20 [sp] Iter 35: bold straps from seeded hypothesis
- #21 [sp] Iter 36: palette-family pass, measured not guessed
- #22 [sp] Iter 37 scope: pocket-star density (invocation gap vs engine work)
- #23 [bikar] resolveLensPockets kernel + DSL `pockets` flag
- #24 [sp] Iter 37: pocket-star density via `pockets`, A/B vs iter-36
- #25 [sp] Iter 38: measured color-role transfer at face centroids
- #26 Plan: engine-restraint audit at the 74% plateau — fed gaps 1–3 below
- #28 [bikar] `!=` comparator in fill/classify/style conditions (Gap 2)
- #29 [bikar] authoritative `sides` in gt.json + contract amendment (Gap 3)
- #30 [bikar] hexagon `pockets star` variant via Hankin 54° (Gap 1)
- #31 [bikar] parser registers queried source names for kernel-applied tags

## 2026-06-11 — stage-gated reconstruction cascade (#32–#35)

Structure → color → weave, each behind an owner gate. Plan: bikar
`.claude/plans/vectorized-squishing-pearl.md`; protocol lives in the
iterate-construction-hypothesis SKILL stage ladder.

- #32 [sp] make-structure.py + structure-diff.sh skeleton tooling
- #33 [sp] analyze-reference.py — line/fill split, standardized palette, swatch sheet
- #34 Protocol + docs + skills amendment: stage field, freeze check, stage gates
- #35 Stage-1 audit of iter-39 → first structure + palette gate packages

## 2026-06-11 — wave-plan studio + wave-run support cascade (#36–#38, #40–#49, #52–#56)

The owner-facing wave-plan studio (plan/palette/iterate/slides pages on
wave-plan-server.py) and the engine/tooling fixes that kept the wave run
moving. The wave run itself (waves 1–15 passed as of 2026-06-11, iters 41–57)
stays open under #50. Skill: wave-planning + iterate-construction-hypothesis
(cookbook + end-of-build reflection).

- #36 [sp] Owner-driven structure matching — center validation + click-to-prioritize
- #37 [sp] Wave-plan experience — radial reconstruction waves over the reference
- #38 [sp] Motif level — composite shapes revolving around the center
- #40 Codify wave planning + incremental radial walk as skill + design doc
- #41 [sp] Interactive grouping editor on the wave-plan page
- #42 UX audit of all review experiences
- #43 [sp] Review-UX recommendations — hub + gate buttons + palette page
- #44 [sp] Wave-switch preview — destination wave highlighted on dropdown change
- #45 [sp] Flower views — repeated unit + orbit called out explicitly
- #46 [sp] Wave views — dotted circle through wave shape midpoints
- #47 [sp] Studio arrow keys flip next/previous view
- #48 [sp] One-command wave-planning entry for a new reference image
- #49 [sp] wave-diff.py — per-wave masked/cropped comparison
- #52 [bikar] evaluator dedup drops concentric same-edge-count faces — area added to dedup key
- #53 [bikar] svg-renderer strapwork bands between layer-0 and higher-layer face groups
- #54 [sp] Studio /iterate page — wave-by-wave progress view (788c4c5)
- #55 [sp] Iteration cookbook distilled into iterate-construction-hypothesis SKILL (8dcec96)
- #56 [sp] Studio /slides reveal.js deck — consistent frame, fixed title, recipe-diff slides (8dcec96, 819c8be)

## 2026-05-29 — pre-existing meta-tasks archival (#80/#85/#100/#129/#132)

Long-lived umbrella tasks that drove multi-cascade work; the underlying
work was shipped piecewise under their own cascade entries above. Archiving
the umbrellas now that all sub-work has cleared.

- #80  [qiyas] [catch22-driver] Restart bikar-medallion-10 iteration under qiyas-orchestrator era — closed; medallion-10 hit A4+A2 interim acceptance bar (see 2026-05-28 girih cascade)
- #85  [bikar] [TOP-PRIORITY] Drive bikar-medallion-10 to convergence (wedge-and-rotate from iter 13) — closed at iter-34 A4+A2 (girih substitution cascade outcome)
- #100 [qiyas] Push qiyas v0.1.1 to ghcr.io — shipped (ghcr publish)
- #129 [qiyas] [TOP-PRIORITY] Detector calibration via construction ground-truth (3-repo cascade) — shipped (I1 cascade)
- #132 [qiyas] [#129 PR3] Calibration corpus of construction-grounded test cases — shipped (corpus + Ticks 1-93 sweep, see 2026-05-28 #132 entry below)

## 2026-05-29 — F2 cross-construction validation cascade (#661 Option C falsified → owner-handback)

The F2 cross-construction signature cascade (qiyas#302 ACCEPTED Option B) tried to
gate retrieval on bikar's authoritative DSL `data-shape-id` (Option C in
`qiyas/docs/decisions/2026-05-29-f2-face-class-is-wrong-retrieval-label.md`).
Steps 1-4 shipped clean (data-shape-id contract, emitter, gt-evidence threading,
F2 relabel), but Step 5 falsified at the producer-discipline premise: real .bkr
templates reuse author-chosen names like `scalene_tri_poly` across geometrically
distinct triangles. Retrieval scored under shape_id gave mAP=0.296 — WORSE than
the face_class baseline (0.607) and far worse than the detector's geom_label
(0.892). Handle-falsification protocol executed: decision doc REOPENED, witness
test in place (`tests/test_identity_f2_eer.py`), Option E drafted (gate on
geom_label, EER=0.035, zero new code), Option F (escalate-to-owner) selected as
recommendation per Tenet 19 stop-rule c. Cross-repo memory entry filed.

- #660 [qiyas]   Accept #302 decision doc — F2 validation Option B (separate cascade, retrieval+EER)
- #661 [qiyas]   F2 cross-construction validation cascade umbrella — falsified at Step 5, handed back to owner via #669
- #663 [bikar]   [#661 Option C step 1] data-shape-id contract amendment — SHIPPED
- #664 [bikar]   [#661 Option C step 2] svg-renderer emits data-shape-id + Tier-0 witness — SHIPPED
- #665 [qiyas]   [#661 Option C step 3] gt-emitter carries data-shape-id into evidence.shape_id — SHIPPED
- #666 [qiyas]   [#661 Option C step 4] F2 relabel to shape_id + 3rd report column — SHIPPED (then falsified)

Witnesses + memory filed with the falsification (Tenet 18, handle-falsification):
- `tests/test_identity_f2_eer.py` — falsifying witness frozen as regression test
- `feedback_synthetic_test_cant_validate_unenforced_producer_discipline` — Tier-0 hand-assignment can't validate unenforced producer discipline; re-score on real corpus before picking a producer-authored gate oracle

## 2026-05-28 — feedback-classes A/B1/B2 round-trip cascade (#670/#315/#316)

Three-slice cascade wiring reviewer verdicts from the closeout dashboard back
into validate-detector reports and forward into the next iteration's tooltips.
Closes the round-trip from "reviewer flags wrong_class in pane" → JSONL → next
report's `per_shape_labels.user_verdict` → next dashboard's SVG `<title>` +
shape_index. The verdict enum is closed-set + pydantic-enforced so widening
requires coordinated producer+consumer change.

- #670 [qiyas] [feedback-classes A] Structured verdict field in closeout-dashboard feedback pane — SHIPPED
- #315 [qiyas] [feedback-classes B1] qiyas validate-detector --apply-feedback FEEDBACK.jsonl — SHIPPED
- #316 [qiyas] [feedback-classes B2] Surface user_verdict in closeout dashboard tooltip + shape_index — SHIPPED

## 2026-05-28 — post-I1 cascade roadmap + I1 ratchet hygiene (#656/#662)

I1 acceptance shipped; closing out post-I1 routing. #656 fixed the ratchet
to walk the construction tree directly instead of trusting the cached
corpus.json index (which silently masked newly-added witnesses). #662 authored
the post-I1 cascade roadmap with dependencies (closes the #304 deferred slot
with a real plan instead of an aspirational task).

- #656 [qiyas] I1 ratchet hygiene — discover_constructions walks tree, ignores corpus.json index
- #662 [qiyas] Author post-I1 cascade roadmap plan with dependencies (closes #304)

## 2026-05-28 — F3 corpus-wide coverage gate authorable subset (#301)

F3 gates G5 (corpus coverage) authored and shipped against the I1 corpus.
G6/M3 (per-shape verdict-vs-truth) deferred to #668 (trigger-gated on closeout
integration) because the truth oracle doesn't exist in the record the gate
would read; ship the authorable subset, don't invent the oracle.

- #301 [qiyas] F3 gates — corpus-wide F3 coverage test (G5 subset; G6/M3 deferred to #668)

## 2026-05-28 — I1 corpus expansion + bikar starter-pattern regression (#299/#659)

- #299 [qiyas] I1 corpus expansion — asymmetric witnesses expected to fail (paired-witness pattern per Tenet 8)
- #659 [bikar] [roadmap L81] Starter-pattern compile regression test + remove stray empty iter-1.bkr

## 2026-05-28 — full-suite foundation re-verification (#658)

The I1 detector metric (macro_ari_fused_vs_b=1.000) is a lossy projection
that masked three failures only the **full** qiyas pytest suite caught
(surfaced once the local cairo env gap was closed). Adjudicated per failure
(real-regression vs stale-baseline), not blanket re-frozen (Tenet 7):

- **Real code defect (fixed):** `svg_audit/_vocab.py::vertex_count_from_params`
  still read the obsolete nested `params.points` / `params.sides`. The
  qiyas#362/#536 ShapeUnion migration flattened those onto the shape dict
  (`StarPolygonShape.points`, `RegularPolygonShape.sides`), so every
  parametric shape resolved to vertex_count=None — collapsing all stars/
  polygons into the A6 vc=None bucket and breaking the emit→audit
  round-trip (`test_baseline_emit`). Fix reads top-level fields with a
  `params` legacy fallback; witness frozen in `tests/test_vocab_vertex_count.py`.
- **Stale baselines (re-frozen w/ provenance):** `test_iter14_detector_baseline_histogram`
  dropped `('regular_polygon',20):9` and `test_star7_red_shape_metadata`
  corpus audit grew 20→110 entries + iter14 (275→266). Both trace to the
  accepted #132 gt-emitter Polsby-Popper sliver filter (bikar 61c207b)
  dropping 9 degenerate ~0-area 20-sided lasso faces, plus the #132 Tick
  witness fixtures entering the corpus. No detector regression.

## 2026-05-28 — medallion-10 girih substitution cascade (iter-31→34, A5 0→100)

The medallion-10 wedge-and-rotate construction hit a ceiling: the 10-fold
girih field couldn't be hand-authored without gap-ridden micro-misalignment,
and the A6 missing-shape audit kept failing because the construction couldn't
produce the baseline's girih vocabulary. This cascade replaced the hand-author
approach with a geometry-derived decagonal girih field, then discovered the A5
band-crossing-integrity fix was an **invocation gap** (Tenet 26 #1 fork): the
`strapwork` weave primitive already existed in the kernel — A5 flipped 0→100
by rendering the decoration lines as woven bands instead of filled faces, no
new geometry. The girih substitution-rule-engine option (C′) was falsified at
the data-availability premise (the Lu-Steinhardt decagon rule is figure-only,
untranscribable) and pivoted to C″ (discover the arrangement from geometry, no
lookup table). Acceptance bar settled as A4+A2 interim (A6 baseline mismatch is
a construction-philosophy gap, not a fixable verdict — see memory). Decision
doc + plan: `bikar/.claude/plans/girih-substitution-rule-engine.md`.

- #646 [bikar]  [#85 iter-31] Girih central decagon tile — Tier-0 construction probe — SHIPPED
- #647 [bikar]  [#85 iter-32] Girih decagonal rosette — central decagon + 10-bowtie ring — SHIPPED
- #648 [bikar]  [medallion-10 girih-ceiling] Add girih field-generator to kernel (Lu-Steinhardt inflation) — superseded by C″ frontier-expansion
- #649 [bikar]  Slice 0 — Tenet 26 + decision-doc Option C′ — C′ falsified at data-availability premise, pivoted to C″
- #650 [bikar]  Slice 1 — Decagonal girih field via frontier expansion (C″) — SHIPPED
- #651 [bikar]  Slice 2 — girih field decagonal DSL sugar — SHIPPED
- #652 [bikar]  Slice 3 — medallion-10 iter-33 + A6/A5 measurement — measured, surfaced A5 invocation gap
- #653 [bikar]  Slice 4 — pocket-filling + strapwork overlay — A5 0→100 via `strapwork` invocation (Tenet 26 #1 fork)
- #654 [bikar]  Close (1) — re-derive A6 baseline from girih-vocabulary reference — A6 6/10→6/6 after vtx=0 catch-all strip
- #655 [bikar]  Close (2) — adopt A4+A2 as interim medallion-10 acceptance bar — ACCEPTED

Witnesses + memory filed with the fix (Tenet 18):
- `feedback_girih_strapwork_is_render_style_not_geometry` — A5 flips via render-style, not geometry
- `feedback_transcription_option_data_availability` — verify transcription data obtainable before costing the option
- `feedback_qiyas_baseline_emit_vtx0_catchall_drift` — strip vtx=0 catch-alls before A6 audit
- `feedback_a6_baseline_construction_philosophy_mismatch` — stop iterating an A6 verdict the philosophy can't produce

## 2026-05-28 — #132 Tier 1 Ticks 76→93 polygon-corner-leakage sweep + Phase 3/4 root-cause + closeout

Continuation of the #132 Tier 1 corpus sweep. Ticks 76→93 mapped a non-
monotonic absorb/escape/leak matrix across polygon symmetry × DCEL vertex
degree × tangent coincidence, chasing a "polygon-corner tag leakage" symptom
through a parity hypothesis that was REFUTED at D_8 (Tick 91: octagon clean-
escapes despite the predicted leak). Phase 3 then found the **root cause** at
the bikar gt-emitter: the face-walker emits a ~0.02 px² 4-vertex all-arc lasso
sliver at lens-anchored polygon-corner vertices; a Polsby-Popper compactness
gate at the gt-emitter (n≥3, lens exempt) dissolves all of them — the eight
prior symptom-probe memories collapse to one root-cause entry. Phase 4
regenerated the i1 baselines against the fixed bikar (61c207b) and re-measured
the closeout gates; acceptance.yaml expected_constructions bumped 12→108. Two
cross-repo process tenets landed alongside: no construction ships without
review-portal visual verification, and the iteration skill must hypothesize
construction-DSL variants (not threshold tweaks).

- #620 [qiyas]  [#132 Tick 76] D_4 cross-polygon shared-C0 — polyclass trap fires universally
- #621 [qiyas]  [#132 Tick 77] Homogeneous-radius degree-4 tangent contamination
- #622 [qiyas]  [#132 Tick 78] Dormant strays at unenrolled circle-crossings stay dormant — PASS
- #623 [qiyas]  [#132 Tick 79] Asymmetric + co-tangent decoupling — radius decoupled from tangent
- #624 [qiyas]  [#132 Tick 80] Degree-6 + co-tangent compound over-emission — closed degree×tangent matrix
- #625 [qiyas]  [#132 Tick 81] Polygon-anchored escape sweep
- #626 [qiyas]  [#132 Tick 82] Boundary collapse probe
- #627 [qiyas]  [#132 Tick 83] Universal-leakage finding (later superseded)
- #628 [qiyas]  [#132 Tick 84] Closed polygon-anchored matrix
- #629 [qiyas]  [#132 Tick 85] Falsified polygon-class-independence
- #630 [qiyas]  [#132 Tick 86] Refuted interior-angle monotonicity
- #631 [qiyas]  [#132 Tick 87] NOVEL HYBRID — octagon partial escape
- #632 [qiyas]  [#132 Tick 88] Falsified universal-leakage
- #633 [qiyas]  [#132 Tick 89] Heptagon D_7 deg-4 — even-vs-odd parity discriminator
- #634 [qiyas]  [#132 Tick 90] Triangle D_3 deg-4 — small-D parity, CLEAN as predicted
- #635 [qiyas]  [#132 Tick 91] Octagon D_8 deg-4 — parity rule REFUTED (clean escape, predicted leak)
- #636 [qiyas]  [#132 Tick 92] D_4 + CL_a shift — H1/H2/H3 parity-replacement search
- #637 [qiyas]  [#132 Tick 93] Scalene quad non-canonical tangent — H1 discriminator probe
- #638 [bikar]  [#132 Phase 3] Bikar source audit — tangent-sort tie-break root cause + PP sliver gate
- #639 [qiyas]  [#132 Phase 4] Regenerate i1 corpus baselines against bikar 61c207b
- #640 [bikar]  [#85 probe] Re-validate medallion-10 iter-30 against bikar 61c207b sliver-fix
- #641 [qiyas]  [#129 PR3 follow-up] Measure post-Phase-4 i1 closeout gates G1-G4 on regen baselines
- #642 [qiyas]  [#641 follow-up] Bump i1 acceptance.yaml expected_constructions 12 → 108
- #643 [qiyas]  [#129 PR3 follow-up] Fix spurious G3 HOLDs from visibility-filter scope mismatch
- #644          Cross-repo tenet: no construction ships without review-portal visual verification
- #645 [sp]     Extend iteration skill to hypothesize/attempt construction-DSL variants (not threshold tweaks)
- #657 [qiyas]  Reconcile #132 polygon-corner-leakage cascade closure post-sliver-filter — closeout verified

Witnesses + memory filed with the fix (Tenet 18):
- `feedback_bikar_gt_emitter_sliver_filter_dissolves_polygon_corner_leakage` — RESOLVED root-cause entry (supersedes 8 symptom probes)
- `feedback_bikar_polygon_corner_leakage_deg4_non_monotonic` — parity rule refuted at D_8
- `feedback_pattern_extrapolation_at_n5_breaks_at_n6` — meta-lesson: pre-compute the discriminator on the next out-of-class witness before strengthening a rule

## 2026-05-27 — #132 Tier 1 Ticks 63→75 + GHA-spend structural cascade + owner-pick execution batch

Batch archive of 22 completed tasks across four threads. Thread 1: qiyas#132
Tier 1 corpus expansion Ticks 63→75 (13 entries) extending shared-vertex /
shared-circle / multi-lens combinatorics — established N-lens-on-shared-C0
independence rule (N=1/2/3, D_4/D_5), promoted Tick 23's degree-6 all-arc
risk to a witnessed bikar limitation, sharpened rule boundary. Thread 2:
GHA-spend Tenet 22 structural cascade — added `paths-ignore` + `concurrency`
+ `timeout-minutes` to workflow YAML across qiyas + bikar; installed
nektos/act for local workflow mirroring; codified governance line in all
three CLAUDE.md files. Thread 3: 2026-05-24 owner picks executed end-to-end
— #525 Phase 1 D4 single-cutover, #138 medallion-10 iter-18 render, #597
evalMirror fix following naming-conventions plan; hier-diff PR2 sector-
aware + PR3 warning rollup. Thread 4: older closeouts (#77 V2.E auto-
capture, #112 hier pixel-diff core implementation).

### Thread 1 — #132 Tier 1 Ticks 63→75 (13 entries, qiyas + bikar)

Tick 63 probed `mirror` primitive (asymmetric scalene mirror across axis);
surfaced bikar evalMirror bug — reflected polygon body silently not emitted
as a second face. Tick 68 falsified path-a intersect-derived shared-vertex
on first try (non-convex-hull-tangent placement + homogeneous-sides classify
predicate). Tick 68b re-authored with convex-hull-tangent + heterogeneous-
sides; SHIPPED PASS, confirms Tick 21 path-a as a working recipe. Ticks
69/70/71 established polygon+lens-on-shared-circle independence at D_4 / D_5
/ D_6 — refined Tick 25's conditional-arc-enrollment rule to a tighter
local-not-propagated boundary. Ticks 72/73/74 extended to multi-lens-on-
shared-C0 (N=2 D_4, N=3 D_4, N=2 D_5) — N-lens independence rule witnessed
across both N and polygon-symmetry dimensions. Tick 75 FALSIFIED — triple-
lens-shared-vertex (degree-6 all-arc incidence) confirms Tick 23's flagged
risk; the rule boundary is now sharply defined (works for spatially-
disjoint or polygon-anchored; breaks for ≥3 lenses converging at one
all-arc vertex). Six new feedback-type memory entries indexed in MEMORY.md
across the 13-tick batch.

- #596 [qiyas]  [#132 Tick 63] Probe `mirror` primitive — asymmetric scalene mirrored across axis
- #611 [qiyas]  [#132 Tick 68] First intersect-derived shared-vertex (Tick 21 path-a)
- #612 [qiyas]  [#132 Tick 68b] Re-author Tick 21 path-a with heterogeneous-sides + convex-hull-tangent
- #613 [qiyas]  [#132 Tick 69] Polygon-and-lens-shared-circle Tier 1 — square on C0 + lens C0×CL
- #614 [qiyas]  [#132 Tick 70] Pentagon-and-lens-shared-circle — D_5 polygon × shared C0
- #615 [qiyas]  [#132 Tick 71] Hexagon-and-lens-shared-circle — D_6 polygon × shared C0
- #616 [qiyas]  [#132 Tick 72] Square-with-two-lenses-shared-circle — multi-lens independence on shared C0
- #617 [qiyas]  [#132 Tick 73] Multi-lens shared-circle — N=3 lenses (Tenet 8 3-witness)
- #618 [qiyas]  [#132 Tick 74] Multi-lens shared-circle — D_5 orthogonal polygon-symmetry witness
- #619 [qiyas]  [#132 Tick 75] Triple-lens-shared-vertex — degree-6 all-arc incidence FALSIFIED (negative witness retained per Tenet 18)

### Thread 2 — GHA-spend Tenet 22 structural cascade (5 entries, qiyas + bikar + sp)

After 2026-05-26 GHA spending-limit breach froze the loop, this cascade
codified the budget discipline as a structural rule. Workflows now carry
`paths-ignore: ['**.md', 'docs/**', '.claude/**']` + `concurrency.group`
with PR-only `cancel-in-progress` + `timeout-minutes`. nektos/act installed
locally to mirror workflows pre-push. CLAUDE.md Tenet 22 (bikar) and
mirror conventions added to qiyas + sp. Owner-only Slice E (raise spending
limit + set org cap) remains pending as #603.

- #599 [qiyas]  [gha-spend] qiyas ci.yml: add paths-ignore + concurrency + timeout-minutes (Slice A)
- #600 [bikar]  [gha-spend] bikar deploy.yml: add paths-ignore + concurrency + timeout-minutes (Slice B)
- #601 [bikar]  [gha-spend] bikar bump-peer-deps + sync-patterns: timeout-minutes audit (Slice C)
- #602          [gha-spend] CLAUDE.md governance line — 3 repos (Slice D)
- #604          [gha-spend] Install nektos/act for local workflow mirror (Slice E my part)

### Thread 3 — 2026-05-24 owner picks executed (7 entries, qiyas + bikar)

#525 Phase 1 D4 schema cutover — single-cutover migration with baseline
regen (no compat shims per cross-repo no-backcompat tenet). #138 Slice 2
rendered medallion-10 iter-18 with visual confirm of design-drift hypothesis
from the 2026-05-22 re-scope decision doc. #597 evalMirror fix gated on
#607's derived-shape naming-conventions plan (mirror/rotate/transform
composition) so the producer-side fix could land coherently with future
rotate/transform work. #598 closed the bikar mental-model doc gap by
authoring the end-to-end cross-repo flow doc. hier-diff PRs 2 and 3
landed sector-aware mode for rotationally symmetric patterns and wired
warnings into the score rollup.

- #597 [bikar]  evalMirror: reflected polygon body not emitted as second face
- #598          mental-model: end-to-end cross-repo flow doc + close bikar mental-model gap
- #605 [qiyas]  [#525] Phase 1 D4 schema cutover — single-cutover, regen baselines
- #606 [qiyas]  [#138 Slice 2 / #516] Render medallion-10 iter-18 + visual confirm
- #607 [bikar]  [#597 prereq] Derived-shape naming-conventions plan (mirror/rotate/transform composition)
- #608 [qiyas]  hier-diff PR2: sector-aware mode for rotationally symmetric patterns
- #609 [qiyas]  hier-diff PR3: wire warnings into score rollup

### Thread 4 — Older standing closeouts (2 entries)

- #77  [qiyas]  [V2.E] Auto-capture on GO — populate fixture corpus from converged sessions
- #112 [qiyas] Implement hierarchical pixel-diff (per #111 plan) — quadtree + SSIM, 3 PRs

---

## 2026-05-26 — V2 iteration-aware analysis cascade closeout (#74 V2.A + #75 V2.B) + #132 Tier 1 Ticks 43→61

Batch archive of 31 completed tasks across two threads. Thread 1: qiyas#74 V2.A
(iter analyze sub-command with verdict + top_edit_candidate + cross-iteration
trajectories) and qiyas#75 V2.B (global warning optimizer — net-delta ranking
via cross-warning interaction matrix) shipped end-to-end across 6 slices each;
sacred-patterns iteration-guide D0 now consumes both layers. Thread 2: qiyas#132
Tier 1 corpus expansion Ticks 43→60 (extensive shared-edge/shared-vertex
polygon×lens combinatorics that surfaced 7 distinct bikar face-walker /
gt-emitter defects — face-walker shared-edge absorption, both-CL-outside
absorption, gt-emitter same-class drop, hetero-class drop, line-primitive
render-only + unclassified polygon drop, D3 chord-sharing merge) plus Tick 61
(bikar decision doc PROPOSED, owner-PENDING).

### #74 [qiyas] V2.A — iter analyze sub-command (Slices 1-6 SHIPPED)

`qiyas iter analyze` ingests a `<root>/<int>/validation/validation.json`
corpus and emits iter.json with verdict.kind (STABLE_AT_GO / CONVERGING /
STAGNATING_AT_{structural,placement} / OSCILLATING / REGRESSING / PENDING),
top_edit_candidate (selected by 5-rule first-match-wins from cross-iteration
trajectories), iterations-to-converge prediction, and warning_trajectories[]
(per-warning presence / cf_delta_series / rank_series / delta_class). sp
iteration-guide.md D0 + Stagnation Detection sections + tools/iteration-
validate.sh consume iter.json first; per-iteration drilldown is the
PENDING-only fallback. Calibration smoke at qiyas/calibration/iter-analyze/.

- #74 [qiyas] [V2.A] qiyas iter analyze — iteration-aware analysis sub-command
- #586 [qiyas] [#74 Slice 2] iter analyze CLI scaffold + walker + synthetic fixture
- #587 [qiyas] [#74 Slice 3] warning_trajectories + delta_class classification
- #588 [qiyas] [#74 Slice 4] verdict + top_edit_candidate + iterations-to-converge prediction
- #589 [sp]    [#74 Slice 5] sacred-patterns iteration-guide consumes iter.json
- #590 [qiyas] [#74 Slice 6] qiyas iter analyze calibration smoke test

### #75 [qiyas] V2.B — Global warning optimizer (Slices 1-6 SHIPPED)

Cross-warning interaction matrix layer: net_delta = adjusted_upside −
Σ p_fires × expected_regression. `qiyas score` writes
`recommended_actions[]` ranked by net_delta in score.json (Slice 3);
`qiyas calibrate-interaction-matrix` rebuilds matrix.json from an
iteration corpus with glob-stripping (`rosette_petal_0` →
`rosette_petal_*`) and confidence bands (high≥20, medium 5-19, low<5)
(Slice 4); `qiyas iter analyze` surfaces `top_edit_candidate.
recommended_action_rank` + `recommended_action_net_delta` +
`recommended_action_predicted_collateral` when score.json is present
(Slice 5); sacred-patterns iteration-guide D0 prefers these fields over
the bare `warnings[0]` directive (Slice 6 sp half). Backward-compat:
empty matrix path + absent-score.json fallback preserved end-to-end.
Calibration smoke at qiyas/calibration/interaction-matrix-smoke/.

- #75  [qiyas] [V2.B] Global warning optimizer — net-delta ranking via interaction matrix
- #591 [qiyas] [#75 Slice 2] InteractionMatrix data model + JSON loader
- #592 [qiyas] [#75 Slice 3] net_delta + recommended_actions emission in score.json
- #593 [qiyas] [#75 Slice 4] qiyas calibrate-interaction-matrix CLI
- #594 [qiyas] [#75 Slice 5] V2.A iter analyze consumes recommended_actions
- #595 [qiyas+sp] [#75 Slice 6] interaction-matrix calibration smoke + sacred-patterns consumer

### #132 [qiyas] Tier 1 corpus expansion — Ticks 43→61

Continues the Tier 1 calibration-corpus expansion from the prior batch (Ticks
22→42) into polygon×symmetric-lens shared-edge/shared-vertex topologies and
their asymmetric-lens counterparts. Surfaced 7 distinct bikar face-walker /
gt-emitter defects (memories: `feedback_bikar_face_walker_short_chord_octagon_absorption.md`,
`feedback_asymmetric_lens_intrudes_polygon_interior.md`,
`feedback_bikar_face_walker_both_cl_outside_lens_absorption.md`,
`feedback_bikar_gt_emitter_drops_same_class_faces.md`,
`feedback_bikar_line_primitive_render_only.md`,
`feedback_bikar_gt_emitter_drops_unclassified_polygons.md`,
`feedback_bikar_gt_emitter_unions_same_class_chord_faces.md`). 9 shipped clean,
10 falsified (kept on disk per Tenet 18). Tick 61 shipped the bikar decision
doc PROPOSED, owner-PENDING.

- #567 [qiyas] [#132 Tick 43] Tier 1 octagon-and-symmetric-lens-shared-vertex
- #568 [qiyas] [#132 Tick 44] Tier 1 hexagon-and-symmetric-lens-shared-edge
- #569 [qiyas] [#132 Tick 45] Tier 1 square-and-symmetric-lens-shared-edge
- #570 [qiyas] [#132 Tick 46] Tier 1 octagon-and-symmetric-lens-shared-edge
- #571 [qiyas] [#132 Tick 47] Tier 1 square-and-asymmetric-lens-shared-vertex
- #572 [qiyas] [#132 Tick 48] Tier 1 hexagon-and-asymmetric-lens-shared-vertex
- #573 [qiyas] [#132 Tick 49] Tier 1 octagon-and-asymmetric-lens-shared-vertex
- #574 [qiyas] [#132 Tick 50] Tier 1 square-and-asymmetric-lens-shared-edge
- #575 [qiyas] [#132 Tick 51] Tier 1 hexagon-and-asymmetric-lens-shared-edge
- #576 [qiyas] [#132 Tick 52] FALSIFIED — both-CL-outside shared-edge absorption witness
- #577 [qiyas] [#132 Tick 53] FALSIFIED — both-CL-outside absorption generalizes from D_4 to D_6
- #578 [qiyas] [#132 Tick 54] FALSIFIED — surfaces new gt-emitter same-class drop defect
- #579 [qiyas] [#132 Tick 55] FALSIFIED — gt-emitter same-class drop generalizes D_4→D_6
- #580 [qiyas] [#132 Tick 56] FALSIFIED — gt-emitter same-class drop placement-variant-independent
- #581 [qiyas] [#132 Tick 57] DISAMBIGUATED — same-class alone doesn't trigger gt-emitter drop
- #582 [qiyas] [#132 Tick 58] FALSIFIED — hetero-class lens drops BOTH faces (worse than homo)
- #583 [qiyas] [#132 Tick 59] FALSIFIED — line primitive render-only + unclassified polygon drop
- #584 [qiyas] [#132 Tick 60] FALSIFIED — D3 gt-emitter merges same-class chord-sharing sub-polygons
- #585 [qiyas] [#132 Tick 61] Decision doc shipped — bikar PROPOSED, owner-PENDING

Cascade #132 continues at task #129 (PR3); parent #129 stays open.

---

## 2026-05-26 — #132 Tier 1 corpus expansion Ticks 22→42 (21-tick batch) + #85 medallion-10 iter-19/20/30 + #106 cascade Options E/G/I + #114 closeout

Batch archive of 31 completed tasks across four threads. Three threads dominate: the qiyas#132 Tier 1 calibration-corpus expansion (Ticks 22→42, 20 entries shipped after Tick 22 falsified), the qiyas#106 partial-shape cascade re-decision sequence (Options E/G/I authored + Option I shipped), and the sacred-patterns#85 medallion-10 cascade iter-19/20/30 deliverables. Plus drain-queue closeout of #114 (logged separately above) and an investigation of #132/#80/#85 corpus render drift (#545).

### #132 [qiyas] Tier 1 corpus expansion — Ticks 22→42 (20 shipped, 1 falsified)

Tier 1 entries extend the I1 calibration corpus into composition territory: triangle+polygon shared-vertex/edge, scalene+asymmetric-polygon (pent/hex/hept/oct), arc-bearing lens topologies (dual-lens, chained-lens, arc-cap), and the heterogeneous symmetric/symmetric family (D_4/D_6/D_8 polygon pairs + arc-bearing D_6+lens, D_4+lens). Each ticked entry shipped with macro_ari_fused_vs_b=1.0, total_merged_with_neighbor=0, ci-local-fast 6/6 green. Tick 22 (quintuple-junction-shared-vertex) FALSIFIED on the face-walker polyclass trap (memory `feedback_classify_by_predicate_cannot_witness_same_class_cross_refs.md`); kept on disk as Tenet 18 witness.

- #546 [qiyas] [#132 Tick 22] Quintuple-junction-shared-vertex FALSIFIED + lesson captured
- #547 [qiyas] [#132 Tick 23] Two-lens-shared-vertex — pure arc-bearing dual-lens topology
- #548 [qiyas] [#132 Tick 24] chained-lens-shared-circle — three lenses sharing CIRCLES in a chain
- #549 [qiyas] [#132 Tick 25] arc-cap-and-scalene-triangle-disjoint — chord+arc 2-sided semicircle witness
- #550 [qiyas] [#132 Tick 26] scalene-and-asymmetric-pent-shared-vertex — 3+5 dual-asymmetric cell
- #551 [qiyas] [#132 Tick 27] scalene-and-asymmetric-pent-shared-edge — 3+5 dual-asymmetric edge cell
- #552 [qiyas] [#132 Tick 28] scalene-and-asymmetric-hex-shared-vertex — 3+6 dual-asymmetric cell
- #553 [qiyas] [#132 Tick 29] scalene-and-asymmetric-hex-shared-edge — 3+6 dual-asymmetric edge cell
- #554 [qiyas] [#132 Tick 30] scalene-and-asymmetric-hept-shared-vertex — 3+7 dual-asymmetric cell
- #555 [qiyas] [#132 Tick 31] scalene-and-asymmetric-hept-shared-edge — 3+7 dual-asymmetric edge cell
- #556 [qiyas] [#132 Tick 32] scalene-and-asymmetric-oct-shared-vertex — 3+8 dual-asymmetric cell
- #557 [qiyas] [#132 Tick 33] scalene-and-asymmetric-oct-shared-edge — 3+8 dual-asymmetric edge cell
- #558 [qiyas] [#132 Tick 34] octagon-and-triangle-shared-vertex — sym-polygon + scalene asymmetric anchor
- #559 [qiyas] [#132 Tick 35] octagon-and-triangle-shared-edge — sym-polygon + scalene edge variant
- #560 [qiyas] [#132 Tick 36] heptagon-and-triangle-shared-vertex — D_7 + scalene vertex
- #561 [qiyas] [#132 Tick 37] heptagon-and-triangle-shared-edge — D_7 + scalene edge
- #562 [qiyas] [#132 Tick 38] square-and-hexagon-shared-vertex — first heterogeneous symmetric/symmetric (D_4+D_6)
- #563 [qiyas] [#132 Tick 39] square-and-octagon-shared-vertex — D_4+D_8 polygon/polygon
- #564 [qiyas] [#132 Tick 40] hexagon-and-octagon-shared-vertex — D_6+D_8, first without square anchor
- #565 [qiyas] [#132 Tick 41] hexagon-and-symmetric-lens-shared-vertex — first arc-bearing symmetric/symmetric
- #566 [qiyas] [#132 Tick 42] square-and-symmetric-lens-shared-vertex — D_4 + symmetric lens

Corpus: 52 → 56 entries; total_visible_shapes 731 → 790 by Tick 42. Tick 43 (octagon+symmetric-lens, completes D_4/D_6/D_8 arc-bearing trio) tracked as #567 (open). Memories: `feedback_bikar_face_walker_polygon_edge_absorbed_by_coincident_arcs.md`, `feedback_per_edge_class_tags_same_trap_as_classify.md`, `feedback_bikar_face_walker_shared_edge_absorption_universal.md`. Cascade #132 continues at task #129 (PR3); parent #129 stays open.

### #106 [3-repo] Partial-shape cascade — falsification + re-decision + Option I shipment

After #106 Option A shipped (Tier 0 single-petal+extend+clip green), medallion-10 iter-20's clip(C0) regression falsified the cascade. Re-decision sequence per `handle-falsification` skill: #539 reopened, #540 authored Option E (intersect-before-clip semantic OR composability test gate), #541 added Option G (Tier 0 composition gate — present-options skill checkbox + single-petal+extend+clip fixture), #543 shipped Option I (qiyas detector handling of `partial:true` faces + bikar post-clip sliver cleanup, autonomous-loop-2026-05-25). Memory: `feedback_cascade_primitive_semantic_composition.md` + `feedback_check_emit_layer_before_option.md`.

- #106 [3-repo] Partial-shape rendering via construction (qiyas + bikar + sacred-patterns)
- #539 [sp] [#106 falsification] Reopen partial-shape cascade decision after iter-20 clip(C0) regression
- #540 [sp] [#106 re-decision] Author Option E for cascade — intersect-before-clip semantic OR composability test gate
- #541 [sp] [#106 re-decision Option G] Tier 0 composition gate — present-options skill checkbox + fixture
- #543 [qiyas+bikar] [#106 re-decision Option I] Investigate qiyas detector partial:true handling + bikar sliver cleanup

Decision doc: `sacred-patterns/docs/decisions/2026-05-07-partial-shape-rendering-via-construction.md` (REOPENED → Option I ACCEPTED). Cascade closes the #106 thread; iter-24+ pickups land in the #85 medallion-10 cascade above.

### #85 [sp] medallion-10 iter-18/19/20/30 + earlier iters (drain)

Pre-iter-23 cascade work: iter-18 ran Tax-B-aware ranking (#123/#127/#128), iter-19 picked up partial-shape cascade probes (#537), iter-20 layered clip pattern to medallion outline (#538) which triggered the #106 falsification above, iter-30 ran rhombus-v4 distance-filter rescaling (#544). Cascade #85 stays open per "medallion-10 stays open / keep striving."

- #123 [sp] [#85] Run bikar-medallion-10 iter-18 with Tax-B-aware ranking
- #127 [sp] [#123] Render iter-18 and validate
- #128 [sp] [#123] Capture iter-18 G3 deliverables
- #537 [sp] [#85] Run bikar-medallion-10 iter-19 — partial-shape cascade pickup
- #538 [sp] [#85] Run bikar-medallion-10 iter-20 — layer in clip pattern to medallion outline
- #544 [sp] [#85] Run bikar-medallion-10 iter-30 — rhombus-v4 distance-filter rescaling

Evaluations: `~/Dropbox/Data/sacred-patterns/bikar-medallion-10/iterations/{18,19,20,30}/evaluation.md`.

### Drain — #114 + #545

- #114 [bikar] Strapwork rotation-canonicalization — see prior 2026-05-25 section above for closeout details (commit `8bc6735`)
- #545 [3-repo] [#132 / #80 / #85] Investigate corpus render drift discovered during Tick 19 — drift root-caused; cascade #132 continues

---

iter-24 composed #106 Option I (extend+clip silhouette) with #114 PR1 (strapwork): A2 cv 0.0406 (cascade best at the time), A4 FULL, A5 COMPLETE, A6 0/18 vs `input/baseline.json` (18-shape rich-inner-zone expectation). iter-25/26/27/28 probed four mechanism-distinct constructions for the inner-star v20 verdict (chord polygon shared layer / chord polygon isolated layer / direct `face` arc declaration / chord polygon at correct baseline scale r=6 spatially isolated) — all four falsified, each at a different pipeline stage. Pattern: this construction philosophy (chord-overlay + strapwork) fundamentally cannot produce a vertex-distinct v20 shape inside the medallion. iter-25 stands as cascade local-optimum at A2 cv 0.0365 (45% better than iter-14's 0.067), A4 FULL, A5 COMPLETE, A6 0/18 reflecting philosophy mismatch with baseline. Memory: `feedback_a6_baseline_construction_philosophy_mismatch.md`. Per user direction "medallion-10 stays open / keep striving," cascade #85 stays open but stops iterating v20 / star-v6 / star-v8 verdicts; next iters target polygon-v0 / rhombus-v4 verdicts the philosophy CAN plausibly produce.

Evaluations: `~/Dropbox/Data/sacred-patterns/bikar-medallion-10/iterations/{24,25,26,27,28,29}/evaluation.md`. No tasks closed (cascade continues at #85).

iter-29 probed inner-star polygon-v0 (5→7 PARTIAL, +2 of 5 added circles registered) — confirmed diminishing-returns slope; cascade pauses pending a higher-net-cf_delta pivot.

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
