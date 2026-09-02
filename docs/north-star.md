# North-star — convergence goal and the cascades getting us there

This doc answers a single question for a cold reader: **what is the destination, what cascades are in flight to reach it, and where is each cascade right now?**

It is the highest-level status document in the sacred-patterns repo. If you (or a future agent) sit down without context, read this first. For session-level operational state, read `iteration-status.md` next. For per-decision rationale, follow links into `docs/decisions/`. For per-cascade detail, follow links into `.claude/plans/`.

**Update discipline:** edit this doc *whenever a cascade closes a slice or surfaces a new blocker*. Each cascade row is a snapshot in time — the "last shipped" and "next slice" columns rot fast. Refresh them in the same PR that ships the slice.

---

## The destination

**Goal:** drive `bikar-medallion-10` (a 10-fold decagonal Islamic medallion pattern) from its current paused state at iter-13 (structural 1/18, composite ~0.74) to **G1–G5 PASS** via the qiyas-orchestrator iteration loop.

**What G1–G5 PASS means** (from `CLAUDE.md` "HARD GATES"):
- **G1** Iteration immutability — every frozen iter stays frozen; new work goes in a new iter folder.
- **G2** Architecture before pixels — structural score = 100% before any pixel-only iteration is allowed.
- **G3** Mandatory deliverables per iter — `evaluation.md`, `retrospective.md`, `guidance.md` every iter.
- **G4** Reference-grounded verification — every structural audit grounded in the reference image, not self-defined labels.
- **G5** Skill-prefixed task naming — operational hygiene.

**The convergence philosophy** is "shape before pixels" (`CLAUDE.md` "Convergence Philosophy"). Pattern-similarity-by-pixels is a regression detector, not a convergence target. The real signal is the qiyas A1–A6 architectural audit, especially **A6 baseline-shape validation** (PASS/PARTIAL/MISSING per shape against a user-verified `baseline.json`).

**Why medallion-10 is the load-bearing case:** it's the first pattern the project has driven through the full modern stack (interpret-pattern → bikar DSL → qiyas-orchestrator iteration loop). Until medallion-10 reaches G1–G5 PASS, the cross-repo system is unproven on real geometry. Once it does, the same loop generalizes to other patterns by changing only the reference image and `baseline.json`.

**The single user-facing task this rolls up to:** `#85 [TOP-PRIORITY] Drive bikar-medallion-10 to convergence`.

---

## Why we are not there yet — the three structural blockers

Medallion-10 paused at iter-13 with composite ~0.74. The remaining ~26% gap is **not** spread evenly across the pattern; it concentrates on three named blockers, each of which spawned a multi-repo cascade:

1. **The detector cannot prove its own correctness on construction-grounded inputs.** Without that proof, every divergence between qiyas and the reference is ambiguous — is the detector wrong, or is the reconstruction wrong? → Cascade A (shape-identity detection).
2. **The DSL cannot express extended-then-clipped construction shapes.** Medallion-10's outer ring is geometrically constructed by extending circle-derived points past the outer boundary and clipping at the medallion edge. With no `extend`/`clip` primitives, those shapes render incomplete and the detector reports them MISSING. → Cascade B (partial-shape rendering).
3. **The iteration agent does not yet have a calibrated counterfactual-cost model.** `warnings[0].counterfactual_score_delta` predicts upside without accounting for the cost of the edit; on saturated meshes the cost dominates and falsified predictions stack up (memory: "cf_delta is upside-only"). → Cascade C (fragmentation/interaction tax).

These three cascades are largely independent. Cascade B has the clearest line to closing medallion-10's specific ceiling; Cascades A and C unblock generalization beyond medallion-10.

---

## The three active cascades

### Cascade A — shape-identity detection (`#142`)

**Question it answers:** can qiyas reliably classify rendered shapes into identity classes (F1) and detect their spatial arrangement (F3) against construction-grounded ground truth from bikar?

**Why it matters for the goal:** without this, every A6 MISSING verdict is "detector limit" vs "real gap" ambiguous. With it, divergences become actionable.

