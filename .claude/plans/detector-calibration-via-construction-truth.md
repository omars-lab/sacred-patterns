# Detector calibration via construction ground-truth

## TL;DR

Today qiyas's encoder produces 70–85% `type=unknown` shapes on real renders, and we have no way to tell whether a warning ("36 extras to remove") points to a real construction artifact or a detector hallucination. This plan closes that loop by treating bikar's construction language as **ground truth** — every `connect`/`divide`/`voids detect`/`strapwork` operation deterministically produces a known set of faces with known types, vertex counts, positions, and parameters. We export that ground-truth set alongside the SVG, render the SVG to PNG, run qiyas's encoder against it, and diff.

The output is a **detector regression suite with synthetic, machine-generated labels** — no human-in-the-loop required to grow it. Every disagreement is a falsifiable detector bug, not an iteration warning.

## Why this is high-priority (and why now)

Three converging signals make this load-bearing:

1. **The Tax-B-aware iter-14 validation (2026-05-04) ranked `extra-shapes` (36 extras) at the top.** When we inspected the encoding, 349/488 ref shapes (72%) and 702/832 recon shapes (84%) were `type=unknown` — the detector is finding *something* in three quarters of cases without being able to classify. The "36 extras" warning may itself be encoder noise. Acting on it before knowing risks a 4th consecutive regression in the iter-15/16/17 pattern.

2. **#75 (V2.B Global Warning Optimizer) is gated on "≥30 calibration data points."** The current path to those points is human-converged sessions — slow (one per several days), expensive (each session is hours), and biased (only successful sessions get tagged). A construction-truth corpus generates *thousands* of data points programmatically and includes the negative cases (failures, edge cases) that human-converged sessions exclude.

3. **Tax B's empirical priors are fitted on three falsified iterations.** The fragmentation cost constant (`0.0007/extra`) and crystallization priors (e.g. `missing-shapes: 0.30`) come from iter-15/16/17. With three points, the model is undeterminable. Construction-truth data lets us fit these constants on hundreds of synthetic edits where we know the right answer.

The pattern across all three: **we keep stacking confidence-shaped models (Tax A, Tax B, the warning optimizer) on top of an unaudited detector.** That ends here.

## What we already have (and what's missing)

Already in place:

- **Construction → SVG**: bikar's `pattern.bkr` → `render.svg` pipeline. Every construction op produces deterministic faces.
- **Internal face graph in bikar**: `packages/core/src/graph/face-extractor.ts`, `half-edge.ts`, `planar-graph-builder.ts` already compute the face set during render. They throw it away after producing SVG.
- **SVG → PNG rasterization**: ImageMagick via `qiyas pixel-diff --rasterizer magick`. Already wired.
- **Qiyas encoder**: `qiyas encode IMAGE` → `encoding.json` with `shapes[]` typed via the `ShapeType` literal in `qiyas/src/qiyas/schema.py`.
- **Diff machinery**: `qiyas validate REF.encoding RECON.encoding` already pairs shapes via Hungarian matching in `qiyas/src/qiyas/diff/`. The shape-pairing logic is reusable for ground-truth-vs-detected.
- **Schema**: `qiyas.schema.Encoding` with `shapes: list[Shape]`, where each `Shape` carries `type`, `params`, `center`, `quadrant`, `bbox`, `area`, `evidence.outline`. The same schema can carry ground-truth shapes — they just bypass the detector.

Missing:

- **Bikar doesn't externalize its known-face set.** The face-extractor knows the answer but emits only SVG.
- **No `qiyas validate-detector` mode that distinguishes ground-truth-error from photo-vs-render error.** The existing `qiyas validate` is built for *two encodings* — both come from the detector, both inherit its biases.
- **No detector-targeted corpus.** `qiyas/src/qiyas/fixtures/` is hand-curated and small; it doesn't cover encoder edge cases systematically.

## Three policy commitments

These bind every PR in this plan and need to hold across all three repos:

1. **Bikar's face-extractor is the single source of ground truth.** When the face-extractor and the qiyas encoder disagree, the encoder is wrong by construction (the SVG was generated *from* the face graph). If the face-extractor itself disagrees with what the SVG visually shows, that's a separate bug to file in bikar — but the plan treats face-extractor output as authoritative within its own scope.

