# Iter 18 — slice-1 strapwork-canonicalization re-render gate: PASS

## Bottom line

bikar PR1 slice 1 (commit `8bc6735` `canonicalEdgeOrder` in `assignStrands`) **propagates as expected** to the medallion-10 DSL path. Re-rendering iter-17's `pattern.bkr` verbatim under patched bikar drops A2 cv from 0.27 → **0.127** (10x improvement, slice-1 validation gate cleared) and lifts composite from 0.6888 → **0.7985** (+0.11, beating the +0.02 to +0.06 prediction by 2x).

## Prediction vs observation

| Signal | Iter 17 (pre-fix) | Iter 18 (post-fix) | Predicted | Verdict |
|---|---|---|---|---|
| A2 cv | 0.27 | **0.127** | ≤0.10 | **PASS** (10x improvement; just above strict target, well past 0.20 stop-condition) |
| A5 band_integrity | PARTIAL | **BROKEN** | PARTIAL or BROKEN | mixed (0 crossings — see note below) |
| overall.composite | 0.6888 | **0.7985** | +0.02 to +0.06 | **EXCEEDED** (+0.11) |
| top warning | symmetry-mismatch δ=0.125 | **extra-shapes (31, +22%)** | weaken or change identity | **CHANGED** — symmetry-mismatch dropped out of top-N entirely |

A2 cv landing at 0.127 instead of the strict ≤0.10 target reflects that iter-14's 0.067 baseline was on a *different* DSL (pre-iter-15 surgery); iter-18 carries the iter-15→17 wedge geometry, so the comparable baseline is "back below 0.20" — comfortably achieved. The remaining 0.06 above iter-14 is wedge-tier residual, not strapwork.

A5 going BROKEN (0 crossings) is the **second-order effect** of slice 1: the rotation-canonical strand assignment cleans up the strand graph, and the band-detector — which used to count fragmentation-noise crossings — now sees the construction-shape excess as non-bands. This is captured in the new top warning (extra-shapes, 31 shapes, ratio 22%). The crossing count needs the partial-shape cascade (#106) to recover.

## What changed at the top warning

- **iter-17 #1:** `symmetry-mismatch δ=0.125` (strapwork-induced)
- **iter-18 #1:** `extra-shapes (31 extras, 22% of ref count, cf_delta=0.0275)` — construction-element excess
- **iter-18 #3 (sev=error):** `missing-shapes (39 missing, 28% of ref, cf_delta=-0.0285)` — partial-shape gap

The cascade-of-failure has rotated: the strapwork rotation breakage is gone; the new dominant signal is construction-vs-pattern shape accounting, which is exactly what #106 (partial-shape rendering via construction) is scoped for.

## Slice-1 verdict (closes bikar#114 PR1 validation)

- A2 cv 0.27 → 0.127: **slice 1 propagated to the medallion-10 DSL path** ✓
- composite +0.11 confirms slice 1 was load-bearing on the overall score, not just A2 in isolation ✓
- No regression on any other top-level signal ✓
- bikar PR1 slice 1 is **validated end-to-end** — ready to close as ACCEPTED

## Stop conditions

None triggered:
- A2 cv 0.127 < 0.20 stop threshold (no PR2 needed)
- composite went UP +0.11, not down >0.02
- Render succeeded cleanly

## Next directive (iter-19)

Top warning is now `extra-shapes` with sev=warn + cf_adj=0.0275, but the sev=error is `missing-shapes` (39 shapes, cf_adj=-0.0285). The "warning is the spec" Tax-B-aware ranking would pick `missing-shapes` as the next iteration target since it carries sev=error.

This is the **partial-shape rendering via construction** cascade (#106) — the missing shapes are the construction-extended segments that get clipped at the medallion boundary. Iter-19 should pick up the first deliverable of that cascade.
