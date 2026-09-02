# Iteration 11 Retrospective

## What worked
- The `connect every 4 on @0.k` per-satellite construction (kept from iter 7's
  breakthrough) continued to produce 11 distinct {10/4} rosettes — the
  structural foundation of the medallion is sound.
- `layer 0` / `layer 1` isolation kept the central rosette and the satellite
  rosettes from interfering on the intersection graph.

## What didn't
- The interstitial zone between center (radius 30) and satellites
  (centered at radius 100) was empty. A6 baseline showed 17 of 18 expected
  shapes MISSING/PARTIAL, dominated by:
    - inner-star polygon-v0: 4 / 21 (75% gap)
    - rosette polygon-v0: 0 / 36 (100% gap)
    - rosette star-v6: 13 / 28 (54% gap)
- A2 symmetry was UNEVEN (cv 7.48%) — sectors disagree on shape counts
  because the empty interstitial leaves wedge boundaries undefined.
- A5 strapwork BROKEN by design (no strapwork built — deferred).

## Why
Iter 11 deliberately deferred the interstitial zone to verify that the 11
same-size rosettes structure was correct in isolation. That verification
succeeded — but left 17/18 baseline shapes MISSING/PARTIAL because the
inner-star, rosette, and transition zones all rely on construction
geometry that was still missing.

## Tool friction encountered (this iteration)
The orchestrator's `validation.json → overall.warnings` was empty: the
published Docker image (`ghcr.io/naqshcoffee/qiyas:v0.1.0`) lacks the
`score run` subcommand, and the rollup script discards per-audit
warnings when `qiyas score` is unavailable. The iteration agent had to
manually derive the priority from `audits.A6.shapes[].status` —
exactly the kind of free-form re-derivation the warnings ranking was
designed to prevent. Filed as
`qiyas/docs/issues/2026-05-02-orchestrator-warnings-empty-when-score-unavailable.md`
with the iter 11 SVG + validation.json + baseline as the reproducer
fixture in `qiyas/fixtures/bikar-medallion-10-iter11.{svg,json,validation.json,baseline.json}`.
