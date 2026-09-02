---
name: detector-trust-gate-satisfied-post-phase4
description: Post-#643 I1 cascade SHIPS=True at 108/108 per-construction PASS (G1+G3+M1+M2 all green); detector-trust gate for #85 resumption satisfied at full I1 acceptance bar
metadata:
  node_type: memory
  type: project
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

After bikar 61c207b sliver-fix (Phase 3) + qiyas 0116d11 i1 corpus regen (Phase 4) + qiyas dd75d49 closeout-report scope fix (#643), `qiyas validate-detector --corpus calibration/i1-corpus/renders --closeout-report` reports **108/108 per-construction PASS** and **SHIPS=True**. Macro gates: M1 PASS at `macro_ari_fused_vs_b = 1.000`, M2 PASS at `n_constructions == 108` (acceptance.yaml bumped 12 → 108 per qiyas#642 + #643 line-75 fix).

**Why:** Initial post-Phase-4 measurement (pre-#643) flagged 24/108 G3 HOLDs (`n_fused_classes equals_field n_b_classes`) on shared-vertex multi-lens constructions, which looked like a real class-namespace gap. Deeper inspection found the impossible combination `petal-6-full: ARI=1.0, n_b=22, n_fused=11` — partitions agreeing perfectly yet class-counts diverging 2× — which is mathematically impossible if both counts are scoped to the same set. Root cause: `n_a_classes`/`n_b_classes` were counted over pre-visibility-filter `a_classes`/`b_classes` sets (validate_detector.py:178), while `n_fused_classes` was counted over post-visibility-filter `union` (validate_detector.py:255). Visibility-filter drops same-color-as-cardinal-neighbor shapes before ARI; after #643 all three counts are scoped to `union`. The G3 "failures" were a measurement-layer bug, not a detector defect. Phase 4 net delta vs HEAD~1 baseline: pre-#643 25 → 24 G3 (real polygon-corner-leakage fix), post-#643 0/108 G3 — zero regressions introduced by Phase 4, zero real G3 gaps remaining. Regression test locked in per Tenet 18 at `tests/test_identity_validate_detector.py` (the `ari==1.0 ⇒ n_fused==n_b` invariant). Measured 2026-05-27 via `qiyas validate-detector --closeout-report` against commit qiyas/dd75d49; verdict at /tmp/post-fix-closeout/verdict.json.

**How to apply:** When the loop picks up #85 (medallion-10 convergence) or any task gated on "detector trust" per the routing plan, the **full I1 acceptance bar is satisfied** — not just the partition-level (G1+M1) bar. qiyas warnings on iter-N+1 renders against bikar 61c207b can be trusted at the I1 acceptance standard. Cite this memory + dd75d49 when proposing #85 resumption. Do NOT re-litigate the "24/108 G3 HOLD" question — it was a measurement-layer bug that no longer exists. Re-measure if bikar gt-emitter or qiyas detector/closeout logic changes materially.

**Companion to:** [[reference_qiyas_calibration_log]] (canonical i1 calibration log location)
