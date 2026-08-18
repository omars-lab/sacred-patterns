---
name: verify-transcription-data-is-obtainable-before-costing-the-option
description: "when a decision-doc option's mechanism depends on transcribing published data (a table, figure, rule set), confirm the data is actually obtainable at the needed fidelity BEFORE recommending/costing it"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When a decision-doc option's mechanism is "transcribe published data X (a substitution-rule table, a figure's edge indices, a coefficient set) and apply it through tested code," the option's viability hinges on a precondition the audit usually skips: **is X actually obtainable at the fidelity the mechanism needs?** Verify that before writing the option's cost/recommendation — not after starting implementation.

**Why:** bikar `docs/decisions/2026-05-28-medallion10-girih-ceiling.md` Option C′ recommended "transcribe the Lu-Steinhardt decagon substitution rule into a `SUBSTITUTION_RULES` table, apply via the tested `attachGirihTile`." The mechanism audit was correct — `attachGirihTile`/`subdivideTile`/renderer were all sound. But nobody checked whether the *table* was transcribable: the real Bowtie-Hexagon-Decagon decagon rule is 80 decagons + 80 bowties + 36 hexagons per parent (not the pentagon/rhombi @ φ² the plan assumed), figure-dependent, and ~80 per-child edge indices that can't be read off a paper figure I can't view. A geometry probe (`/tmp/girih-probe.mjs`) falsified the assumed arrangement in minutes; the correct rule's *unobtainability* was the real blocker. The fix (Option C″) kept the same mechanism but discovered the arrangement from geometry (frontier edge-attachment to convergence) instead of from a transcribed table — moving the only fallible unit to a finite, unit-testable angle→tile chooser.

**How to apply:** Before recommending or costing any option whose mechanism reads "transcribe published X and apply it," add an explicit precondition check to the option's web-research step: locate X at the fidelity the mechanism consumes (the actual edge indices, the actual coefficients — not just "the paper has a figure"). If X is figure-only / unviewable / larger than expected (an 80-row table vs the assumed handful), the transcription is the hidden risk, and a *geometry/data-discovery* variant (compute the arrangement, don't memorize it) is usually the lower-risk sibling option. Run the cheap falsifying probe (does the assumed arrangement even produce the required output?) before writing kernel code.

**Companion to:** [[feedback_check_emit_layer_before_option]] (check the real layer before authoring a complex option), [[feedback_check_mechanism_already_implemented]] (read the target module before costing rework), [[feedback_a6_baseline_construction_philosophy_mismatch]] (the medallion-10 cascade this falsification sits inside), and Tenets 17 (prove the primitive first — the fallible unit must be atomically testable) + 18 (codify the witness probe as a test).
