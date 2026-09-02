---
title: "Retrospective — recovering the bikar DSL from an image (the inverse problem)"
date: 2026-06-06
repos: [bikar, qiyas, sacred-patterns]
window: 2026-04-28..2026-06-01
sources:
  transcripts:
    - qiyas/cb7c407a (64 MB, 2026-04-28..2026-05-12)
    - sacred-patterns/ad36e137 (900 MB, 2026-04-30..2026-06-01)
  decision_docs: 61   # qiyas 40, bikar 18, sacred-patterns 3
  memory_files: 95    # sacred-patterns 87, qiyas 4, bikar 4
  commits_scanned: 239  # theme-or-revert filtered, since 2026-04-01
  subagent_bodies_analyzed: false   # 36 subagent sessions indexed by header only
generated_by: retrospect-hard-problem skill (Stage 1-5)
---

> **Tier legend.** `[A]` durable-confirmed (a decision-doc status/rationale,
> memory file, or commit corroborates it). `[B]` transcript-corroborated (≥2
> independent windows, or a window + compaction summary; no durable doc).
> `[C]` transcript-only — quarantined to Appendix A, never a recommendation.
> Findings are weighted by **date-spread, not hit-count** (the 900 MB session
> dominates by volume; a mistake seen early *and* late outranks ten late hits).

# 0. Executive summary

We are solving the inverse problem — *image → bikar DSL construction* — not by
end-to-end inference but by a **producer-checked loop**: bikar renders a `.bkr`
to SVG carrying authoring-time `data-*` metadata, qiyas fingerprints it through
a 6-stage detector + Hungarian matcher + ARI/composite score, and
sacred-patterns iterates the construction until the score plateaus. This works
extremely well *when bikar is the producer of record* (the "I1" SVG-direct
regime hit ARI=1.0 on a 12-pattern corpus); it has **never been run on a real
photograph** (the "I2" cascade is still deferred). `[A]`

The single biggest recurring mistake is **committing to an option before
empirically validating its premise** — authoring a decision doc, picking an
option, sometimes regenerating a 258-file corpus, and *then* discovering the
premise was false (the F2 `shape_id` oracle, the rotate-block "can't express
neighbor indexing" doc self-falsified within an hour, the iter-5/6/7 SHIP
verdicts run against an uncommitted tree). It recurs across the entire window
and across all three repos. `[A]`

**Top recommendation:** make "validate the premise against the codebase/corpus
*before* authoring options or regenerating artifacts" a first-class, enforced
step — it is partially codified in three sacred-patterns memory files but is
**absent from every repo's CLAUDE.md tenets and from `present-options`/
`handle-falsification`**, which is why it keeps recurring. See recommendations.

# 1. The fundamental approach (what we are actually doing)

**Pipeline as built** `[A: qiyas/.claude/plans/post-i1-task-routing.md;
sacred-patterns/docs/decisions/2026-05-20-universal-dsl-tagging.md]`:

```
bikar .bkr  ──render──▶  SVG + data-* metadata  ──▶  qiyas 6-stage detector
   (producer)            (data-sides, data-face-class,        │
        ▲                 data-symmetry-fold = authoritative)  ▼
        │                                          Hungarian matcher
   iterate construction  ◀── composite/ARI score ── 3-pillar scorer
   (sacred-patterns)         (structural · geometric · symmetry)
```

Two regimes:
- **I1 — SVG-direct (shipped, load-bearing).** bikar is the producer of record;
  qiyas reads the SVG DOM + `data-*` directly (no rasterize→trace round-trip).
  Recovers ~5× more shapes than the raster path and reached **ARI=1.0** on the
  12-pattern corpus. `[A: 2026-05-17-eliminate-rasterize-trace-round-trip.md]`
- **I2 — photo cascade (deferred, never run).** When the input is a photograph
  with no producer, qiyas must rasterize→trace→re-derive every fact. Tasks
  #303/#304 are filed but **deferred and unfired** through the whole window.
  `[A: open_questions, multiple windows]`

