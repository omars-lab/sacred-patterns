# iter-31 visual verdict (Tenet 27 — eyeballed BEFORE reading the score)

**Pre-stated expectation (from hypothesis.md):** a single decagon outline
centered at origin, with internal {10/3} strapwork decoration forming a
10-pointed star at the center and a ring of rhombus/kite decoration faces
between the star and the decagon edge. No white-band interlace expected.

**What rendered (render.png):**
- Decagon outline present (gold `tile_field`, 10 sides) ✓
- 10-pointed blue star ring present (the {10/3} decoration crossings,
  classified `decoration_rhombus` ×40 + `decoration_kite` ×20) ✓
- **Center is a single ivory polygon, NOT a nested v20 star** ✗ (partial)

**Divergence = bug-locator:** the decagon's {10/3} decoration (midpoint
i → i+3, per DECORATION_PAIRS in girih-tiles.ts) crosses to form the
blue star ring but encloses a central *decagonal void* — it does not
pierce to a central point. This is the CANONICAL girih {10/3} behavior,
not a defect: the central decagon void IS the inner field in a single
unsubdivided tile. The baseline's `inner-star--star-v20` (dist 0.00-0.07,
qiyas type hankin_star) is a DEEPER nested star that requires `subdivide`
(nesting a smaller decagon tile at center) — that is an iter-32 refinement,
not an iter-31 failure.

**Verdict: PASS for the Tier-0 probe.** The girih primitive produces
explicit girih vocabulary (10-point star ring, rhombus + kite decoration
faces) that the chord-overlay construction categorically could not. This
confirms the construction-philosophy switch is viable and the primitive
is shipped + working. Per Tenet 17, the central tile is proven; iter-32
composes the attachment ring (`attach <name> edge <N>`) + iter-33 adds
`subdivide 1` to grow the central nested star toward star-v20.

31 faces total: 2 central_star (blue star-point bands), 40
decoration_rhombus, 20 decoration_kite. face_class emitted per Tenet 23.
