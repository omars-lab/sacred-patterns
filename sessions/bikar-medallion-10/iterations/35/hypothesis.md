---
attempt: 35
date: 2026-06-10
gap_targeted: "Goal-vs-render structural divergence: white strapwork bands are far too fine — the lattice reads as dense filigree instead of the reference's bold woven straps. [annotation q12-mismatch-yours-546-499; the noted sibling q12-mismatch-yours-699-199 names the same gap: 'white bands far too fine — dense mesh instead of bold straps']"
construction_hypothesis: "The deco-only weave (iter-34 final) recovered the CORRECT strap network — the probe showed the 2790-strand decoration lattice matches the reference's star/rosette topology. What is wrong now is band WEIGHT, not band count: measured on the images, the reference's straps are ~6% of a rosette's diameter; iter-34's width-6 bands on radius-62 decagons are ~2.5-3%. At half the reference's relative weight, adjacent narrow bands fail to fuse into bold straps and the eye reads mesh."
bkr_change: "Single token: strapwork width 6 → 8 in pattern.bkr (no field, classify, fill, or palette change). Initial ratio-matching guess was 12; the predicted over-widening cost fired (white mass at the dense center), so the in-iteration probe ladder 12 → 10 → 8 settled on the widest setting that keeps the center star and tiles legible."
predicted_lift: "+0.03–0.05 pixel similarity (70.8% → ~74-76%): the white-area fraction rises toward the reference's, and the small white slivers between near-parallel decoration lines fuse into single bold straps. Should clear annotation q12-mismatch-yours-699-199 (the 'too fine' note); the un-noted sibling at (546,499) likely marks the same texture and should clear with it."
predicted_cost: "Over-widening risks: (a) bands swallow the smallest colored pockets (turquoise/cobalt triangles) entirely, flipping small-shape area the wrong way; (b) under-strand trim gaps at crossings scale with width — A5 band-integrity (100 at 1054 crossings in iter-34) could regress if trims overlap; (c) the scalloped-vs-rounded boundary divergence is untouched by this edit and stays."
prior_art_searched: "none — the lever was located by direct measurement of both images (strap-to-rosette ratio), and iter-34's visual-verdict already established the network topology is correct; no new construction technique is involved."
related_memory: "feedback_girih_strapwork_is_render_style_not_geometry (width is a render-style param, exactly the class of change that memory says strapwork tuning should be); feedback_metric_temptation_at_plateau (named root cause: band weight, not a threshold — this is a geometry-ratio fix, not metric tuning)."
detector_untouched: "confirmed — no qiyas param/threshold/cost in this iteration"
---

## Portal evidence (machine-drafted from review-verdict.json)

- verdict: right=0 wrong=2 unsure=0; review_passed=False
- pixel similarity: 70.8%
- pixel warning: Channel drift is uneven: r=84.6 vs b=62.6 (spread 22.0). Pattern may use a wrong palette family rather than a per-shape color mistake.
- gaps (ranked, structure before pixels):
  1. [annotation q12-mismatch-yours-546-499] (Q12 structural_mismatch, rank 0): Goal-vs-render structural divergence: a shape present in one is missing, mis-built, or mis-placed in the other — fix the construction before recolouring.
  2. [annotation q12-mismatch-yours-699-199] (Q12 structural_mismatch, rank 0): Goal-vs-render structural divergence: a shape present in one is missing, mis-built, or mis-placed in the other — fix the construction before recolouring. Reviewer: white bands far too fine — dense mesh instead of bold straps.

## Plan

Why this gap: it is the top-ranked portal gap AND the only named reviewer
finding; iter-34's own ship-gate notes already flagged the residual divergence
as texture-level (lattice aligned, weight wrong). Why this hypothesis: the
strand COUNT was fixed in iter-34 (5640 → 2790, deco-only); the probe render
visually matched the reference's network, so the remaining "too fine" verdict
can only be band weight. Why this is the smallest edit: one numeric token in
the strapwork block; field geometry, classification, palette, and the weaver
input set are untouched.

Expected visual (written BEFORE viewing any render — Tenet 24): the same
rosette lattice as iter-34, but the white bands roughly double in thickness —
each strap reads as a single bold white ribbon, the tiny white triangles at
near-parallel crossings fuse into the ribbon, the blue/turquoise pockets
shrink slightly but stay clearly visible as discrete tiles, and the over/under
weave gaps remain visible at crossings. The render should sit visibly closer
to reference.jpg's bold-strap look. Failure signature to watch: colored
pockets vanishing under white, or white blobs (merged bands) replacing
distinct straps near the center star where decoration lines converge.

## Guardrails check

- This is a CONSTRUCTION edit (.bkr / bikar primitive), not a detector edit:
  yes — a one-token render-style change in pattern.bkr; qiyas untouched.
- Construction-philosophy memory checked — approach not already falsified:
  yes — feedback_girih_strapwork_is_render_style_not_geometry endorses width
  as the style-layer lever; no memory or decision doc records a failed
  width-tune on this session (iter-34 explicitly deferred width until the
  strand-set was right, which it now is).
- predicted_cost names a concrete failure mode I will look for in the render:
  yes — swallowed small pockets and merged-band white blobs near the center;
  plus A5 crossing-trim regression checked in the gt/audit numbers.
