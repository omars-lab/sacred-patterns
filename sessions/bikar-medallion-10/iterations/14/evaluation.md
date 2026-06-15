# Iter 14 — evaluation

## Headline

**composite_score 0.7632 → 0.7842 (+0.021)** — predicted +0.05 to +0.08, actual +0.021. Below predicted but real positive delta.

## Per-metric comparison

| Metric | iter 13 | iter 14 | Δ |
|---|---|---|---|
| composite_score | 0.7632 | 0.7842 | +0.021 |
| structural_score | 1/18 | 1/18 | 0 |
| pixel_similarity | 74.1% | 74.1% | 0 |
| svg-audit score | 2/5 | 2/5 | 0 |
| A6_pass_ratio | 0.056 (1/18) | 0.056 (1/18) | 0 |
| A2 cv | 0.067 | 0.067 | 0 |
| A5 crossings | 13/45 | 17/45 | +4 |
| missing-shapes count | 53 | 45 | −8 (improved) |

## Goal vs reality

**Goal:** turn `inner-star--rhombus-v4` from MISSING (0/10) → PASS by overlaying `connect every 3 on C1` on top of the existing `connect every 4 on C1`.

**Reality:** rhombus-v4 stayed MISSING (0/10). The {10/3} overlay did add edges that intersect the {10/4} edges, but the void detector classified the resulting faces as more `polygon-v0` (no specific vertex count) rather than discrete 4-vertex rhombi.

## What worked

1. **`inner-star--polygon-v0`: PARTIAL (19/21) → PASS (21/21).** The new edges filled in 2 missing 0-vertex polygons. One A6 verdict moved to PASS (offset by another that regressed — see below).
2. **A5 crossings: 13 → 17 (+4).** The {10/3} edges create new intersection points, increasing the band-network crossing count. Still well short of expected 45, but moving in the right direction.
3. **missing-shapes total: 53 → 45 (−8).** Some of the new edges produced shapes that match ref classifications.
4. **composite +0.021.** Real positive delta from these incremental gains.

## What didn't work

1. **Rhombi did not form as discrete 4-vertex faces.** The hypothesis was that {10/4} ∩ {10/3} → 10 rhombic regions classified as `rhombus-v4`. Instead, the void detector broke them into smaller polygon-v0 pieces or merged them into adjacent regions.
2. **`inner-star--star-v6`: EXCESS (7/2) → MISSING (0/2).** The {10/3} edges fragmented the existing 6-vertex stars into smaller polygon pieces, eliminating the v6 candidates that previously existed (even though they were over-count).
3. **structural_score unchanged at 1/18.** One PASS gained, one PASS lost (net zero on the rollup). The shifts net to a wash.
4. **extra-shapes count: 27 → 36.** New edges created 9 more "extra" shapes not present in the ref, partially offsetting the missing-shapes improvement.

## Verdict

Net positive (+0.021 composite, +4 band crossings, +1 A6 PASS class), but the headline goal (close rhombus-v4) failed because the void detector's face-finding doesn't naturally produce v4 rhombi from a {10/4}+{10/3} overlay.

KEEP iter 14 (positive delta). For iter 15, abandon the dual-star-on-same-circle approach for rhombi; pursue a direct construction (e.g., explicit `connect cycle` defining a rhombic wedge then `rotate 10`) or shift to a different blocker (A5 bands needs ~28 more crossings; that's likely the highest-leverage next gap).
