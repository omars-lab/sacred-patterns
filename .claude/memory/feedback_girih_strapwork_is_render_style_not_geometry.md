---
name: girih-strapwork-is-render-style-not-new-geometry
description: A5 band-crossing integrity flips 0→COMPLETE by rendering the SAME girih decoration lines as woven bands instead of filled faces; no new tile geometry needed
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

For girih patterns, A5 (strapwork band-crossing integrity, qiyas svg-audit) is a
RENDER-STYLE concern, not a geometry concern. The girih tile PLANE (decagon +
bowtie + hexagon tiling) and the woven STRAPWORK (lines through tile-edge
midpoints → over/under bands) are TWO INDEPENDENT LAYERS. A field can be
gap-free (A4 high, A1 clean, fold detected) yet score A5=0 if its decoration
lines are rendered as filled FACES rather than woven BANDS — A5 counts
`lens`/`band_crossing` shapes in the qiyas encoding, which filled faces don't
produce.

**Why:** medallion-10 iter-33 (`girih field` + `voids detect` + `fill void`)
scored A5=0 BROKEN with 0 crossing shapes. iter-34 changed ONE thing — replaced
`voids detect`+face-fills with a `strapwork width 4 crossing alternating`
statement over the SAME decoration segments — and A5 went to COMPLETE (100),
2825 crossings detected (348 lens + 2477 band_crossing). bikar already had the
machinery (`computeStrapwork`/`detectCrossings`/`assignStrands` in
strapwork.ts); the girih field already emitted the {10/3} decoration segments
via `girihTileSegments(tile, !bare)`. The only missing piece was a `strapwork`
DSL statement to invoke the weave. No new tile geometry, no pocket-filling
(which was the originally-assumed Slice-4 work — turned out NOT needed: the
Slice-4 plan's own trigger says pocket-filling only ships "if Slice 3 shows the
unfilled pockets cost score," and they didn't). (2026-05-28)

**How to apply:** When a girih/strapwork construction scores A5=0 (or any
"band-network BROKEN" verdict) but is otherwise geometrically sound (A1/A2/A4
healthy, fold detected), do NOT reach for new geometry/pocket-filling first.
Check the RENDER STYLE: are the decoration lines filled faces or woven bands?
Add a `strapwork <width> crossing <alternating|over|under>` statement to weave
the existing decoration crossings. Validate atomically first (Tenet 17):
`girihTile('decagon',...)` → `girihTileSegments(tile,true)` →
`buildIntersectionGraph` → `computeStrapwork` should yield degree-4 crossings
woven into strands with BOTH isOver=true and false (see
`packages/core/tests/kernel/girih-tiles.test.ts`).

**Companion to:** Tenet 26 (extend DSL when construction fights the language — here the DSL already had the primitive, just wasn't invoked), Tenet 24/25 (render-and-look), [[feedback_check_emit_layer_before_option]] (the fix was an invocation/emit-layer change, not an evaluator-semantics change).
