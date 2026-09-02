---
attempt: 38
date: 2026-06-10
gap_targeted: "Color-role mapping — iter-37's verdict routed this first: the new large lens faces (and several whole classes) wear the WRONG fill family. 63% of faces were in the palest class (#BBC5D5) while the reference shows saturated cyan and navy in the same zones."
construction_hypothesis: "Measured role transfer, not guessed (the iter-36 discipline): resized the reference to the render's 996×1024, sampled a 5×5 median at every face center from iterations/37/pattern.gt.json, bucketed per class × size × source against 5 palette anchors. Findings: (a) `.royal` (sides==4 kites) matches royal at only 8/120 centers but NAVY at 50/120 — the kites should be navy; (b) `.cobalt` big pentagons (sides==5, area≥~500px²) match cyan at 0/60(!) but royal at 20/60 — big pentagons should be royal; small pentagons (10) stay cyan (cyan 5/10); (c) the in-lens big 3-sided faces (sides==3 AND area big AND source == _girih_hexagon, ~40 faces) are the reference's colored pocket zone (cyan 14 + navy 15 vs white 9) — they get the saturated cyan the verdict's eye named; (d) `.turquoise` small and `.navy` stay — their best single color is what they already render (small faces sit under white straps in both images; recoloring the navy star centers white would chase center-pixels while destroying the eye-approved rosette reading — the metric-temptation guard applies)."
bkr_change: "Fill-rule pass only, no geometry: add first-match fill `sides == 3 and area >= 360 and source == _girih_hexagon → #32B0CA` (lens pockets cyan) + matching classify .pocket; change sides==4 fill royal→navy; split sides==5 into big→royal / small→cyan. Palette, blueprint, girih field, strapwork untouched."
predicted_lift: "+0.5–1.5 pixel similarity (74.2% → ~74.7–75.7%). Gut number halved per three consecutive over-predictions. Center-match accounting: ~67 of 844 faces flip from wrong to right at their centers (royal→navy +34, cobalt-big→royal +20, royal-sml +7, pockets +6), area-weighted toward big faces. Color-match % should rise more than pixel %."
predicted_cost: "Two named risks to look for in the render: (1) the kites going navy may read darker than the reference's overall key if the white straps don't break them up enough; (2) the in-lens cyan is a coin-flip with navy at measured centers (14 vs 15) — if the render shows cyan where the reference clearly shows navy sub-shapes inside lenses, the residual routes to a lens sub-role split (center face vs side faces), which needs a NOT-source or adjacency selector the DSL may not have yet."
prior_art_searched: "iter-36 hypothesis/verdict (palette histogram method — this reuses its measurement discipline at face-center granularity); iter-37 verdict (routed this gap and suggested the _girih_hexagon source-tag selector used here); bikar docs/language-reference.md fill attributes (sides/area/source all supported, first-match-wins confirmed in fill-resolver.ts)."
related_memory: "feedback_metric_temptation_at_plateau (named explicitly in (d): the white-majority buckets are NOT recolored because that would move the metric while breaking the eye-approved structure); feedback_decomposition_order (structure shipped in iter-37; this is the color pass that order called for)."
detector_untouched: "confirmed — no qiyas param/threshold/cost in this iteration"
---

## Plan

Why this gap: routed #1 by iter-37's verdict, and it is the residual that
iteration predicted ("wrong fill class on the new lens faces").

Why this hypothesis: every remap is backed by a face-center sample table
(844 faces, 5×5 median, 5 anchors); moves where the measurement was a
white-dominated mush were explicitly declined rather than tuned.

Expected visual (written BEFORE viewing any render — Tenet 24): same
geometry as iter-37, with three color shifts — the kite ring around every
rosette turns from mid royal-blue to dark navy; the big pentagons between
kites turn from saturated cyan to royal; the large faces inside each
between-rosette lens turn from pale grey-white to saturated cyan, so the
lens zones finally read as colored pocket-stars instead of blank parchment.
Small triangles and the white strap lattice are unchanged. Failure
signatures to watch: the render going overall darker than the reference
(risk 1), or cyan lenses against clearly-navy reference sub-shapes (risk 2).

## Guardrails check

- Construction edit only (.bkr fill/classify rules); qiyas untouched: yes.
- Construction-philosophy memory checked — not a falsified approach: yes —
  fill-rule remap on measured evidence is the iter-36 method, which landed
  its predicted direction.
- predicted_cost names concrete failure modes to look for: yes — overall
  darkening; cyan-vs-navy sub-role inside lenses.
