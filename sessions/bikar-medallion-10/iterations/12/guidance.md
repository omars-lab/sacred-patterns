# Iteration 13 Guidance

## Priority
Address the rosette-zone regression: rosette star-v6 13→4 was the
biggest single-shape loss. Push Cmid radius from 65 → 80 so it sits IN
the transition zone, not on the rosette/transition boundary.

## Mechanical edit
1. Move `circle Cmid radius 65` → `radius 80`.
2. Add a second middle ring `Cmid2 radius 50` to close the inner-star
   polygon-v0 gap (currently 18/21, very close to PASS — one more
   construction line should close it).
3. Add `layer 3 / connect every 4 on Cmid2`.

## Predicted score lift
- Predicted A6: 1/18 → 2-3/18 (the polygon close-out should clear PASS,
  and rosette star-v6 should recover).
- Predicted A2: cv 0.0878 → 0.06-0.07 (Cmid moved off the boundary
  should help symmetry).
- Predicted pixel: 76.0 → 76-77% (small).

## Caveat
This iteration adds two new construction circles (Cmid moved + Cmid2
new). That's a larger change than mechanical-translation-table
prescribes for one warning. The risk is over-correction. If iter 13
regresses or stagnates, the right next move is to revert to iter 12's
structure and try a single-parameter tweak instead.