2. **Ground-truth shapes use the qiyas `Shape` schema verbatim.** No parallel format. The `pattern.gt.json` file is structurally a `qiyas.schema.Encoding` document with `shapes[]` populated from bikar's face-extractor and `evidence.outline` populated from the actual face polygon. This means `qiyas validate-detector` is conceptually `qiyas validate` with one side coming from disk instead of a fresh encode.

3. **Move, don't copy.** Once the calibration loop produces detector fixes, the encoder fixes ship in qiyas and old workarounds in sacred-patterns (e.g. the `confidence: 0.3` jagged-outline tolerance baked into iter-14's evaluation) are deleted in the same PR. We don't keep "tolerant mode" alive next to "calibrated mode."

## The cascade — three PRs, three repos, sequential

Each PR is independently mergeable. After every PR, the system has a strictly improved capability and the loop keeps working. No long-running parallel state.

### PR1 — bikar: emit `pattern.gt.json` alongside `render.svg`

**Bikar deliverables:**

- New `--emit-truth PATH` flag on the bikar render CLI. When passed, after rendering the SVG, serialize the face-extractor's output to `PATH` as a `qiyas.schema.Encoding`-compatible document.
- For each face in the face graph:
  - `id` — stable id, e.g. `gt_F0042`
  - `type` — derived from the construction op that created the face (a `connect every 4 on C1` produces `star_polygon`; a `voids detect` rectangle becomes `square`; a `divide N` arc-segment becomes `lens`; etc.). The mapping table is canonical and documented (see "Construction → ShapeType mapping" below).
  - `params` — vertex count, the `(N, K)` tuple for star polygons, sides for regular polygons, fill class, etc.
  - `center` — face centroid.
  - `quadrant`, `polar` — derived from center in image space.
  - `bbox`, `area` — from face vertex polygon.
  - `confidence: 1.0` — ground truth is exact.
  - `evidence.outline` — the face's vertex sequence in image-pixel coordinates, after the same coordinate transform applied to the SVG.
- Top-level `image` field populated with the rasterization-target metadata (filename, width_px, height_px, sha256 — sha256 computable post-render from the PNG once produced; CLI flag accepts the target raster path).
- Top-level `symmetry` field populated from the construction's declared `repeat` and `divide` operations (we know the rotational order without running symmetry detection).
- Top-level `stats` field populated by counting.

**Construction → ShapeType mapping** (canonical, documented in the plan):

| Construction op | Resulting face | qiyas `ShapeType` | Notes |
|---|---|---|---|
| `connect every K on C divided into N` (single op, no other interactions) | one or more star-polygon faces | `star_polygon` with params `{N, K, vertex_count: 2N if gcd(N,K)>1 else N}` | The {N/K} schläfli notation. |
| Same op + `voids detect` after intersections | many small faces | mixed: depends on intersection topology — see "Face classification under intersections" below | This is the subtle case. |
| `divide C into N` + `connect adjacent` | regular N-gon | `regular_polygon` with `{sides: N}` | |
| Construction circle alone | circle | `circle` | |
| Two circles intersecting + `voids detect` | two lens faces | `lens` | |
| `strapwork width W mode M on C divided N connecting K` | strapwork band-segment faces and band-crossing faces | `band_crossing` for crossings; `unknown` (TODO: add `strapwork_segment` to the ShapeType literal) for segments | Bikar already has the `band_crossing` shape type per task #63. |
| `repeat at C depth D` | replicated copies of inner ops | type-by-type per inner op | |

**Face classification under intersections** (the hard part):

When `voids detect` runs after `connect every 4 on C1` AND `connect every 3 on C1`, the `{10/4}` and `{10/3}` line graphs intersect, and the resulting face graph contains many small faces that aren't star-polygons in the traditional sense. The face-extractor produces them, but classifying each face's *type* is non-trivial.

Three classification strategies, in priority order:

1. **Vertex-count + zone**. A 4-vertex face in the inner-star zone is a `girih_rhombus` candidate; a 6-vertex face is `unknown` until we add a `girih_hexagon` type. This matches A6's existing classification approach and uses the same zone vocabulary as `qiyas svg-audit`.
2. **Containment in a higher-order construction.** If a face's vertices are exactly the intersection points of two named star polygons, it's tagged with both parents in `evidence.composed_of`.
3. **Default to `unknown`** rather than guess. `unknown` is a valid `ShapeType` and is precisely what we want: a ground-truth `unknown` is *also* a labeled training signal. It tells the encoder "you should also produce `unknown` here, not invent a type."

**Test coverage:**

