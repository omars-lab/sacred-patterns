---
name: run-pipeline-before-authoring-rescope
description: "Before authoring a re-scope plan or decision doc premised on \"the detector finds N of class X\", run the end-to-end pipeline once and verify N — citing prior agents' summaries or partial reads of the baseline is not verification"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

Before authoring any re-scope plan or decision doc whose premise is a measurement (e.g., "the detector finds 0 circles," "qiyas misses 270 unknowns," "iter-N has +70 triangle drift"), run the end-to-end pipeline once on the actual artifact and capture the histogram yourself. Citing a prior agent's summary, eyeballing a baseline JSON, or trusting an old probe-script output does not count as verification — those are the inputs that fail.

**Why:** 2026-05-22 qiyas#138 re-scope. The decision doc `qiyas/docs/decisions/2026-05-22-138-rescope-after-empirical-delta.md` was authored with full options-A-through-E ceremony, accepted as A+B paired, and tasks (#515/#516/#517) were filed — all on the premise "detector finds 0 circles vs baseline expects 12, root cause is svg_primitives._emit_circle dropping circles." Started Slice 1 (#515), ran the actual pipeline before editing as a sanity check, and learned the detector finds **14 circles** via the existing `circle_to_shape` adapter at `src/qiyas/stages/detectors/circle.py:24` (wired in `src/qiyas/stages/shapes.py:289-293`). The "0 circles" claim came from filtering the baseline by `type` field — but the 12 baseline entries are stored as `type=polygon, vertex_count=0, notes="qiyas type: circle"`, a stringly-typed discriminator the comparison ignored. A 60-second `qiyas encode <render.svg> --output /tmp/x.json` plus a histogram diff would have falsified the entire option-set authoring before any task was filed. Falsification log: same doc §9. Witness: task qiyas#518.

**How to apply:**
- When a session starts with "the parent plan says X is broken — let's plan the fix," your first tool call is to reproduce X yourself, not to read the parent plan.
- For qiyas detector claims specifically: `cd qiyas && uv run python -m qiyas.cli encode <path-to-render.svg> --output /tmp/<slug>.json` then a Counter() histogram of `(type, vertex_count_or_sides)` is the minimum bar. Compare against the baseline by honoring **every** discriminator field, including `notes` until the schema migrates to typed discriminators (qiyas#362 cascade).
- For bikar/sacred-patterns claims (face counts, fill counts, edge-tag sets), the equivalent is `make test` on the specific test that would surface the claim, plus a manual smoke if no test encodes it (per Tenet 18, then file a test for the smoke).
- Read prior summaries for **context** (what was tried, what was tested), not for **measurements** (what the current state is). Measurements decay across sessions; they must be re-captured.

**Companion to** [[feedback_experiment_predictions]] (experiment ≠ ship — same shape, this rule is the upstream of that one — verify before ship is downstream of verify before plan), [[feedback_check_mechanism_already_implemented]] (check the module is wired before estimating rework — same family, the bug here was that `circle_to_shape` was already wired and I didn't read it), and CLAUDE.md Tenets 4 (verify before claiming done) and 18 (codify witness as test). Distinct from those because this one fires *before* authoring options, not before shipping a pick.
