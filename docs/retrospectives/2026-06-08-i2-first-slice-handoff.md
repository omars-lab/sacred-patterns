# Handoff — open-work board + recommended pickup (I2 first slice)

> Paste the fenced block into a **fresh, clean session** started from
> `/Users/omareid/Workspace/git/sacred-patterns` (it has cross-repo access to
> `../qiyas` + `../bikar`). This is the **complete open-work board** across all
> three repos, not just one task: the held trees, every open owner-gated decision
> doc, the routing doc's trigger-gated list, and the three deferred image→DSL §4
> builds. The **recommended first pickup is the I2 photo-cascade thin first
> slice** (it validates the project's entire image→DSL premise on a real input for
> the first time) — but the board below is the full map so a cold session can pick
> differently if the I2 premise fails or the owner redirects.
>
> **Scope note:** this file was originally I2-only (2026-06-08); broadened to the
> full board 2026-06-10. The canonical living board remains
> `qiyas/.claude/plans/post-i1-task-routing.md` — this doc is a point-in-time
> snapshot that points *at* it, never a replacement (snapshots rot; the routing
> doc + LEDGERs are generated/maintained, so verify counts against them, per C1).

## Context for the operator (not part of the paste)

The 2026-06-07 session shipped the retrospective's memory + skill + decision-doc
leftovers and marked `2026-06-06-image-to-dsl-recommendations.md` APPLIED. It
deliberately **deferred the three §4 builds** (confirm-and-sequence only):
1. **I2 photo cascade (#303/#304)** — the actual image→DSL inference, never run.
2. **Girih substitution-rule primitive** — producer-side fix for the medallion-10 A6=0 ceiling.
3. **Auto-generated training pipeline** — bikar GT → qiyas verify at scale (substrate for I2).

Sequencing (from the routing doc's 2026-06-07 entry): **I2 thin slice first**
(highest value — proves the premise on a real input), training pipeline (#5) as
its substrate, girih as a parallel ceiling-lift.

**Critical premise fact (verify first, don't trust this doc — counts go stale):**
the **decision-memory cascade + leftovers are still uncommitted** as of 2026-06-10.
The retrospectives themselves DID get committed (`746bed6` "docs: publish image→DSL
retrospective set" — so this handoff file is tracked), but the decision-schema,
`LEDGER.md`, the `2026-06-07-loop-terminal-condition.md` doc, and the
`loop-idle-audit` skill are all still UNTRACKED in the working tree. All three
repos carry held trees (2026-06-10 snapshot: sacred-patterns ~22, qiyas ~84,
bikar ~42 changed files). **Resolving the held trees with the owner is itself an
open item (board item H below)** and should be settled BEFORE layering a new build
on top — you don't want I2 artifacts tangled with an unrelated uncommitted cascade.
Run `git -C ~/Workspace/git/sacred-patterns status --short` + `git log --oneline -3`
(and the same for `../qiyas`, `../bikar`) first.

## Full open-work board (2026-06-10 snapshot — verify against the routing doc + LEDGERs)

This is the complete map of what's open / worth doing across the three repos. It
is a **snapshot**; the live sources are `qiyas/.claude/plans/post-i1-task-routing.md`
(the routing board) and each repo's generated `docs/decisions/LEDGER.md` (open
owner-gates). Verify counts there before acting — do not trust the numbers in this
doc once it's more than a few days old (C1).

### H — Held trees (resolve commit/discard with the owner) — *do this first*
- **sacred-patterns** (~22 changed): the decision-memory cascade + leftovers are
  uncommitted (decision-schema, LEDGER, `loop-terminal-condition` doc,
  `loop-idle-audit` skill — all UNTRACKED) + modified CLAUDE.md/skills. The
  retrospectives already committed (`746bed6`).
- **qiyas** (~84 changed) and **bikar** (~42 changed): large held trees, contents
  un-audited by this handoff — the next session must `git status`/`git diff` them
  and decide commit vs discard WITH the owner before building on them.
- Why first: every other item below either lands new commits or reads the tree;
  an unresolved held tree tangles new work with old (and the GHA-budget tenet means
  you batch + push deliberately, not reflexively).

### G — Deferred image→DSL §4 builds (the original charter of this handoff)
1. **I2 photo cascade (#303/#304)** — *recommended first pickup; fully scoped in
   the paste block below.* Scope: `qiyas/.claude/plans/post-i1-cascade-roadmap.md`
   (I2 section, trigger fired 2026-05-29).
2. **Girih substitution-rule primitive** — producer-side fix for the medallion-10
   A6=0 ceiling. `bikar/.claude/plans/girih-substitution-rule-engine.md` +
   `bikar/docs/decisions/2026-05-28-medallion10-girih-ceiling.md`. Independent of I2.
3. **Auto-generated training pipeline** — bikar GT → qiyas verify at scale + B-AFF
   (CVPR-2023). `sacred-patterns/.claude/plans/bikar-as-training-data-generator.md`;
   sacred-patterns task #5. The natural substrate for I2 — advance alongside/after I2.

### D — Open owner-gated decision docs (PENDING / REOPENED / PROPOSED)
Each is a decision the owner hasn't picked (or a falsified one to re-decide). Ship
a documented default where the decision-pick authorization covers it (reversible);
otherwise present for an owner pick. **Verify each status against the LEDGER** — a
status can have flipped since this snapshot.

- **sacred-patterns (1):**
  - `arc-lens-partial` — `docs/decisions/2026-05-07-partial-shape-rendering-via-construction.md` (REOPENED) — partial-shape #106 cascade.
- **qiyas (13):**
  - `anti-symmetry-floor` — `2026-05-20-qiyas-anti-symmetry-floor-breach.md` (PENDING)
  - `ci-coverage-telemetry` — `2026-05-21-bikar-validate-dsl-contract-ci-shape.md` (PENDING)
  - `closeout-feedback-surface` — `2026-05-12-i1-closeout-report-feedback-surface.md` (PROPOSED)
  - `closeout-report-surface` — `2026-05-12-i1-closeout-report-surface.md` (PROPOSED)
  - `i1-ratchet` — `2026-05-28-i1-ratchet-tree-walk-vs-index.md` (PENDING)
  - `scope-rescope` — `2026-05-12-i1-cascade-closeout.md` (PENDING)
  - `serialization-d4` — `2026-05-23-362-phase-1-d4-cutover-serialization.md` (PENDING)
  - `shape-vocab-typed-params` — THREE docs (PENDING): `2026-05-16-typed-shape-params-vs-object-bag.md`, `2026-05-18-shape-discriminated-union-migration-sequencing.md`, `2026-05-18-shape-vocabulary-vs-detector-tolerances.md` *(note: 3 docs on one tag — the coherence rule allows ≤1 AUTHORITATIVE/ACCEPTED per tag, so these are all open; reconciling them may be one job)*
  - `star7-red-detection` — TWO docs (PENDING): `2026-05-18-star7-red-shape-detection-routing.md`, `2026-05-21-star7-missed-red-shapes-mechanism.md`
  - `svg-direct` — `2026-05-21-iter-14-svg-direct-detector-path-forward.md` (PENDING)
- **bikar (5):**
  - `arc-lens-partial` — `2026-05-17-arc-region-class-precision.md` (REOPENED)
  - `derived-shape-naming` — `2026-05-27-derived-shape-naming-convention.md` (PENDING)
  - `fill-void` — `2026-05-18-fill-void-where-map-population.md` (PENDING)
  - `line-primitive` — `2026-05-26-line-primitive-cascade-D1-D2-D3.md` (PENDING)
  - `mirror-rotate` — `2026-05-26-mirror-rotate-polygon-body-emission.md` (PENDING)

### T — Routing-doc trigger-gated items (from `post-i1-task-routing.md`)
Items waiting on a trigger that hasn't fired or an owner decision (verify each is
still gated — a trigger may have fired):
- **A5** — #25 / #59 / #60
- **code-validation** — #343 / #351 / #352 / #465
- **CI-report** — #484 / #485
- **DSL tagging** — #495
- **hier-diff** — #610
- **#603** — GHA budget (owner-only)

### How to pick (don't idle — `loop-idle-audit`)
Default order: **H (held trees) → recommended G.1 (I2 slice) → lowest-tier broken
thing among D/T** (tenet 20). For any D item, check the decision-pick authority
(ship a reversible documented default) before presenting for an owner pick. Before
declaring "nothing to do," run the idle-vs-blocked test (name the unfired trigger
or the named blocker) — the board above means a bare "idle" is almost never honest.

---

## Recommended first pickup — I2 photo-cascade thin slice (paste block)

````
Task: Build the FIRST THIN SLICE of the I2 photo cascade — the deferred §4.1 item from the 2026-06-06 image→DSL recommendations. I2 is the first time the qiyas detector sees an input it did NOT help create (a real/synthetic photograph, vectorized via VTracer, with NO bikar data-* metadata). Goal of THIS session: one end-to-end run on ONE input, producing a measurable photo-traced-vs-synthetic divergence on the same pattern — NOT the whole cascade.

Read first (in order):
- qiyas/.claude/plans/post-i1-cascade-roadmap.md — the authoritative I2 scope. Read the "I2 — Real photographs → trace → detector" section: capability claim, why-it-matters, and the "Closeout gate (to design)" (acceptable divergence band + hand-annotation path). The revisit trigger FIRED 2026-05-29.
- sacred-patterns/docs/retrospectives/2026-06-06-image-to-dsl-retrospective.md §1 (cap-1: "not actually image→DSL yet" / I1-vs-I2 regimes) + §5 (open alternatives, I2 row) — the WHY.
- sacred-patterns/docs/retrospectives/2026-06-06-image-to-dsl-recommendations.md §4.1 + the APPLIED "Application status" callout — confirms this is the deferred build, not a fresh idea.
- qiyas/.claude/plans/post-i1-task-routing.md — the 2026-06-07 entry sequences I2/girih/training; consult §A/§C per the post-i1 routing memory before picking.
- The I2 source-of-truth task notes: qiyas#303 (I2 design notes), qiyas#304 (revisit trigger). Find them via the routing doc / TaskList; if the task list is empty (post-/clear), the roadmap doc above IS the scope.
- MEMORY.md (auto-loaded) — especially the DSL-as-source-of-truth tenet (C7/23): I2 is explicitly the PRODUCER-LESS fallback path (no data-*; the detector becomes producer-of-record with detector-confidence, per the DETR pattern in Tenet 23's photo-cascade carve-out). Do NOT re-derive the I1 contract here.

This paste block is the recommended FIRST pickup. The full open-work board (held trees, ~19 open owner-gated decision docs, the routing-doc trigger-gated list, and the other two §4 builds) is in the "Full open-work board" section of this same file (sacred-patterns/docs/retrospectives/2026-06-08-i2-first-slice-handoff.md) — read it if the I2 premise fails or the owner redirects.

PREMISE CHECK (tenet C1 — do BEFORE any build or option):
1. Verify the held-tree state (board item H): `git -C ~/Workspace/git/sacred-patterns status --short` + `git log --oneline -3`, and the same for ../qiyas and ../bikar. As of 2026-06-10 the decision-memory cascade + leftovers were STILL uncommitted (decision-schema, LEDGER, loop-terminal-condition doc, loop-idle-audit skill UNTRACKED) and all three repos held trees (~22/84/42 files). If still uncommitted, STOP and resolve commit-vs-discard with the owner BEFORE starting I2 — do NOT start a new build on top of an unrelated uncommitted cascade.
2. Verify the I2 trigger genuinely fired and the scope is still real: confirm the roadmap's "Closeout gate (to design)" is still UNDESIGNED (if a gate already exists, you're refining not creating). Confirm the qiyas detector's VTracer/raster path still exists (grep qiyas for the rasterize→trace entry point; the I1 work added an SVG-direct fast-path that BYPASSES trace — I2 needs the trace path specifically).
3. Pick the ONE input: simplest-first (tenet 17/20). A single primitive or a Tier-0/Tier-1 pattern rendered by bikar, then rasterized to a PNG and re-traced via VTracer — so you have a known ground truth to measure divergence against. Do NOT start with medallion-10 (Tier 3). State the expected visual outcome before you look (tenet 26).

If the premise holds, build the thin slice:
- ONE bikar pattern → render PNG (the "photo" stand-in) → VTracer → traced SVG (NO data-*) → qiyas detector → compare against the same pattern's synthetic (data-*-carrying) detection. Use the existing iteration-validate / qiyas pixel-diff + svg-audit tooling where it fits; do NOT build a parallel scoring path (tenet 11 — one tool path per question).
- Measure the photo-traced-vs-synthetic divergence. That number is the deliverable. Write down what an acceptable band WOULD be (the closeout-gate design) — but per the gate-needs-an-oracle memory, only ship a gate whose truth value is actually in the record; if the band is a guess, propose it, don't enforce it.
- Per tenet 27: view the traced SVG + the detection through the review portal before declaring the slice works. A green number is not the gate; the eye is.
- Per tenet 18: codify the slice as a test/fixture (the traced input + the expected divergence) so the witness outlives the session.

Routing notes (don't build these this session — sequence them):
- Girih primitive (§4.2) and training pipeline (§4.3, sacred-patterns task #5) are the OTHER two deferred builds. If I2's premise FAILS (e.g. the trace path is gone, or the owner redirects), the next-best pickup is the girih primitive (independent, lifts the medallion-10 ceiling) — see bikar/.claude/plans/girih-substitution-rule-engine.md. Don't silently switch; surface the pivot.

Hard rules:
- Premise check FIRST (C1) — a deferred-build doc's "this was never run" claim is exactly the kind that self-falsifies; verify the trace path + trigger against the code, not this prompt.
- Simplest input first (17/20); state visual expectation before looking (26); portal verdict before "works" (27); codify the witness (18); one tool path (11); no data-* re-derivation shortcut on the photo path (23 carve-out).
- This is a BUILD (source under qiyas/bikar) — the qiyas make ci-local source gates DO apply. Run `make ci-local-fast` before any qiyas push; no push without it green (and no push without owner OK if that's still the standing rule — check the push-authorization memory).
- Don't commit/push unless the owner asks OR the standing push-authorization grant covers it (ci-local-fast green). When the thin slice runs end-to-end (or the premise falsifies), report the divergence number + portal verdict + what the closeout gate should be, then stop for review.

Definition of done (if you took the I2 slice):
1. Premise verified (held-tree resolved-or-flagged; trace path confirmed; one input picked).
2. ONE input run end-to-end: bikar render → PNG → VTracer → qiyas detector → divergence vs synthetic.
3. Divergence measured + portal verdict recorded + witness codified as a fixture/test.
4. Closeout-gate band PROPOSED (not enforced unless its truth oracle is in the record).
5. Report the number, the portal verdict, the proposed gate, and the I2/girih/training sequencing state; stop for owner review.

Definition of done (if the I2 premise failed and you took a board item instead):
1. Name which board item (H / G.2 / G.3 / a D decision tag / a T trigger item) and why I2 was deferred — surface the pivot, don't switch silently.
2. For a D decision: either ship a reversible documented default (decision-pick authority) and update the LEDGER (`make ledger`), or present options for an owner pick. For H: report the held-tree audit + a commit/discard recommendation. For G.2/G.3: scope a first slice the way the I2 block scopes I2.
3. Same hard rules (premise C1, simplest-first, portal verdict, witness, one tool path, ci-local-fast before push).
4. Report outcome + the updated board state; stop for owner review.
````
