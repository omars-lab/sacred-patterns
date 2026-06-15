# Iteration 38 — visual verdict (2026-06-10)

## Numbers

| metric | iter-37 | iter-38 (final) | predicted |
|---|---|---|---|
| pixel similarity | 74.2% | **74.2%** (±0, ties high) | +0.5–1.5 |
| color match | 66.8% | **67.8%** (+1.0) | "should rise more than pixel" ✓ |
| gt.json shapes | 844 | 814 | — |

## Predicted vs actual — honest read

The halved gut number STILL over-predicted pixel similarity (+0.5–1.5
predicted, ±0 actual) — but for a measured reason, not a vibe miss. The
first full render (all three remaps) scored **73.3 (−0.9)**, and a
three-way single-change ablation isolated the cause:

| remap alone (vs iter-37) | sim | color |
|---|---|---|
| kites royal→navy | **73.3 (−0.9)** | 67.3 |
| big pentagons cyan→royal | 74.2 (±0) | 67.1 |
| lens pockets →cyan | 74.1 (−0.1) | 67.4 |

**The kite remap was the entire regression and is REVERTED.** Its
center-sample evidence (navy 50/120 vs royal 8/120) lied at face-area
granularity: a kite's center may sit on a navy ref pixel while most of its
area overlaps the reference's white lattice — exactly the hypothesis's
named risk 1 ("kites going navy may read darker than the reference's key").
Method lesson recorded: **center sampling validates color direction; only
an area-weighted sample (or the ablation render itself) validates a remap.**

Shipped iter-38 = pentagons + pockets only: the lens zones now carry
saturated cyan pocket faces and the big pentagons read royal, both visible
in the render and consistent with the pre-stated expected visual. Color
match improved a full point with zero pixel cost.

## Next-gap routing

1. **Pixel-similarity plateau at ~74 is now structural, not chromatic.** Two
   color passes (36, 38) moved color-match +2.6 total while pixel similarity
   gained only via iter-37's geometry. The remaining ~6-point gap to the 80%
   review gate lives in shape disagreement: the reference's pocket-stars are
   STARS (small 5/6-point motifs inside each lens), while our lenses hold 3
   plain hexagon-motif faces. The candidate construction fix is decorating
   the lens hexagon with a star motif (girih hexagons historically carry
   them) — an engine/DSL question first: does the hexagon tile's decoration
   support a star variant, or is that a new decoration table entry?
2. **Boundary ring: scalloped vs rounded** (carried since iter-36).
3. **Per-role color via portal Q7** (carried — adjudicated after the 80%
   gate clears).
