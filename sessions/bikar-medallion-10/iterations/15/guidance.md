# Iter 15 — guidance (post-hoc, what was attempted)

## What changed and why

**Edit:** added `strapwork width 5 crossing alternating` block to iter-14's pattern.bkr. Everything else byte-for-byte identical.

**Source warning:** iter-14's `validation.json → overall.warnings[0] = missing-shapes δ=0.0667` (encoder-vocab noise, see iter-14 guidance for tenet-6 reasoning). Acted instead on the **second-tier signal** of A5 BROKEN status (17/45 crossings) per iter-14 retrospective's recommendation: "iter 15: shift focus to A5 bands ... the path forward — adding strapwork or band rendering — is well-understood."

**Why this edit was expected to produce strapwork:** bikar's `strapwork` block converts every line in the construction into a parallel pair of bands separated by a gap of `width`, with alternating over/under crossings rendered.

## Predicted impact (was)

| Metric | iter 14 | iter 15 (predicted) |
|---|---|---|
| composite_score | 0.7842 | 0.83–0.88 |
| structural_score | 1/18 | 2/18 |
| A5 bands | BROKEN (17/45) | COMPLETE (~45/45) |
| pixel_similarity | 74.1% | 73–75% (small dip ok) |

Total predicted Δcomposite ≈ +0.05 to +0.10.

## Actual impact (was)

See evaluation.md / retrospective.md. Headline: composite −0.124, A5 advanced only one notch (PARTIAL), A2 symmetry regressed (alternating mode breaks 10-fold), extra-shapes spiked (+149 unmatched fragments).

## Stop conditions hit

- Composite drops > 0.02: **TRIGGERED** (−0.124). Per iter-14 guidance pattern, this is a REVERT signal.
