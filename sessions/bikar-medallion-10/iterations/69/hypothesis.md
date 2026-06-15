# Iteration 69 — Stage-2 end-of-stage palette tone pass

The ONE calibration iteration the slice verdicts deferred to (Tenet 7:
no per-slice hex nudging; a single pass against the agreed oracles).
Geometry and face-mapping UNTOUCHED — only palette hex values move.

## Hypothesis

Aligning the three divergent palette entries to their oracles — royal
and cobalt to the k=7 standardized hexes verbatim, deep_navy to the
pooled wave-plan family median — makes every recolored family read as
the reference's tone at zoom, with geometry keyset exact and census
counts identical under renamed hex buckets.

## Oracle table (every change is a read, not a tune)

| entry | current | target | oracle |
|---|---|---|---|
| royal | #2B61B7 | **#2661BF** | k=7 verbatim (`reference-analysis.md`) |
| cobalt | #32B0CA | **#3EAACC** | k=7 `cyan` cluster verbatim |
| deep_navy | #262E3D | **#3C3F47** | pooled median, 209 non-fragment family shapes (k=7 has no slate cluster — it merged into navy/navy_2; the wave-plan is the finer oracle; slice-1 verdict recorded the step-darker divergence) |
| strapwork color | #FFFFFF | **#FCFDFD** | measured lattice line, doc header |

Explicitly NOT changed (recorded per Tenet 7 — no oracle, no tune):
- navy #132A61 — already the k=7 hex verbatim.
- periwinkle #80A1E8, cyan_2 #02C5D4 — added verbatim in iter-68.
- turquoise #BBC5D5 (110 field triangles) and white #FFFFFF canvas —
  no k=7 counterpart (gray #B8B8B8 is rim/lattice blend, skipped per
  the doc); retuning them would be tuning without an oracle.
- strapwork width 8 — the doc measures 5.1px ≈ 0.688% of diameter,
  but width is a Stage-1 geometry/raster choice with its own frozen
  verdicts; out of scope for a fill-tone pass.
- `edges color deep_navy` (width 0.2, near-invisible) inherits the new
  deep_navy hex — accepted, it sits under the strapwork bands.

## Predictions (gates)

1. **Geometry keyset (params excluded)**: 0 missing, 0 new, 675/675.
2. **gt fill census**: pure bucket renames, counts exact —
   #262E3D 210 → **#3C3F47 210**; #2B61B7 51 → **#2661BF 51**;
   #32B0CA 30 → **#3EAACC 30**; #132A61 111, #80A1E8 10, #02C5D4 10,
   #BBC5D5 110, #FFFFFF 1, circles 142 unchanged; total 675.
   Param deltas confined to exactly 291 faces (210+51+30), fill_color
   only — face_class unchanged on every record.
3. **Holds (per-color band, slice-4 lesson)**: deep_navy family waves
   (w2/w4/w7/w10/w11/w15/w16/w19/w21) may move ≤0.5pt — the new R=60
   raises the AA α-threshold from 0.253 to 0.283; royal (w14/w18) and
   cobalt (w5/w13) ≤0.3pt; flower-zone neighbors whose windows overlap
   ±0.3; strapwork #FFFFFF→#FCFDFD stays above NEAR_WHITE_MIN=200 on
   all channels → contributes zero mask change; all other waves
   bit-identical.
4. **Eyeball (Tenet 26, pre-stated)**: at the w15/w2 zoom the slate
   family now reads the reference's gray-slate (#3C3F47 vs the old
   too-black #262E3D — the gap slice 1 recorded closes); royal and
   cyan tiles shift subtly (ΔRGB ≤ 12 each channel) toward the
   reference's tone; the full render side-by-side against the
   reference reads as the same palette family-for-family. Delta-tint:
   ~291 components (the three renamed families) + possibly the
   strapwork bands at |Δ|=2-3 (below the >10 tint threshold → NOT
   tinted), nothing else.

---

## VERDICT — TONE PASS SHIPS — iteration 69 FROZEN

1. **Geometry keyset (params excluded): EXACT** — 675/675, 0 missing,
   0 new.
2. **gt fill census: EXACT** — pure bucket renames at exact counts:
   #262E3D 210→**#3C3F47 210**, #2B61B7 51→**#2661BF 51**,
   #32B0CA 30→**#3EAACC 30**; #132A61 111, #80A1E8 10, #02C5D4 10,
   #BBC5D5 110, #FFFFFF 1, circles 142 unchanged; total 675. Param
   deltas confined to exactly **291 faces, fill_color only** — zero
   face_class changes anywhere.
