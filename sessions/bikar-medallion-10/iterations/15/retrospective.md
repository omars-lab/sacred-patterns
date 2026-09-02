# Iter 15 — retrospective

## What I changed

Single edit to iter-14's pattern.bkr: added `strapwork width 5 crossing alternating` block before `voids detect`. Everything else byte-for-byte identical.

## What I expected vs what happened

| | Expected | Actual |
|---|---|---|
| A5 status | BROKEN → COMPLETE | BROKEN → PARTIAL (only one notch) |
| A5 crossings | 17 → ~45 | 17 → 30 |
| composite | +0.05 to +0.10 | −0.124 (regression) |
| A2 cv | unchanged | 0.067 → 0.1325 (degraded) |
| extra-shapes | mild rise OK | +149 (185 unmatched) |

Predicted Δcomposite +0.05–0.10, actual −0.124. Major over-estimation.

## Why the prediction was wrong

The prediction model assumed: "A5 BROKEN→COMPLETE moves svg-audit 2/5→3/5, ~+0.10 composite." Two errors in that model:

1. **A5 advancement was only one notch** (BROKEN→PARTIAL = same svg-audit binary score), not two. Strapwork at width 5 with `crossing alternating` produces 30/45 crossings — bands cross at the right *positions* but the alternating mode skips some intersections, leaving 15 crossings unrendered.

2. **The model ignored the side-effect on extra-shapes count.** Each strapwork band-pair fragments existing voids into more, smaller polygons. Recon went from ~150 shapes to 343. The 185 unmatched extras drove `extra-shapes` warning δ=0.2176 — well past the predicted +0.10 audit gain. Composite drop is dominated by this single warning.

3. **A2 symmetry degradation was not modeled.** `crossing alternating` over a 10-fold pattern produces 5 over + 5 under per ring of crossings. That is not 10-fold symmetric — it's 2-fold within each crossing and 5-fold across rings. Sector totals diverge (CV 0.067 → 0.1325). A2 went from UNEVEN to MORE UNEVEN.

## What this teaches the meta-loop

**For the BIKAR translation table** (qiyas-warning → DSL idiom): "A5 BROKEN, X/45 crossings" should NOT be naively translated to "add strapwork width N crossing alternating". The translation needs to account for:
- crossing-mode symmetry compatibility with the pattern's n-fold (alternating breaks 10-fold; need a rotational variant)
- void fragmentation cost (each band-pair adds ~10 small shapes per ring; multiplies recon shape count)

**For the warning ranker (qiyas#75 calibration data):** the `A5 BROKEN` warning predicted COMPLETE-on-fix counterfactual_score_delta of ~0.10; actual gain was a NEGATIVE 0.124 due to a side-effect (extra-shapes spike) the counterfactual transformer didn't model. **This is a calibration data point worth recording: warnings that recommend fragmenting/adding-detail edits need a "fragmentation tax" estimator that lowers their predicted lift.**

**For iter 16 directive:** REVERT to iter 14. Do NOT continue stacking on iter 15. Two options for iter 16:
- (a) Try strapwork with a *symmetry-preserving* crossing mode (e.g. all-over or all-under, or `crossing rotational` if bikar supports it). Lower A5 ceiling but no A2 cost.
- (b) Drop strapwork; pursue the next non-A5 blocker. The new top warning post-revert (back at iter-14 state) is `inner-star--star-v8 MISSING` per iter-14 evaluation. That belongs to plan #106 (partial-shape construction) which is multi-week — not the next iter directive.

Recommendation: (a) — try `crossing over` or `crossing under` (constant, not alternating) to preserve 10-fold symmetry while keeping the +1.2% pixel gain and A5 PARTIAL. If bikar lacks a non-alternating mode, file as a bikar issue and pivot to (b).

## Findings to capture (Phase 1.5)

- **bikar/skill** (translation table gap): "A5 BROKEN, X/Y crossings" needs nuance — crossing-mode must be symmetry-compatible with n-fold. Recommend appending row to `iterate-pattern-from-qiyas-warnings/SKILL.md` with the iter-15 evidence.
- **qiyas calibration** (warnings#75 data point): A5-BROKEN counterfactual_score_delta over-estimates by ignoring void-fragmentation tax. Record actual=−0.124 vs predicted=+0.10 for iter 14→15.
- **qiyas/bikar issue** (new, since this is the SECOND calibration miss in two iterations): A6-MISSING (iter 14) and A5-BROKEN (iter 15) both over-estimated lift. Pattern is clear — counterfactual transformer assumes warnings are *additive* and ignores construction interactions. File as qiyas issue: "counterfactual transformer needs side-effect modeling for fragmentation/interaction edits."
- **bikar issue** (potentially): does `strapwork crossing alternating` have a symmetry-preserving variant? If not, that's a bikar feature gap.
