# Iteration 39 — Visual Verdict

Plain English first: we swapped the simple 3-line decoration inside every
lens-shaped pocket for a true star motif (the new `pockets star` engine
variant), and it produced the first pixel-similarity movement above the
74.2% plateau — a genuine but small structural win. A fancier two-tone
coloring of the new star faces *looked* better to the eye but measured
worse, so it was reverted by ablation. Along the way we found and fixed a
real parser bug that had silently broken `source ==` / `source !=` queries
against kernel-applied tags.

## Numbers

| Metric | iter-38 (baseline) | iter-39 (final) | Δ | Predicted |
|---|---|---|---|---|
| pixel similarity | 74.2 | **74.7** | **+0.5** | +0.5 to +1.5 ✓ (low end) |
| color match | 67.8 | 67.5 | −0.3 | +0.5 to +1 ✗ |

Ablation table (all measured against the same reference, qiyas:latest,
control re-measure of iter-38 reproduced 74.2 exactly):

| Variant | pixel | color | verdict |
|---|---|---|---|
| iter-38 baseline (3-chord pockets) | 74.2 | 67.8 | control |
| star geometry + iter-38-style fills (final) | **74.7** | 67.5 | **adopted** |
| star geometry + two-role split (inner cobalt / corner navy) | 72.4 | 66.2 | reverted (−2.3 vs final) |

**Geometry alone is worth +0.5 pixel.** The color prediction missed: the
star vocabulary's small corner faces fall through to the `sides` rules and
slightly dilute the cyan, so color dipped −0.3 instead of rising.

## What happened (debugging story)

1. **Cyan flood.** The hypothesis' fill (`source == _girih_hexagon_star`,
   no guards) matched 1,600/1,932 faces — the whole inter-rosette field
   went cyan. Root cause is semantic, not a bug: the star loop + BOTH host
   decagons' decoration chords partition each lens into ~12 faces, and
   *every* lens face touches a star edge; lenses tile the field. The
   hypothesis' "~7 faces/lens, drop the guards" model was wrong.
   Restoring iter-38's `area >= 360` guard keeps the ~610 big in-lens
   faces (~4.7/lens) and recovers the intended look.
2. **Parser source-registry bug (bikar task #31).** Building a two-role
   split needed `source != _girih_outline` — which matched every face. A
   red/green debug render showed `!=` was vacuously true: the parser
   hashed queried source names but never *registered* them, so
   kernel-applied tags (`addTag`: `_girih_outline`, `_girih_decoration`)
   were unresolvable and `==` silently never matched. Fixed in
   bikar parser.ts (`registerSourceName` at parse time) with a red→green
   regression test in evaluator.test.ts. This unblocks all future
   sub-role splits against kernel tags.
3. **Two-role split reverted by ablation.** With the fix, the split worked
   as designed (70 enclosed star faces cobalt / 1,530 corner faces navy)
   and looked closer to the reference's navy field — but measured −2.3
   pixel vs the simple form. Reverted.

## Method lesson (now confirmed three times)

Eye/center samples validate color *direction* only; **only an ablation
render validates a remap.** iter-38's kite remap (−0.9), iter-39's navy
remap (−2.3). The "looks closer to the reference" intuition lost to the
metric both times this session.

## Expected vs observed (Tenet 24)

Pre-stated expectation: each of the 130 lenses reads as a saturated-cyan
pocket with a white strapwork star band woven through all 6 lens-edge
midpoints; rosettes/kites/pentagons unchanged. **Observed: matches** in
the final form. The one divergence en route (whole-field cyan flood) was
the bug-locator for finding the wrong face-vocabulary model.

## Routing — next gap (iter-40 candidates)

The residual is **diffuse and structural** (heatmap red everywhere, viewed
full-size): our converged field is a much finer mesh than the reference's
bold rosette flowers; the reference shows solid saturated-cyan 8-point
stars AND small dark navy stars on a navy-dominant ground with a thick
white lattice.

- **Falsified this iteration:** navy remap of star corner faces (−2.3).
- **Candidate A (carried since iter-36):** scalloped boundary ring —
  authorable today with `connect arc` chains on a separate layer (engine
  audit confirmed: construction work, not an engine gap).
- **Candidate B (newly unblocked):** different sub-role splits using the
  now-working `!=` against kernel tags (e.g. `_girih_decoration`), but
  any remap must be ablation-gated per the method lesson.
- **Candidate C:** the fine-mesh-vs-bold-rosettes gap suggests the field
  scale/density itself (shell count, tile scale 62) may be the next
  structural lever — would need its own hypothesis.

Gate status: 74.7 / 80 — gap of 5.3 pixel points to the expert-review
gate (task #4).

## Artifacts

- `pattern.bkr` — final (ablation-chosen) form
- `render.svg` / `render.png` — regenerated from final form
- `pattern.gt.json` — 933 shapes
- `diff/pixel-diff.json` — 74.7 / 67.5
- `/tmp/m10-39abl/` — ablation variant scratch (same numbers, confirms regen)
- `/tmp/m10-39dbg/` — red/green role-split debug scaffold that exposed the
  parser registry bug
