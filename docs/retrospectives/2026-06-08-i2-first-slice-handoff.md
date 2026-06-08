# Handoff prompt — pick up the deferred image→DSL approach-level work (I2 first slice)

> Paste the fenced block into a **fresh, clean session** started from
> `/Users/omareid/Workspace/git/sacred-patterns` (it has cross-repo access to
> `../qiyas` + `../bikar`). This continues the work the 2026-06-07 retrospective
> leftovers session deliberately deferred: the three §4 approach-level **builds**.
> The recommendation is to start with the **I2 photo-cascade thin first slice** —
> it validates the project's entire premise (image→DSL) on a real input for the
> first time.

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

**Critical premise fact (verify first, don't trust this doc):** as of 2026-06-07
the prior two sessions' work (decision-memory cascade + leftovers) was **entirely
uncommitted in the working tree** — `git log` HEAD was `5c2163d`. If it's still
uncommitted, that's a held-tree to resolve with the owner BEFORE starting a new
build on top of it (you don't want I2 artifacts tangled with an unrelated 200-file
uncommitted cascade). Run `git -C ~/Workspace/git/sacred-patterns status --short`
and `git log --oneline -3` first.

````
Task: Build the FIRST THIN SLICE of the I2 photo cascade — the deferred §4.1 item from the 2026-06-06 image→DSL recommendations. I2 is the first time the qiyas detector sees an input it did NOT help create (a real/synthetic photograph, vectorized via VTracer, with NO bikar data-* metadata). Goal of THIS session: one end-to-end run on ONE input, producing a measurable photo-traced-vs-synthetic divergence on the same pattern — NOT the whole cascade.

Read first (in order):
- qiyas/.claude/plans/post-i1-cascade-roadmap.md — the authoritative I2 scope. Read the "I2 — Real photographs → trace → detector" section: capability claim, why-it-matters, and the "Closeout gate (to design)" (acceptable divergence band + hand-annotation path). The revisit trigger FIRED 2026-05-29.
- sacred-patterns/docs/retrospectives/2026-06-06-image-to-dsl-retrospective.md §1 (cap-1: "not actually image→DSL yet" / I1-vs-I2 regimes) + §5 (open alternatives, I2 row) — the WHY.
- sacred-patterns/docs/retrospectives/2026-06-06-image-to-dsl-recommendations.md §4.1 + the APPLIED "Application status" callout — confirms this is the deferred build, not a fresh idea.
- qiyas/.claude/plans/post-i1-task-routing.md — the 2026-06-07 entry sequences I2/girih/training; consult §A/§C per the post-i1 routing memory before picking.
- The I2 source-of-truth task notes: qiyas#303 (I2 design notes), qiyas#304 (revisit trigger). Find them via the routing doc / TaskList; if the task list is empty (post-/clear), the roadmap doc above IS the scope.
- MEMORY.md (auto-loaded) — especially the DSL-as-source-of-truth tenet (C7/23): I2 is explicitly the PRODUCER-LESS fallback path (no data-*; the detector becomes producer-of-record with detector-confidence, per the DETR pattern in Tenet 23's photo-cascade carve-out). Do NOT re-derive the I1 contract here.

PREMISE CHECK (tenet C1 — do BEFORE any build or option):
1. Verify the prior sessions' state: `git -C ~/Workspace/git/sacred-patterns status --short` + `git log --oneline -3`. If the 2026-06-06/07 decision-memory cascade + leftovers are STILL uncommitted (expected: HEAD=5c2163d, ~20 untracked/modified docs+skills), STOP and ask the owner whether to commit that held tree first — do NOT start I2 on top of an unrelated uncommitted cascade.
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

Definition of done (this session):
1. Premise verified (held-tree resolved-or-flagged; trace path confirmed; one input picked).
2. ONE input run end-to-end: bikar render → PNG → VTracer → qiyas detector → divergence vs synthetic.
3. Divergence measured + portal verdict recorded + witness codified as a fixture/test.
4. Closeout-gate band PROPOSED (not enforced unless its truth oracle is in the record).
5. Report the number, the portal verdict, the proposed gate, and the I2/girih/training sequencing state; stop for owner review.
````
