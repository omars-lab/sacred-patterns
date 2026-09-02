# Iter 15 — evaluation

## Headline

**composite_score 0.7842 → 0.6604 (−0.124)** — predicted +0.05 to +0.10, actual −0.124. Net regression beyond stop threshold.

## Per-metric comparison

| Metric | iter 14 | iter 15 | Δ |
|---|---|---|---|
| composite_score | 0.7842 | 0.6604 | −0.124 |
| structural_score | 1/18 | 1/18 | 0 |
| pixel_similarity | 74.1% | 75.3% | +1.2 |
| svg-audit score | 2/5 | 2/5 | 0 |
| A6_pass_ratio | 0.056 (1/18) | 0.056 (1/18) | 0 |
| A2 cv | 0.067 | 0.1325 | +0.066 (worse) |
| A5 crossings | 17/45 | 30/45 | +13 (better) |
| A5 status | BROKEN | PARTIAL | ↑ |
| total shapes (recon) | ~150 | 343 | +~190 |
| extra-shapes (vs ref) | 36 | 185 | +149 (worse) |

## Goal vs reality

**Goal:** add `strapwork width 5 crossing alternating` to convert bare lines into interlaced bands. Predicted: A5 BROKEN→COMPLETE, composite +0.05–0.10.

**Reality:** strapwork *did* render — A5 advanced BROKEN→PARTIAL with 30/45 crossings (+13). But the parallel band-pair fragmentation produced 185 unmatched "extra" shapes (band-segment polygons that don't appear in the reference's traced encoding). The extra-shapes warning δ=0.2176 dominates the rollup, eclipsing the A5 gain.

## What worked

1. **A5 advanced one notch:** BROKEN → PARTIAL, crossings 17 → 30 (still short of 45 target).
2. **Pixel similarity rose +1.2%** — bands cover area that was previously bare, so per-pixel match improved.

## What didn't work

1. **343 vs ~150 shapes** — strapwork doubled the recon's shape count. The reference's traced encoding has ~225 shapes; recon has 343, leaving 185 unmatched "extra" (counted against composite).
2. **A2 symmetry regressed** — CV 0.067 → 0.1325 (UNEVEN got worse). Alternating over/under crossings are NOT 10-fold symmetric in the simple `crossing alternating` mode.
3. **Structural unchanged** at 1/18 — A5 only PARTIAL, no PASS class flipped.
4. **Extra-shapes warning leaped** δ=0.2176 — overwhelms A5's small structural gain. Composite drop −0.124 == extra-shapes-cost (~0.21) − pixel-gain (~0.01) − A5-partial-gain (~0.07).

## Verdict

**REVERT.** Net regression −0.124 exceeds the iter-14 stop-threshold pattern (−0.02). KEEP iter 14 as the latest accepted baseline.

For iter 16, fork from iter-14's pattern.bkr (NOT iter-15). Either:
- (a) Try strapwork with a *different* crossing mode that preserves 10-fold symmetry (e.g. `crossing rotational` if bikar supports it), OR
- (b) Drop strapwork entirely and chase a different blocker — A6 has 17 MISSING/PARTIAL shapes; iter 14's `inner-star--star-v6` regressed (EXCESS→MISSING) and could be recovered by removing the {10/3} addition or by a more targeted construction.
