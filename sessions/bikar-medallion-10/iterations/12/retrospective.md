# Iteration 12 Retrospective

## What worked
- Adding Cmid radius 65 + `connect every 3 on Cmid` did fill significant
  gaps in three zones simultaneously:
  - inner-star polygon-v0:    4 → 18 of 21 expected
  - rosette polygon-v0:        0 → 17 of 36 expected
  - transition star-v8:        0 → 2 of 4 expected (achieved PASS)
  - transition star-v6:       35 → 45 (overshot slightly but in range)

## What didn't
- A6 binary score stayed 1/18 — the score only counts PASS shapes, and
  no PARTIAL flipped to PASS for inner-star or rosette zones. The "net
  +3 status improvements" is the right metric, not the binary score.
- A2 symmetry got slightly worse (cv 0.0748 → 0.0878). The new ring's
  intersections with satellite circles aren't perfectly even by sector.
  Probably because Cmid radius 65 cuts through some satellite circles
  (centered at distance 100, radius 30 → inner edge at 70) and the
  intersection points fall in slightly different positions per sector.
- Three rosette-zone shapes regressed:
  - rosette band-segment-v2: 5 → 0
  - rosette star-v6:        13 → 4 (the new ring fragmented these)
  - rosette star-v8:         1 → 0 (lost the PASS)

## Why
The new Cmid ring at radius 65 sits between the rosette zone (~50-70)
and the transition zone (~70-100). It's pulling shape classifications
toward the boundary — adding to transition, fragmenting rosette. The
fix would be to push Cmid further out (radius 80) so it sits firmly in
the transition zone, not on the rosette/transition boundary.

## Tool friction
Same as iter 11 — `overall.warnings` empty. The agent had to manually
diff `A6.shapes[]` between iterations to see which moves were
improvements. The orchestrator should be doing this delta-tracking
(qiyas roadmap: rollup self-test).

## Calibration data point (qiyas#75 V2.B)
Predictions for iter 12 (recorded in iter 11/guidance.md):
- A6 1/18 → 4-6/18 PASS. **Actual: 1/18. Miss.**
- A2 cv tighter. **Actual: cv worse. Miss.**
- Pixel 77-79%. **Actual: 76.0%. Miss.**
- A4 stays FULL. **Actual: stays FULL. Hit.**

Lesson: agent-derived predictions are systematically too optimistic
because they only consider the *adding* of shapes, not the
*reclassification* of existing shapes that the new construction
triggers. A real `qiyas score run` counterfactual delta would have
modeled the latter (it's literally counterfactual = "what changes
when X is different"). Without it, predictions are bullish.
