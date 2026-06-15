# Iteration 13 Evaluation

## Context
Moved Cmid from radius 65 → 80. Added Cmid2 at radius 50 with `connect
every 4`. All other geometry preserved from iter 12.

## A1: Structure
- Faces: 398 → 516 (+118). Two new construction rings each add many
  intersections.

## A2: Symmetry
- cv: 0.0878 → 0.067 (improved! sectors more even now). Predicted hit.

## A6: Baseline Shape Match
- Score: 1/18 → 1/18 (unchanged binary)
- Net status moves: better=4, worse=7, same=7. **Net REGRESSION.**

  Improved (4):
  - inner-star polygon-v0:    18/21 PARTIAL → 19/21 PASS  ✓ (close-out worked)
  - rosette band-segment-v2:   0/4  MISSING → 5/4  PARTIAL
  - rosette polygon-v0:       17/36 PARTIAL → 20/36 PARTIAL
  - rosette star-v6:           4/28 PARTIAL → 16/28 PARTIAL  (recovered)

  Regressed (7):
  - inner-star band-segment-v2: 0/3  MISSING → 7/3  EXCESS
  - inner-star star-v6:         0/2  MISSING → 7/2  EXCESS
  - inner-star star-v8:         1/6  PARTIAL → 0/6  MISSING (lost ground)
  - transition band-segment-v2: 5/3  PARTIAL → 0/3  MISSING
  - transition polygon-v0:      0/4  MISSING → 10/4 EXCESS
  - transition star-v6:        45/41 PARTIAL → 36/41 PARTIAL (further from)
  - transition star-v8:         2/4  PASS    → 0/4  MISSING  ✗ (LOST PASS)

## Pixel similarity
- 76.0% → 74.1% (-1.9pp). Material regression.

## Predicted vs actual
- Predicted A6 1/18 → 2-3/18. **Actual: 1/18. Miss.**
- Predicted A2 cv 0.06-0.07. **Actual: 0.067. HIT.**
- Predicted pixel 76-77%. **Actual: 74.1. Miss (worse).**

## Diagnosis
Adding Cmid2 ring at radius 50 over-tiled the inner-star zone (now has
EXCESS shapes — 7 found of 3 expected for band-segment-v2 and star-v6).
The inner-star zone wants 21 polygons + 10 rhombi + a few stars; we now
have far too many crossing arcs in that zone.

The transition zone also lost shapes because the new Cmid2 ring's
intersections with C1 changed which faces classify as inner-star vs
transition.

## Stagnation alarm
A6 score has been 1/18 for 3 consecutive iterations (11, 12, 13).
Per CLAUDE.md "structural stagnation rule": STOP and perform a Brutal
Honesty Checkpoint. The construction approach (sequential ring
additions) may be fundamentally wrong — what's needed is a
sector-by-sector wedge construction (`rotate 10 around C0.mpt /
connect cycle [...]`) that produces exactly the right shape counts in
each zone, rather than ring-and-hope.

## Next-step recommendation (NOT implemented in this iteration)
Revert to iter 12's structure (Cmid radius 65, no Cmid2). Then for
iter 14, replace `connect every K on <ring>` with explicit
`connect cycle [point1 point2 ...]` wrapped in `rotate 10 around
C0.mpt` — the wedge-and-rotate strategy from
`bikar/.claude/skills/pattern-construction`. This forces sector
symmetry to be exact and lets the agent name *which* faces should
exist in each zone rather than hoping they emerge from ring
intersections.

This is a fundamental approach change, not a parameter tweak. It's
beyond the scope of "translate one warning into one DSL edit" — and
that's exactly the signal: the warnings-driven loop hits a ceiling
when the underlying construction approach is wrong, and only a Brutal
Honesty Checkpoint can break that ceiling.
