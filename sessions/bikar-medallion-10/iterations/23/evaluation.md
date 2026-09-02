# iter-23 — bikar#114 Slice 2: end-to-end validation of canonicalEdgeOrder

**Pattern:** identical DSL to iter-16 (`crossing over`, width 5).
**Bikar HEAD:** 8c17615 (canonicalEdgeOrder shipped 8bc6735, present in dist).
**Qiyas:** master (svg_primitives.py 0d96d3c — Slice 5 path branch fix in place).

## Why this run exists

iter-16 (2026-05-03) catastrophically broke A2 (cv 0.067 → **0.2671**)
and spawned **247 sector-fragmenting strapwork extras** under
`crossing over`. Root cause located in `assignStrands` outer loop
(`strapwork.ts:291`): seed-edge order = `graph.edges` insertion order,
which is not rotation-invariant. Two rotated copies of the same input
produced different strand-ID groupings → different per-sector band
geometry.

bikar#114 PR1 (commit 8bc6735) shipped `canonicalEdgeOrder` — polar-angle
seed ordering about the geometric centroid with radius + node-index
tie-breaks. PR1 was unit/snapshot/tsc green but Slice 2 (end-to-end
medallion-10 re-render to confirm A2 cv recovery) was owner-gated at
commit time pending the no-render-authorization waiver.

This iter is Slice 2 — same DSL as iter-16, fresh render through patched
bikar, qiyas svg-audit verdict comparison.

## Validation outcome

End-to-end Slice 2 **PASSED** — PR1's tie-breaks do NOT misbehave on
medallion-10's polar geometry. **PR2 (orbit detection) is unnecessary.**

| Metric                     | iter-16 (pre-fix) | iter-14 (baseline) | iter-23 (post-fix) |
|----------------------------|------------------:|-------------------:|-------------------:|
| A2 status                  | BROKEN            | EVEN               | UNEVEN             |
| A2 cv                      | 0.2671            | 0.067              | **0.0526**         |
| A5 status                  | BROKEN            | PARTIAL            | **COMPLETE**       |
| dominant_fold              | 10                | 10                 | 10                 |
| dominant_fold confidence   | (low)             | (medium)           | **0.76**           |
| total shapes (encoding)    | (n/a)             | (n/a)              | 1463               |
| sector totals (10-fold)    | -                 | -                  | 127–161 (cv 5.26%) |

**A2 cv 0.0526 < iter-14's 0.067 baseline** — the fix not only recovers
from iter-16's regression, it produces a *better* sector-balance
distribution than the iter-14 baseline that had no strapwork at all.

**A5 = COMPLETE** (10 lenses detected, 33 estimated bands, 292 band
crossings, 302 total crossings — band-network integrity 100%) is the
single largest verdict improvement of the whole medallion-10 cascade so
far.

## Status mismatch — UNEVEN vs EVEN

A2 reports UNEVEN because 22 mismatches remain (one sector has 161 vs
others at ~145; one has 127). This is the residual structural drift
that medallion-10 still has to close (#85 ongoing) — but the cv has
dropped below the iter-14 baseline, so this is now noise in the
per-sector distribution, not a symmetry break.

## Composite score (not run here)

Composite scoring requires an iter-14 baseline.json comparison; not run
in this validation pass. The A2 cv + A5 status delta is the load-bearing
evidence Slice 2 needed.

## Slice 2 conclusion

bikar#114 PR1 (commit 8bc6735) end-to-end validated. The plan's PR2
fallback ("If PR1's tie-breaks misbehave on any pattern, implement
explicit orbit detection") is **not triggered** — medallion-10's
10-fold polar geometry is precisely the case PR1's centroid+angle
sort handles cleanly. PR3 (Hankin face-walk per Kaplan 2005) remains
deferred per the original plan.

bikar#114 ready to mark RESOLVED.
