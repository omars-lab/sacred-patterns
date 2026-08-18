---
name: one-rasterizer-per-comparison
description: Pixel comparisons across iterations are only valid when every image went through ONE rasterization path — mixed rasterizers produce phantom metric drift at all radii
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2527d0a7-dce7-442b-9a81-2d40b2ae42f5
---

Iter-49 (medallion-10 wave 7, 2026-06-11): wave-diff holds drifted vs the iter-48 verdict (wave-1 coverage −7.5, wave-2 iou +9.5) at ALL radii. ViewBox and structure checks falsified the geometry suspects; side-by-side center crops showed iter-48's on-disk render.png came from a softer/blurrier rasterizer than the cairosvg raster of iter-49. Re-rastering iter-48's SVG through the identical cairosvg call collapsed the drift — waves 1–4 bit-identical.

**Why:** anti-aliasing/blur width changes which pixels clear the near-white ink threshold, so a rasterizer swap shifts coverage/iou everywhere simultaneously — it masquerades as global geometric regression.

**How to apply:** never compare PNGs of unknown rasterizer provenance. Canonical path for the medallion-10 wave loop: cairosvg, `output_height=1024`. Root-cause fix shipped per tenet 2: `sacred-patterns/tools/wave-diff.py` (commit 99cad3d) accepts `--render render.svg` and rasterizes internally — always pass the SVG. A "drift at all radii / all waves at once" signature is the tell: suspect the raster layer before the geometry. Companion: [[feedback_mirror_ci_locally]] (tenet 11 — one tool path per question).
