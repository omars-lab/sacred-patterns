---
name: Partial-shape rendering cascade (Option A accepted 2026-05-07)
description: 3-piece qiyas+bikar+sacred-patterns cascade for extended-then-clipped construction shapes; closes the medallion-10 ~74% pixel ceiling
type: project
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
Owner picked Option A on 2026-05-07 for sacred-patterns#106 (partial-shape rendering via construction). Three coupled work-items, in dependency order:
1. **bikar (3-5 days):** four DSL primitives — `boundary <name> = union(...)`, `extend <connect> beyond <mult>`, `clip pattern to <boundary>`, `intersect <circles> at radii [...]`. Mirror CGAL `Boolean_set_operations_2` semantics for the boundary primitive and Asymptote's `clip(picture, path)` for the clip primitive. The `intersect` primitive is the hardest and explicitly deferrable.
2. **qiyas (1-2 days):** partial-polygon detector in encoder + new A6 verdict `CLIPPED-MISSING` (distinct from `MISSING`); fires when ≥half the expected vertices for an N-vertex shape appear as zone-boundary-clipped polylines. Counterfactual transformer maps the verdict to a one-line `extend ...` bikar edit.
3. **sacred-patterns (~1 hr):** translation table row in iteration-guide; cross-repo-deps update.

**Why:** Reason: medallion-10 has been stuck at ~74% pixel similarity for 14 iterations because 30-40% of the bare-region pixels can't close via tile-shape edits — only construction-extent edits close them. The reference uses Kaplan's "boundary segment removal" pattern (extended construction clipped to medallion silhouette); our renderer doesn't express that.

**How to apply:** When working on tasks #255-#260, treat the cascade as one shipment with sequenced PRs. Bikar primitives must land before sacred-patterns translation row. The verifier (#260) re-validates iter-14 *deliberately preserved as the test fixture* — expected lift is +0.05 to +0.10 composite score; if &lt;+0.03, file falsification follow-up rather than rationalize. Strapwork PR (#114) merge ordering is the open coordination question — `boundary` primitive may need to land first if #114 develops a dependency on it.

Decision doc: sacred-patterns/docs/decisions/2026-05-07-partial-shape-rendering-via-construction.md
Mental-model entry: sacred-patterns/docs/dev-mental-model.md §"Decisions that shaped this codebase"
