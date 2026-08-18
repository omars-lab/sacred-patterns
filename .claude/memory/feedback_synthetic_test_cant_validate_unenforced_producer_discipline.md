---
name: synthetic-test-cant-validate-unenforced-producer-discipline
description: "a synthetic Tier-0 test that hand-assigns the very label discipline under test cannot validate that label on a real corpus where the producer doesn't enforce it — re-score against the real corpus before picking a gate oracle"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When a decision-doc option's correctness depends on a *producer-side
discipline* (e.g. "every distinct geometry gets a distinct authored name"),
a synthetic Tier-0 witness that **hand-assigns that discipline** proves only
that the consumer code works *if the discipline holds* — it cannot prove the
discipline actually holds in the real corpus. Re-score the option against the
**real** corpus before recommending it as a gate oracle.

**Why:** qiyas#661 F2 Option C (2026-05-29) gated retrieval on bikar's authored
`evidence.shape_id`. The Tier-0 witness `_MIXED_CORPUS` in
`tests/test_identity_f2_report.py` hand-set `shape_label="tri_poly"` on both
triangles and `"sq_poly"` on both squares — baking in per-geometric-kind
naming. It passed (mAP=1.0) and gave false confidence. On the real schema-1.21
i1-corpus, bikar template authors reuse names like `scalene_tri_poly` across
geometrically *distinct* triangles (cross-construction signature distances
0.0, 8.04, 33.05), so `shape_id` scored WORST of three labels (mAP=0.296,
EER=0.305) — worse than the `face_class` it replaced. This is the person-re-ID
"Noise-II" failure (distinct instances sharing one identity label). The
producer discipline the synthetic test assumed is not enforced anywhere in
bikar. Falsification artifact:
`qiyas/docs/decisions/2026-05-29-f2-face-class-is-wrong-retrieval-label.md`
(Falsification log) + `qiyas/tests/test_identity_f2_eer.py`
(`test_geom_label_is_a_cleaner_eer_oracle_than_shape_id`).

**How to apply:** Before recommending any option whose answer-key / oracle /
ground-truth label is *authored by a producer* (DSL author-name, annotator
label, hand-written id), ask: "does the synthetic test that validated this
hand-assign the label, or does it draw the label from the real producer?" If
hand-assigned, the test validates the consumer, not the label — run the option
against the real corpus and measure the label's quality (EER / mAP / a CLM
alignment number) before costing or shipping it. A detector-*derived* label
(e.g. geometric `type`) is often a cleaner oracle than an authored name,
because it is pinned to the property under test rather than to author intent.

**Companion to:** [[feedback_validate_label_descriptor_alignment_before_gating]]
(re-score under a descriptor-granularity label before tuning),
[[feedback_separation_distance_vs_merge_gate]] (a label's equivalence relation
must match the geometry the descriptor measures),
[[feedback_cascade_primitive_semantic_composition]] (validate real semantics,
not just availability). Reinforces handle-falsification's "audit subbox" — the
synthetic test was the audit that masked the real-corpus gap.
