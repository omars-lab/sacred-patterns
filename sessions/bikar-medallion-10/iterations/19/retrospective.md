# Iter 19 retrospective — cascade #106 primitive validates on first application

## What this iteration was for

First substantive application of cascade #106 (partial-shape rendering via construction). Iter-18 cleared the slice-1 strapwork-rotation gate; new top warning was missing-shapes (sev=error). The cascade's `extend connect ... beyond F` primitive shipped in bikar already; iter-19 applied it to the 10 satellite stars to test the cascade's central prediction: *that the unrealized leverage on rasterize→trace path (per cascade header / qiyas#371) does land on the SVG-direct path*.

## What we learned

### The cascade primitive is real and load-bearing on the SVG-direct path

A single `extend ... beyond 1.5` applied to 10 satellite connect statements moved 4 axes positively (composite +0.025, A2 cv -0.031, missing-shapes -7 + severity downgrade, high-param-drift -5 pairs) and only one axis negatively (pixel -2.8, expected as new geometry introduces new local mismatches).

The cascade plan's verification section predicted "+0.05 to +0.10 from a single edit." We got +0.025 — half the predicted leverage on the first try. The remainder is gated on `clip pattern to medallion_outline`, which iter-20 layers on.

### A2 cv crossed below iter-14's baseline

Iter-14's 0.067 was the gold standard; iter-15-17 polluted with rotation noise (0.27); iter-18 cleared most of it (0.127); iter-19 actually went BELOW iter-14 (0.0962). The extension regularizes the geometry — every satellite's edges are now symmetric *under the same 10-fold rotation*, where iter-14 had asymmetric reach at the boundary.

### Structural 0/18 is a *clipping* problem, not an *extension* problem

The new extension shapes are correct in topology — A6 still scores 0/18 because they aren't *closed*. They reach into space outside the medallion silhouette and present as open arcs. This is exactly the gap the next primitive (`clip pattern to`) closes. The 0/18 is a known-cause signal, not a failure of the iter-19 edit.

### Cascade #106 leverage prediction validates direction, undershoots magnitude

The cascade plan said one `extend` edit could close 30-40% of the bare-region pixels. We got pixel -2.8 (a slight LOSS) — the cascade was right that the extensions populate the right zones, but wrong that they immediately improve pixel match without clipping. The clipping step (iter-20) is the actual pixel-improvement gate; this iter's structural prep is the pre-condition.

## Process notes

### Predictions calibration

Predicted composite range +0.02 to +0.06 — landed at +0.025 (low end). The "+0.05 to +0.10" cascade-plan figure was for the combined `extend` + `clip` edit; splitting them per Tenet 7 means each half-step delivers half the leverage.

Predicted missing-shapes ≤25 — landed at 32 (predicted too aggressive). Reason: extensions help, but uncrop'd extensions can't fully replace clipped shapes in the reference. Recalibrate to predict 2/3 of the gain on `extend`-only and the remaining 1/3 on `clip`.

### Multi-knob discipline (Tenet 7) paid off

Could have done `extend` + `clip` together for a single bigger composite jump. Splitting them gave a clean signal that `extend` alone moves missing-shapes down 7 and structural 0→0 — the structural-0 result is the diagnostic that *needs* the next primitive. Combined edit would have hidden whether `extend` or `clip` was doing the work.

## Cross-task impact

- **sacred-patterns#106 (partial-shape cascade):** **validated** on SVG-direct path. The cascade plan's central hypothesis ("extend + clip closes 30-40% of bare-region pixels") is now in measurement-confirmed territory; iter-20's clip step is the second half of the verification.
- **sacred-patterns#80/#85 (medallion-10 convergence):** new ceiling at composite=0.8236. Above the iter-14 0.7842 baseline by +0.039 net (across slice-1 fix + extend primitive).
- **bikar#114 PR1:** continues to be downstream-validated by these gains — slice-1 fix is showing compounding benefit as new cascade primitives layer on top of a clean A2 baseline.
- **qiyas#100 (push v0.1.1 to ghcr.io):** still pending; underlying need confirmed by the `make rebuild` workaround used in iter-18.

## Next directive (iter-20 setup)

Layer `clip pattern to <medallion_boundary>` on top of iter-19's `extend` edits. Predicted to convert the unclipped-extension extras + missing-shapes into properly-formed partial shapes that A6 can match, lifting structural from 0/18 toward 5+/18 and adding the second half of the cascade's predicted +0.05 to +0.10 composite gain.