- For each construction op, a unit test renders a one-line `pattern.bkr`, emits the gt.json, and asserts the resulting face count + types match a hand-verified expectation.
- One integration test: render `bikar-medallion-10/iterations/14/pattern.bkr`, emit gt.json, assert it has the documented expected face count (read from the face-extractor — *not* from a hand-tagged fixture, to keep this test self-correcting if the face-extractor changes).

**Critical files:**

- (bikar, new) `packages/core/src/render/gt-emitter.ts`, `packages/cli/src/commands/render.ts` (add `--emit-truth` flag), `packages/core/src/render/construction-to-shapetype-table.ts`
- (bikar, new test) `packages/core/tests/gt-emitter.test.ts`
- (bikar, new doc) `docs/ground-truth-emit.md`

**This PR does NOT:**
- Run any qiyas comparison. That's PR2.
- Modify the face-extractor itself.
- Touch the iteration loop.

**Validation gate before merge:**
- Manual run on `bikar-medallion-10/iterations/14/pattern.bkr` produces a gt.json that round-trips through qiyas's `Encoding` pydantic model without validation errors. (This proves the schema contract holds.)

---

### PR2 — qiyas: `validate-detector` sub-command + report

**Qiyas deliverables:**

- New CLI: `qiyas validate-detector --rendered PNG --truth GT.json [--out DIR]`
  - Encodes `PNG` via the existing pipeline → produces an in-memory `Encoding`
  - Loads `GT.json` as the ground-truth `Encoding` (reusing the same pydantic schema)
  - Runs the existing Hungarian shape-matching from `qiyas/src/qiyas/diff/` to pair detected shapes against ground-truth shapes
  - Emits a structured report at `DIR/detector-validation.json` with:
    - **Recall**: fraction of GT shapes successfully detected (matched OR detected-but-typed-wrong)
    - **Classification accuracy**: of detected shapes, fraction with correct `type`
    - **Spurious rate**: detected shapes with no GT counterpart (encoder hallucinations)
    - **Unknown rate**: GT shapes whose detected counterpart is `type=unknown`
    - **Per-type recall**: same as recall but bucketed by GT `type`. Surfaces detector blind spots (e.g. "lens recall is 22%, star_polygon recall is 88%").
    - **Per-zone recall**: bucketed by `quadrant`. Surfaces spatial blind spots.
    - **Spurious-shape clusters**: when the encoder hallucinates, where? (Likely concentrated near strapwork crossings.)
- Plus a Tier-3 HTML report at `DIR/detector-validation.html` showing GT vs detected side-by-side, color-coded by match status, click-into-shape for individual diagnoses.

**Schema contract:**

```python
class DetectorValidation(BaseModel):
    schema_version: str
    rendered_png: str
    truth_json: str
    summary: DetectorSummary  # recall, classification_acc, spurious_rate, unknown_rate
    per_type: dict[str, TypeBreakdown]  # type -> {gt_count, detected, recall, classification_acc}
    per_zone: dict[str, ZoneBreakdown]
    pairings: list[DetectorPairing]  # (gt_id, detected_id | None, status, drift)
    spurious: list[str]  # detected_ids with no GT match
    warnings: list[Warning]  # reuse the existing Warning model
```

**Test coverage:**

- Unit tests against synthetic 2-shape, 5-shape, 20-shape fixtures.
- Integration test: take bikar's gt.json from a known pattern, render to PNG, run validate-detector, assert recall ≥ documented threshold (initially low — say 50% — and tracked as a ratchet).

**The "ratchet" pattern:**

`detector-validation-ratchet.json` lives in qiyas and stores the last-known-good metrics for each fixture. CI fails if recall drops. CI doesn't fail if recall goes up. This converts every encoder change into a measurable improvement or regression.

**Critical files:**

- (qiyas, new) `src/qiyas/detector_validation/__init__.py`, `runner.py`, `report.py`, `cli.py` additions
- (qiyas, new schema) `src/qiyas/detector_validation/schema.py` (or extend `qiyas/schema.py`)
- (qiyas, new fixtures) `tests/fixtures/detector-validation/` with at least 5 small bikar-rendered patterns + their gt.json
- (qiyas, new test) `tests/test_detector_validation.py`
- (qiyas, new plan) `.claude/plans/detector-validation.md` — qiyas-side detail
- (qiyas, new doc) `docs/detector-validation.md` — user-facing CLI reference

**Validation gate before merge:**
- All unit + integration tests pass.
- Running the CLI against a known bikar pattern produces a valid report that round-trips through the schema.
- Initial baseline ratchet committed.

