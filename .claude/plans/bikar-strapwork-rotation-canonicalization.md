# Bikar: rotation-canonicalize strapwork strand assignment

**Status:** RESOLVED 2026-05-25 — PR1 sufficient.
PR1 shipped bikar `8bc6735` (canonicalEdgeOrder).
Slice 2 end-to-end validated via medallion-10 iter-23: A2 cv 0.2671 (iter-16 BROKEN) → 0.0526 (UNEVEN, below iter-14's 0.067 baseline); A5 BROKEN → COMPLETE.
PR2 (orbit detection per approach B) NOT triggered — PR1's centroid+angle sort handles 10-fold polar geometry cleanly.
PR3 (Hankin face-walk per Kaplan 2005) remains deferred per the original plan; trigger remains "future patterns where face-based bands are visually preferable."
See `~/Dropbox/Data/sacred-patterns/bikar-medallion-10/iterations/23/evaluation.md` and `sacred-patterns/CHANGELOG.md` 2026-05-25 entry.

---


## ⚠️ Pre-check required (2026-05-03 — band-construction literature review)

This plan assumes the right model for strapwork in bikar is "post-process an EdgeGraph into strands." That model comes from how bikar already implements strapwork. The Islamic-strapwork literature (Hankin polygons-in-contact, Kaplan 2005, Bonner & Kaplan 2017) describes a **different** construction:

1. Tile the surface with polygons in contact.
2. At the midpoint of each shared polygon edge, sprout two rays at the contact angle (often the "ideal angle" 90°−180°/N — bikar's evaluator.ts:639 already knows this).
3. Rays grow until they meet other rays; X-shapes at meeting points become crossings.
4. Discard the original tiling; the remaining ray segments ARE the band centerlines.
5. Stroke each centerline by ±width/2 to render the band.

In Hankin-PIC, the EdgeGraph the strapwork algorithm operates on is built FROM the geometry, not asserted by the user. The crossing structure is a property of where rays meet, which is determined by the polygon tiling and the contact angle.

For medallion-10, the EdgeGraph fed to bikar's strapwork comes from `connect every K on Cn` — concentric decagrams. These are NOT Hankin midpoint-rays; they're radial chords on circle division points. The 247 extras in iter-15/16 may not be a bug in `assignStrands` rotation invariance — they may be the algorithm correctly turning the wrong input topology into bands.

**Open task #115 audits this question.** If medallion-10 is not Hankin, this plan's PR1 fixes a real bug but not the visible regression — and a separate `decagram strapwork` mode (or a Hankin-derived input pipeline) becomes the actual blocker.

If the audit concludes "medallion-10 IS Hankin (or close enough)," this plan proceeds as written. If "NOT Hankin," PR1 still ships (the bug it fixes IS a bug, regardless), but the visible-impact fix moves to a different plan.

**Don't ship this plan's PR1 until #115 is resolved.**

## Problem

Iter-16 of bikar-medallion-10 (2026-05-03) falsified plan #108's central hypothesis. Setting `crossing over` (uniform over-strands) was supposed to preserve A2 cv at ~0.067 because uniform-over is rotationally invariant in isolation. Instead A2 cv jumped to 0.2671 (BROKEN) and 247 sector-fragmenting extras spawned.

Root cause now precisely located in `bikar/packages/core/src/kernel/strapwork.ts`:

**`detectCrossings` is rotation-invariant** (line 198–205): per-node, edges are sorted by `Math.atan2(otherPt.y - node.point.y, otherPt.x - node.point.x)`. Rotating the input rotates each node's edge-angles uniformly; the sort yields the same neighbor order; pairs are stable.

**`walkStrand` is rotation-invariant** (line 328–386): given a starting edge it follows `crossing.edgePairs` deterministically — those pairs come from `detectCrossings`, which is invariant.

**`assignStrands`'s OUTER loop is NOT rotation-invariant** (line 291): `for (let startEdge = 0; startEdge < graph.edges.length; startEdge++)`. Strand IDs are assigned by **edge insertion order in `graph.edges`**, not by geometric location. Two inputs related by 36° rotation produce the same crossing topology but the `EdgeGraph.edges[]` array can be in a different order — so the same physical edge gets a different `strandId`.

Why this matters downstream:
- The renderer (`svg-renderer.ts:289–339`) groups strands by `strandId` and emits one closed band path per strand.
- If the same physical edge ends up in different strands across rotated copies, the band geometry differs sector-to-sector → 247 extras = 247 band fragments that don't pair across the 10-fold orbit.
- Over/under uniformity (PR1 of plan #108) doesn't help because the bug is in *which edges become strand-mates*, not in over/under choice.

## Three approaches considered

| # | Approach | Where it lives | Pros | Cons |
|---|---|---|---|---|
| **A** | **Canonicalize the start-edge order** in `assignStrands` outer loop. Sort `startEdge` candidates by the polar angle of their geometric midpoint before iterating. | `assignStrands`, ~5 lines | Smallest possible fix; localized to the proven bug; preserves deterministic strand walk; does not touch detect/walk | Sorting by midpoint angle still has tie-break edge cases for edges crossing the +x axis |
| **B** | **Compute symmetry orbits explicitly**, assign strand IDs per-orbit. Detect n-fold (qiyas already does this); group edges by their orbit; assign one strand per orbit, then rotate the assignment to siblings. | New `computeOrbits()` helper + `assignStrandsByOrbit()` | Strongest correctness guarantee; produces *exactly* n-fold-equivalent strands by construction | Requires bikar to know its own n-fold (currently it doesn't); larger surface; needs new tests for orbit detection |
| **C** | **Move strand assignment from edge-walk to face-walk** (Hankin-style). Treat each face of the planar graph as a strand-fragment owner; bands flow along face boundaries. Symmetric faces produce symmetric strands automatically. | New rewrite of `assignStrands`; existing call sites compatible | Closer to the literature (Hankin "polygons-in-contact" — Kaplan 2005); naturally rotation-invariant via planar-map structure | Largest scope; requires LineAggregate.faces walk; substantial test rewrite; defeats "smallest fix" tenet |

**Recommended: A first (PR1), B later (PR2 if A's tie-breaks misbehave), C deferred** unless we hit cases that B can't solve cleanly. C is the "right" long-term answer per the Islamic-strapwork literature, but A is what `assignStrands` is *almost* doing already and matches the plan-style of plan #108 PR1 (small, surgical, testable).

## The fix (PR1)

### Change

In `assignStrands` (`bikar/packages/core/src/kernel/strapwork.ts:291`), replace the naive loop:

```ts
for (let startEdge = 0; startEdge < graph.edges.length; startEdge++) {
  if (assigned.has(startEdge)) continue;
  // ...
}
```

with a polar-angle-sorted loop:

```ts
const edgeOrder = canonicalEdgeOrder(graph);  // returns indices sorted by midpoint polar angle
for (const startEdge of edgeOrder) {
  if (assigned.has(startEdge)) continue;
  // ...
}
```

where `canonicalEdgeOrder` is a new helper:

```ts
function canonicalEdgeOrder(graph: EdgeGraph): number[] {
  // Find geometric centroid of all node points (or use origin if pattern-relative)
  const cx = mean(graph.nodes.map(n => n.point.x));
  const cy = mean(graph.nodes.map(n => n.point.y));

  return graph.edges
    .map(([a, b], i) => {
      const mx = (graph.nodes[a].point.x + graph.nodes[b].point.x) / 2;
      const my = (graph.nodes[a].point.y + graph.nodes[b].point.y) / 2;
      const angle = Math.atan2(my - cy, mx - cx);
      const r = Math.hypot(mx - cx, my - cy);
      return { i, angle, r };
    })
    .sort((p, q) => p.angle - q.angle || p.r - q.r)  // angle primary, radius tie-break
    .map(p => p.i);
}
```

Why this works for n-fold patterns: rotating the input by 2π/n permutes the edges within each orbit; the polar-angle sort assigns consistent visit order across rotated copies; strand IDs are then 0..k-1 in a rotationally invariant sequence; rotated edges land in rotated strands; band geometry is sector-equivalent.

### Tie-break handling

Two failure modes:
1. **Edge midpoint exactly at centroid (r=0):** impossible for medallion patterns (no edge straddles the center), but guard with: if r < ε, sort by node-index pair as final tie-break.
2. **Two edges with identical midpoint angle and radius:** can happen for mirror-symmetric edge pairs. Tie-break by `(min(a,b), max(a,b))` lexicographic node-index — deterministic and rotation-stable for the orbit.

### Why this won't introduce new symmetry breaks

The walk *inside* a strand (in `walkStrand`) is already rotation-invariant. The only non-invariant step was *which edge gets picked as the start of a new strand*. Polar-angle-sorted order is preserved under rotation (a rotation of the input rotates every midpoint by the same angle, preserving sort order modulo a cyclic shift). Cyclic shift only changes WHICH strand gets ID 0 vs 1 — but the strand *set* is identical, and the renderer doesn't care about ID labels.

## DSL surface

**No DSL change needed.** The fix is purely internal to `assignStrands`. The `crossing alternating|over|under` modes from plan #108 PR1 keep working. Existing patterns continue to render. The only observable change: rotated inputs now produce sector-equivalent strand groupings.

## Validation

PR1 passes when **all** of:

1. **Unit test (kernel):** new test in `packages/core/tests/kernel/strapwork.test.ts`:
   ```ts
   it('strand IDs are 10-fold rotation-equivalent under crossing over', () => {
     const graph = buildMedallion10TestGraph();  // helper: 10-fold rotationally symmetric
     const result = computeStrapwork(graph, 5, 'over');

     // Group strand-segments by sector; sector S of an edge = floor((angle + pi) / (2*pi/10))
     const bySector = groupBy(result.strands, s => sectorOf(graph, s.edgeIndex));

     // Each sector should have the same multiset of strand-segment counts
     const counts = sectors.map(s => bySector.get(s).map(/* canonicalize */).sort());
     expect(allEqual(counts)).toBe(true);
   });
   ```

2. **Integration test (DSL):** render iter-15's exact pattern.bkr (the one that broke A2), pass it through bikar, dump the strapwork strand-set. Verify each of the 10 sectors contains an equivalent strand fragment count.

3. **End-to-end (medallion-10):** re-render iter-15 (`crossing alternating`, width 5) and iter-16 (`crossing over`, width 5) with the patched bikar. Run `iteration-validate.sh`. Expected: A2 cv drops from 0.27 (iter-16) and 0.13 (iter-15) back toward iter-14's 0.067, while A5 holds PARTIAL or improves to COMPLETE.

4. **No regressions:** existing 634 bikar tests pass.

## Cost & risk

- **Code:** ~30 lines (helper + loop swap). No external deps.
- **Tests:** 2 new unit tests, 1 integration fixture. ~1.5 hr.
- **Validation:** re-render 3 iterations (14/15/16), parse validation.json, compare A2 cv. ~30 min.
- **Total:** half-day.
- **Risk:** medium-low. If `canonicalEdgeOrder` has tie-break bugs on a non-medallion-10 pattern, the symptom is "alternating mode looks slightly different than before." Mitigation: snapshot test on the existing test corpus to detect any unintended visual change.

## Three PRs

| PR | Scope | Cost | Unblocks |
|---|---|---|---|
| **PR1** | `canonicalEdgeOrder` helper + loop swap + 2 unit tests + 1 integration test + 3-iteration end-to-end validation in bikar-medallion-10 | 0.5d | re-running plan #108 PR1's experiment (iter-17 with `crossing over` should now preserve A2) |
| **PR2** | If PR1's tie-breaks misbehave on any pattern, implement explicit orbit detection (approach B). Add `computeOrbits()` and `assignStrandsByOrbit()`. Keep PR1's loop as the orbit-free fallback. | 1–2d | covers patterns where the centroid-relative angle isn't well-defined (e.g. asymmetric layouts) |
| **PR3** | (Deferred unless needed) Hankin face-walk strand assignment (approach C). Aligns bikar with the Kaplan/Hankin literature on Islamic strapwork. | 3–5d | future patterns where face-based bands are visually preferable |

## How this composes with prior plans

- **Plan #108 (symmetry-preserving crossing modes):** PR1 of #108 (over/under tokens, parser, kernel branch) shipped and stays. The over/under modes were the wrong layer for the symmetry break — but they're correct DSL features and the right validation lever for the current plan. Plan #108 PR2 (`crossing rotational`) is unblocked by THIS plan's PR1: once strand-assignment is rotation-invariant, per-orbit over/under policy can be added on top without re-introducing the bug.
- **Plan #109 (counterfactual fragmentation tax):** Independent. Even after THIS plan ships, qiyas should still tax fix-archetypes that historically spawn extras — bikar may produce other fragment types we haven't seen yet.
- **#85 medallion-10 convergence:** This plan unblocks the `crossing over` experiment that iter-16 was supposed to run. After PR1 ships in bikar, iter-17 can be `crossing over` again and the prediction (A2 cv stays ~0.067, A5 PARTIAL) should hold this time.

## Open questions

- **Should `canonicalEdgeOrder` use origin (0,0) or computed centroid?** For medallion patterns the user-visible center is always (0,0) (per CLAUDE.md "geometric construction from central origin"), so origin is fine and avoids a centroid computation. For BIKAR-style tilings the centroid matters. Default: use origin if all nodes are within radius R of it; else use centroid. Cheap check.
- **Does `walkStrand` need a similar canonicalization?** I claimed no, because it follows pre-sorted `crossing.edgePairs`. Re-verify by reading `walkStrand` once during PR1 implementation; if there's a hidden order dependency in the "walk forward then walk backward" logic (line 337–384), patch that too.
- **What happens for non-rotational symmetric patterns?** Polar-angle sort still gives a deterministic order; just doesn't add value. Mirror-symmetric patterns need approach B.

## References

- Kaplan, C. S. (2005). "Islamic Star Patterns from Polygons in Contact" — Hankin algorithm formalization. Cited in bikar's existing `Hankin` token (`bikar/packages/core/src/dsl/tokens.ts:108`). https://cs.uwaterloo.ca/~csk/publications/Papers/kaplan_2005.pdf
- Bodner, B. L. (2008). "Hankin's 'Polygons in Contact' Grid Method for Recreating a Decagonal Star Polygon Design" (Bridges 2008). https://archive.bridgesmathart.org/2008/bridges2008-21.pdf
- Grünbaum & Shephard (1992). "Interlace Patterns in Islamic and Moorish Art" — Cayley-diagram analysis of strapwork strands; relevant for approach C.
- Combinatorial maps / rotation systems (Wikipedia). https://en.wikipedia.org/wiki/Rotation_system — formal model for the planar embedding underlying approach C.
