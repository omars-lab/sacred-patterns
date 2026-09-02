# Discoveries — bikar-medallion-10

## Confirmed Facts
1. Pattern has 10-fold rotational symmetry (iter 1)
2. {10/4} star polygon creates the primary star structure (iter 1)
3. Strapwork with alternating crossings renders correctly on this geometry (iter 1)
4. Blue palette (5 shades) matches the reference's color range (iter 1)
5. The reference pattern is BAND-DEFINED — white strapwork bands are the structure, colored faces are spaces between bands (iter 2)
6. `connect every 4` alone produces the correct face catalog: 20 kites + 10 triangles + 1 decagon center (iter 2)
7. Pixel similarity is a false metric — structural evaluation (face catalog, zone analysis) is the correct approach (iter 2)

8. `hankin angle 54 on @0.N` successfully creates satellite rosettes at ring-1 positions (iter 3)
9. Layer isolation works: central star (layer 0) + satellites (layer 1) don't interfere (iter 3)
10. Interstitial zone (rhombi, 9-gons) forms naturally at the overlap between central and satellite geometry (iter 3)

## Working Assumptions
1. Satellite rosettes need separate construction, not just inherited repeat
2. Layers may be needed to isolate satellite geometry from central pattern
3. The scalloped boundary may need a clipping mechanism or polygon outline
4. Face-type-based coloring (sides == N) will be more accurate than ring-based

## Disproven Assumptions
1. ~~Simple depth-2 repeat produces satellite rosettes~~ — it just extends the star pattern without creating distinct rosette motifs (iter 1)
2. ~~Adding connect every 3 improves face structure~~ — it clutters the pattern with too many intermediate faces, regression from 63.2% to 61.4% (iter 2)
3. ~~edges from decagon needed for boundary~~ — creates a face not in the reference, user confirmed this is wrong (iter 1 feedback)

## Confirmed Facts (continued)
11. `hankin angle 54 on @0.0` through `@0.9` produces 91 faces with full medallion coverage (iter 6)
12. Docker container needs `core/dist` volume mount to serve latest parser features — without it, stale `dist/index.js` causes parse errors for new syntax (iter 6)
13. Hankin on adjacent ring-1 circles produces MERGED geometry, not isolated satellites — rays from @0.0 intersect with rays from @0.1, creating a connected web (iter 6)

14. **BREAKTHROUGH (iter 7):** `connect every 4 on @0.N` + `radius 0.3 * $radius` + layers = 11 DISTINCT rosettes! Each satellite has proper {10/4} decomposition: 20 kites + 10 triangles + 1 decagonal void.
15. 0.3 * $radius is the sweet spot: satellite diameter (60) < inter-satellite center distance (61.8) prevents overlap
16. `hankin angle 54` does NOT work on small circles — rays too short to self-intersect, producing just polygon outlines (22 faces at 0.5x)
17. `connect every 4` DOES work on small circles — full chords always self-intersect within the circle

## Answered Questions
1. ~~How to construct distinct satellite rosettes?~~ → `connect every 4 on @0.N` with `radius 0.3 * $radius` in a separate layer (iter 7)
4. ~~Same {10/4} as center?~~ → YES, `connect every 4` produces the same star on any circle
5. ~~Would reducing radius isolate?~~ → YES, 0.3x is the sweet spot (iter 7)

## Open Questions
2. How to create the scalloped boundary outline?
3. What is the exact construction for the interstitial zone between center and satellites?
6. Would per-sector explicit construction (one 36° wedge, rotated 10x) fill the interstitial zone?
7. Should center star also use `connect every 4` instead of hankin for visual consistency? (iter 7)
