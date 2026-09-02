# Iteration 6 Retrospective

## What Worked
- hankin angle 54 on all 10 ring-1 circles produces a full medallion with 91 faces — good density
- White strapwork bands render correctly through all zones
- 10-fold symmetry is exact
- Color mapping improved from previous iterations — graduated blues visible
- Docker core/dist mount fix ensures latest parser features are available

## What Didn't Work
- Satellite rosettes still not visually distinct — hankin rays from adjacent ring-1 circles merge at shared intersection points, creating one connected web rather than 10 isolated mini-stars
- Scalloped boundary still absent — no mechanism to clip or mask the pattern boundary
- Color distribution too uniform — need more turquoise at outermost faces

## Hypotheses Updated
- CONFIRMED: hankin on ring-1 circles produces better results than connect every 4 on (540 faces = too dense) or layer isolation (faces can't close)
- CONFIRMED: 91 faces is a reasonable density for this pattern (vs 540 from iter 5)
- DISPROVEN: simply listing all 10 `hankin angle 54 on @0.N` produces isolated satellites — they still merge
- NEW QUESTION: would a smaller satellite circle radius (e.g., repeat at C0 depth 1 with radius 0.8*$radius) produce more compact, isolated satellites?
- NEW QUESTION: would per-sector explicit construction (define one wedge of tiles, rotate 10x) solve the satellite isolation problem?
- NEW QUESTION: can we add a scalloped boundary via a clip-path or by detecting the convex hull of outermost face centroids?

## Plan for Iteration 7
Priority: **satellite isolation** (A3/A6 failures) — this is the single biggest visual difference

Candidate approaches (in order of effort):
1. **Reduce satellite radius** — try `radius 0.7 * $radius` in the repeat block to make satellite circles smaller and further apart, reducing ray overlap
2. **Per-sector construction** — define one 36° wedge explicitly using `connect cycle` statements, then rotate 10x. Most precise but most verbose.
3. **Mixed construction** — hankin for center, explicit interstitial tiles via `face` statements for the zone between center and satellites
4. **Scalloped boundary** — attempt after satellite isolation is solved (lower priority per G2)
