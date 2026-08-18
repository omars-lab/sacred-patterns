---
name: Geometric-algorithm tests need asymmetric witnesses
description: Regular-n-gon test fixtures absorb start-shift / reflection / orientation bugs because their automorphism group masks them. Every invariant test must also be run against a scalene/irregular shape.
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
When writing unit tests for any geometric algorithm (signatures,
distance metrics, classifiers, canonicalization), include an
**asymmetric witness** — a polygon whose only symmetry is the identity
— alongside the symmetric fixture. Examples: scalene triangle,
irregular pentagon with no parallel sides and 5 distinct edge lengths.

**Why:** The I1 iter-2 turning-function implementation passed 12/12
unit tests against regular hexagons (translation, rotation, scale,
start-vertex-shift, orientation-flip invariants), all of which were
trivially satisfied because hexagon vertices are interchangeable
under rotation. When the user asked for a testing standard, I added
asymmetric witnesses (scalene triangle + irregular pentagon) — 6
tests immediately failed, exposing real bugs in start-shift,
orientation-flip, and combined-transform handling that would have
contaminated iter-2's threshold calibration. The bugs were
algorithmic, not numerical.

**How to apply:** For every invariant claim a geometric algorithm
makes, write the test in two flavors — one against a regular n-gon
(`test_X_regular`) and one against an asymmetric polygon
(`test_X_asymmetric`). The asymmetric witness is the load-bearing
case; the regular case is for readability. The full standard lives
at `qiyas/docs/testing-asymmetric-fixtures.md` (cross-referenced
from CLAUDE.md "Conventions" → Tests). Applies to:
identity/signature/distance code, arrangement classifiers,
canonicalization, shape detectors with confidence formulas.