**Why this shape.** The governing choice is **DSL-as-source-of-truth**: the
producer already *knows* sides/face-class/fold at authoring time, so qiyas
should *read* those facts, not re-derive them from jittered raster geometry.
This was made a cross-repo tenet after re-derivation caused a cluster of
detector bugs. `[A: 2026-05-20-universal-dsl-tagging.md, mirrored in all three
docs/dsl-metadata-contract.md]`

**Where it structurally caps out:**
1. **It is not actually image→DSL yet.** The whole loop assumes bikar is the
   producer. The genuine inverse problem (arbitrary photo → DSL) is the I2
   cascade, which has never been exercised. We have built a superb *round-trip
   validator*, not yet an *inference engine*. `[A]`
2. **Hand-authored constructions hit ceilings the DSL can't express.** The
   medallion-10 girih field cannot be expressed cleanly in the current DSL;
   three hand-authored approximations all hit an A6=0 floor for *different*
   geometric reasons. The fix is a producer-side substitution-rule primitive,
   not a detector accommodation. `[A: bikar/docs/decisions/2026-05-28-medallion10-girih-ceiling.md;
   memory/feedback_a6_baseline_construction_philosophy_mismatch.md]`
3. **Scoring labels are not identity.** Choosing what counts as "the same shape"
   across constructions (the F2 oracle) is unsolved-by-default and was got wrong
   once (see §3). `[A: 2026-05-29-f2-face-class-is-wrong-retrieval-label.md]`

# 2. Tried and worked (keep doing)

