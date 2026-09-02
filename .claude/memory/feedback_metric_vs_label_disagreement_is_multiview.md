---
name: Metric-vs-label partition disagreement is a multi-view clustering problem
description: When a metric-derived partition (TF distance) and a label/provenance-derived partition (source_primitives multiset) systematically disagree, the literature frame is "multi-view clustering with complementary views" — three named techniques apply (co-regularization, weighted combination, ensemble consensus). Web-search this frame BEFORE drafting escalation paths from local reasoning.
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
When two partitions of the same items disagree systematically (e.g.
ARI ≈ 0 even though each side has internally strong silhouette), and
one side appears to "lump" what the other "splits", the answer is
**not** to pick one side as truth or to tune a threshold to compromise.
This is **multi-view clustering with complementary views** in the
literature (Kumar/Rai/Daumé NIPS 2011 "Co-regularized Multi-View
Spectral Clustering"; the 2022 PMC8925043 Multi-View Clustering survey).

The field offers three named techniques:
- **Co-regularization** — penalize disagreement in the objective.
  Right when views *should* agree but don't (noise / measurement error).
- **Weighted combination** — fuse view-specific kernels into a single
  distance with a learnable weight. Right when views measure
  *different aspects* and disagreement is information.
- **Ensemble consensus** — publish both partitions and let downstream
  pick. Right when even a fused metric can't capture both signals.

The asymmetric "lumped-by-A" pattern (one view subsumes what the
other separates) is the canonical signature of *complementarity*,
not noise. Co-regularization makes things worse in that case;
weighted combination is the right move.

**Why:** I drafted three escalation paths for the qiyas#167 spec-gap
escalation from local reasoning before web-searching. The search
surfaced a fourth path (multi-view fusion) that's a strictly better
framing of my Path 2, with a body of literature backing the fusion
weight as a constrained optimization rather than a goal-seek tuning.
This is the same lesson as feedback_canonical_algo_web_search.md
(canonical impl > hand debug) but applied to *spec design* not just
algorithm implementation: when you're about to ask the owner to pick
between paths you invented, web-search the problem class first —
the literature may have already named your problem and ruled out
some of your paths.

**How to apply:**
- Before drafting "escalation paths" or "owner decision options" from
  local reasoning, run a 2-3 query web-search for the problem class.
  Look for the field's name for it (here: "multi-view clustering",
  "complementary views").
- If the literature distinguishes sub-cases (here: noise vs
  complementarity), match your data's signature to the right sub-case
  *before* picking a fix.
- For metric-vs-label disagreement specifically: ARI ≈ 0 + asymmetric
  lumping = complementarity = weighted-combination fix, NOT
  co-regularization or threshold tuning.
