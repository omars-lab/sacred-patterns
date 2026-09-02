# Iteration 64 — wave-22 gate: navy outer-rim triplets (FINAL WAVE)

## Hypothesis

Adding TRIPLETS per STAR-TIP axis — one ON-AXIS axial 10-vert kite +
one mirror pair of 7-vert flank shields (30 stamps = 3 × 10 axes) —
reproduces wave 22 of the wave plan: the 30 real navy tiles
(~1048 px ≈ 615 u², r_frac 0.906–0.943, theta triplets about
star-tip axes, ZERO fragments). This is the OUTERMOST and FINAL
wave; the 22-wave campaign completes when it passes.

## Mechanism

- **Model**: `iterations/63/measure/wave22-fit.json` — TWO families:
  - **axial** 6-row symmetric kite (10 verts, w18-style rows with
    on-axis cpt0 endpoints), apex inward at r 246.1, flat rim at
    r 279.1, |x| ≤ 2.75°; fitted IoU 0.972 / snapped 0.965 at
    g=0.25 (snap-escalation point 12 — near-axis driver,
    w13/w17/w18/w20 family);
  - **flank** 7-vert shield, rel 3.75–10.0, r 240.1–272.5; fitted
    IoU 0.968 / snapped 0.959 at g=0.25 (snap point 13 — escalated
    on the 0.01 rule).
- **Rings** (Tenet-5 reuse check, full C0–C128 radius table swept):
  **ZERO exact matches → 13 NEW rings C129–C141**, all
  `divide into 1440`:
  - axial: C129 246.1, C130 246.9, C131 260.1, C132 264.2,
    C133 275.8, C134 279.1;
  - flank: C135 240.1, C136 246.7, C137 251.3, C138 261.0,
    C139 269.5, C140 272.5, C141 260.3.
  Near-misses adjudicated NOT reusable (exact-match protocol):
  251.3 vs C118 251.4 (Δ0.1) and C122 251.6 (Δ0.3); 240.1 vs
  C128 239.4 (Δ0.7); 246.1/246.7/246.9 vs C117 245.2 (Δ≥0.9) —
  snapping fitted radii to harvest rings would be tuning data for
  convenience (Tenet 7). C106 (235.0) does not recur in this wave.
- **Cycles** (STAR-TIP cpt convention, cpt = rel/0.25, mirror =
  (1440 − cpt) % 1440), three `rotate 10` cycles:
  - axial (single, self-mirrored): `[C129.cpt0 C130.cpt1 C131.cpt10
    C132.cpt11 C133.cpt10 C134.cpt0 C133.cpt1430 C132.cpt1429
    C131.cpt1430 C130.cpt1439]`
  - flank+: `[C135.cpt17 C136.cpt32 C137.cpt37 C138.cpt40
    C139.cpt33 C140.cpt21 C141.cpt15]`
  - flank−: `[C135.cpt1423 C136.cpt1408 C137.cpt1403 C138.cpt1400
    C139.cpt1407 C140.cpt1419 C141.cpt1425]`
- **Color**: new faces fill navy via the leading
  `fill void where layer == 1 color navy` rule; wave 22's reference
  color IS navy — expected Stage-2 **audit-only** (first color
  match since w17/w20; confirm at verdict, no backlog entry if
  confirmed).

## Clearance proof (clearance-wave22.py)

The cleanest late-wave clearance of the campaign:

- **ZERO overlap px against ALL 21 prior waves** (first zero-overlap
  clearance since the pre-w21 era). On-target 89.3%; off-target
  3433 px = 100% near-white band, 0 fragments (plan has none),
  0 OTHER. (Tenet-26 divergence note: I pre-stated bright halo
  overlap px as likely; actual is strictly zero — the conservative
  half of the expectation, recorded.)
- Model-vs-model min gaps, all above the 4.21u survival precedent,
  tightest exactly where pre-stated (flank vs w21 sail, axial vs
  flank): flank+ vs w21 outer sail **4.55u**; axial vs w21 inner
  wedge ±5.18u; flank+ vs w21 inner 5.27u; flank+ vs w20 pentagon
  (dart-18 mirror) **5.31u**; axial vs flank+ **5.43u**; flank+ vs
  w18 star 9.43u; axial vs w18 star 11.10u; flank± across star-tip
  line 34.05u; axial vs w20 pent 34.20u; flank across dart line
  72.65u.

## Predictions (gates)

1. **Census**: 632 → **675** (+13 circles: 129→142; +10 ten-vert
   faces: unknown/10v 1→11; +20 seven-vert faces: unknown/7v
   60→80). EXACT or the iteration fails.
