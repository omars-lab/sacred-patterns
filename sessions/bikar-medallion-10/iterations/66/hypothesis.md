# Iteration 66 — Stage-2 color, slice 2: the cyan wave family (w5 + w13)

Second Stage-2 iteration. Geometry UNTOUCHED; same layer-as-color-family
mechanism proven in iter-65.

## Hypothesis

Wrapping the w5 arrowheads and w13 teardrops in `layer 3` with one new
fill rule (`fill void where layer == 3 color cobalt`) flips exactly the
20 family tiles from navy #132A61 to cobalt #32B0CA — matching the
reference's saturated-cyan tiles in those zones — with geometry keyset
exact and holds within the slice-1-calibrated AA band.

## Family adjudication (Tenet 6 — the hex is the truth, not the label)

Re-measured from `wave-plan.json` per-shape hexes this iteration:

- **w13's wave-color label says "turquoise" but its median hex is
  #49B3CB** — saturated cyan, sitting next to the k=7 standardized
  `cyan` cluster #3EAACC (`input/reference-analysis/reference-analysis.md`)
  and far from our pale `turquoise` palette entry #BBC5D5. The plan's
  own per-shape labels are split (4 turquoise / 6 cyan): the labeler
  couldn't separate them; the measurement can. **w13 is cyan family.**
- w5 median #52A1C4 — also the cyan cluster. **Slice 2 = {w5, w13}.**
- w9 median #19C3D0 ≈ the distinct `cyan_2` cluster #02C5D4 — brighter
  glaze, NOT this slice (needs its own palette entry; slice 3).

Tile counts: w5 10 + w13 10 = **20 tiles**, each a single 6-vert
rotate-10 cycle → 20 faces.

**Palette-wide finding (recorded, deferred):** the standardized palette
doc says "Stage 2 palette blocks use these hex values verbatim", but the
current .bkr palette hexes (cobalt #32B0CA, royal #2B61B7, deep_navy
#262E3D, turquoise #BBC5D5) predate it and diverge from both the k=7
clusters and the wave-plan medians (e.g. deep_navy renders darker than
the measured ~#3D4047 slate; the k=7 table has no slate cluster at all —
it merged into navy/navy_2). Per the slice-1 verdict, tone calibration
is ONE end-of-stage pass against the swatch sheet + wave-plan medians —
slices map faces to families; they do not retune hexes (Tenet 7 spirit:
no per-slice constant nudging).

## Mechanism

Same as iter-65 (see that hypothesis for the bikar-source verification
and rejected alternatives): wrap both cycles in `layer 3` … `layer 1`;
add `classify .cyan_wave where layer == 3` (gt-emitter drop guard);
add `fill void where layer == 3 color cobalt` to the leading cascade.
Pattern name → `medallion10_iter66`.

## Predictions (gates)

1. **Geometry keyset (params excluded)**: 0 missing, 0 new across all
   675 records.
2. **gt fill census**: #132A61 181→**161**, #32B0CA 10→**30**;
   #262E3D 210, #BBC5D5 110, #2B61B7 21, #FFFFFF 1, circles 142
   unchanged; total 675. Param deltas confined to exactly the 20 family
   faces; face_class .center_star→**.cyan_wave** for all 20 (lex-first:
   "cyan_wave" sorts before the co-stamped "navy" sides>=6 class).
3. **Holds (slice-1-calibrated band, not bit-identical)**: w5 and w13
   may move ≤0.3pt (cobalt's high G/B channels tip MORE AA edge pixels
   over NEAR_WHITE_MIN than navy did — expect small coverage drops);
   adjacent-window neighbors (w4/w6/w12/w14) ±0.1; all other waves
   bit-identical.
4. **Eyeball (Tenet 26, pre-stated)**: the 10 arrowheads (mid ring,
   star-tip axes) and 10 teardrops (outer-mid, star-tip axes) read as
   the same saturated cyan as the flower pockets, distinct from navy
   neighbors — matching the reference's cyan tiles in the same zones;
   render delta confined to ~20 tile interiors, zero change elsewhere.

---

## VERDICT — SLICE 2 PASSES — iteration 66 FROZEN

1. **Geometry keyset (params excluded): EXACT** — 675/675, 0 missing,
   0 new.
2. **gt fill census: EXACT** — #132A61 181→161, #32B0CA 10→30, all
   other buckets unchanged. Param deltas confined to exactly 20 faces,
   fill #132A61→#32B0CA, face_class .center_star→.cyan_wave on all 20
   (lex-first prediction correct this slice).
3. **Holds: PASS inside the calibrated band** — 19/22 bit-identical;
   w5 −0.1 cov, w13 −0.1 cov (the recolored waves), w4 +0.1 iou
   (adjacent window). Nothing outside ±0.1; band model from slice 1
   confirmed on its first reuse.
4. **Eyeball (Tenet 26/27) PASS** — render-delta-tint.png: exactly
   **20 components**, old color (19,42,97)=navy, new (50,176,202)=
   cobalt, two 10-fold rings on star-tip axes (arrowheads mid-ring,
   teardrops outer-mid), zero change elsewhere.
   eyeball-w5 / eyeball-w13 ref-vs-render crops: both families read
   as the reference's saturated cyan in the same zones. Tone note:
   cobalt #32B0CA vs measured medians #52A1C4/#49B3CB — same family,
   slight saturation difference, deferred to the end-of-stage palette
   pass with the rest.

**Slice 2 complete: w5 + w13 are cobalt (cyan family).**
Remaining Stage-2 face-mapping: slice 3 royal {w14, w18} (existing
palette entry, zero hex changes); slice 4 periwinkle {w3} + cyan_2
{w9} (two NEW palette entries — verbatim k=7 standardized hexes
#80A1E8 / #02C5D4, which is reading the agreed target, not tuning);
then the end-of-stage palette tone pass + review-portal verdict.
w8/w12 band-rerouting items are separate (geometry, not color).
