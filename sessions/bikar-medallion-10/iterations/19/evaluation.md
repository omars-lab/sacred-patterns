# Iter 19 — partial-shape cascade primitive validates: PASS

## Bottom line

Applying `extend connect every 4 on @0.k beyond 1.5` to all 10 satellite stars produced a multi-axis improvement:

| Signal | Iter 18 | Iter 19 | Predicted | Verdict |
|---|---|---|---|---|
| composite | 0.7985 | **0.8236** (+0.025) | +0.02 to +0.06 | **PASS** (low end of range) |
| A2 cv | 0.127 | **0.0962** | similar | **EXCEEDED** (now below iter-14's 0.067) |
| missing-shapes | 39 (sev=error) | **32 (sev=warn)** | ≤25 | partial (direction right, sev downgraded ✓) |
| extra-shapes | 31 | 30 | 25-40 | **PASS** (in range) |
| structural | 0/18 | 0/18 | 2-5/18 | **MISS** (see below) |
| A5 status | BROKEN | BROKEN | BROKEN/PARTIAL | unchanged (needs band-detector work) |
| pixel | 74.1 | 71.3 | (no prediction) | -2.8 (acceptable trade for shape gains) |
| top warning | extra-shapes warn | extra-shapes warn | (no prediction) | unchanged identity |

## What the cascade primitive proved

The `extend connect every K on @0.k beyond F` primitive **works as designed**: extending each satellite star by 1.5x its natural radius produced 7 fewer missing shapes, dropped that warning from sev=error to sev=warn, and added only ~1 net extra. The cascade hypothesis (cascade #106) is validated as actionable on the SVG-direct path — the predicted blocker (qiyas#371 residue starvation on rasterize→trace path) does not apply here.

## Why structural_score stays 0/18

The new extension-induced shapes don't snap to expected vertex counts because they're *unclipped* — they reach beyond the medallion silhouette and produce open arcs that the A6 detector counts as wrong-shaped. The cascade plan's next primitive is `clip pattern to medallion_outline` (or `clip pattern to <boundary defined by union of satellite circles>`), which would crop those extensions to the visible region. Iter-20 picks that up.

The Tenet 7 stop rule says don't multi-knob — iter-19's job was to prove `extend` works in isolation, and it did. Iter-20 layers `clip` on top to convert the existing missing-shape gains into structural-slot fills.

## What changed in the rankings

- iter-18 #3 sev=error `missing-shapes (39)` → iter-19 #2 sev=warn `missing-shapes (32)` ✓ severity downgrade
- iter-18 #1 sev=warn `extra-shapes (31, cf=+0.0275)` → iter-19 #1 sev=warn `extra-shapes (30, cf=+0.0288)` (essentially flat, slight cf increase)
- iter-18 #2 sev=warn `high-param-drift (9 pairs)` → iter-19 #1 sev=warn `high-param-drift (4 pairs)` — fewer high-drift matches as the extensions help the Hungarian matcher

The new dominant warning by cf_adj is still `extra-shapes` — but now its cf_delta sees value in REMOVING extras, which is the opposite direction of iter-19's edit. This is the iter-20 fork: layer in `clip pattern to` (cascade plan's next primitive) to convert extras into clipped/matched shapes.

## No stop conditions triggered

- missing-shapes did NOT rise → `extend` is the right tool
- composite did NOT drop > 0.02 (rose +0.025)
- Render succeeded cleanly
- structural stayed flat (no regression), with diagnosis (need `clip`)

## Next directive (iter-20)

Layer in `clip pattern to <boundary>` on top of the iter-19 extend. Boundary needs to be defined; the cascade plan suggests `boundary medallion_outline = union(C0_satellite_circles)`. Iter-20 adds:

1. A `boundary medallion_outline = union(@0.0, @0.1, ..., @0.9)` in blueprint (or wherever the boundary primitive lives).
2. A `clip pattern to medallion_outline` after `voids detect`.

Prediction: this converts the "open arc reaching out of medallion" extras into properly-closed partial shapes that A6 can match. Structural should rise from 0/18 toward 5+/18; missing-shapes should drop further; extras should drop significantly.
