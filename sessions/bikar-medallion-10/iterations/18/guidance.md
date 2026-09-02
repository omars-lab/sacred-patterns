# Iter 18 — slice-1 strapwork-canonicalization re-render gate

## Premise (no DSL edit)

iter-18 reuses iter-17's pattern.bkr verbatim. The only thing that changes is the bikar core: commit 8bc6735 (PR1 slice 1 of #114, bikar-strapwork-rotation-canonicalization) shipped a `canonicalEdgeOrder` helper that fixes a rotation-non-invariant strand assignment in `assignStrands`. iter-15/16/17 were polluted by this bug — A2 cv regressed from 0.067 (iter-14) to 0.27 across those three.

The validation gate for slice 1 is: re-render iter-17's DSL under patched bikar and check A2 cv drops back toward iter-14's 0.067, A5 holds PARTIAL or improves.

## Predictions

- **A2 cv:** 0.27 → expected ≤0.10 (toward iter-14's 0.067 baseline)
- **A5 band_integrity:** PARTIAL → PARTIAL (or BROKEN if 0 crossings — no change either way)
- **overall.composite_score:** 0.6888 → expected +0.02 to +0.06 from the A2 recovery
- **overall.warnings[0]:** symmetry-mismatch δ=0.125 should weaken or change identity (the symmetry breakage that produced this rationale was partly the strapwork bug)

## Stop conditions

- A2 cv stays ≥0.20 → slice-1 fix did not propagate to this DSL path. Open PR2 (explicit orbit detection, plan #113 §approach B).
- composite drops > 0.02 → unexpected regression from a "no-op" re-render. Snapshot mismatches need triage before any further iteration.
- Render fails → bikar regression. Bisect against iter-14.

## What this iter does NOT do

No new symmetry edits, no wedge-and-rotate refactor, no rhombi work. This is purely the slice-1 gate. Iter 19 picks up the next directive based on whichever signal dominates after the bug is removed.

## Cross-task

Closes the slice-2 validation gate for bikar#114. If green, unblocks qiyas#112 (hierarchical pixel-diff implementation can start). Provides the post-#536 measurement for #80's "calibration data point" success criterion.
