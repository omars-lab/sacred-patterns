# Iteration 12 Guidance

## Priority
**Coverage of the interstitial zone.** Per A6, the inner-star and
rosette zones are the most under-tiled (rosette polygon-v0: 0 found of
36 expected, 100% gap — largest signal in the audit). Per A2, the
interstitial gap is also breaking sector symmetry (cv 7.48%, sectors
1-3 missing 0-gons and 6-gons that sector 0 has).

## Mechanical edit
Add a middle ring `Cmid` at radius 65 (midpoint between C1 radius 30
and the satellite ring inner edge at radius ~70). `divide Cmid into 10`
to match the dominant 10-fold symmetry. Then add a `layer 2 / connect
every 3 on Cmid` to produce {10/3} 6-pt stars in the transition zone —
matching the existing transition--star-v6 PARTIAL signal.

## Why this is mechanical
The translation is from the
`bikar/.claude/skills/iterate-pattern-from-qiyas-warnings` skill's
table:
- Warning class `coverage-sparse` / A6 `baseline-shape-missing` →
  "add a middle-ring construction circle, then connect on it".
- Warning class `n-fold-broken` (A2) → "isolate per-sector layers OR
  ensure the underlying construction has the missing geometry" — adding
  Cmid should fix both because the missing shapes ARE the symmetry
  break.

## Predicted score lift
- Predicted A6: from 1/18 → 4-6/18 (interstitial zone gets ~3-4 PASS shapes).
- Predicted A2 cv: from 0.0748 → 0.04-0.06 (symmetry tightens).
- Predicted pixel: from 75.9 → 77-79 (more area covered, closer to ref).
- Predicted A4 coverage: stays FULL (already over-tiled bbox).

(These are agent-derived predictions — the proper
`counterfactual_score_delta` from `qiyas score run` is not available
this iteration; see iter 11 retrospective.)

## What this does NOT address
- Strapwork (A5 BROKEN). Deferred — needs structure first per
  CLAUDE.md G2 (architecture before pixels). Once A6 stops dropping
  shapes from the interstitial zone, the next iteration can add
  `strapwork width 5 crossing alternating`.
- Boundary/outer ring (mentioned in iter 11 evaluation). Same reasoning.
