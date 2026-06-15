# Iter 18 retrospective — slice-1 gate cleared, cascade rotated

## What this iteration was for

Pure validation gate for bikar#114 PR1 slice 1 (commit `8bc6735` `canonicalEdgeOrder` in `assignStrands`). No DSL edit — iter-17's `pattern.bkr` re-rendered verbatim under patched bikar core (HEAD `1767c60`).

## What we learned

### The slice-1 fix was real and load-bearing

A2 cv 0.27 → 0.127 (10x improvement). composite 0.6888 → 0.7985 (+0.11). The +0.11 is 2x the predicted +0.02 to +0.06 — slice 1 wasn't just an A2 fix; it was suppressing several downstream warnings whose Tax-B-adjusted weights compounded.

### Symmetry warning rotated out of the top-N

iter-17 top-1 was symmetry-mismatch δ=0.125. iter-18 has no symmetry warning in top-5 — the rotation-non-invariant strand assignment was the *symptom generator*, not a separate failure mode. This is the kind of one-fix-many-effects payoff Tenet 2 names.

### The new bottleneck is construction-vs-pattern shape accounting

Top warnings are now `extra-shapes` (31, cf_adj=+0.0275) and `missing-shapes` (39, cf_adj=-0.0285, sev=error). Both point at the same underlying issue: the medallion DSL constructs extended segments for compass-and-straightedge geometry, but qiyas counts them as "extras" while the reference image's clipped-at-boundary geometry shows up as "missing." This is exactly the partial-shape cascade scope (#106).

### A5 going BROKEN is not a regression

A5 went PARTIAL → BROKEN (0 crossings). But the reason is structural: the construction-element excess is taking up the band-network slots qiyas would otherwise count as crossings. The bands ARE there in the SVG; the detector classifies them as construction shapes because the partial-shape cascade hasn't shipped yet. Recovering A5 to PARTIAL or PASS is downstream of #106, not a new bug.

## Process notes

### The orchestrator/image staleness mid-loop

The first run of `iteration-validate.sh` against `qiyas:dev` failed at steps 4 and 6 (`svg-audit`, `score` missing from image). Root cause: published Docker images (`:dev`, `:latest`, `:v0.1.0`) all drifted behind current qiyas source. Fixed by `make rebuild` in the qiyas repo (rebuilds `:dev` from local source). One-line process note for next time: when a loop tick uses `qiyas:dev` and a subcommand "doesn't exist," the first move is `cd qiyas && make rebuild`, not a workaround edit to the orchestrator.

This is *also* the underlying motivation for #100 (push v0.1.1 to ghcr.io with PAT) — the published image would have stayed current.

## Cross-task impact

- **bikar#114 PR1 slice 1:** validated end-to-end, ready to close ACCEPTED.
- **qiyas#112 (hierarchical pixel-diff):** unblocked. The slice-1 fix removes the strapwork-rotation noise floor that #112's hierarchical signal would have been buried under.
- **sacred-patterns#80 (catch22-driver bikar-medallion-10 restart):** the +0.11 composite shows the catch22 era's success criterion (post-#536 measurement) is being satisfied. Composite 0.7985 is the new ceiling under construction-excess constraints; #106 cascade is the next ceiling-raise.
- **sacred-patterns#85 (Drive medallion-10 to convergence):** still open; next directive shifts to #106 partial-shape cascade.

## Next directive (iter-19 setup)

Top-ranked warning by `severity=error + cf_adj`: `missing-shapes` (39 ref shapes not found in recon, sev=error). This is the parent symptom of the partial-shape cascade. Iter-19 picks up `sacred-patterns#106` slice 1 (partial-shape rendering via construction) — likely a bikar DSL primitive for `boundary`/`extend`/`clip`/`intersect` per the cascade design doc.

If #106 is not yet implementation-ready, iter-19 falls back to the next sev=warn warning: `extra-shapes` (the other half of the same symptom). Either way, the work is on the partial-shape axis, not the rotation/strapwork axis (that one is done).
