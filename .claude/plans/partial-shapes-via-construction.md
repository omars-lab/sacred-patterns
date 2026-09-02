# Partial-shape rendering via construction (qiyas + bikar)

> **Decision doc:** the option weighing for this work has been promoted to
> [docs/decisions/2026-05-07-partial-shape-rendering-via-construction.md](../../docs/decisions/2026-05-07-partial-shape-rendering-via-construction.md)
> (PROPOSED, awaiting owner pick). This plan stays as the *concrete observations*
> and *target shape* for Option A; the decision doc is where the alternatives
> (B qiyas-only, C bikar-only, D manual baseline edits) are weighed and where
> "what would change this recommendation" lives.

> **Leverage status — 2026-05-20:** Cascade shipped (bikar schema 1.19 + qiyas
> partial_polygon detector + sacred-patterns iteration-guide row), but
> **predicted CLIPPED-MISSING leverage on iter-14 medallion-10 is unrealized**
> on the rasterize→trace path: residue extractor emits 110 two-to-four-vertex
> fragments that starve the detector (witness: qiyas#371). Resolution path is
> ACCEPTED Option E in
> [qiyas/docs/decisions/2026-05-20-partial-polygon-residue-starvation.md](../../../qiyas/docs/decisions/2026-05-20-partial-polygon-residue-starvation.md):
> defer to B1 Option B (qiyas#398, render.svg-direct path) landing, then
> re-measure. If the new path naturally produces un-fragmented residue, the
> detector fires and this cascade's leverage is validated post-B1 — without
> further qiyas code change. If it still starves, Option A (LineAggregate
> provenance refactor) becomes the next path. Until then, *do NOT assume this
> cascade delivers the predicted lift on raster-traced inputs.*

## The problem

Side-by-side: reference vs iter-14 recon (medallion-10).

The reference shows **partial / clipped shapes** at every interior boundary:
- Where two satellite rosettes meet, the rosette tips that *would* extend into the neighbor's territory are rendered as **half-rosettes** (clipped along the shared chord).
- Where the medallion outer boundary cuts through a satellite, the partial wedge is still drawn (a slice of the rosette).
- Where the central rosette meets the satellites, the inter-satellite gap is filled with a **partial pattern** — typically a clipped tip of an imagined satellite that "would" sit in that gap.

Our BKR renders only the **whole shapes within their natural circle** (each satellite rosette is contained inside its 0.3·R circle, and edges that cross outside are not drawn). The void detector then fills the bare in-between regions with whatever flat polygon happens to fall there.

This is the dominant remaining mismatch and explains a large fraction of:
- A6 MISSING shapes (the partial half-rosette tips would register as 6/8/14-vertex stars)
- A5 BROKEN bands (the bands continuing into adjacent satellites are missing)
- pixel similarity plateau at 74% (large bare regions where ref has structure)

## Why it's a shared qiyas/bikar deficit

**Bikar can't currently express the construction:** the DSL has `repeat at C0 depth D` to grow circles outward, but no idiom for "extend each construction circle's reach so its edges intersect neighboring circles, then clip the union to the medallion boundary." Each `connect every K on C` is bounded by the division points of C — you can't ask for "the edges of C's star polygon that fall inside circle C'."

**Qiyas can't currently *describe* the missing construction:** A6 reports "inner-star--star-v8 MISSING (0/6)" but doesn't say *why* — is it because we never drew an 8-pointed star anywhere, or because we drew one that got clipped away by a clipPath, or because two intersecting rosettes *should* have produced an 8-pointed star at their intersection but we didn't construct the intersection? The current encoding loses this information.

This is the user's exact framing: "make the proper shapes in blueprint and connect the proper vertices, not by directly drawing them." We need a construction primitive that says *"vertex set X exists; trace the polygon that would form if extended; clip it to the visible region."*

## Concrete observations from medallion-10

Looking at the reference, the partial-shape mechanism appears to be:

1. Each satellite's construction circle (radius 0.3·R, centered at one of the C0.cpt points) extends *beyond* its physical extent — its star edges continue into neighbor space.
2. Where two satellite circles' star edges meet, they share intersection points. A new shape is implied at those intersection regions: an 8-pointed star (between two adjacent satellites) and a 4-pointed rhombus (where their edges cross the central rosette's outer edge).
3. The medallion's outer boundary clips everything to its overall silhouette, leaving the *partial* shapes visible.

In BKR this would look something like:

```
# Hypothetical syntax — does NOT exist yet
boundary medallion_outline = union(C0_satellite_circles)
extend connect every 3 on @0.* clip-to medallion_outline
intersect @0.0 with @0.1 to detect inter-satellite-shapes
```

This is mostly **missing primitives**, not a missing parameter.

## What needs to change

Three coupled work-items, in priority order:

### qiyas side: A "partial-shape" verdict in A6

Today A6 returns PASS / PARTIAL / MISSING / EXCESS based on count. Add a new verdict **CLIPPED-MISSING**: distinguishes "no construction even attempted" from "construction exists but got clipped away." Indicators:

- `inner-star--star-v8 MISSING` *and* the recon has 8-vertex partial-shape edges in that zone (>= ~half the expected vertex count visible) → CLIPPED-MISSING (the ref shape is partially formed at that location but not a complete polygon).
- vs. `MISSING` with no partial edges in zone → genuinely absent construction.

This requires the encoder to detect *partial polygons* — paths that look like they would close into an N-vertex shape if extended. Likely implementable as: "polylines whose endpoints fall on the zone boundary and whose interior arc subtends an angle consistent with an N-fold construction."

The point: turn vague "MISSING" into actionable "CLIPPED-MISSING — extend construction beyond its natural bounds."

### bikar side: Construction-extension primitives

DSL additions (smallest viable set, in dependency order):

- `boundary <name> = union(<set of circles>)` — define a clip region as the union (or intersection, or convex hull) of named circles.
- `extend <connect-statement> beyond <radius_multiplier>` — apply a `connect every K on C` but generate the star polygon edges from a *virtually-larger* C, then clip to whatever boundary is active. This lets satellite stars "reach into" their neighbors.
- `intersect <circle-set> at radii [r1, r2, ...]` — emit auxiliary intersection points where construction circles overlap, addressable as `@intersect.0`, `@intersect.1` for subsequent `connect cycle` statements.
- `clip pattern to <boundary>` — apply medallion-silhouette clipping after voids detect, so the outer partial-rosette tips remain visible.

These four primitives let the construction "imagine" the extended pattern and then clip to what's visible — exactly the mechanism the reference uses.

### sacred-patterns side: warning-translation table row

Once qiyas emits `CLIPPED-MISSING` and bikar exposes the four primitives, the iteration skill's translation table gains a row:

| qiyas warning | DSL idiom |
|---|---|
| `A6 ... CLIPPED-MISSING vertex_count=N in zone Z` | extend the relevant `connect every` beyond its natural radius; add `clip pattern to medallion_outline` |
| `A6 ... MISSING vertex_count=N in zone Z` (with no clipped edges) | (current) add construction at expected radius |

## Sequencing

This is **not** the next iter-16 directive — it's a multi-week qiyas+bikar feature. Iter 15 is rendering now (strapwork); iter 16 should chase whatever warnings[0] surfaces under the new strapwork-rendered baseline. The partial-shapes work runs in parallel:

1. **qiyas#NEW-A** (1-2 days): partial-polygon detection in encoder + CLIPPED-MISSING verdict in A6.
2. **bikar#NEW-A** (3-5 days): the four DSL primitives. Sequence: `boundary` → `extend` → `clip pattern` → `intersect` (the last is hardest and may be deferred to a follow-up).
3. **sacred-patterns#NEW** (≤1 hr): translation table row + iteration-guide note.

Once all three land, iter-N+1 (whatever iteration we're on then) will get a `CLIPPED-MISSING` warning that maps directly to a one-line `extend ...` edit. That single edit could plausibly close the largest single gap remaining (the inter-satellite partial-shape regions), which from the visual diff looks like 30-40% of the bare-region pixels.

## What we shouldn't do

- **Don't draw partial shapes literally in BKR** (e.g. `polygon "half-star" vertices [...]`). That would be tenet 5 violation (parallel structure to the construction system) and tenet 1 violation (over-specifying instead of finding the smaller primitive that does the job). The whole point of construction is that you describe the *generative* rule, not the resulting pixels.
- **Don't expand baseline.json with partial-shape entries** until qiyas can detect them. The baseline today says "expect 6 v8 stars in inner-star zone"; if 4 of those are partial in the reference, that's qiyas's responsibility to discover at encoding time, not the human's responsibility to enumerate by hand.
- **Don't conflate this with strapwork.** Strapwork is a *render-style* transformation (replace lines with parallel band-pairs); partial shapes are a *construction-extent* problem (how far do construction edges reach). Iter 15 tests the strapwork hypothesis; this plan tests the construction-extent hypothesis. Both can land independently.

## Verification

When all three pieces are in place, re-validate iter 14 (the pre-strapwork baseline). Expected:
- A6 inner-star--star-v8: MISSING → CLIPPED-MISSING (qiyas now distinguishes)
- After applying the `extend` edit: CLIPPED-MISSING → PASS, plus collateral gains in v6/v14/v20 that share the same intersection mechanism
- composite +0.05 to +0.10 from a single edit (the leverage the qiyas#75 warning ranker has been waiting for)

## Cross-repo dependencies

- qiyas: new encoder feature + new A6 verdict (touches stages/encoder + svg_audit/a6.py)
- bikar: 4 new DSL primitives (touches parser + compiler + scene-graph)
- sacred-patterns: 1 translation row + 1 iteration-guide note

Add these to `docs/cross-repo-dependencies.md` under a new "partial-shapes via construction" section.