**Specs landed:** F1 within-construction signature (#143), F2 cross-construction signature (#144), F3 arrangement classifier (#145). Implementations landed for D1/D2/D3/D4 (#148–#151). Plan: `.claude/plans/shape-identity-detection-cascade.md`.

**Current state:** I1 detector-calibration loop (#152) is the in-flight phase. Iterations are tracked at `qiyas/calibration/i1/`. Most recent ships: γ-narrow closeout (#252), α resolver gate (#279), bikar B3 root-cause refactor (#169), and the F1.v3 bidirectional-fusion spec (#175–#177).

**Last shipped:** bikar PR2 slice c (commit `8fa72dd` on 2026-05-11) — gt-emitter schema 1.17 with per-shape `extension_factor`. Required by qiyas's CLIPPED-MISSING/EXTENDED-EDGE detectors to know which boundaries went through virtual-radius scaling.

**Next slice:** continue I1 iteration on the calibration corpus per `qiyas/.claude/skills/iterate-detector-calibration/SKILL.md`. The named open gaps are tracked in the tally at `qiyas/calibration/i1/tally.json`. Phase 1.B corpus expansion is complete; remaining work is closing the named identity-fidelity gaps on petal-N-2ring and Phase 1.A constructions.

**What closing this unlocks:** Cascade B verification (#260) becomes meaningful because we can trust that the post-extend/clip render's A6 verdicts reflect real geometry, not detector noise.

---

### Cascade B — partial-shape rendering (`#106`)

**Question it answers:** can bikar express the construction primitives (extend, clip, optionally intersect) that medallion-10's outer-ring shapes require, and can qiyas's CLIPPED-MISSING detector translate the resulting `extension_factor` tags into actionable warnings?

**Why it matters for the goal:** direct ceiling-breaker for medallion-10. The ~26% remaining gap at iter-13 is dominated by shapes the DSL cannot construct today.

**Decision doc:** `docs/decisions/2026-05-10-extend-virtual-radius-mechanism.md` (ACCEPTED). Plan: `.claude/plans/partial-shapes-via-construction.md`. qiyas-side spec done (#255), implementation done with 7 slices (#256, #261–#267).

**bikar #258 PR breakdown:**
| PR | Slices | Status |
|---|---|---|
| PR1 boundary | #269 #270 #271 #272 | ✅ done |
| PR2 extend | #273 #274 #275 #276 #277 #278 | ✅ done (just landed: 8fa72dd) |
| PR3 clip | unfiled | ⏳ **next slice** |
| PR4 intersect | unfiled | deferred (likely not required for medallion-10) |

**Last shipped:** bikar #258 PR2 — the `extend ... beyond N` modifier with `extension_factor` riding through the gt-emitter to schema 1.17. Cross-repo: gt-emitter `extension_factor` → qiyas `source_primitives` → CLIPPED-MISSING/EXTENDED-EDGE warnings.

**Next slice (highest leverage for the goal):** **bikar #258 PR3 — `clip` primitive.** Spec already exists in `.claude/plans/construction-extension-primitives.md`. This is the second half of the partial-shape mechanism: without it, extend-then-clip cannot be expressed in a `.bkr` file, and medallion-10's outer-ring construction stays blocked.

**What closing this unlocks:** sacred-patterns #259 (CLIPPED-MISSING translation row in iteration-guide) becomes meaningful, then #260 (re-validate iter-14 against the full cascade) becomes the empirical test of whether the partial-shape mechanism actually lifts the score. If #260 confirms lift, #85 resumes with the new primitives unblocked.

---

### Cascade C — fragmentation/interaction tax (`#109`)

**Question it answers:** when the iteration agent picks the next edit from `warnings[0].counterfactual_score_delta`, can it weigh the *cost* of fragmentation/interaction (lost score from breaking neighboring shapes' archetypes) against the *upside* the warning predicts?

**Why it matters for the goal:** without it, iter-15/16/17-style falsified predictions repeat on every saturated mesh. The agent picks an edit that should add 0.05 to the composite but actually subtracts 0.03 because the edit fragments three previously-PASSing neighbors. Memory: "cf_delta is upside-only — model the cost."

**Decision context:** documented in qiyas decision docs (Tax A foundation per #117; Tax B fragmentation per #118 in-progress). Tax A is shipped; Tax B is in PR2 of the qiyas counterfactual-tax plan.

**Last shipped:** Tax A foundation (#117, #119, #120 wiring), `counterfactual_adjusted_score_delta` surfaced through validation.json (#121, #122).

**Next slice:** finish Tax B fragmentation cost (#118) — the fix-archetype classifier. The Docker image already rebuilds with Tax B; the missing piece is the classifier behavior under the full corpus.

**Outstanding risk:** `#124` (don't clamp negative adjusted_delta to 0 in score rollup) — when Tax B's cost exceeds the warning's upside, the agent currently sees 0 instead of a negative number, which silently makes "do nothing" look like "no improvement available" when it should look like "this edit is actively harmful."

**What closing this unlocks:** the iteration agent can rank warnings by net-delta instead of upside-only, ending the falsified-prediction cycle on saturated meshes like medallion-10 iter-15+.

---

## Cross-cascade interaction map

```
Cascade A (detector capability)
  │
  ├─→ Cascade B verify step (#260)    ← A's identity-fidelity must be high enough
  │                                     that B's score-lift measurement is trustworthy
  │
  └─→ Cascade C tax calibration       ← cost models depend on identity classes being
                                        stable across iterations

Cascade B (partial-shape rendering)
  │
  └─→ #85 medallion-10 convergence    ← direct ceiling-breaker; A6 MISSING shapes
                                        in the outer ring become constructable

Cascade C (fragmentation tax)
  │
  └─→ #85 medallion-10 convergence    ← stops the agent from picking actively-harmful
                                        edits on saturated meshes
```

**Read this map as:** A and B together are necessary to *finish* medallion-10. C is necessary to *not stall again on the next pattern after medallion-10*.

---

## Path from here to G1–G5 PASS on medallion-10

In priority order (highest leverage first), assuming we want medallion-10 to reach convergence:

1. **Ship bikar #258 PR3 (clip).** Smallest unblocked slice with the largest ceiling-lifting potential. Spec exists; pattern follows PR1/PR2.
2. **Wire sacred-patterns #259** — add CLIPPED-MISSING/EXTENDED-EDGE translation rows to the iteration-guide so the iteration agent can act on those warnings without manual interpretation.
3. **Run #260 verify** — re-render iter-14 with the new `extend`/`clip` primitives in `pattern.bkr`, run the full cascade, confirm A6 CLIPPED-MISSING drops to PASS and composite lifts. This is the empirical test of Cascade B.
4. **Resume #85 iteration** on the modern qiyas-orchestrator path. Each iter: read `warnings[0]` from `validation.json`, apply the recommended edit, re-render, re-validate. Continue until G1–G5 PASS.
5. **In parallel, finish Cascade C Tax B (#118).** This protects iter-15+ from the falsified-prediction failure mode. Can run alongside steps 1–4 without conflict because Tax B is opt-in via Docker image tag.
6. **Cascade A I1 (#152) runs in the background.** Identity-fidelity improvements compound across all future patterns, not just medallion-10. Treat it as continuous improvement, not a gate on #85.

**Stop conditions for this plan:**
- If #260 verify *fails* to show score lift after Cascade B ships, halt #85 work and surface the divergence. The mechanism would need to be re-spec'd, not iterated around.
- If Cascade C Tax B falsifies more than 2 predictions in a row on medallion-10, switch the iteration agent to "human-in-loop edit selection" until C is calibrated.

---

## Where to look for more detail

| Layer | File |
|---|---|
| Iteration-loop operational state per session | `docs/iteration-status.md` |
| Per-decision rationale (all repos) | `docs/decisions/` |
| Per-issue rationale (all repos) | `docs/issues/` |
| Per-cascade plans | `.claude/plans/` (this repo, qiyas, bikar) |
| Cross-repo task linkage | `docs/cross-repo-dependencies.md` (mirrored in all three repos) |
| Convergence philosophy & hard gates | `CLAUDE.md` |
| Validation contract (orchestrator output schema) | `docs/validation-overall.md` + `qiyas/docs/validation-envelope.md` |
| qiyas mission, value-add, use cases | `qiyas/docs/product-vision.md` |
| qiyas architectural decisions in narrative form | `qiyas/docs/dev-mental-model.md` |
| bikar architectural decisions in narrative form | `bikar/docs/decisions/` |

---

## Update log

- **2026-05-11** — Initial draft. Cascade B PR2 (extend) just shipped at commit `8fa72dd`. Cascade B PR3 (clip) is the next named slice. Cascades A and C remain in-flight in the background.
