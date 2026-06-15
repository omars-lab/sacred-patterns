# Iter 14 — guidance

## What changed and why

**Edit:** added `connect every 3 on C1` to Layer 0 (one new line). Everything else is iter 13 byte-for-byte.

**Source warning:** `validation.json → svg-audit → audits.A6.shapes` reports `inner-star--rhombus-v4` as MISSING (`found=0, expected=10`) — the inner-star zone has zero 4-vertex shapes against an expectation of 10 rhombi.

**Why this edit produces rhombi:** Layer 0 already overlays the {10/4} rosette on C1 (10 division points connected every 4th). Adding `connect every 3 on C1` overlays a {10/3} decagram on the same circle. The {10/4} edges and {10/3} edges intersect at 10 lens-shaped/rhombic regions arranged 10-fold around the inner star. After `voids detect`, those intersection regions become 4-sided faces, classified as `rhombus-v4` by qiyas's encoder, and inherit the existing `fill void where sides == 4 color royal` rule.

**Why we did NOT chase the literal `warnings[0]` rationale:** the top warning is "53 missing shapes" with rationale "if recon had the 53 missing ref shape(s), they would match perfectly." Diff.json categorization shows those 53 are 37 circles + 15 lenses + 1 girih_rhombus. Circles and lenses are encoder-vocabulary artifacts from the photo-traced reference (round photographic regions classified as circles), not constructions our SVG needs to render. Acting on the literal rationale would have us add 37 random circles, which would not improve the score and would regress visual fidelity. (CLAUDE.md tenet 6 — verified inherited claim before acting.)

## Predicted impact

| Metric | iter 13 | iter 14 (predicted) |
|---|---|---|
| composite_score | 0.7632 | 0.81–0.84 |
| structural_score | 1/18 | 2/18 |
| A6 inner-star--rhombus-v4 | MISSING (0/10) | PASS (8–12/10) |
| pixel_similarity | 74.1% | 73–75% (small dip ok; structural gain offsets) |

Total predicted Δcomposite ≈ +0.05 to +0.08.

## What to verify after rendering

1. `validation/svg-audit/svg-audit.json → audits.A6.shapes[?id="inner-star--rhombus-v4"]` shows `status=PASS` with `found` between 8 and 12.
2. `validation/validation.json → overall.composite_score` ≥ 0.79 (lower bound of predicted range, allowing for rollup nonlinearity).
3. `validation/validation.json → overall.warnings[0]` is no longer the same item — should rotate to a different blocker (likely `inner-star--star-v8 MISSING` or A5-bands related).

## Stop conditions specific to this iter

- Render fails or no rhombi appear: revert to `connect every 4` only on C1, log as DSL gap (multiple `connect every` on same circle may not work as expected), file qiyas/bikar issue.
- Composite drops > 0.02: revert, file qiyas-side issue (rhombi added but scored as regression — likely a coverage or symmetry side-effect).
- Rhombi appear but get classified differently (e.g. as lenses or triangles): file qiyas-side encoder classification issue, keep iter 14, move on.
