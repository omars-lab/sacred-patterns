# iter-32 visual verdict (Tenet 27 — eyeballed BEFORE reading the score)

**Pre-stated expectation:** central decagon star + ring of 10 bowties
radiating outward, their decoration forming a second star ring between the
decagon and the rim; full-radius 10-fold rosette reaching ~r=0.6.

**What rendered (render.png):**
- Central decagon + blue {10/3} star ring ✓ (as iter-31)
- 10 bowties radiating outward ✓
- **BUT the bowties are DETACHED SPOKES, not a filled rosette** ✗ — large
  white gaps between adjacent bowties; the figure looks like a pinwheel/sun
  with gaps, NOT the canonical filled Lu-&-Steinhardt decagonal rosette.

**Divergence = bug-locator (the visual caught it before the score):** the
bowtie is a *connector* tile, not a *rim* tile. Ringing the decagon with
ONLY bowties leaves the inter-bowtie gaps unfilled — the canonical girih
decagonal medallion fills those gaps with decagons and/or pentagons. The
construction used the wrong rim tile.

**Score confirms:** composite 1/5 (down from iter-31's 2/5, iter-30's 3/5).
A4 coverage HALVED to 48.6% (the white gaps), A2 fold dropped to 50, and
the encoder LOST the `rosette` type iter-31 had — the detached spokes broke
the rosette gestalt. A6 still 0/18, candidates_in_zone=0 for all shapes.

**Verdict: construction defect, NOT a philosophy falsification.** The girih
philosophy is still right (iter-31 proved the vocabulary). The defect is
the rim-tile choice (bowtie-only ring). iter-33 should fill the gaps with
the canonical alternating decagon/pentagon rim.
