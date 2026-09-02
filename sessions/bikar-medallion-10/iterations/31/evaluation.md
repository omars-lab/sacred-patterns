# iter-31 evaluation — central girih decagon tile (Tier-0 probe)

**Construction change (detector untouched):** switched construction
PHILOSOPHY from chord-overlay to girih tiling. Single statement:
`girih decagon 61.8` + classify rules. No detector threshold touched.

## Scores (vs iter-30)

| metric | iter-30 | iter-31 | note |
|--------|---------|---------|------|
| composite | 3/5 | 2/5 | expected drop — single tile has no medallion |
| A1 match% | 100 | 100 | semantic census still valid |
| A2 fold | 85 | 0 | single tile → no repeated sectors to score |
| A4 coverage% | 100 | 96 | tile fills its own bbox |
| A5 band | 100 | 0 | no band network in a bare tile |
| A6 pass | 0/18 | 0/18 | unchanged — see below |

## The signal (why this is NOT a falsification)

The probe's purpose (per hypothesis.md): does the girih primitive emit
girih vocabulary the chord-overlay categorically couldn't? **YES.** The
encoder's shape census on iter-31:

- `rosette` ×1  ← girih star center; chord-overlay NEVER produced this
- `decagon` ×1  ← explicit decagon frame
- `regular_polygon` ×20, `isoceles_triangle` ×10  ← decoration faces

iter-30's chord-overlay census had ZERO `rosette` and ZERO `decagon`
types. This is the construction-philosophy switch working exactly as the
feedback_a6_baseline_construction_philosophy_mismatch UPDATE predicted.

## Why A6 stayed 0/18 (the Tier-0 ceiling, not a defect)

`candidates_in_zone = 0` for ALL 18 expected shapes (vs iter-30 which had
4–80 candidates landing in zones). Root cause: **a single central tile has
no full-radius medallion extent.** The A6 audit normalizes shape distances
to the render's bbox radius (331px here). With only the central tile
present, every detected shape sits at a normalized distance that misses
the baseline's zone bands (inner-star 0.0–0.35, rosette 0.35–0.55,
transition 0.55–0.86, outer 0.86–1.0). The tile fills ~the whole bbox, so
its decoration faces land near r≈0.3–1.0 of *its own* bbox — not the zone
structure of a full medallion.

This is precisely the Tier-0 result Tenet 17 expects: prove the primitive
renders correct vocabulary (DONE — `rosette`+`decagon` detected) BEFORE
composing it into the zone-structured full medallion. A6 cannot score on a
single tile; it needs the ring.

## Verdict: PASS for Tier-0. Proceed to iter-32 (composition).

The primitive is proven. iter-32 composes the attachment ring: a central
decagon + 5 or 10 decagons attached edge-to-edge via `attach <name> edge
<N>`, with bowtie/hexagon connectors filling the gaps (the canonical
Lu-&-Steinhardt decagonal medallion). That produces the full-radius
medallion with zone-distributed star vocabulary, which is what A6 scores.

**Falsification guard (skill stop-rule 1):** iter-31 is NOT a falsified
variant — it is the FIRST girih iteration and it confirmed the hypothesis
(girih vocabulary emitted). The "same approach falsified twice" stop rule
does not apply. iter-32 is a DIFFERENT construction (composition), not a
re-tweak of iter-31.