3. **Holds: prediction-3 MAGNITUDES FALSIFIED on the slate family;
   regression gate PASSES.** Royal (w14/w18) and cobalt (w5/w13)
   stayed inside ≤0.3 ✓. Slate-family movers exceeded the ≤0.5 band:
   **w10 cov −2.6, w21 −0.8, w2 −0.7** (others in-band). Mechanism as
   predicted (R 38→60 raises the binding AA α-threshold 0.253→0.283,
   widening the near-white edge band the ink mask loses) — the
   magnitude model is what failed, worst on **small high-perimeter
   tiles** (w10's teardrops). This is the slice-4 lesson recurring one
   color family later: Δα alone doesn't size the move; perimeter/area
   of the recolored tiles multiplies it. **iou improved broadly
   (+0.2…+1.2 across most windows)** — the expected sign that the
   tone alignment moves the render toward the reference. Adjudication
   that the coverage dips are raster-only: gate 1 keyset exact (zero
   geometry deltas) + gate 4 tint confinement (every changed pixel
   sits in a renamed-family tile interior or its AA edge).
4. **Eyeball (Tenet 26/27) PASS** — full side-by-side
   (`eyeball-full-ref-vs-render.png`): reads family-for-family
   against the reference — navy field, royal outer band, cobalt/cyan
   accents, periwinkle inner flower, bright cyan_2 interstices, white
   lattice. w15/w2 zoom (`eyeball-w15-w2-ref-vs-render.png`): the
   slate family reads gray-slate matching the reference picks at the
   same zones (**#373B43 / #42454D — straddling the shipped pooled
   median #3C3F47**); the slice-1 too-black gap is closed. Delta-tint
   (`render-delta-tint.png`): **1641 components / 171,378 px**, NOT
   the predicted ~291 — explained, not alarming: royal's
   ΔRGB=(−5,0,8) sits mostly BELOW the >10 tint threshold, so royal
   tiles tint only in partial fragments (fragmenting component
   count), and AA edge rings split tile interiors into multiple
   components. Pixel mass is dominated by the two big honest renames:
   old-cobalt (50,176,202) 66k px and old-deep_navy (38,46,61) 51k px.
   The ~2.7k near-white px (253-254,*,*) are AA edge pixels at
   recolored-tile/strapwork boundaries where the #FFFFFF→#FCFDFD
   strapwork shift (|Δ|≤3, sub-threshold alone) compounds with the
   adjacent tile recolor to cross the threshold — confined to band
   edges, zero band-interior tinting. Confinement holds: no tinted
   pixel outside renamed-family tiles + their AA borders.

**Stage-2 COLOR IS COMPLETE.** Face-mapping (slices 1–4, iters
65–68) + this tone pass: deep_navy 210 @ #3C3F47, cobalt 20 + 10
field pockets @ #3EAACC, royal 30 + 21 field squares @ #2661BF,
periwinkle 10 @ #80A1E8, cyan_2 10 @ #02C5D4, navy 111 @ #132A61,
turquoise field 110, white canvas 1, strapwork #FCFDFD. w8/w12
band-rerouting items are separate (geometry, not color).

## Review-portal verdict (Tenet 27) — RECORDED

Session: `qiyas/out/review/render.svg-1b88a5e4/` (iter-69 render.svg
vs `input/reference.jpg`). **The review-readiness gate PASSED at
registration: pixel similarity 80.5% — first campaign render to
clear the 80% expert-review floor without `--force`.** Compare
artifacts (`compare/diff-visual.png`, `diff-heatmap.png`) viewed
against the pre-stated expectation (differences concentrate on
lattice width + photo cast + registration edges, NOT family-level
color): CONFIRMED — heatmap is edge-dominated, tile interiors
low-diff; the diff-visual's 19.4% render-only ink is lattice-overlap
webbing + the outer rim ring. The machine's asymmetric-channel-drift
warning (r=63.8 vs b=35.1) is adjudicated as that same band-width
overlap (blue ink against near-white lattice maximizes the r-diff),
not a wrong palette family. Verdict in `annotations.json`: 7 entries
— six `color_wrong` **right** (one per family: deep_navy_wave,
royal_wave, cyan_wave, periwinkle_wave, cyan2_wave, navy field), one
`style_wrong` **wrong** on `band_width` (white lattice proportionally
wider in the reference; disposition=backlog, rides with the w8/w12
geometry items).
