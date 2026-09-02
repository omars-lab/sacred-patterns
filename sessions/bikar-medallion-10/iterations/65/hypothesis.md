# Iteration 65 — Stage-2 color, slice 1: the deep_navy wave family

First Stage-2 iteration. Stage-1 (structure) closed at iter-64 — all 22
waves frozen-passing. G2 license: structural work is 100%, so pixel-level
(color) iterations are now permitted. Geometry is UNTOUCHED this iteration.

## Hypothesis

Moving the nine deep_navy-family waves' connect-cycles into a new
`layer 2` block and adding one leading fill rule
(`fill void where layer == 2 color deep_navy`) flips exactly the 210
family tiles from navy #132A61 to deep_navy #262E3D — matching the
reference's two-tone navy/slate split — while every geometric witness
(census, keyset, all 22 wave-diff holds) stays bit-identical.

## Family adjudication (Tenet 6 — plan is ground truth)

`wave-plan.json` `color` fields, re-read this iteration: deep_navy =
**w2, w4, w7, w10, w11, w15, w16, w19, w21**.

**Divergence from the iter-64 backlog (recorded):** the backlog listed
w4/w7/w10/w11/w15/w16/w19/w21 and *omitted w2* — it was assembled from
per-wave verdict notes starting at w3. The plan's color field says w2
(dart kites, middle flower) is deep_navy. Plan wins; w2 joins the slice.

Tile counts: w2 10 + w4 10 + w7 40 + w10 20 + w11 20 + w15 10 + w16 40 +
w19 20 + w21 40 = **210 tiles**, all simple (non-self-intersecting)
cycles → 210 faces. Cross-check from gt-64 fill census: navy #132A61 has
391 faces = 11 (w1 {10/4} star) + 380 (all wave-2..22 tiles); the family
is 210 of those 380.

## Mechanism — layer as the color-family channel

The DSL knows at authoring time which wave each cycle belongs to
(Tenet 23: propagate, don't re-derive). Channel chosen: **layer number**.

- Verified in bikar source this session: `layer N` only (a) stamps
  `layer:N` tags on segments (`environment.ts tagSegments`), read by the
  fill/classify `layer` attribute as the min across a face's boundary
  tags, and (b) groups faces back-to-front in the SVG (`<g data-layer=N>`).
  Tiles are spatially disjoint, so z-order between layers 1 and 2 cannot
  change a pixel. Strapwork weaves only `_girih_decoration` segments
  (`strapworkSourceGraph`), so layer moves cannot enroll cycles in bands.
- Rejected alternatives (logged per Tenet 19): per-wave `.className` tags
  on cycles would change `face.sources`/face_class semantics and only
  feed a `style` block, not the legacy fill cascade; migrating the whole
  fill cascade to a `style` block is a far larger blast radius (style
  selectors can't express the existing two-attribute rules like
  `ring == 0 and sides == 10`). Layer is the minimal in-DSL channel.
- Edits: wrap the 9 waves' cycles in `layer 2` … `layer 1` (17
  wrapper-pair insertions around 20 rotate-blocks); add
  `classify .deep_navy_wave where layer == 2` (gt-emitter drops
  unclassified faces — the layer-1 `center_star` classify no longer
  reaches them); add `fill void where layer == 2 color deep_navy` as the
  leading cascade rule. Pattern name → `medallion10_iter65`.

## Predictions (gates)

1. **Geometry keyset (params EXCLUDED)** — key
   `(type, center, bbox, area, polar, quadrant)`: **0 missing, 0 new**
   across all 675 records. Geometry is untouched; this is the hold
   witness. (Carve-out vs the campaign's full keyset: `params` now
   carries the *intended* deltas — fill_color and face_class — so it
   leaves the key and becomes prediction 2.)
2. **gt fill census**: #132A61 391→181, **#262E3D 0→210**, #BBC5D5 110,
   #2B61B7 21, #32B0CA 10, #FFFFFF 1 unchanged; total 675, circles 142.
   Param deltas (fill_color, face_class) confined to exactly the 210
   family faces.
3. **wave-diff holds**: all 22 waves **bit-identical** to the iter-64
   baselines (w22 86.10/52.07 included) — wave-diff's ink mask is
   non-near-white, color-agnostic (`tools/wave-diff.py` line 174), and
   deep_navy (38,46,61) is as inky as navy (19,42,97).
