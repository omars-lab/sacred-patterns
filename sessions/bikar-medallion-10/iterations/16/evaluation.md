# Iter 16 — Evaluation

## Verdict: REVERT to iter 14

| Metric | iter 14 | iter 15 | iter 16 | Δ vs 14 |
|---|---|---|---|---|
| composite_score | 0.7842 | 0.6604 | **0.6089** | **−0.175** |
| pixel_similarity | n/a | n/a | 75.1% | — |
| structural_score | n/a | n/a | 1/18 | — |
| A1 (census) | PASS | PASS | PASS | = |
| A2 cv | 0.067 | 0.1325 | **0.2671** | +0.20 (worse) |
| A2 status | OK | (cv-only) | **BROKEN** | regression |
| A4 coverage | FULL | FULL | FULL (549%) | = |
| A5 bands | BROKEN | PARTIAL | PARTIAL | improved one notch |
| A6 pass ratio | n/a | n/a | 1/18 (5.6%) | — |
| extra shapes vs ref | n/a | 185 | **247** | worse |

## Plan #108 hypothesis: FALSIFIED

The plan predicted `crossing over` would preserve A2 cv (~0.067) because uniform over-strands are rotationally invariant. Reality: A2 cv almost **doubled again** (0.1325 → 0.2671) and A2 went from cv-only to fully BROKEN.

**Why the prediction was wrong (best current hypothesis):**

The prediction assumed that the *over/under choice* was the only rotation-symmetry-breaking lever. It isn't. The strand-tracing algorithm in `bikar/packages/core/src/kernel/strapwork.ts` (`assignStrands`) walks edges in graph-traversal order — that order is **not rotationally invariant** when crossings are not strictly local. Setting all `isOver=true` removes the alternation toggle but does not change which edges get grouped into the same strand or how strand IDs are assigned across sectors. The 247 extras (vs iter-15's 185) suggest the band-rendering geometry itself is being thrown off by something that changes between sectors.

This is exactly the failure mode plan #109 (counterfactual fragmentation tax) was designed to surface — qiyas's `extra-shapes` warning ranked rank-1 with cf_delta=0.2253, which dominates everything else. The "small A5 lift" that plan #108 expected to be a worthwhile tradeoff turned into a 0.175 regression.

## Top warnings (qiyas ranked)

1. `extra-shapes` (error, cf_delta=0.2253): 247 extras, 178% of ref count
2. `missing-shapes` (warn, cf_delta=0.0131): 14 missing
3. `high-param-drift` (warn, cf_delta=0.0019): worst pair drift 0.69

The structural rollup is dominated by `extra-shapes` for the second iteration in a row. The strapwork block, in any of its three crossing modes, is producing fragments that flood the recon shape pool.

## Decision

**REVERT to iter 14.** Strapwork in its current form (any crossing mode) costs ~0.18 composite even when it improves A5. The right next move is NOT to keep iterating on crossing-mode variants — the cost isn't in crossing, it's in band rendering producing closed-form fragments that qiyas pairs as extras.
