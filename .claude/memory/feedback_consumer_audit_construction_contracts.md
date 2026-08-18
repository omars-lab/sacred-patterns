---
name: Consumer audit must cover construction-time contracts, not just graph-walk contracts
description: When auditing whether a kernel refactor is safe, reading downstream consumers of the output is insufficient; the audit must also cover upstream DSL/primitive code that constructs the inputs with implicit shared-vertex assumptions
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
When planning a kernel-level refactor (vertex-merge policy, edge-key strategy, canonicalization rule), the standard "consumer audit" — read every file that consumes the kernel's output and verify the refactor doesn't break their contracts — is **necessary but not sufficient**. The audit must also cover the **upstream construction code** (DSL evaluators, primitive emitters, gt-emitter) that produces the kernel's *inputs* with implicit shared-vertex assumptions baked in.

**Why:** 2026-05-19 bikar Option C cascade. The slice-1 audit (`bikar/.claude/plans/option-c-consumer-audit.md`) read all 5 EdgeGraph consumers (planar-graph-builder, face-extractor, polygon-union, evaluator, strapwork) and produced a verdict of "safe to refactor." Slice-2 implementation revealed the verdict was wrong: every petal-N-ring construction in the corpus relies on two arcs from *different circles* having *intentionally shared endpoint coordinates* — that's the entire mechanism by which a "lens face" closes between two circles. The DSL emits `connect arc P1 -> P2 on circleA` plus `connect arc P1 -> P2 on circleB` where P1 and P2 are the two arc-arc intersection points; the implicit contract is "these endpoints must canonicalize to the same vertex index in the planar graph." Option C un-merged them, the lens faces dissolved, every healthy baseline regressed. Three Option-C variants tried in one session, all falsified. Tenet 7 stop rule fired.

The audit missed this because it only checked the *output* side. The construction-time contract — "DSL primitives produce arcs whose endpoints are intentionally coincident across different circles to make face closure work" — was implicit in the DSL evaluator and gt-emitter, not in any consumer of the EdgeGraph.

**How to apply:** When authoring a kernel-refactor consumer audit:

1. **List downstream consumers** (the standard step). Read each one's contract with the kernel output.
2. **List upstream producers** (the new step). For each function that constructs the kernel's input, name the *implicit invariants* it relies on the kernel preserving. For bikar, this means at minimum: the DSL evaluator's `compile-*` functions, the gt-emitter, the polygon-union input prep, the strapwork primitive builder, any test helper that hand-crafts edges and feeds them to `buildIntersectionGraph`.
3. **Run the refactor against a hand-picked test fixture that exercises the implicit invariant before doing a corpus-wide sweep.** For Option C, the petal-debug test would have caught the lens-face regression in <1s; instead the consumer audit declared "safe" and slice-2 implementation surfaced it only after a full vitest run.
4. **The audit verdict must explicitly name what it didn't check** — "this audit covers EdgeGraph consumers but does not cover EdgeGraph producers; before shipping, run construction-time fixtures." That sentence is the load-bearing addendum.

**Companion to tenets 4 (verify before claiming done), 7 (stop after 2nd tweak), and 17 (prove the primitive before composing):** tenet 4 says verify your own claims; this tenet says verify the audit's claims by exercising the construction side; tenet 7 names when to stop iterating local probes and escalate; tenet 17 says start from the atomic witness (a single petal lens face) before declaring composite-scale safety.

**Cross-repo:** the same trap exists for qiyas detector refactors (does the detector audit cover the signature-compute callers that feed it?) and for sacred-patterns iteration-loop refactors (does the orchestrator audit cover the validate-svg preflight and qiyas-diff wrapper?). Audit both sides.
