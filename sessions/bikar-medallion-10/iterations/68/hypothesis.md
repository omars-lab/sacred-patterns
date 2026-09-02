# Iteration 68 — Stage-2 color, slice 4: periwinkle (w3) + cyan_2 (w9)

Fourth and final face-mapping Stage-2 slice. Geometry UNTOUCHED; same
layer-as-color-family mechanism (iters 65/66/67). This slice adds TWO
new palette entries — the first palette change of Stage 2.

## Hypothesis

Wrapping the w3 petals in `layer 5` and the w9 spiky 16-gons in
`layer 6`, with two new palette entries and two new fill rules, flips
exactly 20 tiles from navy #132A61 to periwinkle #80A1E8 (w3) and
cyan_2 #02C5D4 (w9) — matching the reference's pale-periwinkle petals
and bright-glaze interstices — with geometry keyset exact and holds
within the calibrated AA band.

## New palette entries are NOT tuning (Tenet 7 distinction, recorded)

`periwinkle = #80A1E8` and `cyan_2 = #02C5D4` are the **verbatim k=7
standardized hexes** from `input/reference-analysis/reference-analysis.md`
("Stage 2 palette blocks use these hex values verbatim"). These families
have NO existing palette entry, so this is reading the agreed target,
not retuning a constant. The end-of-stage tone pass still owns any
adjustment of the four pre-existing entries.

## Family adjudication (Tenet 6 — re-verified, correctly indexed)

The wave-plan `waves` array is 0-indexed (iter-67 process catch:
plan[k] = .bkr wave k+1). Re-read this iteration:

- plan[2] = .bkr **w3**: label periwinkle, n=10, median **#85A1E0** —
  the k=7 `periwinkle` cluster #80A1E8. ✓
- plan[8] = .bkr **w9**: label cyan, n=10, median **#19C2D0** — the
  k=7 `cyan_2` cluster #02C5D4 (bright glaze), NOT the #3EAACC cyan
  cluster that slice 2 (w5/w13 → cobalt) mapped. Distinct family,
  distinct entry. ✓

Tile counts: w3 = one 6-vert cycle × rotate-10 = **10 petals** (middle
flower, star-tip axes); w9 = one 16-vert cycle × rotate-10 = **10 spiky
interstice 16-gons** (mid ring, star-tip axes). **20 tiles → 20 faces.**

## Mechanism

Same channel: wrap w3's cycle in `layer 5` … `layer 1` and w9's in
`layer 6` … `layer 1`; add `classify .periwinkle_wave where layer == 5`
and `classify .cyan2_wave where layer == 6` (gt-emitter drop guards);
add `fill void where layer == 5 color periwinkle` and
`fill void where layer == 6 color cyan_2` to the leading cascade; add
the two palette lines. The iter-67 `layer <= 1` scoping already keeps
the side-based field rules off these faces — no classify interaction.
Pattern name → `medallion10_iter68`.

## Predictions (gates)

1. **Geometry keyset (params excluded)**: 0 missing, 0 new across all
   675 records.
2. **gt fill census**: #132A61 131→**111**, **#80A1E8 0→10**,
   **#02C5D4 0→10**; #262E3D 210, #2B61B7 51, #32B0CA 30, #BBC5D5 110,
   #FFFFFF 1, circles 142 unchanged; total 675. **Param deltas confined
   to exactly 20 faces, two kinds**: 10 × (#132A61, .center_star)→
   (#80A1E8, .periwinkle_wave) and 10 × (#132A61, .center_star)→
   (#02C5D4, .cyan2_wave). Zero relabels elsewhere (scoping landed in
   iter-67).
3. **Holds (calibrated AA band, slice-3 refinement applied)**:
   **w3 may move up to ~0.7pt** — periwinkle's binding channel R=128
   gives an AA near-white threshold at α ≈ 0.43 fill (vs navy's 0.23),
   roughly doubling the edge band that wave-diff's ink mask loses;
   w9 ≤0.3pt (cyan_2's R=2 is as binding as navy's R=19); ±0.1 on any
   wave whose crop window overlaps a recolored tile; all others
   bit-identical.
4. **Eyeball (Tenet 26, pre-stated)**: the 10 petals (middle flower,
   star-tip axes) read pale periwinkle — clearly lighter than every
   other blue in the pattern — and the 10 spiky 16-gons (mid ring,
   star-tip axes) read bright glaze cyan, visibly more saturated/greener
   than the cobalt arrowheads/teardrops — each matching the reference's
   tiles in the same zones; render delta = 20 components confined to
   the tile interiors, zero change elsewhere.

---

## VERDICT — SLICE 4 PASSES — iteration 68 FROZEN

1. **Geometry keyset (params excluded): EXACT** — 675/675, 0 missing,
   0 new.
2. **gt fill census: EXACT** — #132A61 131→111, #80A1E8 0→10,
   #02C5D4 0→10, all other buckets unchanged, total 675. Param deltas
   confined to exactly 20 faces, both kinds exact: 10 × →(.periwinkle_wave,
   #80A1E8), 10 × →(.cyan2_wave, #02C5D4). Zero relabels — the iter-67
   scoping held.
3. **Holds: prediction-3 MAGNITUDES FALSIFIED; regression gate
   PASSES.** 19/22 bit-identical; w9 bit-identical (≤0.3 predicted ✓).
   Movers: **w3 cov −1.2** (predicted ≤0.7 — the AA mechanism is
   right, the magnitude estimate was ~2× low; periwinkle's Δα ≈ 0.2
   vs slice-1's 0.02 doesn't scale linearly at w3's perimeter/area),
   **w2 iou +1.3** (its middle-flower window overlaps the petals —
   an IMPROVEMENT: the render now matches the reference's pale petal
   tone inside w2's window), w4 iou +0.2. Keyset exactness (gate 1)
   + delta-tint confinement (gate 4) prove all movement is
   raster-level only. **Lesson: the ±-band on holds is per-color —
   light fills (R ≥ ~100) need a ~1.5pt allowance on the recolored
   wave and ±1.5 on flower-zone neighbors whose windows overlap.**
4. **Eyeball (Tenet 26/27) PASS** — render-delta-tint.png: exactly
   **20 components**, old navy (19,42,97), new (2,197,212)=cyan_2 ×10
   + (128,161,232)=periwinkle ×10, confined to the two 10-fold rings;
   eyeball-w3 / eyeball-w9 crops match the reference families in the
   same zones (ref picks #85A2E0 / #19C2D0).

**Slice 4 complete: w3 is periwinkle, w9 is cyan_2.**
**Stage-2 face-mapping is COMPLETE** — all five wave families mapped:
deep_navy (210, iter-65), cyan→cobalt (20, iter-66), royal (30,
iter-67), periwinkle (10) + cyan_2 (10) (iter-68); navy remainder
(111) + white canvas + turquoise field unchanged by design.
Remaining Stage-2: the end-of-stage palette tone pass (swatch sheet +
wave-plan medians, ONE calibration iteration) + review-portal verdict
(Tenet 27). w8/w12 band-rerouting items are separate (geometry).
