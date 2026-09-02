# Iteration 39 — Hypothesis

```yaml
attempt: 39
date: 2026-06-10
gap_targeted: >
  Structural gap routed by iter-38's verdict: the reference shows genuine star
  motifs inside every decagon-overlap lens, but iter-38 poses hexagon tiles
  with the fixed 3-chord pair-table decoration. Two color passes moved
  color-match +2.6 while pixel similarity stayed flat — the construction could
  not express the star. The engine gap was closed in bikar a0680d8
  (`pockets star` → Hankin 54° star motif, tag `_girih_hexagon_star`).
construction_hypothesis: >
  Swapping the lens hexagons' 3-chord motif for the Hankin 54° star
  (`pockets star`) and retargeting the pocket fill/classify rules to the new
  `_girih_hexagon_star` source tag will recover the lens-interior structure
  the reference shows: each of the 130 lenses becomes a saturated-cyan pocket
  with a white strapwork star band woven through all 6 lens-edge midpoints.
bkr_change: >
  Three deltas from iter-38's pattern.bkr (one construction idea — the star
  motif; the fill/classify retarget is forced by the tag rename, not a second
  idea):
  (1) `girih field decagonal 62 shells 2 pockets` → `... pockets star`;
  (2) `classify .pocket where source == _girih_hexagon_star` (drop the
      sides==3/area>=360 guards — they described the OLD 3-chord face
      vocabulary; the star vocabulary is ~7 faces per lens: 1 inner star
      decagon + 4 corner quads + 2 corner triangles);
  (3) `fill void where source == _girih_hexagon_star color cobalt` stays the
      FIRST fill rule (first-match-wins).
predicted_lift: >
  +0.5 to +1.5 pixel similarity (gut halved per over-prediction history;
  74.2 → ~74.7-75.7). Color match +0.5 to +1 (67.8 → ~68.3-68.8): the
  saturated cyan #32B0CA returns to the lenses — iter-38's star-tag fallout
  during the composite check showed lens faces falling through to pale
  turquoise #BBC5D5, which this retarget fixes.
predicted_cost: >
  (a) Cyan-everywhere inside the lens may overshoot if the reference shows
  navy inner stars with cyan only in the corner pockets — residual would
  route to a sub-role split using the new `!=` comparator in iter-40.
  (b) Strapwork width 8 may be too thick at lens scale and swallow the tiny
  corner triangles at the 72° lens corners.
  (c) More small faces under bands → speckle risk in the pixel diff.
prior_art_searched: >
  iter-38 visual-verdict.md (routing #1 = star motifs in lenses);
  bikar plan .claude/plans/vectorized-squishing-pearl.md (Gap 1 design:
  Hankin 54° = decagon {10/3} tangent-chord angle, motif joins the
  decoration network so the strapwork weaver weaves it);
  composite verification in /tmp/m10-star (130 lenses confirmed:
  1300 star segs / 10; star variant also cleans a degenerate speckle zone
  the 3-chord motif produced).
related_memory: feedback_metric_temptation_at_plateau.md
detector_untouched: confirmed — qiyas frozen; construction-side edits only.
```

## Expected visual (stated BEFORE viewing the render — Tenet 24)

Each of the 130 lenses reads as a saturated-cyan (#32B0CA) pocket with a
white strapwork star band woven through all 6 lens-edge midpoints — 4 star
points at the 144° corners, 2 straight midpoint chords at the 72° corners.
Rosettes, kites, pentagons, and the field outside the lenses are unchanged
from iter-38.