4. **Eyeball (Tenet 26, pre-stated before viewing)**: in the iter-65
   render the 210 family tiles read as the darker, grayer slate tone
   (#262E3D), clearly distinct from the remaining royal-leaning navy
   (#132A61) tiles (w1 star, w6 shields, w8 diamonds, w12 bells, w17
   houses, w20 pentagons, w22 rim) — matching the reference's two-tone
   split in the same zones: darts (w2) + pentagrams (w4/w15) + the
   interstice/teardrop/bird families darker; star/shield/bell/rim
   bluer. Render delta iter-64→65 confined to the 210 tile interiors
   (~210 components), zero px change elsewhere.

## Stage-2 verdict bar for this slice

Holds + keyset prove no geometric regression; the *color acceptance* is
the eyeball against the reference crops (w15 priority witness, w2 — the
backlog-divergence wave — and one w7/w16 outer-family zoom), each with
the expectation above written down before viewing.

---

## VERDICT — SLICE 1 PASSES — iteration 65 FROZEN

1. **Geometry keyset (params excluded): EXACT** — 675 records both
   sides, **0 missing, 0 new**. Geometry untouched, proven.
2. **gt fill census: EXACT** — #132A61 391→181, #262E3D 0→210,
   #BBC5D5 110, #2B61B7 21, #32B0CA 10, #FFFFFF 1, circles 142,
   total 675. Param deltas confined to exactly **210** faces, all
   fill #132A61→#262E3D.
   **Refinement (Tenet 4, recorded):** I predicted face_class would
   move uniformly to `.deep_navy_wave`; the classifyFallback lex-first
   rule split the 210 into `.deep_navy_wave` 150 / `.deep_navy` 20
   (10-sided, `sides == 10` rule sorts first) / `.cobalt` 40 (5-sided).
   Confinement prediction holds; the label half needed the lex-sort.
3. **Holds: prediction 3's "bit-identical" wording FALSIFIED;
   regression gate PASSES.** 15/22 bit-identical. Seven waves moved
   ≤0.3 points: w2 −0.3 cov, w4 −0.1 cov, w7 +0.1 cov, w10 −0.3/−0.1,
   w21 −0.1/−0.1 (all family waves) + neighbors w3 +0.1 iou,
   w6 −0.1 iou. **Mechanism identified:** the ink mask is
   color-agnostic for *solid* fill but not for anti-aliased tile-edge
   pixels — fill blends with white at edges, and deep_navy's higher R
   channel (38 vs 19) tips a thin blend band (~75–77% white) over the
   NEAR_WHITE_MIN=200 threshold. Keyset exactness (gate 1) proves the
   shift is raster-level only. Magnitude is in family with the
   campaign's accepted sub-point AA noise (iter-64 w18 −0.02,
   w20 −0.01/−0.02). **Lesson for slices 2+: predict "holds within
   ±0.3 on recolored waves + adjacent-window neighbors, bit-identical
   elsewhere" — not bit-identical everywhere.**
4. **Eyeball (Tenet 26/27) PASS** — expectation pre-stated above.
   - render-delta-tint.png: **212 components** (~210 tiles + 2
     single-px AA slivers), dominant old color (19,42,97)=navy,
     dominant new (38,46,61)=deep_navy; zero change in bands, field,
     or any non-family tile.
   - eyeball-w15 / eyeball-w2 / eyeball-w16 ref-vs-render crops: the
     two-tone split is present in the render in the same zones as the
     reference — slate family tiles clearly darker than the
     royal-leaning navy neighbors. **Palette note (recorded, not a
     blocker):** reference slate measures ~#34373F (wave-plan hex);
     our deep_navy #262E3D renders a step darker/blacker at zoom. If
     Stage-2 final acceptance wants a closer tone match, retuning the
     palette constant is a one-line follow-up — defer to the
     end-of-stage full-palette eyeball.

**Slice 1 complete: w2/w4/w7/w10/w11/w15/w16/w19/w21 are deep_navy.
Remaining Stage-2 backlog:** w3 periwinkle, w5/w9 cyan, w13 turquoise,
w14/w18 royal (new palette entries periwinkle/cyan; new layers 3+),
w8/w12 band-rerouting items; w6/w17/w20/w22 audit-only confirmed navy.