| Approach | Evidence | Why it worked | Load-bearing now? |
|----------|----------|---------------|-------------------|
| **SVG fast-path / DSL-as-source-of-truth** — read `data-*` instead of re-deriving | `[A]` commit ea793b4; 2026-05-20-universal-dsl-tagging.md | Producer knowledge is exact; raster re-derivation jitters. Dissolved qiyas#400/#488/#490 at once | **Yes** — the spine of I1 |
| **Turning-function + provenance fusion** for shape identity | `[A]` 2026-05-11-i1-entry-5-mirror-only-geometry.md | TF alone saturated ~0.50 on bilateral arms; provenance alone over-fragmented; fusion closed to ARI=1.0 | Yes |
| **`qiyas trace` diagnostic CLI** — made a reconcile-drop visible | `[B]` qiyas window, 2026-04-28T04:00 ("massive insight") | Field-reads hid the Sq-Oct face-recovery defect; the trace surfaced it | Yes — render-and-look, automated |
| **Review portal + Playwright browser smoke** — automated render-and-look | `[A]` commits in #38/#64/#70; CLAUDE.md tenet 19/25/27 | The user repeatedly caught visual bugs metrics missed; the portal/smoke codified the gate | Yes — ship gate in all 3 repos |
| **Empirical root-cause over backlog hypotheses** (raster fold #26) | `[B]` qiyas 2026-04-28T18:49 | Per-fold MSE matrix disproved 3 backlog hypotheses; the threshold was wrong, not the engine | Yes — pattern repeated for F2 |
| **F2 cross-construction retrieval on `geom_label`** (after falsifying shape_id) | `[A]` 2026-05-29 doc, Option E ACCEPTED 2026-06-01, EER=0.035 | The detector's geometric type is canonical; the author's name is not | Yes — shipped CI-green |

# 3. Tried and failed / dead ends (stop doing)

| Approach | Failure mode | Evidence | Superseded by |
|----------|--------------|----------|---------------|
| **F2 oracle = author `shape_id`** | Author reuses generic names across geometrically different shapes; mAP=0.296 (worst of 3) | `[A]` 2026-05-29-f2-face-class-is-wrong-retrieval-label.md (REOPENED→Option E) | `geom_label` (the detector geometric type) |
| **Medallion-10 girih via hand-authored primitives** (single tile, 50-tile manual ring, computeSubdivision approx) | All hit A6=0, each gap-ridden for a *different* reason | `[A]` bikar 2026-05-28-medallion10-girih-ceiling.md; feedback_a6_baseline_construction_philosophy_mismatch.md | (Open) producer-side substitution-rule primitive |
| **medallion-10 clip-primitive variants** (iter-20/21) | clip(C0) composite 0.697 = regression vs prior | `[A]` cascade #106 reopened, Options E/F/G/H drafted | (Open) owner pick pending |
| **Image-derotation by shape-count cost** | Shape-count too coarse — Star-8 0.999→0.610; many angles share a count | `[B]` qiyas 2026-04-28T14:13 | Hungarian composite cost / rotation_aware_match |
| **Raster fold=1 as "honest observation" (xfail)** | The fold *was* cleanly recoverable; xfail would have hidden a fixable threshold | `[B]` qiyas, superseded same day by #26 | MSE-threshold fix (0.30→0.55) |
| **Tolerance-sweep that set the tol on the re-exported fn object** | No-op — measured default behavior; a self-inflicted false-green | `[A]` qiyas#18; memory note on module shadowing | Access `sys.modules[...]` directly |
| **Petal-N-2ring multi-class via existing rotate-block** | Blocked at N=6; then the "needs DSL extension" doc self-falsified | `[A]` 2026-05-05 rotate-block doc SUPERSEDED ("premise falsified") | The capability already existed (invocation gap) |

# 4. Repeated mistakes  ← MOST VALUABLE

Clustered from 37 transcript-witnessed mistakes across 6 windows, anchored to the
durable record. Spread, not count, is the signal.

| # | Mistake | Date-spread | Tenet | Durable evidence chain | Codified? | Why it recurred |
|---|---------|-------------|-------|------------------------|-----------|-----------------|
| M1 | **Commit to an option before validating its premise** (F2 shape_id; rotate-block "can't express" doc; A5 "RESOLVED—ribbons" contradicted by code; SHIP run on uncommitted tree) | 04-30 → 05-29 (whole window) | "verify before claiming done" / committing-at-options-level | 2026-05-29 F2 doc REOPENED; 2026-05-05 rotate-block SUPERSEDED ("premise falsified"); feedback_gate_needs_oracle_in_record.md; feedback_synthetic_test_cant_validate_unenforced_producer_discipline | **partial ✓** (3 SP memory files; **✗ in every CLAUDE.md + present-options/handle-falsification**) | The premise-check is folklore, not an enforced step in the option-authoring path |
| M2 | **Inherited/stale claim propagated without re-verifying** (iter-6 "arc_bearing=0" false; doc frontmatter ACCEPTED contradicting its own PENDING body; stale compact-prompt re-planned shipped #26) | 04-28 → 05-30 | "trust but verify inherited claims" (SP Tenet 6) | feedback_adjudicate_missing_items_via_git_before_loadbearing.md; 2026-05-07 SP doc REOPENED | **partial ✓** (1 SP memory file; ✗ in qiyas/bikar) | Claims read as snapshots-of-truth; no habit of re-emitting/git-checking before load-bearing use |
| M3 | **Deferral-as-optimization / capability-limiting** (SVG arc support deferred; LOC-cheaper warning shortcut; low-confidence fallback instead of fixing) | 04-28 → 05-25 | "don't limit capability to optimize" / "fix root cause not fallback" / "fix simplest broken thing first" | qiyas project-memory `feedback_dont_limit_capability.md` | **✓ (qiyas)** but still recurred in SP | The codified lesson lives in *qiyas* project-memory only; SP/bikar agents don't load it; not a shared tenet |
| M4 | **Over-caution / idle churn in the autonomous loop** (stalled with status summaries; one-shot authorization "blocker"; 15-tick idle holding 58 commits; 11+ ticks re-asserting "converged-idle"; too many clarifying questions) | 04-28 → 05-25 | "bias for action" | qiyas CLAUDE.md tenet 19; SP routing-doc Held=0 rule | **✓ (tenet exists)** yet recurred repeatedly | Tenet exists but the loop had no operational test for "am I idling vs genuinely blocked"; GHA-budget freeze got mis-read as a hard blocker |
| M5 | **Shipped a verdict/visual without the render-and-look** (overlay in wrong quadrant; ellipse-stretch; blue-on-black; blank render in a review report; cairosvg dropped 27% of content) | 04-28 → 05-05 | "render-and-look" / "no ship without review-portal pass" | CLAUDE.md tenets 18/19, 24/25, 26/27 (all 3 repos) | **✓ (strong tenets)** — and the user *still* caught several | Tenet was right; the *automated* enforcement (browser smoke) was built only after the user caught the bugs by hand |
| M6 | **Tuned/forced the metric instead of fixing the cause** (raise shape counts to force agreement; tests over-indexed on one fixture) | 04-28 → 04-30 | "don't tune constants to pass one fixture" / "prove the primitive / solve the general problem" | CLAUDE.md tenet 7 (SP); 2026-05-07 petal-6 doc SUPERSEDED ("gap is a stale fixture, not metric") | **✓ (tenet)** — owner had to intervene twice in one window | Reflex under plateau pressure; the tenet is stated but the plateau is exactly when it's ignored |
| M7 | **Wrote/edited a file (or CLAUDE.md mirror) without reading it first** (6× "File has not been read yet"; duplicate §1 headers; duplicate decision docs #400 vs existing) | 04-30 → 05-30 | operational hygiene / "read the existing shape before adding" | transcript tool_errors (6 in one window) | **✗** | Pure mechanical haste; no pre-write read habit; not enforced anywhere |
| M8 | **CI/GHA over-polling burning billable minutes** | 05-17 → 05-25 | "every push burns billable GHA minutes" | CLAUDE.md GHA-budget tenet; 2026-05-26 spend-limit freeze (memory) | **✓ (tenet)** — recurred anyway | The tenet governs *pushes*; the waste was *Monitor-driven status polling*, which the tenet doesn't name |

**The pattern behind the pattern:** M1, M2, M6 are one family — *acting on an
unverified belief* (a premise, an inherited claim, a metric reading). M3, M4 are
another — *under-doing* (defer, idle) when the contract is bias-for-action. The
strongest tenets (M5, M6, M8) still saw recurrences, which says **a tenet alone
does not prevent the mistake at the moment of temptation** (plateau, resume,
budget-scare); an *operational check at that moment* does.

# 5. Not yet tried (open alternatives)

| Alternative | Feasibility | Governing tenet/skill | Source |
|-------------|-------------|-----------------------|--------|
| **I2 photo cascade** — the actual image→DSL inference (rasterize→trace→re-derive, HSV color-seg, no `data-*`) | Medium-high; scoped (#303/#304) but never started | iterate-detector-calibration; DSL-as-truth fallback path | `[A]` deferred all-window |
| **Producer-side girih substitution-rule primitive** (Lu-Steinhardt table) to render the field gap-free | Medium; bikar plan exists (girih-substitution-rule-engine.md) | "extend the DSL when construction fights the language" | `[A]` bikar 2026-05-28 ceiling doc |
| **Auto-generated training pipeline** — bikar generates many patterns w/ known GT, verify detection at scale (+ B-AFF affine matching) | Medium; raised, never built | — (no skill yet) | `[B]` open_questions ×2 |
| **A self-aware "qiyas-diff → deterministic .bkr tweak" skill** with a per-iteration *construction-vs-qiyas-bug-vs-DSL-gap* checklist | Medium; the routing exists in iterate-construction-hypothesis but the diff→edit mapping is manual | iterate-construction-hypothesis (extend) | `[B]` open_questions, repeated |
| **Recursive quadrant image-diff** for regional convergence signal | Low priority; abandoned once | — | `[A]` abandoned |
| **True closed-loop convergence** — loop until qiyas says reconstructed ≈ original, no human | The stated goal; gated on owner picks (#129, #106, #669-class) | learn-new-pattern orchestrator | `[B]` the recurring "what does the loop loop-until?" question |

# 6. Recommendations (→ 2026-06-06-image-to-dsl-recommendations.md)

Ordered by value. Full wording in the companion recommendations doc.

1. **Codify the premise-check (M1) as a cross-repo tenet AND a `present-options`
   guard.** "Before authoring options or regenerating any artifact, validate the
   framing premise against the codebase/corpus — not the task text." `[A]`
2. **Promote the three SP-only process lessons (M1/M2/M3) to shared tenets or at
   least mirror the memory files into qiyas/bikar `memory/`.** The lessons exist
   but only sacred-patterns agents load them. `[A]`
3. **Give the autonomous loop an operational idle-vs-blocked test (M4)** and a
   named carve-out that a GHA-budget freeze is *not* a work blocker. `[A]`
4. **Extend the GHA-budget tenet to cover status *polling*, not just pushes (M8).**
   `[A]`
5. **Add a pre-write "read first" mechanical guard (M7)** — cheap, currently
   enforced by nothing. `[B]`
6. **Pick up I2 (#303) and the girih substitution primitive** as the two moves
   that turn the round-trip validator into an actual inference engine and lift
   the medallion-10 ceiling. `[A]`
7. **Author the qiyas-diff→.bkr-tweak skill** with the construction-vs-bug-vs-gap
   checklist the loop keeps asking for. `[B]`

---

## Appendix A — Confidence ledger (Tier-C quarantine)

Transcript-only, single-source; recorded but NOT promoted to facts or
recommendations:

- `[C]` Specific composite-score values for one-off probe iterations (e.g.
  individual clip-probe deltas) appear in single windows without a decision-doc
  echo — directional only, exact numbers unverified.
- `[C]` Claims about *why* a particular reviewer-UX choice was made
  (engine-driven vs reviewer-driven "things to review") — raised once, no doc.
- `[C]` The "11 stale dependabot PRs are pre-cascade noise" classification —
  agent's own judgment, no owner confirmation.

## Appendix B — Source manifest & noise budget

- **Transcripts parsed:** qiyas `cb7c407a` (64 MB, 16,760 signal lines of
  ~17k), sacred-patterns `ad36e137` (900 MB, **streamed in 3.8 s at 60 MB RSS**,
  144,901 signal lines). bikar's own project dir is memory-only; its construction
  history surfaces via cross-repo refs in the other two transcripts + its 18
  decision docs.
- **Discarded by type** (no analytic signal): permission-mode, file-history-
  snapshot, attachment, queue-operation, last-prompt, ai/custom-title, system,
  mode — ~40% of lines, dropped before downstream processing.
- **Extracted signal:** 1,272 human corrections (1,140 SP + 132 qiyas), 662
  unique compaction summaries, 1,272 segments, ~3,971 theme hits.
- **Map windows:** 6 (1 qiyas + 5 sacred-patterns), ~65k tokens each, by
  date-range. 64 approaches / 37 mistakes / 31 pivots / 34 open-questions
  returned.
- **Ground truth:** 61 decision docs (40/18/3), 95 memory files (87/4/4), 239
  theme-or-revert commits, 2 living routing docs.
- **Subagent bodies:** NOT analyzed (36 subagent sessions indexed by header
  only; `--include-subagents` would promote them in a deeper run).
- **Known gaps:** bikar's primary work has no large standalone transcript here,
  so bikar-internal mistakes are under-represented relative to qiyas/SP; the
  retrospective leans on bikar's decision docs + cross-repo mentions for it.
