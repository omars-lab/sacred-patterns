---
name: qiyas-baseline-emit-vtx0-catchall-drift
description: qiyas baseline emit produces spurious vtx=0 generic-polygon catch-all buckets that A6 can never match; strip them after emit
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

After `qiyas baseline emit`, strip any `expected_shapes[]` entry that is `type: polygon` with `vertex_count: 0` before using the baseline with `qiyas svg-audit --baseline` — those are emit-time-unresolved catch-all buckets that A6 can never satisfy.

**Why:** the emitter's `vertex_count_for()` (`src/qiyas/svg_audit/_vocab.py`) resolves vertex counts from a shape's *params* dict and returns `None` for shapes whose params lack an explicit `n`/`sides`/`points`; `baseline/core.py:277` then writes `vc if vc is not None else 0`, producing a `vertex_count=0` `polygon` bucket. But the A6 *auditor* re-encodes and resolves vertex counts *geometrically* (the A1 census shows clean 3/4/5/6/7/8/13/20-gons), so it looks for actual 0-vertex shapes, finds none, and marks the catch-all bucket MISSING. The resolved `-v3`/`-v5` buckets already census the same shapes correctly. This is emit-time-vs-audit-time vocabulary drift, not a real shape class. Concretely: medallion-10 girih close-1 (2026-05-28) emitted 10 buckets, 4 were `vtx=0` polygon catch-alls (counts 261/80/280/540); stripping them took A6 from a misleading "6/10 with 4 spurious MISSING" to a clean **6/6 = 1.0 PASS** on iter-33. The audit against the OLD connect-on-circle baseline had scored 0/10 — so the re-baseline + strip is what made A6 a fair live metric for the girih vocabulary.

**How to apply:** whenever you generate a baseline via `qiyas baseline emit` for any new construction vocabulary (girih, future tiling families) and then audit against it, post-process the JSON to drop `{type: polygon, vertex_count: 0}` entries. The principled fix would be to make `vertex_count_for` fall back to geometric resolution (so emit and audit agree) — file that as a tooling task if this recurs a third time. Until then, the strip is a one-line `python3` filter.

**Companion to:** [[feedback_a6_baseline_construction_philosophy_mismatch]] (that lesson: 3+ falsified construction variants for the same A6 verdict means the construction philosophy can't produce the baseline's vocabulary — the fix there was to MOVE the baseline to the construction's vocabulary, which is exactly what close-1 did here). Tenet 7 (don't tune to fit — stripping unsatisfiable buckets is correcting a tooling artifact, not goal-seeking the score).
