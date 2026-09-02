# Iteration 6 Evaluation

## Context
- Approach: hankin angle 54 for center + hankin angle 54 on all 10 ring-1 circles (@0.0 through @0.9)
- Refinement of iter 3 (best structural result so far) with better color mapping
- Engine fix applied: core/dist Docker volume mount to serve latest parser

## A1: Structure
- Segments: 432
- Faces: 91 (bounded)
- Face catalog: needs programmatic check, visually shows mix of kites, triangles, pentagons

## A2: Symmetry
- Expected: 10-fold
- Observed: EXACT — all structures repeat every 36°
- Notes: clean 10-fold rotational symmetry

## A3: Face Distribution
- Expected: kites (inner ring), triangles (star tips + satellite tips), pentagons/decagons (centers)
- Actual: mix of kites, triangles, and larger polygons visible
- Match: PARTIAL — face types present but distribution differs from reference
- Missing: satellite centers should show distinct decagonal voids

## A4: Coverage
- Expected: full medallion with scalloped boundary
- Observed: PARTIAL — pattern extends to full medallion size but boundary is angular, not scalloped
- Gaps: boundary region lacks the smooth scalloped edge of the reference

## A5: Strapwork
- Expected: white bands, ~5-7px width, interlaced
- Observed: COMPLETE — white strapwork bands weave through all zones
- Crossings: correct alternating over/under

## A6: Visual Match
- Overall: 45% estimate
- Matching regions:
  - Central 10-pointed star shape ✅
  - White strapwork band network ✅
  - 10-fold symmetry ✅
  - Blue color scheme ✅
- Non-matching:
  - Satellite rosettes not visually distinct — hankin rays merge into one connected web
  - No scalloped boundary
  - Color gradient not matching — too uniform navy, needs more turquoise at outer tips
  - Inner kites narrower than reference
  - Missing the distinct "mini-star" appearance of each satellite

## Key Differences (bulleted)
- Satellites: reference has 10 clearly distinct mini 10-pointed stars; iter 6 has a connected outer web
- Boundary: reference has smooth scalloped (circular arc) boundary; iter 6 has angular edges
- Color: reference shows smooth navy→royal→cobalt→turquoise gradient; iter 6 is mostly navy/royal
- Inner ring: reference kites are wider and more prominent
- Interstitial zone: reference has clearly defined face shapes; iter 6's interstitial is less organized

## Engine Gaps Discovered
- **Core/dist Docker mount** — RESOLVED: added `./packages/core/dist:/app/packages/core/dist` to docker-compose.yml volumes. Without this, Docker container serves stale parser that lacks recent features (e.g., strapwork `color`, `connect every K on`).
- **Satellite isolation remains the core challenge** — hankin on ring-1 circles produces connected geometry, not isolated mini-stars. This is a construction technique limitation, not an engine bug.

## Structural Comparison (vs reference checklist)
- [x] Symmetry order: 10-fold ✅
- [x] Central motif: star with decagonal void ✅
- [x] White strapwork bands ✅
- [~] Satellite rosettes: outer structure present but not visually distinct as 10 individual stars
- [ ] Scalloped boundary: not present
- [~] Color gradient: improved but still too uniform
- [x] Band continuity: bands weave through all zones ✅
