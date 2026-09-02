---
name: Vertex-identity lifting can't fix linkage-layer bugs
description: bikar Option E (DSL-supplied EndpointIdentity → getNodeIndex merge key) targeted the wrong pipeline layer for petal-N-ring N=4 bug; Phase 1b had located it in buildHalfEdges linkage step, not vertex-merge. Slice 3 v1 (separator) regressed lens construction; v2 (additive) lands clean but cannot un-merge so doesn't fix the bug. The "same architectural fix for N=4 and N=8" assumption was suspect.
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
**Rule:** When Phase-1-style probes have already located a bug in pipeline layer L, don't accept an option whose mechanism touches layer L-1 even if the option is elegant. Re-read the probe output BEFORE drafting options.

**Why:** bikar#424 cascade (2026-05-19). Phase 1b probe explicitly logged: "N=4: 1 distinct near-origin vertex (full merge). 8 outgoing half-edges share it. CCW linkage glues opposing-arc segments into wrong face cycles. Bug here IS in the linkage step's geometric assumption." Despite that, the cascade selected Option C / Option E whose mechanism is in `getNodeIndex` (the vertex-merge step, layer L-1 from linkage). Three falsifications followed:
- Option C all-points: regressed lens construction (vertex-merge can't be tightened without breaking legitimate cross-circle merges).
- Option C endpoint-only: same class of regression.
- Option E v1 (separator): same class of regression.
- Option E v2 (additive): no regression but can't un-merge, so N=4 stays broken (probe `node /tmp/check-petal-N.mjs`: N=4: 0, N=6: 6, N=8: 0, N=10: 10, N=12: 8).

Option B (chord-bisector sort key in `compareOutgoing`) was the option targeting the correct layer (linkage) from day 1 — but was deprioritized because Option C "generalized better" and "matched CGAL more closely." The CGAL alignment argument was a red herring; CGAL's merge layer behaves differently because its linkage layer also behaves differently.

**How to apply:**
- When a decision doc has a "Phase 1b says bug is in layer X" finding, the Recommendation in §6 must explicitly cite which layer the picked option's mechanism touches and either (a) match X, or (b) argue why the cross-layer fix is correct.
- Before authoring §5 options, list candidate options BY LAYER (sort layer, merge layer, splitter layer, primitive layer). Don't let one layer's options crowd out another's just because that layer's options are easier to articulate.
- Falsification of one option in layer L-1 should auto-promote the layer-L option, not generate another layer-L-1 option.
- Companion to `feedback_separation_distance_vs_merge_gate.md`: there too, the picked mechanism (Jaccard distance) targeted the wrong layer (the metric, not the equivalence relation). Same shape of error.

**Failure mode this prevents:** building 7 days of slices (audit, plan, implementation through Slice 3) on an option whose mechanism cannot reach the bug. The work itself isn't wasted (the DSL identity infrastructure has standalone value) but the cascade close gets delayed by exactly the duration of the wrong-layer detour.
