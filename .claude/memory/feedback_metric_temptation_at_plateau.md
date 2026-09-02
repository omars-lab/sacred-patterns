---
name: metric-temptation-at-plateau
description: "When a score plateaus, the reflex to raise counts / tune a constant / over-fit a fixture is the exact moment Tenet 7 governs — name the root cause you are NOT fixing before touching any threshold."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 346af4f5-c695-4afc-832d-ec66056fd627
---

A plateau in a convergence metric (qiyas composite/ARI, pixel-similarity, A6 PASS count) is the moment the reflex fires: raise shape counts to force agreement, widen a tolerance, soften a confidence formula, over-index a test on one fixture. That reflex is exactly what Tenet 7 (don't tune constants to make a test green) and Tenet 21 (full-suite, not a corpus subset, for a constant tweak) govern — but the tenet names the *rule*, not the *trigger-moment*. The plateau IS the trigger-moment.

**Why:** Retrospective mistake M6 (`docs/retrospectives/2026-06-06-image-to-dsl-retrospective.md` §4) recurred *despite* Tenet 7 already existing — the owner had to intervene twice in a single window (04-28→04-30): raising shape counts to force metric agreement, and tests over-fit to one fixture. The tenet was stated and still ignored, because a plateau applies pressure precisely when the rule is most tempting to break. M6 is one of the "acting on an unverified belief" family (with M1 premise-skip and M2 stale-claim) — here the unverified belief is "the metric reading is the problem, so move the metric." The 2026-05-07 petal-6 doc was SUPERSEDED on exactly this: the gap was a stale fixture, not the metric.

**How to apply:** at any plateau, BEFORE touching a threshold/constant/count, write down in one line the **root cause you are NOT fixing** by moving the metric. If you can't name a structural cause the tweak would mask, the tweak is goal-seeking — stop. If you've tweaked the same constant/formula twice for one failing case, that's the Tenet 7 stop rule: either the case is known-deferred (`xfail`/`skip` with a doc ref) or the spec is wrong for a structural reason that needs a write-up first. Constants change only after two independent fixtures (one to fit, one to judge) + a written rationale naming the noise floor absorbed. Per Tenet 27, a green metric is necessary-not-sufficient; the plateau is when it most tempts you to skip the review-portal look.

**Companion to:** tenets 7 (don't tune to fit), 8 (solve the general problem), 17 (prove the primitive first), 21 (full-suite acceptance for constant tweaks), 27 (no ship without portal verdict), and C1 via [[validate-premise-before-options]] (the plateau's premise — "the metric is the problem" — is itself a premise to validate). Sibling of [[adjudicate-missing-items-via-git-before-loadbearing]] in the "verify the belief before acting on it" family.
