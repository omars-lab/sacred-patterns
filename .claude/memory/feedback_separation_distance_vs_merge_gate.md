---
name: Separation-distance vs merge-gate are different jobs
description: A distance that cleanly separates classes is not the same as one that preserves the equivalence relation; the merge gate must match the partition definition by construction
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
When fusing partitions or building a same-class predicate from a distance,
the distance must reproduce the **equivalence relation** of the truth
partition exactly — not merely separate its classes by a margin.

**Why:** The qiyas#171 probe found set-based Jaccard distance over
distinct provenance tags cleanly separated B-classes (within = 0,
between ≥ 0.167). That made it look usable as the F1 fused metric.
Implementing F1.v3 against it failed 3 corpus tests in iter-5: medallion10's
gt_G0000 and gt_G0001 share the *same set* of distinct tags but B places
them in B0 vs B4 because their *multisets* differ (`source_primitives`
multiplicities aren't equal). B-partition keys on
`tuple(sorted(source_primitives))` — multiset equality. Set-based Jaccard
silently merged them; the merge gate didn't match the relation it was
supposed to reproduce.

**How to apply:**
- When picking a distance to *flag* disagreements (a probe / diagnostic),
  separation is enough — set-based may be fine.
- When picking a distance/predicate as a *merge gate* for a partition,
  read the source code that defines the truth partition and reproduce its
  equivalence relation **literally**. If B groups by `tuple(sorted(X))`,
  the gate is multiset equality, not Jaccard distance over distinct X.
- This is independently discoverable from the truth-partition code — no
  test fixture needed to find it. Looking for it explicitly avoids the
  "tune the constant" trap (tenet 7): the fix is structural, not numeric.
- Red flag during impl: corpus tests fail 100% of disagreements while unit
  tests pass — that's "the equivalence relation is wrong," not "the
  threshold is wrong." Don't tune; re-derive the gate from the partition
  definition.
