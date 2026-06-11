# Wave Planning — the incremental radial walk (design doc)

Plain English: before reconstructing a pattern from a photo, we plan WHICH
shapes to copy in WHAT order. The plan has two levels: **waves** (one wave =
one kind of simple shape) and **flowers** (composite shapes built from several
waves that repeat around the center). The owner gates the plan before any
construction starts; iteration then walks the plan inside-out, one wave at a
time, with each wave's diff cropped to its own region. The whole-image diff is
a trend log, never the steering signal.

Tool: `tools/plan-waves.py <session-dir> --center X Y --diameter D [--seat W=F]`
(runs under the qiyas venv: `/Users/omareid/Workspace/git/qiyas/.venv/bin/python`).
Protocol home: `.claude/skills/iterate-construction-hypothesis/SKILL.md` →
"Stage 1 is wave-based". First execution: bikar-medallion-10, 2026-06-11.

## Why this exists (the owner directives, 2026-06-11)

- "It's obvious the structures do not match … start by getting structure to
  match in center and work our way around radially outward."
- "Planning experience that shows the first wave of shapes radially … until we
  agree on waves and all shapes from original image exhausted."
- "Not go for one shot diff."
- "The wave only includes the same kind of shape … their midpoints should be
  equidistant from origin … same shape / similar / rotated versions of each
  other … similar area, etc."
- "Group into more complex shapes … there is a shape that is similar to our
  middle shape that revolves around the origin — it's a mix of several waves."

## Pipeline

1. **Validate the center.** Auto-detect (mass center of the medallion mask),
   owner confirms/adjusts with one click (`review/structure-priorities.html`
   Step 1). Every radius and angle is measured from this point.

2. **Exhaust the shapes (bridge-snap segmentation).** Tiles = medallion mask
   minus near-white (all channels ≥ 200). JPEG softening leaves 1–3px
   sub-threshold gaps in the ~5px white lattice, so adjacent tiles fuse
   (witnessed: whole medallion → ONE component). Fix: 4-connected binary
   erosion (2 iterations) → label the cores → grow labels back over the full
   tile mask via nearest-seed EDT. Coverage stays 100% and the JSON reports
   `coverage_of_tile_area` so "all shapes exhausted" is checkable.
   Components < 25px are fragments: they inherit the nearest real shape's
   wave (exhaustiveness) but are excluded from kind statistics.

3. **Group shapes into same-KIND waves.** Two real shapes are the same kind
   iff ALL hold (thresholds as shipped):
   - midpoints equidistant from center: |Δr_frac| < 0.04
   - similar area: max/min ratio < 1.3
   - same/rotated copies: rotation-invariant central-moment match —
     φ1 = (μ20+μ02)/area² within 25% relative, eccentricity proxy
     ecc = √((μ20−μ02)²+4μ11²)/(μ20+μ02) within 0.2 absolute
   - similar color: raw mean-RGB euclidean distance < 60 (NOT palette names)
   Kinds = connected components of the pairwise all-criteria graph, ordered
   inside-out by mean radius (bigger shapes first on ties).
   **Validation: kind counts must respect the fold.** A 10-fold pattern
   yields counts of 1/10/20/40; a 7 or 13 means the grouping is wrong.

4. **Group waves into composite FLOWERS (motifs).** The biggest tiles
   (≥ 0.8 × max area) are anchor stars; anchors cluster into radial rings
   (gap > 0.1 r_frac splits rings). Each ring seeds one flower family. A wave
   joins the family the majority of its members sit nearest to (euclidean to
   anchor centroids). Within a family, each shape belongs to one INSTANCE
   (one physical flower): fold-divisible waves chunk consecutive-by-angle
   into instances aligned to the anchors; non-divisible waves (lost slivers)
   fall back to per-member nearest-anchor.
   **Validation, the composite analog of the fold check: every instance of a
   family must hold the same wave-multiset.** Deviations are reported, not
   hidden.
   A flower is the DSL-native unit: build one instance, `rotate` fold times.

5. **Owner gates the plan.** `wave-plan.html` (flowers row + waves row, one
   group bright per frame, all-flowers / all-waves colored maps, plain
   language only — Tenet 27). Construction starts only after "waves agreed",
   recorded in `session.json` → `stage_gates.structure.wave_plan.agreed`.
   Owner corrections re-seat waves via `--seat WAVE=FLOWER` (1-based), no
   code change.

6. **Iterate the radial walk.** Each `stage: structure` iteration targets the
   lowest unmatched wave; its gate visual and diff are cropped/masked to that
   wave's region. Wave N passes before wave N+1 opens.

## Witnessed dead ends (do not retry)

| Attempt | Failure | Replacement |
|---|---|---|
| Raw radius-histogram bands | outer field has no radial density valleys — 93% of the pattern landed in one wave | same-kind connected components |
| Palette-NAME color equality | names flicker at k-means cluster boundaries — one kind of 10 split 4 "turquoise" / 6 "cyan" | raw mean-RGB distance < 60 (within-kind ≈ 40, across families ≈ 110) |
| Plain labeling without erosion | JPEG-soft lattice gaps fused the medallion into one component (41 "shapes") | bridge-snap: erode → label → grow back (100% coverage) |
| Per-member nearest-anchor instances | kinds sitting exactly between two flowers (18° offset) coin-flip on jitter — [1,…,1,2,2] splits over 9 instances | consecutive-by-angle chunking for fold-divisible waves |
| Spoke-offset as flower-membership test | flower petals legitimately alternate on/off spoke (waves 2/4/6/8/12 at 18° are clearly petals) | euclidean family vote + owner gate adjudication |

## Medallion-10 result (first execution)

426 shapes (380 real + 46 fragments), 100% coverage. 22 same-kind waves,
counts all 10-fold. 3 flowers: the middle flower (×1, 21 shapes), the inner
flowers (×10, 15 shapes each), the outer flowers (×10, 21 shapes each) — the
owner's "similar to our middle shape" confirmed by count (21 = 21). Open
adjudication at the gate: wave 13 (turquoise ring, r≈0.59) seats "inner" by
distance but the owner's eye says "outer"; wave 15 (small navy stars, r≈0.65)
seats "outer" but the owner's list skipped it.

## Future work

- **Generalized composite-repeat detection** (tracked as bikar task #39): as
  the radial walk extends outward, grow candidate composites (seed + adjacent
  shapes) and test whether the same composite recurs ANYWHERE — rotational
  repeats around the center AND repeats at other radii/positions (e.g. a
  border motif that also appears in an interstitial zone). A confirmed repeat
  becomes a motif: build once, stamp everywhere. The current implementation
  covers the anchor-seeded rotational case only.
- Per-wave diff cropping tooling (lands with the first wave-1 structure
  iteration).
