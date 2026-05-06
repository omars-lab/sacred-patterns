# Shape-identity detection cascade — capability-led detector validation across constructions

## Context

Companion to qiyas issue `2026-05-04-no-shape-identity-detection.md`. That issue establishes the capability gap: the qiyas detector has no notion of shape identity (within or across constructions) and no notion of recurrence/arrangement, which together block construction-hint generation (qiyas#76) and reduce every per-iteration ratchet (#131, #141) to a metric that can't express "the 11 satellite-decagons should be one identity-class with 11 instances."

This plan turns the issue's recommended Option A into a sequenced cascade. Three foundation specs, then a small bikar corpus, then qiyas implementation, then iteration. Each phase ends with the system in a coherent state — future-us can stop without leaving things half-migrated.

## Three policy commitments

These bind every PR in this cascade:

1. **Cross-construction proof gate.** No detector PR merges until it's validated against a corpus of ≥3 distinct bikar constructions, not just iter-14. This is the bright line that prevents the over-fitting trap that has cost three rollbacks this quarter (Tax B iter-15/16/17, K-sweep prototype, eps-tuning).
2. **Spec before code.** Each foundation primitive (signature, arrangement, identity-fidelity metric) gets a written spec reviewed and accepted before any qiyas code lands. Specs include: definition, computation algorithm, tolerance policy, failure modes, why-not-the-other-options.
3. **Identity is the convergence target, count is a sub-metric.** The validate-detector ratchet is identity-fidelity (per-class instance counts + per-instance geometry-distance), not raw count-fidelity. Count-fidelity (qiyas#141) becomes a derivative — given identity-classes, "instances per class" is the count check. Identity-fidelity subsumes it.

## Grounding facts from exploration

These are load-bearing for the plan; they came from reading the actual K-sweep results, qiyas schema, and bikar construction repo state.

- **The K-sweep (qiyas#139) produced concrete numbers.** Best K=6 fidelity 0.487 on iter-14. Above K=6, anti-aliasing seams fragment cyan triangles 180→343–385. Naive color-region segmentation is not a path to count fidelity.
- **The qiyas `Shape` schema has no identity field.** `qiyas/src/qiyas/schema.py` defines `Shape` with `type`, `params`, `center`, `quadrant`, `bbox`, `area`, `evidence.outline`. No canonical hash, no identity-class link, no arrangement metadata. Adding identity is a schema extension, not a refactor.
- **Bikar truth carries enough for ground-truth identity annotation.** `pattern.gt.json` schema_version 2 includes per-shape `params.fill_color`, `polar.{r, theta_deg}`, `area`, `bbox`. Identity-class can be inferred from these without bikar-side schema changes — but it's faster and more authoritative if bikar emits identity-class directly.
- **Bikar can already render multiple medallion-N constructions.** `medallion-10/iterations/14/pattern.bkr` is one of many. The construction language supports parameterized N. Building medallion-6 and medallion-12 variants is hours, not weeks.
- **No mirror-only or scaled-concentric construction exists in bikar today** (per a fast scan; needs verification). Building these is novel construction-design work, not just parameter substitution.
- **qiyas#76 (V2.D Construction hints) is currently a "design spike" with no implementation plan.** The hint sub-command is a downstream consumer of the same identity+arrangement primitives this plan builds. Folding qiyas#76 into this cascade avoids rebuilding the same logic twice.

## The cascade

Four phases. Each ends with the system in a coherent state.

### Phase 0 — Foundation specs (no code)

Three written specs that define the primitives this whole cascade builds on. Each spec gets owner review before the next phase starts.

**Sacred-patterns deliverables:** none.

**Qiyas deliverables (specs only):**

**F1. Within-construction shape-identity signature spec** (`qiyas/.claude/plans/shape-identity-signature.md`)
- Definition: a canonical hash on a shape such that two geometrically-equivalent shapes (same vertex count, same interior angle sequence, same side-length-ratios, same arc-curvature ratios; differing only by rigid motion + uniform scale) produce the same hash.
- Computation: vertex count + sorted interior-angle vector (rounded to deg-tolerance) + sorted side-length-ratio vector (sides normalized by perimeter, rounded to ratio-tolerance) + has_arcs flag + sorted arc-curvature-ratio vector.
- Tolerance policy: deg-tolerance and ratio-tolerance are explicit parameters. Default 0.5° and 0.005 respectively. Justify defaults from anti-aliasing analysis on a clean test case.
- Failure modes: degenerate shapes (collinear vertices), near-circles (low vertex count + high arc-curvature), shapes with mixed straight + arc edges where the order matters.
- Why not other options: SHA over coordinate list (fails rotation), Hausdorff distance to canonical-form library (no library exists), shape-context histograms (overkill, opaque).

**F2. Cross-construction shape-identity signature spec** (`qiyas/.claude/plans/cross-construction-identity.md`)
- Same signature as F1 with one extension: a **scale-bucket** parameter that controls when "approximately equal" pentagons hash equal across constructions. Without scale buckets, a pentagon at radius 100 and a pentagon at radius 200 produce equal F1 signatures (good for within-construction-of-different-sizes) but make cross-construction comparison say "everything is the same" if the signature ignores absolute scale entirely.
- Tolerance escalation: cross-construction tolerance is wider than within-construction (different rasterizers, different render sizes). Default 1.0° and 0.01.
- Failure modes: when does cross-construction comparison make sense vs not? E.g., comparing decagons across medallion-10 and medallion-12 makes sense; comparing a satellite-pentagon to a strapwork-band-segment doesn't.
- Why not other options: separate cross-construction signature (duplication, drift), no cross-construction comparison (forecloses corpus aggregation).

**F3. Recurrence/arrangement classification spec** (`qiyas/.claude/plans/arrangement-classifier.md`)
- Definition: given a set of shapes that share an identity-class, classify their spatial arrangement as one of: `n_fold_rotation(center, n)`, `mirror(axis)`, `translation_tile(vector)`, `scale_concentric(center, ratio)`, `irregular_cluster`.
- Computation: for n-fold rotation, fit center-of-shape-centroids as candidate rotation center, then check if shape centers form an n-fold orbit around it. For mirror, find candidate axis from centroid-pairs, verify per-shape mirror-equivalence. For translation, find shortest centroid-pair vector, verify it tiles. For scale-concentric, fit common center, verify centroid-radii form geometric progression.
- Tolerance policy: per-arrangement-type tolerance on positions, angles, ratios.
- Failure modes: ambiguous cases (4 shapes could be 4-fold rotation OR 2-fold mirror), sparse cases (2 shapes can be classified many ways), composite arrangements (an outer 10-fold of inner 5-folds).
- Why not other options: skip arrangement classification (forecloses construction hints), use only n-fold (misses mirror/translation/scale), use ML clustering (opaque, hard to debug).

**Validation gate:** all three specs reviewed and signed off before Phase 1 starts.

**Critical files:**
- (qiyas, new) `.claude/plans/shape-identity-signature.md`, `.claude/plans/cross-construction-identity.md`, `.claude/plans/arrangement-classifier.md`

### Phase 1 — Corpus authoring (smaller-first)

Build a 3-construction proof corpus. Validate report machinery on it. Expand to 8 only after the report works.

**Smaller-first corpus (Phase 1.A):**
1. `medallion-10/iter-14` (existing; the hard case).
2. A simple `{10/3}` star alone, no satellites or central decagon. Tests trivial-case sanity. (`bikar/patterns/Stars/Star-10.bkr`)
3. A simple 7-fold star (`bikar/patterns/Stars/Star-7.bkr`). Tests different-N trivial case with multiple identity-classes (4 classes × 7-fold). **Substituted for the originally-planned `{6/2}` hexagram (2026-05-04):** the bare hexagram's 6 turquoise triangles share visual edges, and the bikar gt-emitter (#136) union-finds adjacent same-color faces, collapsing them into a single shape — leaving only 3 emitted shapes vs the ~7 needed for arrangement-classifier validation. Star-7 emits 30 clean shapes (Counter: 7 blue pentagons + 7 red squares + 7 pearl pentagons + 7 blue triangles + 1 center + 1 circle), giving arrangement-classifier richer multi-class signal at trivial cost.

**Full corpus (Phase 1.B, deferred until 1.A ships):**
4. `medallion-6` (build new) — lower n-fold scaling check.
5. `medallion-12` (build new) — higher n-fold scaling check.
6. Non-medallion girih tiling (5-tile girih: decagon + bowtie + hexagon + ...) — translation-tile arrangement, no global rotation.
7. Mirror-only-symmetry pattern — reflection-identity, not rotation-identity. Critical orthogonal case.
8. Scaled-concentric stress case — three concentric rosettes at three sizes. Tests scale-invariance.

**Phase 1.B authoring discipline (added 2026-05-05):** Phase 1.B is
authored as a *parametric corpus*, not 5 hand-rolled one-offs. Each
construction is a bikar `.bkr` template that takes parameters; a driver
script emits one render+gt pair per parameter combination. This makes
Phase 1.B serve two consumers with the same corpus: (a) today's
`qiyas validate-detector` regression run, (b) tomorrow's B-AFF training
run if/when detector-time per-pair identity becomes a real consumer
need. The architectural seam is documented in
`.claude/plans/bikar-as-training-data-generator.md` — five rules
(deterministic renders, per-shape pixel outlines, parametric templates,
authored splits, single `corpus.json` index). Owner sign-off gate on
those rules before Phase 1.B starts.

**Bikar deliverables:**
- For Phase 1.A: render 3 patterns to PNG + `pattern.gt.json`. Constructions 2, 3 may already exist as test fixtures; verify and use.
- For Phase 1.B: build 5 new constructions (4–8 above). Constructions 4, 5 are parameter variations on medallion-10, cheap. Constructions 6, 7, 8 are novel construction-design work.

**Sacred-patterns deliverables:**
- Identity-class annotation tool: walk `pattern.gt.json` shapes, group by computed F1 signature (sanity check that bikar-truth shapes form identity-classes the way we expect), emit `pattern.identity.json` alongside `pattern.gt.json`. This is the **answer key** the detector will be compared against.
- Annotation review for each corpus construction — manually verify that auto-grouped identity-classes match human intuition. Document any mismatches as inputs to F1 spec refinement.

**Validation gate:** for the 3-construction Phase 1.A corpus, identity-annotation produces sensible classes (e.g., for iter-14: ~6–8 identity-classes covering the 275 truth-shapes with class-sizes matching the construction's symmetry).

**Critical files:**
- (bikar, new) `bikar/patterns/Stars/Star-10.bkr` (commit `7a4ee2a`); Star-7 already existed
- (qiyas, new) `qiyas/tests/fixtures/corpus-phase1a/{star10,star7,medallion10-iter14}/` — pattern.bkr + render.svg + render.png + pattern.gt.json per construction. Located in qiyas (not sacred-patterns) so D1/D2/D3 implementation can consume them as test fixtures without cross-repo path coupling.
- (sacred-patterns, new) `tools/annotate-identity-classes.py`

### Phase 2 — Qiyas implementation (signatures, arrangement, validate-detector, hint)

This is the bulk of the LOC. Four sequential slices.

**D1. Implement F1+F2 signature computation in qiyas**
- Add `Shape.identity_signature: str` field to schema (post-detection populated; doesn't change detection).
- Add `qiyas/src/qiyas/identity/signature.py` implementing the F1+F2 spec.
- Compute signature for every detected shape after Stage-3 classification.
- Hash format: stable, version-prefixed (`v1:...`) so future spec updates don't silently break corpus comparisons.

**D2. Implement F3 arrangement classification in qiyas**
- Add `Encoding.arrangements: list[Arrangement]` field. Each `Arrangement` carries `identity_signature`, `arrangement_type`, parameters (center, n, axis, vector, ratio).
- Add `qiyas/src/qiyas/identity/arrangement.py` implementing the F3 spec.
- Compute arrangements as a post-detection pass: group shapes by `identity_signature`, classify each group's arrangement.

**D3. Implement `qiyas validate-detector` sub-command**
- Inputs: corpus directory containing `pattern.gt.json` + `pattern.identity.json` + rendered PNG per construction.
- For each construction: run encoder on PNG, compute identity-signatures + arrangements on detected shapes, compare against ground-truth identity-classes from `pattern.identity.json`.
- Output: per-construction report + aggregated coverage table. Per-construction includes: identity-class precision/recall (did we find the right classes?), per-class instance count (right number of instances?), arrangement-detection (did we identify the right arrangement type with right parameters?), per-instance geometry-distance (within-class shape match).
- This **replaces** qiyas#131's original count-fidelity-only scope. The identity-fidelity report is a strict superset.

**D4. Implement `qiyas hint` sub-command (folds qiyas#76)**
- Inputs: rendered PNG.
- For each detected arrangement: emit a construction-hint in a format consumable by sacred-patterns iteration loop. E.g. `{"hint_type": "n_fold_rotation", "n": 10, "center": [600, 600], "instance_signature": "v1:..."}`.
- This is the load-bearing downstream feature that motivated identity-detection in the first place.

**Validation gate:** each slice ships with unit tests + integration test against the Phase 1.A corpus. D3 ships only when it produces a coherent identity-fidelity report on all 3 corpus constructions, not just iter-14.

**Critical files:**
- (qiyas, edit) `src/qiyas/schema.py` (Shape.identity_signature, Encoding.arrangements)
- (qiyas, new) `src/qiyas/identity/signature.py`, `src/qiyas/identity/arrangement.py`, `src/qiyas/cli.py` validate-detector + hint sub-commands
- (qiyas, new) tests for each
- (qiyas, new) `qiyas/.claude/plans/validate-detector.md`, `qiyas/.claude/plans/hint-sub-command.md` (slice-design docs)

### Phase 3 — Iterate against the corpus to close named gaps

The validate-detector report (D3) becomes the iteration loop. Each row in the per-construction report names a discrete failure (e.g., "medallion-10: detector found 2 instances of class X, truth has 11"). Each failure becomes a discrete ticket. Each detector PR targets one ticket and re-runs the corpus report, must show the target row improved without regressing others.

**Sacred-patterns deliverables:** 
- Wire `qiyas validate-detector` into iteration-validate.sh as a new signal alongside the existing pixel-diff/svg-audit/etc.
- Define convergence bar: "≥80% identity-fidelity on Phase 1.A corpus" or similar — value TBD based on Phase 2 baseline numbers.

**Qiyas deliverables (per gap, one PR each):**
- N detector PRs, each targeting one named gap. Common candidate fixes (in increasing-cost order):
  - Lower classifier confidence floor for typed-shape vocabulary (cheap; the elevators from Option 1 of the prior issue).
  - Morphological closing of binary before contour extraction (medium; addresses stroke-gap recall issue).
  - Watershed segmentation from edge-binary (high; addresses recall structurally).
  - Shape-fitting with arrangement priors — once the detector knows "this looks like a 10-fold pattern," it can search for missing instances at expected positions (highest leverage).

**Phase 1.B corpus expansion (concurrent):** as gaps stabilize on the Phase 1.A corpus, expand to the full 8-construction corpus to catch over-fits to the small corpus.

**Validation gate:** convergence bar holds across the full Phase 1.B corpus. Then this cascade is done; per-iteration ratchet (#131 superseded scope) takes over for incremental detector improvements.

**Critical files:** dependent on which gaps surface; cannot enumerate upfront.

## End state

```
Iteration loop calls (sacred-patterns):
   qiyas validate-detector --corpus DIR  → identity-fidelity report
   qiyas hint IMAGE                      → construction hints from detected arrangements

Detector knows:
   - Each shape's identity-class (canonical signature)
   - Each set of identical-class shapes' arrangement (n-fold/mirror/tile/concentric)
   
Sacred-patterns iteration loop consumes:
   - Identity-fidelity score per-construction (from validate-detector)
   - Construction hints (from qiyas hint) — feeds back into pattern construction

Corpus state:
   8 bikar constructions, each with truth + render + identity-class answer key
   Coverage report flags per-class precision/recall/arrangement per construction
   New detector PRs gated on cross-construction proof
```

## Verification — end-to-end

After each phase, run this loop to confirm the cascade is healthy:

1. **Phase 0:** all three specs reviewed + signed off by owner.
2. **Phase 1.A:** identity-annotation tool produces sensible classes on all 3 corpus constructions; manual review confirms.
3. **Phase 2 D1+D2:** computed signatures + arrangements on iter-14 detector output match what F1/F2/F3 specs predict.
4. **Phase 2 D3:** validate-detector report on Phase 1.A corpus produces coherent per-construction numbers (not all-zeros, not all-perfect).
5. **Phase 2 D4:** hint sub-command on iter-14 emits at least the obvious 10-fold-rotation arrangements (10 satellites, 10 satellite-cores, 10 inter-satellite triangles).
6. **Phase 3:** convergence bar holds across Phase 1.B corpus.

## Open items (do not block Phase 0)

- **Phase 1.B progress 2026-05-05 (resolved hard stops + iter-7/iter-8 findings):**
  Both gates from the original HARD STOP block resolved:
  1. **Scaffolding gate.** Owner ("b" / 2026-05-05) selected full Phase
     1.B discipline. Slice 1 (#189) recorded sign-off on
     `bikar-as-training-data-generator.md` 5 rules. Slices 2-4 shipped
     scaffolding (`qiyas/calibration/phase-1b-corpus/`, `corpus.json`,
     `splits.json`, `regenerate.py`, `petal-N-ring.bkr.tmpl`).
  2. **#178 inherited claim falsified ✓ corrected.** Renamed to
     "[Phase 1.A corpus addition] Author Star-10.bkr" (the only
     template that actually shipped). Phase 1.B parametric authoring
     rerouted under #187/#192.

- **iter-7 SHIP (2026-05-05).** Phase 1.B petal-N-ring (N=6/8/10): all
  three entries pass `fused_v3 ARI = 1.000` with arc-only edges
  (448/576/704 arc primitives). Verdict at
  `qiyas/calibration/i1/iter-7-arc-corpus-validation.md`.

- **iter-7 falsified iter-6 inherited claim (Tenet 6).** iter-6 said
  Phase 1.A was "polygon-only (verified `arc_bearing_shapes=0`)". The
  schema-1.13 refresh (#188) revealed Phase 1.A actually has 896/64/64
  arc edges across medallion10/star10/star7 — the proxy was wrong, not
  the patterns. Re-running iter-5 against the refreshed fixtures
  preserves fused_v3=1.000 on all three. SHIP holds; the "no
  arc-coverage" claim was incorrect from the beginning.

- **iter-8 HARD STOP (run 2026-05-05).** Multi-class arc-bearing
  fusion-delta validation on `petal-6-full` (verbatim copy of
  `bikar/patterns/Petal Tutorial/Petal-Full.bkr`). Result:
  fused_v3 ARI = 0.709, pre-fusion ARI = 0.645, fusion delta = +0.064.
  **Below the cascade-plan target of 1.000.** F1.v3 is not broken
  (delta is positive) but the equivalence-by-construction guarantee
  iter-5 SHIP'd on polygon corpora does not hold on arc geometry under
  this corpus structure. Verdict at
  `qiyas/calibration/i1/iter-8-multiclass-fusion-delta.md`.

  **bikar gap surfaced (Tenet 6 falsification of iter-7).** bikar's
  gt-emitter does NOT emit 2-vertex arc-lens faces as `gt_G` shapes —
  the perimeter-detection logic keys edges by undirected vertex pairs
  (`gt-emitter.ts` `edgeKey(v[j], v[(j+1) % v.length])`), and a
  2-vertex face's two arc edges share the same vertex pair, so the
  walk treats them as a single collapsed edge and skips the face.
  Empirical confirmation: `Petal-1-Ring.bkr`, `Petal-2-Ring.bkr`,
  any direct `face` statement with 2 arc sub-statements all emit
  zero `gt_G` shapes despite producing colored 2-vertex faces in the
  planar graph. This means **iter-7's "petal-N-ring is single-class
  arc-bearing" framing was wrong**: petal-N-ring emits 0 face shapes;
  the iter-7 `n_arc_bearing=N` count was construction CIRCLES (which
  carry arc outlines via `approximateCircleOutline` 64-vertex
  densification at `gt-emitter.ts:582-589`), not arc-bounded faces.
  iter-7's SHIP holds at the level it actually tested (no regression
  on circle distributions) but did not exercise arc-bounded face
  geometry. Filed for the bikar repo as a follow-up: needs lens-face
  emission fix.

  **Why the for-loop work (bikar#195) didn't unblock iter-8.** The
  for-loop DSL feature shipped (commits `21fd213` + `a4f34a8` on
  bikar main), and iter-8 prototyped a `petal-N-2ring.bkr.tmpl` that
  used it correctly (parser/evaluator paths verified end-to-end on
  `/tmp/for-loop-smoke.bkr`). But the underlying bikar gap is
  upstream of for-loops: even fully unrolled hand-written
  `Petal-2-Ring.bkr` doesn't emit lens faces. The for-loop feature
  is correct and useful for other patterns; it just can't paper over
  the lens-emission gap.

  **Why petal-6-full didn't reach 1.000.** Three structural reasons,
  all in the corpus / upstream:
  1. 9 of 10 B-classes are singletons (each layer-N outer-petal
     carries a unique `:arc:#k` invocation tag from the per-block
     connect counter). Singleton classes give no fusion signal.
  2. 5 inner-triangle faces emitted via `face .inner_petal`
     statement carry empty `source_primitives` (the `face` statement
     bypasses the tag-collection machinery), pooling them into B0
     along with all 43 construction circles.
  3. No multi-instance arc-bearing class exists in this corpus —
     the medallion10-style "40 instances of B7" geometry doesn't
     have an analog on arc geometry yet.

  **Cascade is paused at iter-8.** Recommended owner-decision paths
  (Tenet 7: do not tune to make the test green):
  1. Bikar fix: patch `gt-emitter.ts` to handle 2-vertex lens faces
     (e.g., key edges by `(vertices, arcCenter, sweepCCW)` tuple).
     Then `Petal-2-Ring.bkr` emits 6 X + 6 Y petal faces with
     distinct arc-invocation tags — clean 2-class arc-bearing
     corpus, 6 instances each, perfect fusion-delta witness.
  2. Bikar feature: `face .className` statement that propagates
     source_primitives from constituent arcs.
  3. Spec accommodation: accept that F1.v3 has structurally weak
     signal on singleton-heavy partitions and document it (no code
     change). iter-8's +0.064 fusion lift is then "passing" even
     though absolute ARI < 1.000.
  4. Different multi-class arc template (avoid the `face`-statement
     and per-layer-singleton issues; requires bikar lens-emission
     fix to be testable at all).

  iter-7 SHIP holds as the load-bearing arc-path coverage. iter-8
  closes by surfacing the structural finding and the F1.v3
  falsification on this corpus structure; it does NOT falsify F1.v3
  in general.
- **Owner decisions resolved 2026-05-04 (Omar) — went with all three recommendations:**
  1. Corpus size: 3 first (Phase 1.A) → expand to 8 (Phase 1.B). ✓
  2. qiyas#76 (construction hints) folded into this cascade as #151 (D4). ✓
  3. qiyas#131 metric scope replaced by identity-fidelity from #150; count-fidelity demoted to sub-line. ✓
- **Scaled-concentric and mirror-only construction designs (corpus 7, 8)** — unclear if bikar can express these today. Surfaces as a sub-question for Phase 1.B.
- **Cross-rasterizer identity-stability** — F2 spec's tolerance defaults are guesses until measured against multiple rasterizers (CairoSVG, ImageMagick, headless-Chromium). Calibrate during Phase 2 D1.
- **Performance budget** — F1/F3 are O(N) and O(N²) respectively where N is shapes-per-construction. iter-14 at N=275 is fine; if the corpus grows beyond a few-thousand-shape constructions, revisit.

## Cross-references

- Issue: `qiyas/docs/issues/2026-05-04-no-shape-identity-detection.md` (this plan's source).
- Predecessor issue: `qiyas/docs/issues/2026-05-04-detector-undercounts-and-misclassifies-rendered-pattern.md` (the K-sweep that surfaced the capability gap).
- Supersedes scope of: qiyas#131 (validate-detector).
- Folds in: qiyas#76 (construction hints sub-command).
- Bikar work: corpus authoring for constructions 4–8.
