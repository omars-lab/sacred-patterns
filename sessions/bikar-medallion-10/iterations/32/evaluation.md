# iter-32 evaluation — decagonal rosette (central decagon + 10-bowtie ring)

**Construction change (detector untouched):** composed iter-31's central
girih decagon into a full-radius figure by ringing it with 10 bowtie tiles
(`girih bowtie 61.8 attach core edge N`, N=0..9). No detector threshold
touched.

## Scores (vs iter-31, iter-30)

| metric | iter-30 | iter-31 | iter-32 | note |
|--------|---------|---------|---------|------|
| composite | 3/5 | 2/5 | **1/5** | regressed — see visual-verdict |
| A1 match% | 100 | 100 | 100 | semantic census still valid |
| A2 fold | 85 | 0 | 50 | ring restored *some* fold, not 10 |
| A4 coverage% | 100 | 96 | **48.6** | HALVED — the white inter-bowtie gaps |
| A5 band | 100 | 0 | 0 | no band network |
| A6 pass | 0/18 | 0/18 | 0/18 | candidates_in_zone=0 for all 18 |

## The signal (visual caught it BEFORE the score — Tenet 27)

visual-verdict.md (written before reading the score) predicted a filled
10-fold rosette; the render showed **10 DETACHED bowtie spokes with large
white gaps between them**, not a filled rosette. The bowtie is a
*connector* tile, not a *rim* tile — ringing the decagon with bowties only
leaves the inter-bowtie gaps unfilled.

The score confirmed the visual: A4 coverage halved to 48.6% (the gaps), and
the encoder LOST the `rosette` type iter-31 had — the detached spokes broke
the rosette gestalt.

## Why this closes a third A6=0 result — and what it means

Three girih authoring paths have now produced A6=0 / candidates_in_zone=0:

1. **iter-31 (single central tile):** correct vocabulary (`rosette` +
   `decagon` detected), but a single tile has no full-radius medallion, so
   distance normalization misses every zone band.
2. **iter-32 (manual bowtie ring):** detached spokes + gaps; wrong rim tile;
   coverage halved; lost the rosette type.
3. **subdivide smoke** (`girih decagon 161.8 subdivide 1`, /tmp): the kernel's
   `computeSubdivision` is documented as "a simplified approximation" — it
   places pentagons at vertices + a central decagon + rhombi at edge
   midpoints, producing a **ring of detached pentagons around an empty central
   decagon**, the SAME gap problem as iter-32. It does NOT produce the
   overlapping-rosette field.

**The reference (viewed directly this iteration) is a FIELD of ~11
overlapping decagonal rosettes** — the full Lu-&-Steinhardt decagonal
quasicrystal seed (one central rosette + a 10-fold ring of surrounding
rosettes, white strapwork bands between them). bikar's girih primitive, as
shipped, cannot author that field:
- single tile → no radius;
- manual `attach` → would need a hand-placed graph of ~50 tiles, none of which
  exist anywhere in the repo (grep found zero multi-tile girih `.bkr`);
- `subdivide` → decorative approximation, not the rosette field.

## Verdict: construction-philosophy CEILING (skill stop-rule #2)

This is NOT "girih variant 3 will fix it." Two consecutive girih iterations
plus the subdivide smoke all hit the same A6=0 floor for structurally
different reasons, all rooted in one fact: **the girih primitive can't
produce the full-radius multi-rosette field the baseline's zone bands were
derived from.** Per the iterate-construction-hypothesis skill, a
construction-philosophy ceiling triggers `present-options`, not another
variant. Decision doc:
`bikar/docs/decisions/2026-05-28-medallion10-girih-ceiling.md`.

iter-31's vocabulary win still stands — the girih primitive emits girih
shape types. The ceiling is about *field extent*, not vocabulary.
