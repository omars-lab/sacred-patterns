# medallion-10 `band_width` portal verdict re-framed: white-lattice deficit is tile-bleed, not a thin strapwork stroke

**Status:** OPEN

**Discovered:** 2026-06-12, during task #23 pickup (medallion-10 w8/w12 band-rerouting +
band-width geometry slice). Surfaced by checking the inherited iter-69 portal
verdict's `band_width` **wrong** finding against measured render/reference evidence
(Tenet 6 — trust-but-verify inherited claims; Tenet 7 — don't tune a constant to
move a symptom).

## Symptom

The iter-69 review-portal session (`qiyas/out/review/render.svg-1b88a5e4/`,
render.svg vs `input/reference.jpg`) recorded one `style_wrong` verdict=**wrong**
on `band_width`, expected `"white lattice proportionally wider — reference measures
5.1px at 730px diameter"`, note: *"19.4% render-only ink, mostly webbing where
render tiles bleed over the reference white lattice + the outer rim ring."*

Read literally, the verdict points at the white strapwork band being too thin —
i.e. "bump `strapwork width`."

## Root cause

The literal reading is falsified. Three independent measurements (all on
`iterations/69/render.cairo.png` 1010×1024, medallion ≈ 989px, and
`input/reference.jpg` 753×722, medallion ≈ 738px) agree the strapwork **centerline
stroke is already adequate** and the white deficit lives in **tile area**, not band
width:

1. **Rendered lattice centerline width** — interior white-run scan across sampled
   rows inside the medallion disk: **median 9px** (p25 4.8 / p75 14). The reference
   target from `reference-analysis.md` is 0.688% of diameter ≈ **6.8px**. The render
   centerline is already at/above target — *not* too thin.

2. **White-in-disk fraction** — fraction of near-white pixels inside the medallion
   bounding box: **reference 0.550 vs render 0.339.** The reference carries ~21
   percentage points (≈ 62% relatively) MORE white space. The lattice channels in
   the reference are wide and open; in the render the colored tiles crowd them.

3. **Per-wave IoU** — `w8` (middle-ring navy diamonds) IoU **0.334** coverage 0.84
   (under-covers) and `w12` (middle-ring navy bells) IoU **0.463** coverage 1.0 —
   the two worst navy middle-ring waves. The mis-fit is in **tile geometry**
   (shape/size), exactly where #23 already points, not in the strapwork stroke.

Mechanism: the navy middle-ring tiles (waves 8/12, fitted iters 49–53) are
over-sized / mis-shaped, so they extend into the white lattice channels the
reference leaves open. The portal's "19.4% render-only ink … webbing where render
tiles bleed over the reference white lattice" is precisely this bleed — render ink
falling where the reference has white. Widening the painted white centerline would
*not* remove the bleed: the tiles would still overrun the gap; the webbing persists.

## Options considered

- **Option A — bump `strapwork width 8 → larger` (the literal verdict reading).**
  Pros: one-line change. Cons: **falsified by measurement 1** — centerline is
  already at target; this is a Tenet-7 tune-to-green that paints a wider white
  line *over* tiles that still bleed, leaving the webbing. Does not move
  white-in-disk fraction toward 0.550 because the deficit is tile area, not line
  thickness. **Rejected.**

- **Option B — re-fit w8/w12 (and adjacent navy middle-ring waves) tile geometry
  to shrink/reshape them so the white lattice channels open to the reference's
  width.** Pros: attacks the measured root cause (tile area), is exactly the
  geometry slice #23 scopes, improves the two worst IoUs directly, moves
  white-in-disk fraction toward the reference. Cons: per-wave geometry refit is
  more work than a constant bump; must respect the four-gate per-slice protocol +
  G1 immutability (new iteration). **Selected** — it is the root-cause fix and the
  in-scope #23 work.

- **Option C — global tile-inset pass (shrink every wave tile by a uniform ε to
  open all channels at once).** Pros: single knob, moves white-fraction globally.
  Cons: a uniform inset is itself a tune-to-green (Tenet 7) that ignores that only
  *some* waves bleed (w8/w12 worst); it would shrink already-correct tiles and
  regress their IoU. The deficit is not uniform. **Rejected** as a first move;
  revisit only if per-wave refit leaves a uniform residual.

## Decision

**Option B** — re-fit the worst navy middle-ring waves (w8 first, then w12) so the
tiles stop bleeding into the white lattice, in `iterations/70` (iter-69 is FROZEN
per G1). Do **not** change `strapwork width`. Acceptance per the medallion four-gate
protocol (geometry keyset, gt fill census + param-delta confinement, wave-diff holds,
Tenet-26 delta-tint eyeball) plus a Tenet-27 portal verdict re-recording the
`band_width` aspect against the refit.

Decided 2026-06-12 by the autonomous loop under the decision-pick authorization
(reversible, evidence-grounded, applies the existing #23 scope). The divergence from
the inherited portal verdict's literal wording is recorded here per Tenet 6.

## Update 2026-06-14 — per-wave isolation falsifies "w8/w12 are the culprits"

A quick check ranked every wave by its `wave-diff.json` IoU/coverage vs the
reference photo (iter-69 wave-diff, all 22 waves). The result overturns the
task's named scope:

| family | waves | IoU range | coverage | reading |
|---|---|---|---|---|
| **deep_navy** (layer-2 tile overlays, #3C3F47, 210 faces) | w7, w10, w11, w15, w16, w19, w21 | **0.204–0.262** | 0.83–1.00 | full self-coverage **+ spill** — the real bleed |
| navy (the task's named waves) | **w8** 0.334 / **w12** 0.463 | 0.33–0.46 | 0.84 / 1.00 | middling; w8 *under*-covers (not bleeding) |

High coverage (~1.0) + low IoU (~0.24) = "paints all of its own footprint plus
a lot outside it" — exactly the ink-falling-where-reference-is-white that the
portal's "19.4% render-only webbing" measures. The deep_navy family's IoUs are
**roughly half** of w12's, and w8 actually under-covers — so retargeting at
w8/w12 would barely move the 0.339→0.550 white-in-disk gap.

`deep_navy` (#3C3F47) is confirmed the **layer-2 wave-overlay tile family**
(`fill void where layer == 2`), NOT the background field (`navy` #132A61). These
are the colored ring tiles between rosettes — exactly where the white lattice
should breathe. This is the class the deficit belongs to (Tenet 8: solve the
class, not the named instance; Tenet 20: fix the measured-worst, not the named one).

**Scope correction:** the iter-70 refit should target the deep_navy family
(worst-first: w19 0.204, w15 0.243, w16 0.244, w10 0.251, w7 0.253, w11 0.261,
w21 0.262), not w8/w12. w8/w12 ride along only if their own IoU regresses.

## Follow-ups

- iterations/70 — **deep_navy family** tile refit (worst-first: w19/w15/w16),
  shrink/reshape to open the white lattice channels. (Was: w8 navy diamond —
  superseded by the 2026-06-14 isolation finding above.)
- The portal `band_width` finding stays `disposition=backlog` until the refit
  re-records it; update the iter-69 annotation's downstream when iter-70 ships.
- If a uniform white-fraction residual survives the per-wave refits, file the
  global-inset question (Option C) as a separate decision then, not now.
