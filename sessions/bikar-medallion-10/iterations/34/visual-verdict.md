# iter-34 visual verdict — Slice-4 strapwork overlay (bikar#653)

## Expectation written BEFORE viewing the render (Tenet 24)

The change from iter-33: add a `strapwork width <w> / crossing alternating /
color white` block to the converged gap-free girih field. iter-33 renders the
field as flat blue filled faces with thin navy edges — no white bands, so it
reads as a dense blue mosaic, NOT the reference's white-lattice look.

**What I expect to see in iter-34/render.png:**

1. The same blue decagonal field as iter-33 underneath, BUT now with **white
   interlacing bands** drawn over the decoration centerlines — the same lines
   that iter-33 drew as thin navy edges become thick white woven straps.
2. At each degree-4+ crossing the bands should **alternate over/under** (one
   strand passes over, the neighbor under, with a trimmed gap on the under
   strand) — the woven-lattice signature of the reference.
3. The blue fills (navy decagons, royal/cobalt/turquoise small shapes) should
   show **between** the white bands, matching the reference's blue-tile-between-
   white-strap structure.
4. Net: the render should move visibly toward `input/reference.jpg` — a white
   interlacing lattice over a 10-fold blue star field — rather than iter-33's
   bandless blue blob.

**Risk I'm watching for (per the handoff Step-1 two-outcome fork):** the girih
field's decoration density is high (9692 SVG paths in iter-33). If every internal
decoration centerline gets woven, the bands may be too dense / tangled at the
many degree-4+ vertices, hiding the blue fills and reading as a white mess rather
than a clean lattice. THAT outcome is the real Slice-4 work (weave only seam
lines, or pocket-fill first) and routes via /iterate-construction-hypothesis.

## Observation AFTER viewing the render

**Outcome 2 (tangled / too-dense) — confirmed exactly as the handoff predicted.**

The strapwork weaver DID run — `render.svg` has 5640 `data-strand` band paths
across `<g class="strapwork-over">` / `<g class="strapwork-under">`, woven
over/under at crossings. But the result is a **fine white mesh**, not the
reference's bold sparse white interlacing straps. The white bands cover the whole
field at fine pitch, the blue fills survive only as small dark islands between
them, and the 10-pointed star structure of the reference is NOT legible.

Side-by-side reading vs `input/reference.jpg`:
- Reference: ~bold white straps weaving around clean blue 10-point stars +
  small colored shapes; the straps are SPARSE (one strap per decoration line,
  tile boundaries invisible).
- iter-34: dense fine white mesh; far too many strands.

**Root cause (located, not guessed):** `girihTileSegments(tile, true)`
(girih-tiles.ts:168) returns `[...tile.edges, ...tile.decorationLines]` — i.e.
the field pushes BOTH the tile polygon OUTLINE edges AND the strapwork decoration
lines into `env.segments` (evaluator.ts:2183). `computeStrapwork` then weaves
**all** of them. So every decagon/bowtie/hexagon boundary edge becomes a band on
top of the actual strapwork decoration bands — roughly doubling/tripling the
strand count and producing the mesh. In the reference (and in Hankin/Kaplan
canon) the tile boundaries are *erased scaffolding*; only the decoration lines
are the visible straps.

**Verdict: this is the genuine Slice-4 fork-2 work, NOT a width/color tune.**
No band-width tuning fixes a count-of-5640-vs-~150 problem. The fix is to weave
ONLY the decoration centerlines, not the tile outlines. Routing + options below
(evaluation.md). A5 will not be meaningfully live until the strand set is the
decoration network, not outlines+decorations.

**Strand-count witness (codify per Tenet 18):** iter-34 field with strapwork
emits 5640 strands; the decoration-only network should be a small fraction
(decoration lines per tile × tile count, no outline edges). This count is the
regression witness for whichever fix ships.

## Decisive probe (2026-06-07) — decoration-only weaving recovers the reference lattice

Before routing, I ran a standalone probe (`/tmp/girih-deco-weave-probe.mjs`)
that builds two strapwork edge graphs from the SAME field and weaves each:
- `both` (current: `tile.edges` + `tile.decorationLines`) → **5640 strands**,
  reproduces the iter-34 dense mesh (`/tmp/weave-both.png`).
- `decoration-only` (`tile.decorationLines` only) → **2790 strands**,
  produces a **clean white interlacing 10-point-star lattice**
  (`/tmp/weave-deco-only.png`) that visibly matches the reference's white-strap
  network — interlocking decagonal rosettes, 10-point central star, woven
  rosette ring.

**This re-routes outcome-2.** The handoff's fork-2 named (a) seam-only weaving
or (b) pocket-filling-first. The actual lever is cleaner than either: **weave
decoration lines only, exclude the tile polygon outlines.** That is a
render-style change (which segments feed the weaver — consistent with memory
`feedback_girih_strapwork_is_render_style_not_geometry`), NOT the multi-day
geometric pocket-filling, and NOT a change to `computeStrapwork` itself (it gets
a filtered input graph).

**Second finding — the field is decagons-only (69 decagons, 0 bowties/hexagons).**
Per the decision doc's Slice-1 spillover note, pocket-filling is deferred. So the
small turquoise/cobalt pocket-stars in the reference (which come from
bowtie/hexagon decoration lines) will be ABSENT even after the deco-only fix —
but the dominant white rosette lattice is recovered without them. Pocket-filling
is a *secondary refinement* (still deferred), not the blocker for recovering the
reference's defining look + making A5 live.

**Routing decision:** implement deco-only weaving (small, render-style, scoped).
Does NOT trip the handoff stop rule (which gates a multi-day `computeStrapwork`
kernel rewrite / crossing into geometric pocket-filling). Pocket-filling remains
deferred and would be surfaced separately if the owner wants the pocket-stars.

## Final ship gate (Tenet 25) — after the deco-only fix shipped

Rendered the final iter-34 (`render.svg` 2790 strands → `render.png`) and viewed
it; ran `qiyas pixel-diff` vs `input/reference.jpg` and viewed the overlay +
heatmap. Verdict against the expectation above:

- ✓ White interlacing bands present, woven over/under — the rosette star-lattice
  reads clearly, matching the reference's defining white network.
- ✓ Legible 10-point central star + ring stars.
- ✓ pixel-diff similarity **70.4%** (iter-33 was 65.5%); overlay
  (`diff/diff-overlay.png`) shows strong structural alignment of the lattice;
  heatmap interior is mostly green (shared) — divergence concentrates at the
  scalloped-vs-rounded boundary ring.
- ✓ A5 band-integrity COMPLETE 100 (1054 crossings) — the metric the look feeds.

The dense-mesh risk flagged before viewing the first render DID fire on the
naive overlay (5640 strands) and was resolved by the deco-only weave (2790). The
final render clears the ship gate: it visually matches the reference's white-strap
look at the lattice level, with the pocket-star detail honestly noted as deferred
(decagons-only field). **Shipped on a viewed render + recorded pixel-diff, not a
green metric alone.**
