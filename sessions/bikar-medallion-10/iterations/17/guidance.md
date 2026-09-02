# Iter-17 Guidance — REVERT to iter-14, then reassess strategy

## Decision: REVERT

iter-14 stays the working baseline (composite=0.7842). iter-15, iter-16, iter-17 all regressed; all reverted.

## Do NOT next-iterate naively from warnings[0]

iter-17's warnings[0] is now `symmetry-mismatch` (cf_delta=0.125), but that warning is a SECONDARY effect of having added the {10/2} — it's not present in iter-14's warnings. Reverting to iter-14 erases this warning.

**The actionable warnings array to use for the next iteration is iter-14's, not iter-17's.** iter-14's top warning was `missing-shapes` (cf_delta=0.0667), and that's what iter-17 just tried and failed to address by adding more polygon-mesh.

## Pattern: cost-blind counterfactual deltas

iter-15, iter-16, iter-17 all failed for the same root reason: qiyas's `counterfactual_score_delta` models the upside of a fix without modeling the cost of the edit. Three iterations of falsified predictions is enough evidence.

**Next iteration should NOT be a fresh edit attempt** until either:
- (a) **Plan #109 lands** (counterfactual fragmentation/interaction tax — qiyas models cost), OR
- (b) We deliberately make a *small, isolated* edit that doesn't add edges to the saturated central mesh — e.g., target an outer-zone shape (Cmid or Cmid2) where there's no existing mesh density to fragment.

## Recommended next move

**Option A (preferred): work on #109 in qiyas first.** The fragmentation tax is the missing model. Without it, the iteration loop is gambling. iter-15/16/17 cost three iterations to confirm what the loop's prior behavior already suggested.

**Option B (fallback if #109 is far): try a small outer-zone edit.** Pick an A6 MISSING shape that lives in the OUTER ring (`transition--*` or `rosette--*`). Outer zones have less existing mesh density (`Cmid` and `Cmid2` only have one connect each at iter-14), so adding an edge there is less likely to fragment existing matches. This is a lower-stakes test of the same hypothesis class.

**Option C (defer convergence): pivot to #115 first.** If medallion-10 isn't actually a Hankin-PIC pattern, then the strapwork plan #113→#114 needs reframing AND the central decagrams may be the wrong central construction. Audit before more iterations.

## What NOT to try next

- **More central-zone decagrams.** Adding {10/5} (the diameter star) or further connect-blocks on C1 is the same class of edit that just failed; expect the same fragmentation tax.
- **Strapwork in any current crossing mode.** iter-15 (alternating) and iter-16 (over) both broke A2. Mode `under` would behave identically to `over`. `rotational` and `weave` aren't implemented. Per plan #113 + task #115, strapwork is blocked anyway pending the Hankin audit.
- **Iterating without G3 deliverables on the prior iteration.** iter-15/16/17 all wrote G3 docs; that discipline is working. Keep it.

## Construction knowledge to add to learnings

**Encoder classifies post-`voids detect` faces, not the polylines you draw.** Adding line edges to a face graph doesn't necessarily produce the polygon you'd visually expect — the encoder sees only the carved faces. A `connect every 2 on C1` does NOT guarantee a single 20-vertex star face if other connects already cross C1's interior. This belongs in `.claude/skills/generate-drawing/learnings/construction-antipatterns.md` as "encoder-classification trap."

## Files to revert / keep

- iter-14/* — KEEP as working baseline
- iter-15, iter-16, iter-17 — KEEP folders (each has G3 deliverables for the historical record); none promoted to baseline
- Any aggregate iteration-status tracker — update to reflect iter-14 as current baseline
