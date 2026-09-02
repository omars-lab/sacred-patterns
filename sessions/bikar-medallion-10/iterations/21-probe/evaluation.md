# Iter 21-probe — L1 fix for cascade #106 clip-boundary spec — FALSIFIED

## Bottom line

| Signal | iter-19 (ceiling) | iter-20 (FAIL) | **iter-21-probe** | Verdict |
|---|---|---|---|---|
| composite | 0.8236 | 0.697 | **0.7947** | **STOP** (−0.029 vs iter-19; > 0.02 limit) |
| structural | 0/18 | 0/18 | 0/18 | still 0 |
| missing-shapes | 32 (warn) | 39 (error) | **36 (error)** | partial recovery, still error |
| extra-shapes | 30 | 34 | **42 (error)** | **REGRESSED** further |
| pixel | 71.3 | 72.9 | 72.0 | flat |
| top warning | extra-shapes | symmetry-mismatch | **extra-shapes (sev=error)** | new error tier |

## What was tried

Iter-20's hypothesis was that `boundary outline = union(C0) + clip pattern to outline` would close the cascade #106 prediction. It regressed catastrophically because `union(C0)` is the wrong silhouette — the medallion silhouette is `union(C0, S0..S9)` since satellites at distance 1.0·R from origin with radius 0.3·R reach 1.3·R.

Iter-21-probe is the L1 fix:
- Renamed the satellite `repeat at C0 depth 1 / circle center($point) radius 0.3 * $radius / divide into 10` into 10 explicit named circles `S0`–`S9` (required because the shipped grammar's `union(...)` only accepts `TokenType.Identifier`, not `@N.k` repeat-addresses).
- `boundary outline = union(C0, S0, S1, S2, S3, S4, S5, S6, S7, S8, S9)`.
- `clip pattern to outline` as before.
- `extend connect every 4 on Sk beyond 1.5` for k=0..9 (renamed from `@0.k`).

## How it failed

L1 partially recovered the prediction: composite climbed from iter-20's 0.697 → 0.7947 (+0.097), missing-shapes ticked down 39 → 36, no symmetry-mismatch error. **But it still drops -0.029 below iter-19's 0.8236**, and *extra-shapes regressed further* (30 → 42, severity escalated to error).

## Root reason (current best understanding)

The `extend + clip` primitive interaction creates **clipped sliver polygons** at the medallion boundary — the extension arcs reach beyond the silhouette but the clip leaves tiny fragments along the boundary curves. These show up as 42 extra shapes (vs 30 unclipped in iter-19) with severity=error.

Closing the missing-shapes gap (36 vs iter-19's 32) requires the extension geometry to *intersect with the inner stars/rosette before being clipped*, but the current `clip` mechanism drops faces wholly outside the boundary rather than letting them intersect first. This is a **mechanism-level interaction failure**, not a boundary-spec failure.

## What this falsifies in the doc

- [ ] The picked option's mechanism (cascade clip-after-extend interaction is L2-wrong, not L1)
- [x] The option enumeration (the cascade plan needed an `intersect`-before-clip step or a different clip semantic, not `extend → clip`)
- [ ] The doc's framing question (the framing — "extend then clip" — may still be sound; the *primitive choice* was incomplete)
- [x] The audit / impact analysis the doc relied on (the plan asserted `extend + clip` would close the partial-shape gap, without validating that the clip semantics preserve intersections — it doesn't, on this corpus)

## Cascade variants attempted (Tenet 7 stop rule)

- **Variant 1 (iter-20):** `boundary outline = union(C0) + clip pattern to outline` — FALSIFIED (-0.13 composite).
- **Variant 2 (iter-21-probe):** corrected to `union(C0, S0..S9)` — FALSIFIED (-0.029 composite, extra-shapes error).

Two falsifications. Per Tenet 7 stop rule, **invoke handle-falsification protocol** rather than authoring Variant 3.

## Stop conditions evaluated

- composite drop > 0.02 vs iter-19 ceiling: **TRIGGERED** (-0.029)
- missing-shapes severity stays error: **TRIGGERED**
- extra-shapes regressed: **TRIGGERED**
- structural still 0/18: **TRIGGERED**

## Rollback action

Iter-21-probe stays in `iterations/21-probe/` (NOT promoted to iter-21). Iter-19 (composite=0.8236) remains the medallion-10 ceiling.

## Next directive

Per §F mechanical critical-path check + handle-falsification skill:
1. Reopen `sacred-patterns/docs/decisions/2026-05-07-partial-shape-rendering-via-construction.md` with structured frontmatter + falsification log section (both variants documented).
2. Switch to a different critical-path task — don't author Variant 3 of cascade #106 clip primitive without first running the full L2/L3 introspection per the skill.
3. Capture cross-repo memory: `feedback_extend_then_clip_creates_sliver_polygons.md` (or similar — the lesson is about primitive-interaction not visible from the cascade plan's audit alone).
