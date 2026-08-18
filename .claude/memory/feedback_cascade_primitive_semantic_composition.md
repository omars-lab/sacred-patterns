---
name: cascade-primitive-semantic-composition
description: "Cascade plans that compose multiple shipped DSL primitives must validate primitive *semantics* compose (not just primitive *availability*); otherwise the cascade's prediction is unbacked"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When a cascade plan recommends layering N existing primitives (e.g., `extend` + `boundary` + `clip` in cascade #106), the plan's quantitative prediction (+composite, -missing-shapes, etc.) is only trustworthy if the plan **validates that the primitives' semantics compose** for the target geometry — not just that each primitive ships and the syntax parses.

**Why:** sacred-patterns#106 cascade (`partial-shape rendering via construction`) was authored 2026-05-07 and ACCEPTED based on a plan that listed `extend → clip` as a clean two-step. Two variants falsified on bikar-medallion-10:
- iter-20 `clip(C0)` regressed composite by -0.13 (wrong boundary spec)
- iter-21-probe `clip(C0+S0..S9)` regressed by -0.029 with extra-shapes severity=error

The root reason for *both* variants: bikar's `clip` primitive is `extend → drop-faces-wholly-outside-boundary`, not `extend → intersect-with-inner-geometry-before-clip`. The cascade plan implicitly assumed intersection-during-clip; the actual primitive doesn't do that. The plan's audit ("4 primitives ship: extend, boundary, clip, intersect") validated availability but not composability.

**How to apply:** before authoring a cascade plan that composes ≥2 DSL primitives:
1. **Read each primitive's implementation** (not just its grammar/docs) and write down what it does to the half-edge graph or vertex/face structure.
2. **For each pair of composed primitives, ask: does P1's output satisfy P2's input invariants?** (e.g., does `extend`'s arc geometry survive `clip`'s face-drop pass in the way the plan needs?)
3. **If the composition was never tested on a simple fixture, file a Tier 0 single-primitive composition test BEFORE measuring against the composite target.** Per Tenet 17 (prove the primitive first), the cascade prediction should be validated on `single-petal + extend + clip` BEFORE medallion-10.
4. **In the falsification log, distinguish L2 (primitive's mechanism wrong) from L3 (option enumeration missed a needed primitive/semantic).** The 2026-05-25 case is both: `clip` works as documented (not L1), but the cascade needed `clip-with-intersection-preserve` semantic that wasn't enumerated (L3).

**Companion to:** [[feedback_consumer_audit_construction_contracts]] (audit upstream producers, not just downstream consumers — same shape on the *primitive composition* axis), [[feedback_cf_delta_cost_blind]] (cascade predictions optimistic when they don't model interaction cost), Tenet 7 stop rule (two variants of cascade #106 clip primitive falsified — stop authoring variants, run handle-falsification fully).

**Failure mode this prevents:** the next cascade plan layering `boundary + extend + clip + intersect` on top of new bikar primitives will repeat the same shape — predicting +leverage from a four-step that the four primitives can't actually express in composition. With this rule, the cascade ships a Tier 0 composition test as part of the plan's slice-1, and the composability claim becomes measurable before any composite-target measurement is taken.
