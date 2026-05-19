---
name: debug-kernel-change
description: Verification ladder for edits to kernel-level geometry code — `buildIntersectionGraph`, `buildHalfEdges`, `extractFaces`, vertex-merge policy, edge-key strategy, canonicalization rules. Apply BEFORE shipping any change to bikar's `packages/core/src/kernel/` or `packages/core/src/graph/`. The ladder forces full-suite acceptance (tenet 21), both-sides consumer audit (tenet 22), tenet-7 stop-rule introspection, and witness-to-test promotion (tenet 18) — the workflow that would have caught the bikar#424 Option D regression and the Option C falsification BEFORE they shipped.
user_invocable: true
argument: "<change-summary>"
---

# debug-kernel-change

Kernel changes are the highest-blast-radius edits in the bikar codebase. A wrong vertex-merge tolerance, a wrong edge-key strategy, a wrong half-edge linkage rule silently corrupts every face downstream — every DSL pattern, every gt-emitter fixture, every detector measurement built on top. The bikar#424 cascade spent eight options across two sessions because the verification ladder was implicit; this skill makes it explicit.

The shape of the failure this skill exists to prevent: an agent runs a corpus sweep, sees no regression, declares "Option X ships," commits — and the next agent (or the same agent on the next loop) discovers via a synthetic test failure that Option X regressed an invariant the corpus didn't probe. The cost of running this ladder is ~30-60 minutes; the cost of skipping it is one falsified option per skipped step, each rediscovered from scratch.

## When to invoke

Trigger this skill **before** committing any edit to:

- `bikar/packages/core/src/kernel/intersection-graph.ts` — `buildIntersectionGraph`, `PointIndex`, `splitAndAddArc`, vertex-merge policy, edge canonicalization.
- `bikar/packages/core/src/graph/planar-graph-builder.ts` — `buildHalfEdges`, CCW-next linkage rule, twin assignment.
- `bikar/packages/core/src/graph/face-extractor.ts` — face walker, outer-face heuristic, cycle closure rules.
- Any function that emits `EdgeGraph` edges with implicit invariants the kernel preserves (DSL evaluator `compile-*` functions, gt-emitter, strapwork primitive builder, polygon-union input prep).
- `EPSILON`-derived geometric tolerances anywhere in the geometry pipeline.

**Also trigger** when changing a type signature or schema in the geometry pipeline — `EdgeGraph`, `HalfEdge`, `Face`, `ArcMeta`, `endpointIdentity`. Type-shape changes route through producer-side code the consumer-only audit misses (tenet 22).

**Don't trigger** for:
- DSL grammar / parser changes that don't touch kernel internals (use `/dsl-design` instead).
- Pure rendering changes (svg-utils, theme engine).
- Test-only edits, comment-only edits, doc-only edits.

The trigger is: a change whose correctness depends on geometric invariants that *some other code path* (DSL, gt-emitter, downstream detector, fixture-driven test) relies on implicitly.

## When to STOP and apply this skill instead of continuing

Mid-session, if you hit any of these, halt and run the ladder:

- You're about to commit a change to a kernel file having only run a corpus sweep, not the full vitest suite.
- You're about to claim "no regression" based on a curated subset of tests.
- You ran a probe script, observed the expected behaviour, and are about to ship without writing the test that asserts the invariant.
- You audited downstream consumers of an `EdgeGraph` (or other kernel output) and are about to ship without auditing upstream producers.
- The change is a constant tweak (tolerance, threshold, epsilon multiplier) and you haven't yet asked "is this the first tweak in service of this failure case?" (tenet 7 stop rule).

The cost of running this skill is bounded; the cost of any single skipped rung is one falsified option.

## The verification ladder — six rungs, run in order

### Rung 1 — Name the change and its witness

Before any code edit, write down two things:

1. **What this change is supposed to fix.** A specific failure mode, in plain language: "petal-N-ring N=4 produces 0 lens faces; expected 4," not "improve face-extractor correctness."
2. **Which test(s) currently witness the failure.** A vitest test name or a probe script path. If no test witnesses the failure, the very first edit is to write one (see Rung 6 — write the witness as a test BEFORE the fix, so the test goes red→green).

If you can name the fix but not the witness, you're about to ship a change with no measurable acceptance criterion. STOP. Write the test, run it red, then proceed.

### Rung 2 — Audit both sides (consumer + producer)

Per tenet 22: a kernel-refactor audit must cover both directions.

