# Iteration 62 — wave-20 gate: navy outer-lobe pentagon mirror pairs

## Hypothesis

Adding ONE MIRROR PAIR of 6-vertex outer-lobe pentagons per DART axis
(20 tiles total, wave-10/14/17 mirror-pair topology) reproduces wave 20
of the wave plan: the 20 medium navy tiles (~614 u², r_frac
0.829–0.838) flanking each dart line in the outermost lobe band.

## Mechanism

- **Model**: `iterations/61/measure/wave20-fit.json` — 6-vert free
  polygon, fitted IoU 0.966, snapped IoU 0.964 at g=0.25 (M=1440;
  9th snap-escalation data point — driver is near-axis vertex
  precision, rel 2.75 at g=0.5 costs 0.033 IoU). Model area 599.4 u²
  vs consensus 603.8 u².
- **Rings**: six NEW circles C113–C118 (241.7, 230.2, 222.7, 226.5,
  245.2, 251.4), all `divide into 1440`. Tenet-5 reuse check: nearest
  existing are C102 222.6 (Δ0.1), C105 229.9 (Δ0.3), C103 224.6
  (Δ1.9) — no exact match, so no reuse (exact-match protocol; snapping
  the fitted radius 0.1u to harvest a ring would be tuning data for
  convenience).
- **Cycles** (DART-axis cpt convention, cpt = (18 ± rel)/0.25):
  - `rotate 10`: `[C113.cpt85 C114.cpt83 C115.cpt94 C116.cpt115 C117.cpt106 C118.cpt95]`
  - mirror `rotate 10`: `[C113.cpt59 C114.cpt61 C115.cpt50 C116.cpt29 C117.cpt38 C118.cpt49]`
- **Color**: 6-vert faces are caught by the existing
  `fill void where sides >= 6 color navy` rule, and wave 20's
  reference color IS navy — correct by default. Stage-2 status:
  audit-only (like w17), no backlog entry needed.

## Clearance proof (run before authoring — clearance-wave20.py)

- Zero overlap px vs ALL waves 1–19 and unbuilt 21–22.
- On-target 89.6% of stamp; off-target 100% near-white band, 0 OTHER.
- Model-vs-model min gaps, all above the 4.21u survival precedent:
  pent+ vs pent− 22.09u; vs w17 pent+ (same dart axis — prime radial
  suspect) **4.80u**; vs w19 kite axis-36 mirror (prime angular
  suspect) **4.81u**; vs w18 star 9.64u; vs w14 shield 34.58u; vs w16
  inner/outer 35.55/21.35u.

## Predictions (gates)

1. **Census**: 556 → **582** (+20 six-vert faces: unknown/6v 110→130;
   +6 circles: 113→119). EXACT or the iteration fails.
2. **Waves 1–19**: bit-identical wave-diff numbers (hold baselines).
3. **Wave 20**: coverage/iou RISE from baseline 50.8/24.9 — live
   acceptance signals (like w18), not saturated.
4. **Eyeball (Tenet 26, pre-stated)**: 20 wide convex navy tiles, two
   per dart axis flanking the dart line in the band outside the w17
   house-pentagons and angularly between the w19 kite pairs; same
   ~2–3px registration offset as w18/w19 overlays.

---

## VERDICT — WAVE 20 PASSES — iteration 62 FROZEN

1. **Census EXACT**: 556 → 582. Buckets: circle 113→119 (+6 rings),
   unknown/6v 110→130 (+20 pentagons), every other bucket identical.
   All 556 iter-61 outlines survive BYTE-IDENTICAL in iter-62's
   gt.json (outline-keyset diff: 0 missing, 26 new).
2. **Holds**: waves 1–18 bit-identical. **w19 moved** — cov
   99.69→99.73 (+0.004), iou 20.73→20.45 (−0.28): first
   non-bit-identical hold of the campaign. Adjudicated as a
   measurement-window artifact, NOT a geometric interaction — the new
   pentagon ink (4.81u from the kite's axis-36 mirror member) enters
   w19's evaluation window and grows the IoU union; the kite
   geometry itself is byte-identical per (1). Mechanism note for
   future waves: holds whose windows abut a NEW wave may shift
   sub-point in iou with zero geometry change — adjudicate via the
   gt outline-keyset diff, which is the authoritative no-interaction
   witness.
3. **Wave 20 (live signals)**: 50.8/24.9 → **88.8/43.4** — both
   rose as predicted. Coverage in-family with accepted live waves
   (w1 82.2, w8 84.2, w2 87.1); iou in-family with w17 45.1 / w14
   46.2. Residual ceiling ≈ 91%: per-tile variance vs the consensus
   model (clearance math: 19095 on-target px / ~20900 ref px even
   with zero registration error).
4. **Eyeball (Tenet 26/27) PASS**: pre-stated expectation confirmed —
   overlay-w20-on-ref.png + zooms (axes 18, 90) show every red
   outline on a wide navy shoulder tile, two per dart axis;
   render-zoom-axis90-iter61-vs-62 shows exactly two new wide navy
   pentagons flanking the dart line and nothing else changed. Offset
   is the known ~2–3px registration plus per-tile variance.
5. **Stage-2**: audit-only — wave 20's reference color is navy and
   the 6v faces land in the existing `sides >= 6 -> navy` rule. No
   backlog entry.
6. **Snap-escalation data point 9**: g=0.5 loss 0.033 > 0.01 →
   g=0.25; driver near-axis vertex precision (rel 2.75), w13/w17/w18
   family.

**Next: wave 21** per wave-plan.json — 39 real deep_navy small tiles
(~86u², r_frac 0.820–0.863, theta clusters ~±2–4 about STAR-TIP
axes — note 39 ≠ 40: one member missing/fragmented in the plan;
check fragment list at measurement). Baselines on THIS iteration's
render: **w21 63.1/22.3, w22 39.3/24.1** (both live).
