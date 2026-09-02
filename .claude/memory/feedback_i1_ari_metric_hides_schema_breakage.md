---
name: i1-ari-metric-hides-schema-breakage
description: "the I1 detector ARI=1.000 metric is a lossy projection that masks schema-migration breakage; verify foundation-green against the FULL pytest suite of all three repos, not the detector metric alone"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

Foundation-green for the loop means **all three repos' full test suites pass**, not "the I1 detector metric is 1.000."

**Why:** 2026-05-28 (#658), after closing the local cairo env gap, the full qiyas pytest suite surfaced 3 failures that `macro_ari_fused_vs_b=1.000` did not catch. The most consequential was a real code defect: `svg_audit/_vocab.py::vertex_count_from_params` still read the obsolete nested `params.points`/`params.sides` after the #362/#536 ShapeUnion migration flattened those onto the shape dict (`StarPolygonShape.points`, `RegularPolygonShape.sides`). Every parametric shape resolved to vertex_count=None, collapsing all stars/polygons into the A6 vc=None bucket and breaking the emit→audit round-trip. The ARI metric averages over a different code path (fused detector encoding) and never exercises the A6 (zone, vertex_count) bucketing, so it stayed at 1.000 while the audit layer was silently broken. Three idle loop ticks had reported "foundation green" on the metric alone before broadening the check found it.

**How to apply:** before declaring the loop idle or the foundation green, run the FULL pytest suite (`make ci-local` parity, not just `ci-local-fast`, and not just `validate-detector`) — at minimum when a schema migration (#362/#536-class), a producer-side regen (corpus rebaseline), or a shared-helper refactor has landed since the last full run. A green detector metric is necessary but not sufficient; the metric is one projection and shared bucketing/audit helpers live on other paths. When a metric and a test disagree, trust the test — it exercises the concrete code path the metric abstracts away.

**Companion to:** [[feedback_pinned_baselines_decay_with_mypy_refactors]] (pinned fixtures fire on legitimate downstream change — adjudicate per-failure), [[reference_qiyas_local_cairo_dyld_path]] (closing the cairo gap is what made the full local suite runnable under the GHA freeze), Tenet 4 (verify before claiming done), Tenet 7 (don't blanket re-freeze).