**Downstream consumers** (the standard step). For an `EdgeGraph` change, that's `planar-graph-builder`, `face-extractor`, `polygon-union`, the evaluator's face-classification step, strapwork. Read each one's contract with the kernel output and verify the change doesn't break it.

**Upstream producers** (the new step from tenet 22). For each function that constructs the kernel's input, name the *implicit invariants* it relies on the kernel preserving. For bikar at minimum:

- DSL evaluator `compile-*` functions in `packages/core/src/dsl/` — do they emit arcs from different circles with intentionally shared endpoint coordinates? (lens-face mechanism)
- `gt-emitter.ts` — does it bake any shared-vertex assumption into its emitted edges?
- `polygon-union.ts` input prep — does it pre-canonicalize coordinates?
- `strapwork.ts` primitive builder — does it rely on edge-identity for crossing detection?
- Test helpers that hand-craft edges and feed them to `buildIntersectionGraph`.

**Reference:** `bikar/docs/architecture.md` is the canonical map of which functions consume which kernel outputs and which produce which kernel inputs (sacred-patterns#430).

**Output of this rung:** a verdict that explicitly enumerates (a) the consumers covered, (b) the producers covered, (c) the implicit invariants identified. The sentence "this audit covers consumers but not producers" is the load-bearing addendum that prevents the false verdict — write it explicitly or expand the audit.

### Rung 3 — Probe the simplest atomic witness

Before the corpus sweep, before the full suite, run the change against the **simplest possible witness** that exercises the invariant the change touches (tenet 17).

For petal-N-ring family changes: that's `single-petal.bkr` (Tier 0) — does it still emit 2 lens faces? For arc-merge changes: that's a 2-arc fixture (one circle whose arc passes through the origin of another) — does the half-edge linkage still produce the expected face count?

If the atomic witness fails, the change is **falsified at the construction-time layer** regardless of what the consumer audit said. Don't proceed to corpus or suite — the fix is wrong; pivot.

If the atomic witness passes, proceed to Rung 4.

### Rung 4 — Run the full vitest suite (NOT a corpus sweep)

Per tenet 21: a corpus sweep is not the acceptance bar. Run:

```bash
cd bikar && npx vitest run --reporter=dot
```

— or the make-equivalent. The bar is full-suite green; a curated corpus subset is insufficient because synthetic test fixtures (`packages/core/tests/kernel/petal-debug.test.ts`, `packages/core/tests/graph/`, etc.) probe failure modes the corpus deliberately avoids.

**If the suite reveals a regression in a synthetic test the corpus didn't probe** (the bikar#424 Option D failure mode — `petal-debug.test.ts > layer 8 inner-triangle face`), the change is falsified. Do NOT pivot to "scoped tolerance" or "per-call-site override" — that's the second tweak tenet 7 names as the stop signal. Revert and pivot to an architectural fix (see `bikar/docs/decisions/` for the existing option enumeration; apply `/handle-falsification` if a decision doc exists for this change).

**If the suite is green**, proceed to Rung 5.

### Rung 5 — For constant tweaks specifically: apply the tenet 7 stop rule

If the change is a constant tweak (tolerance widening, threshold loosening, epsilon multiplier, fold-symmetry slack, detector confidence floor), the suite passing is necessary but not sufficient. Separately confirm:

1. **First tweak in service of this failure case?** If you've already tweaked the same constant once (or a sibling constant) in service of the same failing test, STOP. Tenet 7 has fired — the constant-tweak approach is falsified; author the decision doc for the architectural fix.
2. **≥2 independent witnesses?** The new constant value must be justified by at least two unrelated test cases, not one. If only one fixture motivates the new value, you're overfitting to one input.
3. **Named rationale for the new value?** The commit message (or decision doc) must name *what noise floor the new value absorbs* and *why the old value was wrong*. "Bumped EPSILON*100 → EPSILON*1000 to make N=8 pass" is not a rationale; it's a symptom narrative.

If any of these three fail, the change is not ready. Pivot to the architectural fix; do not ship the tweak.

### Rung 6 — Codify the witness as a test, promote any probe script

Per tenet 18: the witness that justified the fix MUST exist as a vitest test before the commit lands. If the witness is currently a probe script (`/tmp/probe-*.mjs`), a `console.log` sweep, or a shell command, write the test now.

The test asserts the **invariant the witness probed** — not the symptom narrative, the actual measured property:
- Face count for an N-value of an `.bkr` template.
- Edge-tag set on a specific face.
- `endpointIdentity` value at a known intersection.
- Whatever the smoke produced.

Run the test red (against the pre-fix code) → green (against the post-fix code). Commit fix + test together.

**Probe-promotion check:** if the probe script you wrote contains a view that would be useful for *future* debugging of the same kernel surface (vertex enumeration, half-edge dump, face-walker trace), file a follow-on task to promote it to a first-class debug method on `EdgeGraph` / `PlanarGraph` (the bikar#431 pattern — see `bikar/packages/core/src/graph/debug-views.ts`). The probe script will rot in `/tmp`; the debug method will be there for the next agent.

**Acceptable deferral:** if the test requires non-trivial scaffolding (a new fixture, a corpus regen, a cross-repo data dependency), file the test as a tracked follow-on task **blocked by** the fix's commit AND mention the task ID in the commit message. The witness still lives — in the task graph instead of the test suite, with an owner.

## Anti-patterns this skill names

- **"I swept a few representative patterns and nothing broke" → ship.** Representative ≠ exhaustive. Tenet 21 requires the full suite; synthetic fixtures exist precisely because corpus templates don't probe the failure modes those fixtures encode.
- **"I read every consumer of `EdgeGraph` and the refactor is safe" → ship.** Tenet 22: read the producers too. The bikar#426 Option C audit declared safe by reading 5 consumers; slice-2 implementation surfaced the producer-side implicit shared-vertex contract in 30 seconds.
- **"The probe script proved it works" → ship without writing a test.** Tenet 18: the witness must outlive the session. Probe scripts live in `/tmp` and disappear; tests live in the suite and run on every CI.
- **"The constant tweak is just an epsilon adjustment, not really an algorithmic change" → ship after corpus sweep.** Tenet 7 + 21: epsilon changes are algorithmic changes — they redefine which inputs canonicalize to which outputs. Treat them with full-suite rigour.
- **"Option X failed, let me try Option X-variant-2" → keep iterating.** Tenet 7 stop rule fired at the first variant. After two falsifications of the same option family, the option is wrong, not the variant. Author the decision doc for the next option class.
- **"This change touches the kernel but it's tiny" → skip the ladder.** The ladder cost is bounded (~30-60 minutes). The blast radius of a wrong kernel change is unbounded. The "tiny" framing has been wrong every time it's been used in this codebase.

## How this skill composes with others

- **Apply BEFORE `/handle-falsification`:** this skill prevents the falsification; `/handle-falsification` handles it after the fact. If the ladder catches the regression at Rung 3 or 4, you save the falsification round-trip entirely.
- **Apply ALONGSIDE `/decision-doc`:** if Rung 4 reveals a regression and Rung 5 catches the tenet-7 trigger, the next move is `/decision-doc` for the architectural fix. The skills compose: this one names *when* to escalate; `/decision-doc` structures *what* to escalate.
- **Companion to `/present-options`:** if the change is one of several options under consideration, `/present-options` enumerates them; this skill verifies the picked one before shipment.

## Verification

Before considering this skill's application complete, confirm:

- [ ] Rung 1: change goal + witness test named in the commit message (or pending-test task ID).
- [ ] Rung 2: audit verdict explicitly names consumers + producers covered.
- [ ] Rung 3: atomic witness ran green.
- [ ] Rung 4: full vitest suite ran green (paste the test-count line into the commit message).
- [ ] Rung 5 (constant tweaks only): first-tweak check + 2-witness check + rationale all green.
- [ ] Rung 6: witness test committed alongside the fix; probe-promotion task filed if applicable.

If any check fails, the change is not ready to ship. Don't commit just to clear the working tree — that's the failure mode tenet 12 names ("meaningful AND tested," not "any change").

## Sources

- `sacred-patterns/CLAUDE.md` tenets 4, 7, 17, 18, 20, 21, 22 — the tenets this ladder operationalizes.
- `~/.claude/projects/.../memory/feedback_narrow_corpus_sweep_tenet7_trap.md` — Option D falsification.
- `~/.claude/projects/.../memory/feedback_consumer_audit_construction_contracts.md` — Option C falsification.
- `~/.claude/projects/.../memory/feedback_check_mechanism_already_implemented.md` — Option G falsification (premise-already-implemented).
- `bikar/docs/architecture.md` — geometry pipeline architecture (sacred-patterns#430).
- `bikar/packages/core/src/graph/debug-views.ts` — first-class debug methods (bikar#431).
- `bikar/docs/decisions/2026-05-19-face-extractor-origin-coincidence-fix.md` — the bikar#424 cascade Phase 1a-1h falsification log.
