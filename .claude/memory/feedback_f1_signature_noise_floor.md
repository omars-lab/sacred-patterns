---
name: f1-signature-noise-floor
description: F1 signature step=0.5° is the same magnitude as the qiyas detector's actual rasterization noise on the Phase 1.A corpus, so naive multi-probe LSH only catches a thin slice of mismatches; widening the bin or switching to tolerance-bounded matching is a spec-level decision, not an implementation tweak
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
When iterating qiyas detector identity-fidelity (#152), don't reflexively reach
for textbook bin-edge fixes (multi-probe LSH, shifted-grid quantization)
without first measuring the actual noise floor in the corpus.

**Why:** I1 iter-1 (2026-05-04) implemented multi-probe signature emission
predicting +0.40 macro lift; got +0.044. Direct evidence: detector noise on
star7 pentagons is commonly EXACTLY 0.5° on multiple angles per shape — i.e.
one full bin step, not the sub-bin jitter multi-probe is designed to absorb.
A bin-step-sized noise floor cannot be rescued by shifting the grid by
half a bin; both grids' centers will be one bin apart in opposite directions.

**How to apply:** Before proposing any signature-quantization change, sample
3-5 unmatched truth/detector pairs from the D3 report and compute the actual
per-element angle/ratio drift. If drift ≈ bin step (or larger), the
legitimate moves are spec-level:

- **Widen the bin (step=1.0°)** — collapses F1 into F2 semantics; would
  also collapse medallion10 truth classes that are 0.5° apart by design
  (C1 vs C30, C2 vs C11). Owner decision required.
- **Tolerance-bounded set match** — abandon quantization-as-hash; emit raw
  angle/ratio sequences and match per-element with hard tolerance. Closer to
  what F1 was conceptually after but breaks the "signature is a string hash"
  contract D3 and D4 depend on.
- **Detector-side noise reduction** — investigate `cv2.approxPolyDP` epsilon
  or polygon smoothing upstream of signature computation. Doesn't touch
  signature semantics.

These are mutually exclusive at the spec level. Don't pick one in a single
iteration without surfacing the choice. The iterate-detector-calibration
skill's "spec_divergence_surfaced" stop_state in tally.json is the correct
exit condition when the next move requires a spec rewrite, not a parameter
tweak.

**Concrete numbers from iter-1 for future agents:**
- Baseline (canonical exact-match only): macro 0.002.
- After multi-probe with one half-shifted grid: macro 0.046.
  - star10: 0.0 → 0.133 (one shifted-rescue match — mechanism IS sound)
  - star7: 0.0 → 0.0 (noise > half a bin step, mechanism doesn't reach it)
  - medallion10: 0.006 → 0.006 (already matched what canonical could match)
- Ceiling under any pure-quantization strategy at step=0.5° appears to be
  in the low single digits. Reaching the 0.7 acceptance threshold needs a
  spec move.
