# iter-30 review-portal visual verdict (Tenet 27)

**Date:** 2026-05-28
**Reviewer:** autonomous loop (claude)
**Artifacts viewed:** `input/reference.jpg` vs `iterations/30/render-preview.png` (rasterized from render.svg via magick)

## Expectation written BEFORE viewing render (Tenet 24 ordering)

iter-30 should show ~11 rosette clusters of teal/blue petals in 10-fold
symmetry, but WITHOUT the white interlacing strapwork bands and WITHOUT
the crisp 8-pointed star tiles the reference has — a petal-rosette field
rather than a girih-strapwork interlace.

## Observed divergence

Confirmed and LARGER than the 3/5 metric conveyed. The render is a dense
dark-blue spiky rosette field with correct 10-fold symmetry but is missing
the ENTIRE defining structure of the reference:
- NO white interlacing strapwork bands (the reference's dominant visual feature)
- NO explicit blue 8-pointed star tiles (~11 of them in the reference)
- NO decagon rosette frames around the perimeter
- NO black crossing-stars at band intersections

The two images are barely the same pattern family. A1/A4/A5 scored 100%
and overall 3/5, yet the eye shows a categorical construction mismatch in
seconds — this is the exact failure mode Tenet 27 was codified to catch.

## Verdict: CONSTRUCTION-PHILOSOPHY CEILING CONFIRMED VISUALLY

The reference is a girih-tile strapwork medallion. The cascade's
chord-overlay + wedge-and-rotate philosophy cannot produce white-band
interlace + explicit star tiles. Baseline expectations (v6/v8/v10 stars,
polygon-v0 fields) are VISUALLY REAL — not an over-counted baseline.
Falsification memory option (b) [re-inspect reference] is now resolved:
the baseline is correct; the construction is the wrong technique.

Route: present-options decision doc for girih-construction path (NOT
another parameter-tweak iteration; that would be falsification #6).
