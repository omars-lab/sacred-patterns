# Iteration 63 — wave-21 gate: deep_navy wedge two-family mirror pairs

## Hypothesis

Adding TWO families of mirror-pair tiles per STAR-TIP axis (wave-16
two-family topology; 40 stamps total = 2 families × {+,−} × 10 axes)
reproduces wave 21 of the wave plan: the 39 real deep_navy small tiles
(~86 u², r_frac 0.820–0.863, theta clusters ~±2–4 about star-tip
axes; the 40th member is fragmented in the plan but the rotated cycle
stamps it anyway, mirroring the w16 fragmented-member precedent).

## Mechanism

- **Model**: `iterations/62/measure/wave21-fit.json` — TWO families:
  - **inner** 5-vert wedge, |rel| ≈ 2.05, fitted IoU 0.910 / snapped
    0.911 at g=0.25, area 80.3 u² (snap-escalation point 10 —
    smallness driver, w11/w15/w16/w19 family);
  - **outer** 7-vert sail, |rel| ≈ 5.7, fitted IoU 0.938 / snapped
    0.921 at g=0.25, area 88.1 u² (snap point 11 — smallness driver).
- **Rings** (Tenet-5 reuse check, full radius table swept):
  - **REUSE C104** (232.2, already `divide into 1440`) for outer
    vert 7 — exact radius match, compatible division.
  - **REUSE C106 with re-division 20 → 1440** for outer vert 6
    (235.0 exact match). Its ONLY existing reference is `C106.cpt0`
    (line 543, w18 star cycle); cpt0 ≡ 0° on any M, and
    1440 = 72×20 puts every old grid point on the new grid —
    re-division is geometry-preserving. NEW PRECEDENT recorded:
    M→M′ re-division is allowed iff M′ is an integer multiple of M
    and every existing reference is a preserved point.
  - **10 NEW rings C119–C128** (all `divide into 1440`):
    C119 236.8, C120 236.6, C121 239.1, C122 251.6, C123 241.5
    (inner); C124 228.8, C125 227.3, C126 227.9, C127 238.1,
    C128 239.4 (outer). Near-misses adjudicated NOT reusable
    (exact-match protocol): 251.6 vs C118 251.4, 241.5 vs C113
    241.7, 227.3/227.9 vs C116 226.5, 228.8 vs C105 229.9 —
    snapping fitted radii to harvest rings would be tuning data for
    convenience (Tenet 7).
- **Cycles** (STAR-TIP cpt convention, cpt = rel/0.25, mirror =
  (1440 − cpt) % 1440), four `rotate 10` cycles:
  - inner+: `[C119.cpt6 C120.cpt9 C121.cpt12 C122.cpt11 C123.cpt3]`
  - inner−: `[C119.cpt1434 C120.cpt1431 C121.cpt1428 C122.cpt1429 C123.cpt1437]`
  - outer+: `[C124.cpt18 C125.cpt22 C126.cpt24 C127.cpt29 C128.cpt27 C106.cpt17 C104.cpt17]`
  - outer−: `[C124.cpt1422 C125.cpt1418 C126.cpt1416 C127.cpt1411 C128.cpt1413 C106.cpt1423 C104.cpt1423]`
- **Color**: new faces fill navy via the leading
  `fill void where layer == 1 color navy` rule; wave 21's reference
  color is DEEP_NAVY → **Stage-2 backlog entry required** (like
  w15/w19), recorded at verdict.

## Clearance proof (clearance-wave21.py + localize-w18-overlap.py)

First non-zero overlap counts of the campaign — adjudicated BENIGN,
not shrunk away (Tenet 7):

- Overlaps: w18 14 px, w20 13 px, w22 15 px (0.2% of stamp each);
  exactly the 42 OTHER px in attribution (on-target 76.1%,
  near-white 22.5%, w21-fragments 0.8%).
- **Mechanism (named, Tenet 3)**: overlapped px are bright
  anti-aliased band-edge px (mean RGB 180–186, just under the
  near_white ≥200 threshold) that the EDT grow-back assigned to
  neighbor wave seeds. They are band halo, not tile ink.
- **Witnesses**: w20/w22 contacts have ZERO px surviving 2-px stamp
  erosion (pure boundary graze). The w18 contact (11/14 px surviving
  erosion) was localized: outer+ member at axis 36, centroid
  r=230.7u rel +5.18, RGB mean 186, and the blob sits **6.85 u from
  w18 shape 67's real dark ink core** — farther than the 5.02u
  model-vs-model gap, proving the px lie in the white band between
  the tiles. (Tenet-26 divergence note: I pre-stated the inner tip
  as the suspect; the actual contact is the outer flank — recorded.)
