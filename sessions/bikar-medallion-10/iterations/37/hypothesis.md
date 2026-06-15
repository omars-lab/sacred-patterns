---
attempt: 37
date: 2026-06-10
gap_targeted: "Pocket-star density — iter-36's verdict routed this first: between the rosettes the reference shows a few LARGE solid colored shapes (the cyan pocket-stars), while our render shows a dense fractured white mesh of small faces. Zoom comparison (/tmp/zoom-pair.png) made the mechanism visible: each between-rosette region is the overlap LENS of two decagons, and BOTH decagons' {10/3} decorations run through it, fracturing one big motif into many slivers."
construction_hypothesis: "The decagonal field is an overlapping-rosette tiling (no holes — the earlier 'fill the gaps with tiles' premise was falsified by measurement: every candidate loop centroid sits INSIDE two decagons). The historical B-H-D reading treats each decagon-decagon lens as a girih HEXAGON tile carrying its own sparse 3-line decoration. New engine primitive (bikar task #23, Tenet 26: extend the DSL instead of hand-authoring): `resolveLensPockets` finds every lens by exact pairwise convex intersection (130 lenses at shells 2), clips the host decagons' decoration OUT of each lens, and emits the posed hexagon's 3 decoration lines instead. Fewer, longer decoration lines in the lens → fewer, larger faces → the big solid pocket shapes the reference shows. Side effect shipped with the same engine change: a field-dedup fix (negative-zero key) removes 5 coincident duplicate decagons from the shells-2 field (66→61 tiles), deleting silently-doubled segments that existed in iters 33–36."
bkr_change: "One token: `girih field decagonal 62 shells 2` → `girih field decagonal 62 shells 2 pockets`. Palette, classify, fill, edges, strapwork all unchanged from iter-36."
predicted_lift: "+2–6 pixel similarity (72.9% → ~75–79%). The lens interiors stop being white-mesh-dominated and become large fillable faces; since fill rules key on sides counts, bigger simpler faces should catch the colored fills the reference shows in those zones. Structure similarity should rise; the channel-drift warning (30.3 spread at iter-36) should shrink because large colored lens faces replace white lattice exactly where the reference pairs colored pixels against our white."
predicted_cost: "Face side-counts in the lens zones change wholesale, and the existing classify/fill rules (keyed on sides 3/4/5/10/>=6) were tuned against the OLD fractured topology — the new large lens faces may land in the wrong fill class (e.g. a 6-sided lens face catching the navy >=6 rule instead of reading as a cyan pocket-star). If the lenses come out the wrong COLOR but the right SHAPE, that's the predicted residual, and it routes to a fill-rule pass, not a construction failure. Also the dedup fix changes the iter-36 baseline geometry slightly (duplicate segments removed) — strictly an improvement, but it makes the A/B not perfectly isolated to the pockets flag."
prior_art_searched: "bikar docs/decisions/2026-05-28-medallion10-girih-ceiling.md — its falsification log already records that pentagon/rhombi substitution hand-authoring was a dead end and names the B-H-D system (decagon+hexagon+bowtie) as the real structure; this iteration is the engine-primitive route that decision doc's Tenet-26 addendum called for. LEDGER checked: no prior decision covers lens re-reading; an addendum to the girih-ceiling doc ships with the bikar commit."
related_memory: "feedback_decomposition_order (structure before strapwork/color — this IS the structural fix the last three verdicts kept deferring); feedback_validate_premise_before_options (the hole-filling premise was checked against geometry before building — and falsified, redirecting to lens semantics); feedback_metric_temptation_at_plateau (iter-36 diagnosed the channel drift as a structural-density symptom rather than tuning color further — this iteration fixes that named root cause)."
detector_untouched: "confirmed — no qiyas param/threshold/cost in this iteration"
---

## Plan

Why this gap: routed #1 by iter-36's verdict; deferred in iters 34, 35, and 36
(Tenet 28's stop rule fired: deferred twice means build it now); and it is the
named root cause capping the palette work (iter-36's honest miss — +1.5 actual
vs +4–8 predicted — was diagnosed as colored reference pocket-stars pairing
against our white mesh).

Why this hypothesis: measured, not guessed. The lens anatomy was probed
(6 vertices = 4+4 with 2 shared, centroid inside exactly 2 decagons, corner
signature 72,72,144,144,144,144 = the girih hexagon), the kernel fix was
proven at Tier-0-style witnesses first (shells-1 kernel render, then a DSL A/B
smoke at shells-1) before touching the shells-2 medallion, per Tenet 17.

Why this is the smallest edit: one keyword. The engine carries the complexity;
the construction stays declarative.

Expected visual (written BEFORE viewing any render — Tenet 24): same global
layout and palette as iter-36 — but in each between-rosette zone the dense
white micro-mesh is replaced by a few LARGE faces bounded by the lens hexagon
and its 3 sparse decoration lines. The white strapwork inside lenses thins to
the hexagon motif. The rosette {10/3} stars survive outside the lenses with
chords trimmed at lens rims (the rosettes should still read as stars). Color
inside the lenses: whatever fill class the new big faces land in — cyan/cobalt
if they read as ~5-sided, navy if >=6-sided; WATCH THIS, it is the predicted
residual. Failure signatures to watch: rosettes losing their star definition
(over-clipping), or hairline slivers at lens rims (clip tolerance artifacts).

## Guardrails check

- This is a CONSTRUCTION edit (.bkr / bikar primitive), not a detector edit:
  yes — bikar kernel + one .bkr keyword; qiyas untouched.
- Construction-philosophy memory checked — approach not already falsified:
  yes — the falsified premise (hole-filling) was caught and re-scoped BEFORE
  geometry shipped; the lens reading is the alternative the falsification
  pointed to, not a retry of the dead end.
- predicted_cost names a concrete failure mode I will look for in the render:
  yes — wrong fill class on the new lens faces, and rim slivers.
