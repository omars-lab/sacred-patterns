---
name: pattern-extrapolation-at-n5-breaks-at-n6
description: "A pattern fit at N=5 witnesses with zero counter-examples is NOT load-bearing enough to make confident predictions outside the witness range; falsifiable next-witness predictions must be PROBES, not confidence-boosters. The parity rule (qiyas#132 Ticks 82-90, N=5 witnesses) was falsified at Tick 91 D_8 — the rule's mechanism (even-D edge symmetry) was a property held by ALL members of the predicted-LEAK class but only HALF predicted LEAK. Always pre-compute the mechanism on the OUTSIDE-CLASS witness before strengthening a rule on the IN-CLASS one."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

A pattern fit at N=5 witnesses with zero counter-examples is NOT load-bearing enough to make confident predictions outside the witness range; always pre-compute the predicted mechanism on the NEXT out-of-class witness BEFORE strengthening the rule.

**Why:** qiyas#132 Tick 90 (2026-05-27) wrote "the parity rule's predictive structure is now sharp enough at N=5 witnesses to make a strong falsifiable pre-render prediction for D_8 (predicted LEAK)." The predicted mechanism was "even-D polygon-edge tangents symmetric about polygon-interior axis → leak." Tick 91 D_8 came in CLEAN — REFUTING the rule. The mechanism's predicted-symmetric property is a property held by ALL inscribed regular even-N polygons by construction (it's the definition of "regular"). If I had pre-computed the symmetric-property check on D_8 BEFORE writing the prediction, I would have seen D_8 has the property too — and would have noticed the mechanism doesn't actually discriminate D_4/D_6 from D_8. The "N=5 witnesses, zero counter-examples" framing felt strong but masked a weak mechanism that the corpus hadn't yet challenged.

Specifically: D_3 edges (30°/150°), D_4 edges (45°/135°), D_5 (54°/126°), D_6 (60°/120°), D_7 (64.29°/115.71°), D_8 (67.50°/112.50°). ALL pairs are symmetric about 90° (polygon-interior-axis at P=(100,0)). The "symmetric about polygon-interior axis → leak" mechanism predicts ALL of them LEAK; only D_4, D_6 actually leak. The mechanism never actually predicted anything — it was a property that happened to correlate with parity at N=5 but didn't cause parity.

**How to apply:** Before authoring a "strengthen the rule to N=K+1" tick, do this pre-computation:
1. Pick the next *out-of-class* witness (the one the rule predicts will fall in a different verdict bucket than recent witnesses).
2. Compute the mechanism's discriminating property ON THAT NEXT WITNESS using the rule's own formula.
3. If the property's *value* on the next witness is different from the in-class witnesses, the rule is genuinely discriminating — proceed.
4. If the property's value is the SAME on the next witness as in-class witnesses, the rule is NOT discriminating — the correlation is coincidental, and the prediction is unjustified. Don't author the strengthening tick; pick a different probe that tests the actual discriminator.

For the parity rule specifically: the "symmetric about polygon-interior axis" property is true for ALL regular polygons (even AND odd, since odd-N has axis symmetry through one vertex). The rule was framed as if even-N's symmetry was special, but odd-N also has axis symmetry through the vertex at P. The mechanism was wrong from the start — it should have been caught by computing edge tangents for D_5 (which also has axis symmetry through P) before predicting D_7 CLEAN. The Tick 87 D_5 PASS happened to be CLEAN for some OTHER reason, and the parity rule retrofitted "symmetry" as the mechanism.

**Companion to:**
- Tenet 7 (don't tune to fit) — the parity rule was tuned-to-fit at N=4 witnesses by retrofitting symmetry as the mechanism.
- Tenet 8 (multi-witness — 2+ class members) — N=5 is comfortably above the 2-witness floor, which is why this entry's lesson is *additional* to Tenet 8: even passing the multi-witness gate, the mechanism can still be wrong if it wasn't pre-computed on the discriminating witness.
- Tenet 17 (simplest-first within tier) — the simplest-first sequencing within the Tier 1 polygon-anchored matrix is what surfaced this; without it, D_8 might have been skipped entirely.
- [[feedback_bikar_polygon_corner_leakage_deg4_non_monotonic]] — the falsified parity rule itself.
- [[feedback_canonical_algo_web_search]] — when in doubt about an algorithm's mechanism, web-search rather than retrofit; this entry adds "and pre-compute on the next out-of-class witness."