2. **Waves 1–21**: hold baselines bit-identical, EXCEPT holds whose
   IoU windows abut wave 22 (w21 prime candidate — gaps 4.55–5.43u;
   w18/w20 possible) may shift sub-point — adjudicate via the
   corrected geometry-keyset diff (type/center/bbox/area/params/
   polar: all 632 prior records byte-identical, 0 missing).
3. **Wave 22**: coverage/iou RISE from baseline 39.26/24.07 — live
   acceptance signals.
4. **Eyeball (Tenet 26, pre-stated)**: per star-tip axis, three new
   navy tiles completing the medallion's outer rim — an on-axis
   kite pointing inward (apex r 246 nesting between the w21 wedge
   pair, flat top at r 279) and two leaning shields flanking at
   rel 4–10 (riding just outside the w21 sails, inside nothing —
   they ARE the rim); rendered navy matching the reference; same
   ~2–3px registration offset as w18–w21 overlays.

---

## VERDICT — WAVE 22 PASSES — iteration 64 FROZEN — CAMPAIGN COMPLETE

1. **Census EXACT at total and vertex level**: 632 → 675. Buckets:
   circle 129→142 (+13 rings), **decagon/10v 21→31** (+10 axial
   kites), unknown/7v 60→80 (+20 flank shields), every other bucket
   identical. Geometry-keyset diff (corrected key:
   type/center/bbox/area/params/polar/quadrant): **0 missing,
   43 new** — all 632 prior records byte-identical.
   **Prediction divergence (Tenet 4, recorded)**: I predicted the
   10-vert faces would land in unknown/10v (1→11); the gt
   classifier types any 10-vert polygon as `decagon`, so they
   landed in decagon/10v (21→31). The vertex-level prediction
   (+10 ten-vert faces) was correct; the type-label half was wrong.
   Bucket-label predictions must use the classifier's type map
   (3/4/5/6/8/10 sides → named types), not `unknown/<n>`.
2. **Holds**: waves 1–17 and 19 **bit-identical**. w18 −0.02 iou
   and w20 −0.01 cov/−0.02 iou (sub-point rounding). **w21 moved**
   84.25/27.39 → 83.94/26.07 (−0.31 cov, −1.32 iou) — exactly the
   predicted prime candidate: wave 22's triplets sit 4.55–5.43u
   from every w21 tile, so their ink enters w21's IoU window and
   grows the union; geometry-keyset (1) proves zero geometric
   interaction. Scale in family with the established
   adjacency-count mechanism (w18 moved −2.66 when w21 ringed it).
3. **Wave 22 (live signals)**: 39.26/24.07 → **86.10/52.07** —
   the largest single-wave jump of the campaign (cov +46.8,
   iou +28.0). IoU 52.07 lands in the large-tile family (w13 51.8,
   w9 53.3, w5 53.1) as expected for ~615 u² tiles.
4. **Eyeball (Tenet 26/27) PASS**: overlay-w22-on-ref + zooms
   (axis 0, axis 90) show every red outline tracking a navy
   outer-rim tile; the axis-0 zoom shows the full triplet (on-axis
   kite + two shields). Render delta iter-63→64
   (render-delta-tint.png): exactly 30 tile-sized components
   (~1880–1944 px each), dominant new color (19,42,97) = navy
   #132A61, radial extent 232.9–280.5u — the interior is
   px-untouched.
5. **Stage-2 color: AUDIT-ONLY confirmed** — wave 22's reference
   color is navy and the faces fill navy via the `layer == 1` rule.
   First direct color match since w17/w20; NO backlog entry.
6. **Snap-escalation data points 12/13** (recorded at fit time):
   axial g=0.5→0.25 near-axis driver (w13/w17/w18/w20 family);
   flank g=0.5→0.25 via the 0.01 rule.

### CAMPAIGN COMPLETE — all 22 waves PASSED (iters 41–64)

The wave protocol is closed: every wave of
`input/reference-analysis/wave-plan/wave-plan.json` has a frozen
passing iteration. Final structural state: 675 gt shapes, census
stable, all holds adjudicated, final-sbs-ref-vs-render.png records
the Stage-1 endpoint (shape before pixels — Convergence Hierarchy
levels 1–3 done wave-by-wave).

**Next: Stage-2 color pass** — the accumulated backlog, in wave
order: w3 periwinkle, w4 deep_navy, w5 cyan, w6 navy-verify,
w7 deep_navy, w8 navy-verify + band rerouting, w9 cyan,
w10 deep_navy, w11 deep_navy, w12 band-separation rerouting,
w13 turquoise, w14 royal, w15 deep_navy (priority witness),
w16 deep_navy, w18 royal, w19 deep_navy, w21 deep_navy
(w17/w20/w22 audit-only matches). Mechanism: per-wave `classify`
rules + palette fills replacing the blanket `layer == 1 → navy`
rule — pixel-level work is now licensed because structure is 100%
(G2 gate satisfied).