---

### PR3 — calibration corpus + first detector fixes

**Sacred-patterns + bikar deliverables (single coordinated shipment, opens after PR2 merges):**

- Build `qiyas/tests/fixtures/detector-validation/corpus/` with at least 20 pattern fixtures, each a `pattern.bkr` + `pattern.gt.json` + `pattern.png` triple. Coverage targets:
  - **Single-construction patterns** (one `connect`, one `divide`) — baseline easy cases.
  - **Two-overlay patterns** (`{10/3}` + `{10/4}` on the same C) — the iter-14 case. Tests detector under face-graph fragmentation.
  - **Strapwork patterns** with each crossing mode (alternating, over, under). Tests the `band_crossing` and (TBD) `strapwork_segment` types.
  - **Tiny faces** (faces < 10px²) — tests sub-pixel detection and the noise-vs-signal threshold.
  - **Faces against background** (a single shape on white) — tests baseline detection without interference.
  - **Composite faces** (a rosette = central polygon + petals) — tests `evidence.composed_of`.
  - **Empty pattern** (just construction circles, no `voids detect`) — tests detector behavior when there are no closed faces.
- Run the full corpus through `qiyas validate-detector`. Generate the initial ratchet baseline.
- File detector-error-class issues in `qiyas/docs/issues/` for each significant gap (e.g. "lens recall is 22% — encoder needs better lens classifier"). Each issue cites the corpus fixture that surfaces it.
- **At least one detector fix shipped in this PR** to prove the loop closes (probably the easiest one — likely a confidence-threshold tweak, a missing shape-type registration, or fixing the type-vocabulary gap that produced the 70%+ unknown rate). The fix's PR description includes the recall delta from the corpus.

**Critical files:**

- (qiyas, new) `tests/fixtures/detector-validation/corpus/` × 20 fixtures
- (qiyas, new) `tests/fixtures/detector-validation/ratchet.json`
- (qiyas, new) at least 5 docs in `qiyas/docs/issues/` (one per detector gap)
- (qiyas, edited) detector module(s) implementing the chosen first fix
- (sacred-patterns, edited) `CLAUDE.md` — add detector-validation to the convergence-philosophy section as the *upstream* gate before iteration warnings can be trusted
- (bikar, edited if needed) any face-extractor patches discovered while building the corpus

