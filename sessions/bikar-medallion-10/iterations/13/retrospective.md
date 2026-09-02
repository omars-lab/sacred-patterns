# Iteration 13 Retrospective

## What worked
- A2 symmetry improved (cv 0.0878 → 0.067) — moving Cmid off the
  rosette/transition boundary helped.
- inner-star polygon-v0 finally hit PASS (19/21).
- rosette star-v6 recovered (4 → 16, getting closer to 28 expected).

## What didn't
- Net A6 regression (better=4, worse=7).
- Pixel regression (-1.9pp).
- inner-star and transition zones now have EXCESS shapes (more found
  than expected) — the two new construction rings produce too many
  intersection-derived faces.

## Why
The hypothesis "more rings = more correct shapes" is failing. Each new
ring adds intersections everywhere, not just in the zone it was meant
to address. The classification of existing shapes shifts as new
construction is added.

## What to do differently
**Stop adding rings.** The next iteration should NOT add construction
geometry. It should either:
1. Revert to iter 12 (best A6 net delta of the three) and shift to
   wedge-and-rotate construction, OR
2. Stop iteration session here, report findings, and request user
   decision on whether to pivot to wedge-and-rotate.

Per the budget ("aim for 5 iterations max ... headline deliverable is
the bikar skill (Step 0) + ≥3 high-quality journal entries"), I am
choosing (2) — three iterations is enough calibration data and the
session has surfaced the high-value qiyas issues. Iter 14 would
require a fundamental approach change that's its own deliverable.

## Tool friction
Same as iter 11/12 — `overall.warnings` empty. Adding to journal:
when warnings ARE empty, the iteration agent can't tell whether the
correct response is "your last edit was fine, keep iterating" or
"your approach is wrong, pivot". A real warnings array with
counterfactual deltas would have made this distinction obvious
(`counterfactual_score_delta < 0.05` is the documented "ask user"
trigger from iteration-guide.md).
