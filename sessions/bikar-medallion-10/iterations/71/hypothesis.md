# iter-71 — Strapwork band_width 8 → 10 (close the owner's lattice-proportion gap)

**What was flagged:** In the iter-69 review-portal verdict, the owner marked one
`style_wrong` on **band_width**: the reference's white interlacing lattice is
proportionally *wider* than the render's. It rode the backlog with the w8/w12
geometry items. This is the lowest-tier actionable real visual gap (Tenet 20) —
one styling parameter, not a geometry/topology change.

**The fix (one line, derived not guessed — Tenet 9/7):**

```
- width 8     # render lattice proportionally thinner than the reference
+ width 10    # 1.25× — sits inside the measured ref/render bracket
```

`crossing alternating` and `color #FCFDFD` unchanged. The strapwork is a
deco-overlay (bikar#653 deco-only weaving): widening the band does not touch the
face graph.

## How the target was derived (not tuned toward iou)

Two independent band-width measurements of `input/reference.jpg` vs iter-70's
`render.png`, both as a fraction of the medallion's colored-bbox diameter (scale-
invariant across the 753² photo and the 1024² render):

| method | ref / render | reading |
|---|---|---|
| EDT-ridge centerline median | 1.27× | reference lattice ~27% wider |
| interior white-run median | 1.13× | reference lattice ~13% wider |

`width 10` (1.25×) sits inside [1.13, 1.27]. NOT pushed higher: the white-*area*
ratio (ref 1.83× the render) tempts a larger move, but that metric conflates the
photo's soft ink-bled edges and white-paper background with true band width — the
Tenet-7 trap. The DECISIVE gate is the eye (below), and the eye says width 10
already lands in the reference's proportional family.

## Gate — all three passed

**1. Census-equality (PRIMARY):** iter-70 → iter-71, **675 shapes both, zero
bucket delta** across every (type,sides) bucket. A strapwork width change is a
pure overlay; the face graph is unchanged, exactly as a width-only edit must be.
(`71/pattern.gt.json` vs `70/pattern.gt.json`.)

**2. Eyeball (DECISIVE, Tenet 24/27):**
- *Expected before viewing:* white lattice bands read visibly wider; slightly
  less navy field / colored tile interior shows between bands; geometry
  unchanged (same stars, petals, darts); no bands merge into blobs.
- *Observed (`bandwidth-zoom-ab.png`, mid-ring 5.6× zoom, w8 vs w10):* exactly
  that — the bands are cleanly wider, tiles correspondingly smaller, geometry
  identical. **Bonus:** at width 8 the dark-navy regions showed horizontal
  hatching/stripe artifacts (thin-band rasterization aliasing); at width 10 those
  stripes are GONE — the navy reads as clean solid fill. A real quality gain the
  widening bought for free.
- *Vs reference (`bandwidth-vs-ref-zoom.png`, matched relative window):* the
  iter-71 lattice now reads in the reference's band-width family — no longer the
  visibly-thinner lattice it was at width 8. Remaining ref differences are color
  saturation / field tint (known color-stage residuals), not the band_width gap.

**3. iou:** attribution-only, NOT tuned (Tenet 7).

Artifacts: `bandwidth-ab-vs-ref.png` (full triptych), `bandwidth-zoom-ab.png`
(w8 vs w10 mid-ring), `bandwidth-vs-ref-zoom.png` (vs reference matched window),
`render.svg`, `render.png`, `pattern.gt.json`.

## Status

iter-71 is the new frozen best (supersedes iter-70). The owner's band_width
verdict is addressed in the render; the owner re-judges it in the review portal
(do NOT self-clear — only the owner flips a verdict). Open front after this:
bikar#653 Slice-4 strapwork overlay (the remaining visual gap, multi-session
engine work) + structure/color OWNER stage gates.
