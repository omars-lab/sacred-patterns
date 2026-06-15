# Iteration 1 Evaluation

## A1: Structure
- Segments: many (depth-2 repeat generates dense geometry)
- Faces: 71 bounded faces
- Strapwork: 8-unit width bands with alternating crossings

## A2: Symmetry
- Expected: 10-fold
- Observed: EXACT — 10 division points, connect every 4 + every 2
- Notes: symmetry looks correct structurally

## A3: Face Distribution
- Expected: kites, triangles, rhombi, pentagons, decagons
- Actual: mostly triangles and small polygons from dense intersection graph
- Match: PARTIAL — shapes exist but proportions differ from reference
- Missing: clear kite faces are not visually prominent

## A4: Coverage
- Expected: circular medallion with scalloped edge
- Observed: extends well beyond expected boundary — depth-2 repeat makes pattern very wide
- Gaps: no gaps, but pattern is too large / extends too far

## A5: Strapwork
- Expected: white interlaced bands
- Observed: COMPLETE — strapwork renders, bands are visible
- Crossings: correct over/under alternating
- Issue: band width may need adjustment

## A6: Visual Match
- Overall: ~30% structural match (despite 63.2% pixel similarity which includes background)
- Matching: 10-fold symmetry, blue palette, strapwork presence
- Non-matching:
  - Pattern extends too far (depth-2 ring-2 circles go way beyond reference boundary)
  - No clear satellite rosettes visible as distinct elements
  - Face coloring too uniform — reference has distinct color zones
  - Central star shape not prominent enough
  - No scalloped boundary (reference has circular outline with lobes)

## Convergence Metrics
- Similarity: 63.2% (baseline — first iteration)
- RMSE: 0.368
- Trend: N/A (first iteration)
- Heatmap: diff-heatmap.png shows major differences in boundary shape and face coloring
