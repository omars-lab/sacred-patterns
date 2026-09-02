# Iteration 67 — Stage-2 color, slice 3: the royal wave family (w14 + w18)

Third Stage-2 iteration. Geometry UNTOUCHED; same layer-as-color-family
mechanism proven in iters 65/66. This slice also carries ONE root-cause
classify change (scoping, not tuning) — see below.

## Hypothesis

Wrapping the w14 shields and w18 star medallions in `layer 4` with one
new fill rule (`fill void where layer == 4 color royal`) flips exactly
the 30 family tiles from navy #132A61 to royal #2B61B7 — matching the
reference's royal-blue tiles in those zones — with geometry keyset
exact and holds within the calibrated AA band. Existing palette entry;
zero hex changes.

## Family adjudication (Tenet 6)

`wave-plan.json` per-shape hexes, re-read this iteration: w14 median
#3468BA, w18 median #3267BA — both squarely the k=7 standardized
`royal` cluster #2661BF (`input/reference-analysis/reference-analysis.md`),
consistent with their plan labels. No label/hex conflict this slice.

Tile counts: w14 = two 6-vert mirror cycles × rotate-10 = **20 shields**
(outer edge, star-tip axes); w18 = one 20-vert axis-symmetric cycle ×
rotate-10 = **10 ten-pointed star medallions** (outermost band, star-tip
axes). **30 tiles → 30 faces.**

## Classify scoping — root-cause fix, not a label workaround

Problem: layer-4 faces would co-match the side-based rules
(`.navy where sides >= 6` — both w14 6-vert and w18 20-vert), and
classifyFallback is lex-first over the face's class set: "navy" <
"royal_wave", so every royal tile would export the dishonest label
`.navy`. Slices 1/2 dodged this only by lex luck (`cyan_wave` < `navy`)
or absorbed it as recorded refinements (slice 1's 20 `.deep_navy` +
40 `.cobalt`).

Root cause: the five side-based classify rules are FIELD vocabulary
(star tiling + girih) but are written unscoped, so they leak onto wave
faces that already carry an authoritative family class (Tenet 23: the
DSL knows the family at authoring time). Fix: scope all five with
`and layer <= 1` so they match only field (layer −1), layer-0, and
layer-1 faces. Grammar verified in bikar source this session:
`parser.ts:118` maps `<=`, `fill-resolver.ts:258` evaluates it; the
`and` form already exists in this file (`.pocket where source == … and
area >= 360`).

**Deliberate side effect (predicted, not collateral):** the 60 slice-1
faces that lex-split away from `.deep_navy_wave` (20 `.deep_navy`
10-sided + 40 `.cobalt` 5-sided) now match ONLY `.deep_navy_wave` and
relabel to it. Honest labels for all 240 wave faces; fills untouched
(fill rules are predicate-driven, not class-driven).

## Mechanism

Same channel as iters 65/66: wrap w14's two cycles + w18's cycle in
`layer 4` … `layer 1`; add `classify .royal_wave where layer == 4`
(gt-emitter drop guard); add `fill void where layer == 4 color royal`
to the leading cascade; scope the five side-based classify rules with
`and layer <= 1`. Pattern name → `medallion10_iter67`.

## Predictions (gates)

1. **Geometry keyset (params excluded)**: 0 missing, 0 new across all
   675 records.
2. **gt fill census**: #132A61 161→**131**, #2B61B7 21→**51**;
   #262E3D 210, #32B0CA 30, #BBC5D5 110, #FFFFFF 1, circles 142
   unchanged; total 675. **Param deltas confined to exactly 90 faces**:
   - 30 royal tiles: fill #132A61→#2B61B7 AND face_class
     `.center_star`→`.royal_wave` (they were layer-1 `center_star`
     lex-winners in iter-66);
   - 60 slice-1 relabels: face_class `.deep_navy`→`.deep_navy_wave`
     (20) + `.cobalt`→`.deep_navy_wave` (40), **fill unchanged**.
   - Layer-3 faces: NO change (already honest `.cyan_wave`).
3. **Holds (calibrated AA band)**: w14 and w18 may move ≤0.3pt
   (royal's higher G/B channels tip AA edge pixels over
   NEAR_WHITE_MIN); adjacent-window neighbors (w13/w15/w17/w19)
   ±0.1; all other waves bit-identical.
4. **Eyeball (Tenet 26, pre-stated)**: the 20 shields (outer edge,
   star-tip axes) and 10 ten-pointed star medallions (outermost band,
   star-tip axes) read as saturated royal blue — clearly bluer/brighter
   than both the navy field and the slate deep_navy family — matching
   the reference's royal tiles in the same zones; render delta confined
   to the 30 tile interiors, zero change elsewhere.

---

## VERDICT — SLICE 3 PASSES — iteration 67 FROZEN

1. **Geometry keyset (params excluded): EXACT** — 675/675, 0 missing,
   0 new.
2. **gt fill census: EXACT** — #132A61 161→131, #2B61B7 21→51, all
   other buckets unchanged, total 675. **Param deltas confined to
   exactly 90 faces, all three predicted kinds and counts exact**:
   30 × (#132A61, .center_star)→(#2B61B7, .royal_wave);
   40 × .cobalt→.deep_navy_wave (fill unchanged);
   20 × .deep_navy→.deep_navy_wave (fill unchanged).
   The classify-scoping fix worked: all 240 wave faces now carry
   honest family classes.
3. **Holds: PASS inside the calibrated band** — 18/22 bit-identical;
   w14 −0.1 cov, w18 −0.1 cov (the recolored waves), w16 +0.1 iou,
   w21 +0.1 iou. **Refinement (Tenet 4, recorded):** the moving
   neighbors were w16/w21 (outer-edge windows overlapping the royal
   tiles), not the predicted w13/w15/w17/w19 — magnitude inside the
   ±0.1 band; the band model holds, the neighbor-set naming was a
   guess. Slices 4+: predict "±0.1 on any wave whose crop window
   overlaps a recolored tile" instead of naming specific waves.
4. **Eyeball (Tenet 26/27) PASS** — render-delta-tint.png: exactly
   **30 components**, old (19,42,97)=navy, new (43,97,183)=royal,
   two 10-fold rings on star-tip axes (medallions + shield pairs),
   zero change elsewhere. eyeball-w14 / eyeball-w18 ref-vs-render
   crops: both families read royal blue in the same zones as the
   reference (ref picks measured #356BBC / #3269BB — royal cluster).

**Process catch (Tenet 6, recorded):** the wave-plan `waves` array is
**0-indexed** — plan index k = .bkr wave k+1 (plan[13] label=royal
n=20 = .bkr w14's shields; plan[17] label=royal n=10 = .bkr w18's
medallions). My first crop script indexed plan["14"]/plan["18"]
(= .bkr w15/w19, deep_navy) and the slate hexes flagged the mismatch
before viewing — the family adjudication was re-verified against the
correctly-indexed records rather than trusted from the backlog.

**Slice 3 complete: w14 + w18 are royal.**
Remaining Stage-2 face-mapping: slice 4 periwinkle {w3} + cyan_2 {w9}
(two NEW palette entries — verbatim k=7 standardized hexes #80A1E8 /
#02C5D4, layers 5/6); then the end-of-stage palette tone pass +
review-portal verdict. w8/w12 band-rerouting items are separate
(geometry, not color).
