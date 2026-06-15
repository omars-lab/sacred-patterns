---
iteration: 32
date: 2026-05-28
skill: iterate-construction-hypothesis
detector_untouched: confirmed
gap_targeted: >
  iter-31 proved the central girih decagon tile emits girih vocabulary
  (encoder detected `rosette` + `decagon` types the chord-overlay never
  produced) but A6 stayed 0/18 because a single tile has no full-radius
  medallion extent — candidates_in_zone=0 for all 18 expected shapes. The
  gap iter-32 closes: compose the central tile into a full-radius
  decagonal medallion so detected shapes land in the baseline's zone
  bands (inner-star 0.0-0.35, rosette 0.35-0.55, transition 0.55-0.86).
construction_hypothesis: >
  A canonical Lu-&-Steinhardt decagonal rosette — central decagon ringed
  by 10 bowtie tiles (one per decagon edge, via `attach core edge N`) —
  produces a full-radius medallion whose girih decoration populates the
  inner-star + rosette zones with star/rhombus/kite vocabulary. The 10
  bowties extend the figure to ~r=0.6 (transition zone reach) and their
  decoration lines weave the strapwork bands the baseline expects.
bkr_change: >
  iter-31 had ONLY `girih decagon 61.8`. iter-32 adds 10 `girih bowtie 61.8
  attach core edge N` statements (N=0..9), aliasing the central decagon as
  `core`. Smoke-tested 2-bowtie attach already (renders edge-to-edge
  correctly). This is a DIFFERENT construction (composition), not a tweak
  of iter-31 — per skill stop-rule, the falsified-twice rule does not apply.
predicted_lift: >
  A6 0/18 -> >0: expect candidates_in_zone > 0 for inner-star + rosette
  shapes once the medallion has full radius. A2 fold should recover toward
  10 (the ring restores 10-fold rotational symmetry a single tile lacked).
  A4 coverage should stay high. Composite 2/5 -> 3/5 plausible if A2
  recovers. The discriminating signal: do ANY inner-star or rosette
  expected_shapes flip from MISSING (cand_zone=0) to PARTIAL/EXCESS
  (cand_zone>0)?
predicted_cost: >
  Low-medium. 10 attach statements, one render, one encode (DYLD path
  set), one audit. The attach mechanism is proven.
prior_art_searched: >
  Lu & Steinhardt 2007 — the decagonal rosette (decagon + ring of bowties)
  is the canonical girih medallion seed shown in their Fig 2. bikar
  attachGirihTile (girih-tiles.ts:289) implements edge-to-edge placement;
  smoke-tested /tmp/girih-attach-smoke.png 2026-05-28.
related_memory: >
  feedback_a6_baseline_construction_philosophy_mismatch (girih is the
  right philosophy), Tenet 17 (iter-31 proved the primitive, iter-32
  composes), Tenet 27 (visual-verify before score).
---

## iter-32 — decagonal rosette (central decagon + 10-bowtie ring)

iter-31 proved the central tile. iter-32 composes the canonical
Lu-&-Steinhardt seed: ring 10 bowties around the central decagon, one per
edge. This is the smallest composition that produces a full-radius,
10-fold-symmetric medallion.

**Expected visual (write BEFORE looking — Tenet 27):** a central decagon
with its {10/3} blue star ring (as in iter-31), now surrounded by a ring
of 10 bowtie tiles radiating outward, their decoration lines forming a
second ring of star points between the decagon and the medallion rim. The
overall silhouette is a 10-fold rosette reaching ~r=0.6. White-band
interlace still not authored (no strapwork weave yet) — just tile +
decoration faces.