**This PR does NOT:**
- Promise to fix every detector gap. The corpus + ratchet are the deliverable; ongoing fixes are individual tickets.
- Resume iteration on bikar-medallion-10 (#85) until the recall ratchet is high enough to trust warnings — gating policy decided after we see initial numbers.

**Validation gate before merge:**
- 20+ fixtures populated.
- Ratchet baseline committed and reproducible from CI.
- At least one detector fix shipped, with measured improvement against the ratchet.

---

## End state

```
Authoring loop:
   bikar render pattern.bkr --emit-truth gt.json --raster pattern.png
   qiyas validate-detector --rendered pattern.png --truth gt.json --out report/

Iteration loop (sacred-patterns) — UNCHANGED in shape, but now trustable:
   ./tools/iteration-validate.sh ... → validation.json
   warnings[0] is now grounded in a detector with measured recall, not an unaudited one

Detector development loop (qiyas):
   1. Pick a detector-validation issue from qiyas/docs/issues/
   2. Patch detector
   3. Run corpus through validate-detector
   4. If recall improved on the issue's fixture without regressing the ratchet → ship
   5. Update the ratchet
```

The detector-development loop has its own retrospective discipline (each fix PR cites which fixtures improved, by how much, and why). This converts qiyas from a black box into an auditable pipeline.

## Verification — end-to-end

After PR3 merges, run this flow to confirm health:

1. Fresh clone of all three repos.
2. Build a new bikar pattern from scratch (any `pattern.bkr`).
3. `bikar render --emit-truth ...` produces gt.json.
4. `qiyas validate-detector` produces a recall report.
5. Hand-inspect five randomly sampled spurious detections in the HTML report. Confirm they're either real detector errors (file an issue) or face-extractor errors in bikar (file an issue).

If step 5 produces sensible diagnoses every time, the loop is working.

## Open items (do NOT block PR1)

- **Strapwork-segment shape type.** The `ShapeType` literal in `qiyas/schema.py` doesn't include a strapwork-segment type today. Adding it can wait until PR3's strapwork fixtures need it; until then, those segments are correctly labeled `unknown` in ground truth.
- **Construction-language extensions.** If bikar grows new ops between now and PR1, the construction-to-ShapeType table must extend correspondingly. Filing a precommit hook in bikar to enforce this is a follow-up after PR1.
- **Coordinate-system parity.** The face-extractor works in bikar's coordinate space; the rasterized PNG inherits that space modulo the rasterization viewport transform. PR1 must document that transform precisely or the gt.json positions will be off by the SVG viewport mapping. Easiest path: bikar's CLI passes the rasterization parameters (viewport, transform) so gt.json positions are pre-applied.
- **Ground-truth correctness audit.** The face-extractor itself could have bugs (e.g. miscounting strapwork-band crossings — task #59/#60 are still in_progress on this exact area). PR1 explicitly assumes face-extractor correctness; if PR2's first runs surface face-extractor bugs, those are new tickets in bikar (not blockers for the cascade).
- **Recall threshold for resuming #85.** When does the loop become trustable enough to resume bikar-medallion-10 iteration? Defer the answer — pick after PR3's first numbers come in. A reasonable starting heuristic: per-type recall ≥ 80% on `star_polygon`, `regular_polygon`, `circle`, `lens` (the constructions used in medallion-10).

## Cross-repo dependencies

This plan adds rows to the dependency mirror in `docs/cross-repo-dependencies.md` (sacred-patterns, qiyas, bikar — all three carry the mirror):

| Owner | Depends on | Note |
|---|---|---|
| bikar PR1 (gt.json emit) | qiyas/schema.py `Encoding` schema | Contract — bikar imports the schema docs (not the Python code) and matches its JSON output. |
| qiyas PR2 (validate-detector) | bikar PR1 shipped | Needs gt.json files to test against. |
| Corpus PR3 | qiyas PR2 + bikar PR1 | Both required before corpus can be built. |
| sacred-patterns iteration loop trust gate | Corpus PR3's ratchet | Iteration warnings are gated on detector recall ratchet. |

## Connection to existing plans/tasks

- **#75 (V2.B Global Warning Optimizer)** — the optimizer's calibration corpus comes from this loop (synthetic, large) instead of from human-converged sessions (organic, small). PR3's corpus is precisely V2.B's training data.
- **#109 (Tax B fragmentation cost)** — already shipped, but its priors were fitted on three falsified iterations. After PR3 ships, refit on synthetic data and measure whether the tax constants change materially.
- **#111/#112 (Hierarchical pixel-diff)** — orthogonal: improves the pixel-side detection pipeline. Both improvements compose; this plan tunes the *encoder* (semantic shapes), #111 tunes the *pixel-diff* (where structures disagree). They're independent lanes.
- **#106 (Partial-shape rendering via construction)** — the strapwork fixtures in PR3 will exercise this if it lands first; if not, the corpus uses the existing crossing modes.
- **#115 (Audit: is medallion-10 a Hankin-PIC pattern?)** — independent. The corpus pattern set should include both Hankin-PIC and decagram-strapwork variants once we know the difference.

The cumulative effect: every existing task that depends on "trust the detector output" gets a measurable, falsifiable trust gate. Every existing task that *was* gated on "wait for human-converged calibration data" gets unblocked.

## Why not just fix the detector directly?

A reasonable counter-argument: "Skip the ground-truth pipeline. Just look at the encoder's outputs on iter-14, find the bugs, fix them."

We've tried that. The encoder produces 832 shapes on iter-14, 702 of them `unknown`. Eyeballing 702 outline polygons is not a development methodology. Without a *system* for measuring "did this fix improve recall on lenses, regress recall on stars, or shift unknowns to spurious detections?", every detector edit is a guess. The cost of building the ground-truth loop is roughly two weeks of work; the cost of *not* having it is the next dozen iterations of #85 being uninterpretable.

## Out of scope

- Replacing qiyas's pixel-based encoder with an SVG-aware encoder. (That's a much larger change and would obviate this plan, but is a separate decision.)
- Generating ground truth from the JPG reference photo. (Photos don't have a construction; we can only ground-truth what we generated ourselves. The photo remains the iteration *target*; it's not in the calibration loop.)
- Auto-fitting Tax-A / Tax-B priors from the corpus. (Worth doing post-PR3, but lives in #109's followup, not this plan.)
- Sacred-patterns side iteration UX changes beyond the trust gate. The orchestrator and warnings array shape are unchanged; only their trustworthiness rating changes.
