---
name: bikar-face-walker-polygon-edge-absorbed-by-coincident-arcs
description: "bikar's face-extractor absorbs a polygon edge A→B when two arc-edges span the same endpoint pair; the polygon edge does NOT survive as a distinct DCEL boundary"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When a bikar `polygon` edge A→B shares both endpoints with one or more arc-edges (e.g., a lens whose two arcs span the same chord as a polygon edge), the face-walker absorbs the polygon edge: it greedily picks the arcs as boundary-closers for the lens halves, and uses the OTHER arc (not the polygon edge) to close the "triangle" face. The polygon edge A→B does not appear in any face's boundary. The expected 2-face split (triangle + lens) becomes a 3-face split with sides=(4, 4, 5).

**Why:** Tick 17 of qiyas#132 (2026-05-26, commit qiyas 293ad56). The scalene-and-lens-shared-edge template placed CL1 and CL2 on the perpendicular bisector of polygon edge AB at offsets +30 / -50, so both circles pass through A=(100,0)=C0.cpt0 AND B=(62.349,78.183)=C0.cpt1 (verified to 1e-6). Expected gt.json: 5 shapes (3 circles + 1 triangle + 1 lens). Actual: 3 shapes (3 circles only) — the classify-by-`sides==3`/`sides==2` rules matched zero faces because the actual emitted faces had sides=(4, 4, 5). Render.svg confirmed: `data-sides="4"` for both face-index=0/1 (lens-half + chord) and `data-sides="5"` for face-index=3 (the triangle absorbing one arc in place of edge A→B). Witness preserved at `qiyas/calibration/i1-corpus/templates/scalene-and-lens-shared-edge.bkr.tmpl` and `qiyas/calibration/i1-corpus/renders/scalene-and-lens-shared-edge/render.svg`.

**How to apply:**
- Before authoring a Tier 1 fixture where a lens-arc endpoint pair coincides with a polygon edge's endpoint pair, expect the face-walker to absorb the polygon edge.
- The arc-polygon shared-edge-endpoint-pair compositional dimension cannot be witnessed via current bikar DSL semantics. Two viable DSL extensions: (a) `connect arc ... on Circle` semantic that explicitly preserves a coincident polygon edge as a parallel DCEL edge; (b) a new `connect lens A -> B between C1, C2` lens-as-first-class-primitive form that doesn't depend on shared chord geometry.
- For Tick 17-shape problems (lens topology + adjacent polygon), pivot to single-shared-vertex (Tick 16, which DID work cleanly) or to lens-disjoint-from-polygon (Tick 14) instead.
- Do not try to work around this by jittering one endpoint off the polygon vertex — the witness contract REQUIRES exact coincidence; near-coincidence is a different topology with its own absorption pattern.

**Companion to:** [[feedback_classify_by_predicate_cannot_witness_same_class_cross_refs]] (qiyas#132 Tick 9 + Tick 15 — DSL extensibility gap from a different angle), Tenet 7 (don't tune to fit), Tenet 17 (prove the primitive first — this is a Tier 1 primitive whose own implementation gap was hidden until exercised), Tenet 18 (codify every debug witness — falsified render.svg + gt.json are the witness).
