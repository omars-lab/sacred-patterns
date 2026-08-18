---
name: a6-baseline-construction-philosophy-mismatch
description: "when an A6 baseline expects a rich shape vocabulary the current cascade's construction philosophy can't produce, stop iterating construction variants — the gap is philosophical, not tunable"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When a sacred-patterns iteration cascade ships construction variants
to close an A6-missing-shape verdict and 3+ variants falsify for
*different mechanism reasons* (chord subdivision, strapwork
crossings, encoder-side dropouts), the gap is a construction-vs-
baseline philosophy mismatch — not a tunable parameter.

**Why:** The medallion-10 cascade falsified 5 variants across 2 A6
verdicts (iter-25/26/27/28 on inner-star--star-v20, iter-30 on
inner-star--rhombus-v4). Each had a *different* root cause:
intersection subdivision in iter-25, strapwork band crossings in
iter-26, encoder collapse to circle in iter-27, chord-too-short →
v2 segments in iter-28, and chord-rhombi absorbed by strapwork
band-crossing classifier (no new `type=square` shapes emitted in
target distance band) in iter-30. The pattern: each construction
variant satisfied the bikar/DSL contract but produced geometry the
qiyas detector either subdivided, collapsed, or reclassified at a
different pipeline stage. The baseline's "rich shape vocabulary"
(18 distinct shape classes including standalone rhombi, v6/v8/v20
stars, polygon-v0 at specific distance bands) requires every shape
to have visibly distinct, non-subdividable geometry at the expected
distance bands — which the chord-overlay + strapwork construction
philosophy of this cascade *fundamentally can't produce*.

**The generalized falsification:** the mismatch is not specific to
v20 — it applies to **every A6 verdict whose expected distance band
conflicts with strapwork-medallion's intersection-face geometry**.
4-vertex chord-network intersection faces have centroids determined
by the chord network's geometry (not the underlying circle's radius),
so simply adding a divided circle at a target radius does NOT
guarantee chord intersections land at the corresponding distance
band. The baseline likely derives from a different construction
philosophy (girih tiling with explicit rhombus/star tiles), which
no amount of chord-network parameter tuning can reproduce.

**How to apply:** After 3 falsified construction variants targeting
the same missing-shape verdict in an A6 cascade, OR after the same
pattern recurs across 2+ distinct verdicts in the same cascade, stop
iterating those verdicts. Document the local-optimum frame, note the
cascade's A2/A4/A5 wins, and either (a) close the cascade and file
a separate workstream for the baseline-expected vocabulary using a
different construction philosophy (e.g., girih tiling primitives:
decagon/pentagon/rhombus/bow-tie/hexagon as tile types), or (b)
re-inspect the reference image to verify the baseline's shape
expectations match what's visually present.

When falsification 5+ recurs across verdicts, pivot OFF the cascade
to other backlog work — chasing more parameter variants is pure
cost (per [[feedback_cf_delta_cost_blind]]) with zero expected
upside.

The construction-philosophy gap is invisible from any single
variant's falsification — it only becomes legible when multiple
variants fail for *different* mechanism reasons. That's the
signal.

**UPDATE 2026-05-28 — the girih option is NOT owner-gated; the
primitive already exists.** Visual verdict recorded at
`~/Dropbox/Data/sacred-patterns/bikar-medallion-10/iterations/30/visual-verdict.md`
confirms the reference is a girih-tile strapwork medallion (white
interlace bands + explicit blue 8-pt stars + decagon rosette frames),
which the chord-overlay philosophy categorically cannot produce —
matching this memory's diagnosis at the visual level, and resolving
its option (b) (re-inspect reference): baseline expectations are
VISUALLY REAL, not over-counted. BUT this memory's option (a)
assumed girih needs an owner-funded multi-day primitive build. That
assumption is FALSE as of bikar HEAD: `packages/core/src/kernel/
girih-tiles.ts` already implements all 5 Lu-&-Steinhardt tiles
(decagon/pentagon/hexagon/rhombus/bowtie) with decoration-line pairs,
edge-attach (`attachGirihTile`), and subdivision; the DSL exposes
`girih <type> <edgeLength> [at <pos>] [rotate <deg>] [attach <name>
edge <N>] [.className]` (parser.ts:1747, evaluator wired, `Girih-
Decagon.bkr` starter demos it). Rendered /tmp/girih-decagon.svg
2026-05-28: the primitive produces a decagon with internal {10/3}
star strapwork — the exact vocabulary the baseline expects. So the
medallion-10 ceiling is an ACTIONABLE construction-side iteration
(via `iterate-construction-hypothesis`), not a `present-options`
owner-funding decision. This is the `feedback_check_mechanism_already_
implemented` / `feedback_check_emit_layer_before_option` lesson again:
**a 2-day-old memory's cost estimate for "build a new philosophy"
can be stale — grep the target module before declaring a philosophy
unreachable.** Next construction iterations: 31 = central decagon
tile vs baseline; 32+ = ring attachment via `attach edge N`.

**Companion to:** [[feedback_cf_delta_cost_blind]] (predictions vs.
outcomes), [[feedback_narrow_corpus_sweep_tenet7_trap]] (Tenet 7
stop rule mechanics), [[feedback_cascade_primitive_semantic_composition]]
(cascade primitives composing semantically).
