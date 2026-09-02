# Iter 20 — layer in clip pattern to medallion outline (cascade #106 second primitive)

## Premise

Iter-19 confirmed `extend connect ... beyond F` lifts composite (+0.025), drops A2 cv below iter-14 baseline (0.096 < 0.067 close), and downgrades missing-shapes from sev=error to sev=warn. But structural_score stayed at 0/18 because the new extension shapes reach outside the medallion silhouette and present as open arcs — A6 can't match them to its expected vertex counts.

The cascade plan's next primitive is `clip pattern to <boundary>`. Adding it should crop the extension geometry at the medallion edge, converting open arcs into closed partial shapes that A6 recognizes.

## The edit

Two changes:

1. **In the `blueprint medallion` block**, add a boundary declaration after the circle/divide statements but before the `repeat`:

```
boundary outline = union(C0)
```

This defines the medallion silhouette as the outer C0 circle (radius 100). `union(<single>)` is valid per `gt-emitter-clip.test.ts`.

2. **In the `pattern medallion on medallion` block**, add the clip statement after the existing layers but before `voids detect`:

```
clip pattern to outline
```

`clip pattern to <boundary>` lives in the pattern block per `gt-emitter-clip.test.ts`; it partitions the half-edge graph by the boundary, drops outside faces, and annotates boundary-incident edges.

## Predictions

- **composite:** 0.8236 → expected +0.02 to +0.04 (completing the cascade plan's "+0.05 to +0.10 from a single edit" prediction over iters 19+20).
- **structural:** 0/18 → **expected 3-7/18** (the predicted big move — clipping converts open arcs into the closed partial polygons A6 expects in zones inner-star, transition, rosette).
- **missing-shapes:** 32 → expected ≤20 (clipped partial shapes now match the reference's clipped tips).
- **extra-shapes:** 30 → expected 15-25 (open-arc fragments outside C0 are dropped).
- **pixel:** 71.3 → expected +1 to +5 (large bare regions outside C0 finally trimmed; structural shapes inside now properly closed).
- **A2 cv:** 0.0962 → similar or slightly better (clipping respects 10-fold symmetry).
- **A5 status:** BROKEN → BROKEN/PARTIAL (clipping doesn't directly affect band detection; that's gated on detector work outside cascade #106).

## Stop conditions

- **structural stays 0/18** → `clip` is parsing but not producing closed partial polygons. Could be: (a) `union(C0)` doesn't define the right boundary (try `union(C0, Cmid)` or named satellite circles), (b) `clip` cropping is incomplete — drops faces but doesn't close edges at boundary. Read the validation.json A6 diagnostics for the specific shapes affected.
- **composite drops > 0.02** → unexpected interaction. Likely the clip is over-aggressive and dropping legitimate inner structure. Try `boundary = union(C0, Cmid, C1)` to expand the kept region.
- **Render fails** → bikar bug in the clip path under our specific use of `extend + clip` together. Bisect by removing extends, keeping just clip.

## Rollback path

If composite drops, revert iter-20's two-line edit (the boundary + clip lines); iter-19 remains the new floor at composite=0.8236.

## What this iter does NOT do

- No `intersect` primitive (cascade plan's 4th primitive, deferred unless a specific intersection point is needed for downstream work).
- No fill rule changes (existing rules cover any shape clip produces).
- No layer/circle/divide additions.
- No strapwork.

## Cross-task

- If green, completes the cascade #106 SVG-direct-path verification. Cascade can be marked ACCEPTED ready-for-close on its primary axis.
- If red, narrows whether `clip` is the blocker (vs. needing `intersect` or boundary refinement).