- Model-vs-model min gaps, all above the 4.21u survival precedent:
  inner± 6.32u; inner vs outer 6.60u; outer± 34.42u; inner vs w18
  star **5.21u**; outer vs w18 star **5.02u**; outer vs w20 pent
  (dart-18 mirror) **5.06u**; inner vs w20 pent 21.23u; outer vs
  w19 kite 6.98u; outer vs w16 fin 21.92u.

## Predictions (gates)

1. **Census**: 582 → **632** (+20 five-vert faces: pentagon/5v
   20→40; +20 seven-vert faces: unknown/7v 40→60; +10 circles:
   119→129 — C104/C106 reused, no new circles for them). EXACT or
   the iteration fails.
2. **Waves 1–20**: hold baselines bit-identical, EXCEPT holds whose
   IoU windows abut wave 21 (w18/w20 candidates per the clearance
   contacts) may shift sub-point — adjudicate via the gt
   outline-keyset diff (all 582 prior outlines byte-identical),
   per the iter-62 mechanism note.
3. **Wave 21**: coverage/iou RISE from baseline 63.1/22.3 — live
   acceptance signals.
4. **Eyeball (Tenet 26, pre-stated)**: per star-tip axis, four new
   small deep-navy-zone tiles — a narrow wedge pair tight against
   the axis (|rel|≈2, r 237–252) and a wider sail pair flanking at
   |rel|≈5.7 (r 227–239), nested between the w18 star flank and the
   w20 pentagons, radially outside the w19 kites; rendered navy
   (Stage-2 pending); same ~2–3px registration offset as w18–w20
   overlays.

---

## VERDICT — WAVE 21 PASSES — iteration 63 FROZEN

1. **Census EXACT**: 582 → 632. Buckets: circle 119→129 (+10
   rings), pentagon/5v 20→40 (+20 inner wedges), unknown/7v 40→60
   (+20 outer sails), every other bucket identical. Geometry-keyset
   diff (type+center+bbox+area+params+polar): **0 missing, 50 new**
   — all 582 prior shape records byte-identical.
   **Witness correction (Tenet 4)**: the "outline-keyset" diff
   cited since iter-62 keyed on a nonexistent `outline` field and
   was vacuous as written. The corrected key is the full geometric
   record (type/center/bbox/area/params/polar). Re-ran iter-61→62
   under the corrected key: 0 missing / 26 new — the iter-62
   conclusion stands; only the witness mechanism was misdescribed.
   All future hold adjudications use the corrected key.
2. **Holds**: waves 1–17, 19, 22 bit-identical (sub-0.05 rounding
   only). **w18 moved** iou 57.1→54.44 (−2.66, cov +0.00) and
   **w20 moved** iou 43.4→42.97 (−0.43, cov +0.06) — exactly the
   two holds the clearance contacts predicted. Adjudicated as
   measurement-window artifacts per the iter-62 mechanism note:
   wave 21's 40 new tiles sit 5.02–5.21u from every w18 star flank
   and 5.06u from the w20 pentagons, so their ink enters those
   waves' IoU windows and grows the union; coverage unchanged/up +
   geometry-keyset (1) prove zero geometric interaction. Scale
   note: −2.66 is ~10× the w19 precedent (−0.28) because wave 21
   rings EVERY star with four tiles instead of grazing one window
   edge — the artifact scales with adjacency count, not with risk.
3. **Wave 21 (live signals)**: 63.1/22.3 → **84.25/27.39** — both
   rose as predicted. Coverage in-family with accepted live waves
   (w1 82.2, w8 84.2, w2 87.1); iou in-family with the small-tile
   class (w15 24.3, w16 24.3, w10 25.4, w11 25.8, w19 20.4) whose
   ceiling is set by per-tile variance + registration on ~86u²
   tiles.
4. **Eyeball (Tenet 26/27) PASS**: pre-stated expectation
   confirmed — overlay-w21-on-ref.png + zooms (axes 0, 90) show
   every red outline on a small dark-navy wedge/sail tile nested
   between the star flank and the lobe band;
   render-zoom-axis90-iter62-vs-63 shows exactly four new navy
   tiles flanking the top star tip and nothing else changed.
5. **Stage-2 backlog entry**: wave 21 reference color is DEEP_NAVY
   but the faces fill navy via the leading `layer == 1` rule —
   queued with w15/w19 (deep_navy family) for the Stage-2 color
   pass.
6. **Snap-escalation data points 10/11** (recorded at fit time):
   both families g=0.5 → g=0.25, smallness driver
   (w11/w15/w16/w19 family).

**Next: wave 22** per wave-plan.json — 30 navy tiles (~1048 px,
r_frac 0.906–0.943, theta triplets about star-tip axes — the
outermost wave; campaign completes when it passes). Baselines on
THIS iteration's render: **w22 39.26/24.07** (live).
