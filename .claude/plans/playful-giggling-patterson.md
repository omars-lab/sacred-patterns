# Trust the Validator — make qiyas verdicts deterministic, visibility-correct, adversarially proven, and calibrated

## Context

The first I2 photo-cascade slice (2026-06-10, `qiyas/calibration/i2/README.md`) proved the I2 premise at Tier 0 but exposed that **the validator's own verdicts aren't yet trustworthy** on cross-format comparisons:

1. **Path-dependent verdicts** — the same traced SVG yields `extra=0` (default align path: derotate image → raster re-encode, which applies `contour_min_area=25` + circle-support filters) vs `extra=7` (`--no-rotation-align`: SVG fast-path, which applies **no filtering at all**). One input, two shape sets — a tenet-11 violation at the verdict layer.
2. **Raster-invisible reference shapes punish the score** — synthetic render.svg carries unstroked construction circles a raster/photo can never show; the SVG fast-path encodes them; cross-format diffs get `missing=2/3`. The visibility filter already exists and its thresholds are **ACCEPTED** (2026-05-21, Option A: ΔRGB≤4, K=2 — `src/qiyas/identity/visibility_filter.py`) but it lives downstream in closeout, opt-in — not in the `encode_image → compute_diff` path.
3. **Alignment inflates position drift** — image derotation pivots at `(w/2, h/2)` (`diff/align.py:171-173`) while the matcher rotates shapes about the pattern centroid; off-center pattern + 180° derotation → `position_drift_px` 303 vs 134 for visually-coincident shapes.

Beyond these bugs, exploration found **nothing anywhere validates the validator adversarially**: no test plants a defect and asserts it's caught; no null-hypothesis baseline (ARI(detector,B) > ARI(random,B)); no direct `encode_image` determinism test; no external oracle on the hand-rolled ARI.

**Verified mechanism facts the plan relies on** (read from code, not inferred):
- `prealigned_rotation_deg != 0` **skips** the matcher's rotation sweep (`diff/matcher.py:185-188`); the matcher's own sweep (k·360/fold about pattern centroid) is the rotation mechanism for un-prealigned inputs.
- The aligned/derotated image is consumed **only** to re-encode the recon; tier-2/3 report panels receive the *original* recon image (`cli.py:293-310`) — so when align fires, shape overlays are drawn in the wrong frame (latent overlay bug, fixed for free by Phase 1).
- Image pre-align IS load-bearing for **rotated raster recons** (`tests/test_diff_alignment.py` pins Sq-Oct@45° ≥0.95; matcher-only scored 0.799 historically) — it cannot be deleted outright, only scoped to raster inputs.
- `_read_bgr` (`align.py:139-159`) rasterizes SVG recons via cairosvg so they can be image-derotated — this is exactly how SVG inputs leak into the raster-filtered path.

Trust = (a) **deterministic** (one canonical verdict path per input class), (b) **visibility-correct** (cross-format comparison judges only what raster can show), (c) **adversarially proven** (planted defects caught, null hypotheses rejected), (d) **calibrated** (I2 band over 8 witnesses, not 1), (e) **attested** (a contract doc mapping each trust claim to its suite).

All work in `/Users/omareid/Workspace/git/qiyas`. Each phase ships standalone (tenets 1/12); decision docs via the new frontmatter schema + `make ledger`.

## Phase 0 — Determinism floor + freeze the defect witnesses (S, ~1d)

- **Create `tests/test_encode_determinism.py`**: encode each of the 7 Tier-0 `calibration/i1-corpus/renders/single-*/render.svg` + one PNG twice in-process and once via subprocess; byte-compare canonical JSON dumps (reuse the sorted-dump pattern from `write_diff`, `diff/__init__.py:76-87`; conventions from `tests/test_baseline_emit.py`).
- **Extend `tests/test_i2_trace_divergence.py`** with `xfail(strict=True)` characterization tests for the unification targets: extra-count path-equality across align modes; lens `position_drift_px ≤ 150`. They flip to XPASS→hard-fail when Phases 1–2 land (tenet 18; strict-xfail is the repo's canonical pattern for known-regression-awaiting-fix).
- Acceptance: `uv run pytest tests/test_encode_determinism.py tests/test_i2_trace_divergence.py` — determinism green, xfails xfailing. No decision doc.

## Phase 1 — One canonical shape-diff path per input class (defects 1+3) (M, ~2-3d)

- **`src/qiyas/cli.py` (validate, ~line 268) + `src/qiyas/diff/__init__.py` (`compute_diff_images`, 232-272)**: pre-align fires only when recon is **raster** AND ref `dominant_fold > 1`. SVG recons always take fast-path encode + matcher rotation sweep (exact for vector inputs). Remove `--no-rotation-align` (path is input-class-determined, not flag-determined — tenet 11).
- **`src/qiyas/diff/align.py`**: pivot derotation at the recon **pattern centroid** (available from the winning candidate's encoding in `_alignment_score`) instead of `(w/2, h/2)`; delete `_read_bgr`'s SVG/cairosvg branch (SVG never reaches align anymore).
- **`tests/test_diff_alignment.py`**: keep all rotated-PNG pins (the load-bearing Sq-Oct@45° case must stay ≥0.95); add an off-center rotated-PNG pivot witness; add SVG-recon-never-prealigned test.
- **Decision doc** `docs/decisions/2026-06-XX-shape-diff-canonical-path.md` (tag: `svg-direct` family — check LEDGER for supersede relations first, per C5).
- Acceptance: Phase-0 xfails flip; `uv run pytest` **full suite** (scores shift → tenet 21); re-run I2 slice 0 and update `calibration/i2/README.md` (expect drift ~134, extras consistent across the now-single path).

## Phase 2 — Unified encode-time shape filtering (defect 2) (M-L, ~3-4d)

- **Create `src/qiyas/stages/shape_filter.py`** — a post-encode stage applied in `src/qiyas/pipeline.py` for **both** routes:
  - min-area: apply `PrimitivesParams.contour_min_area` (import from `stages/primitives.py:64`, don't duplicate the constant) to fast-path emissions;
  - raster-visibility: `filter_merged_with_neighbor` (`identity/visibility_filter.py:105`) with the ACCEPTED Option-A defaults, sampling the pipeline's already-rasterized PNG (`pipeline.py:140-160` produces it for SVG inputs; raster inputs use themselves).
  - Per tenet 3, no silent drops: filtered shapes stay in the encoding flagged (`raster_invisible` / `below_min_area` + filter evidence) and are excluded from scoring by extending the existing `_split_scoreable` precedent (`diff/__init__.py:280-284`, the `unknown` exclusion).
  - Debug escape hatch on `encode` only (not on `validate`).
- **Decision doc** for *placement* (encode-time, both paths), citing the accepted threshold doc for constants. Fix the stale "PENDING" reference in `calibration/i2/README.md` (the threshold decision is ACCEPTED 2026-05-21).
- **Documented default (owner can override at review):** historical i1 baselines/tallies are **regenerated** under the new policy in the same shipment, per tenet 24 (no compat annotations, break + regen).
- Acceptance: single-petal vs traced.svg goes `missing 2→0`, `extra 7→0` on the canonical path; upgrade `tests/test_i2_trace_divergence.py` to assert `extra_in_recon == []`; full suite + regen `fixtures-canonicals` expected encodings (tenet 21).

## Phase 3 — Adversarial proof: planted defects, null hypothesis, ARI oracle (M, ~2-3d)

- **Create `tests/test_planted_defects.py`** — 5 mutation operators on Tier-0 SVGs, mutated in-memory via ElementTree; assert the validator **catches** each:
  1. delete-shape → appears in `missing_in_recon`, structural drops;
  2. displace-shape (+25px, ≫ noise floor) → `position_drift_px` above floor + warning fires;
  3. duplicate-shape → `extra_in_recon` non-empty *after* Phase-2 filtering (the filter must not eat real geometry);
  4. recolor-to-neighbor → visibility filter flags it, diff reports it missing (positive-evidence proof the ΔRGB≤4/K=2 policy fires) — needs Phase 2;
  5. corrupt `face_class` in a gt.json copy → `ARI(fused,B) < 0.9999`, i.e. gate G1 of `calibration/i1/acceptance.yaml` FAILS on the mutant.
- **Create `tests/test_ari_oracle.py`**: (i) frozen oracle vectors — partition pairs with `sklearn.metrics.adjusted_rand_score` values computed offline, recorded in a JSON fixture with provenance (**documented default:** fixture, not a sklearn dev-dep — honors the hand-rolled rationale in `identity/ari.py:17-20`); (ii) property tests (ARI(X,X)=1, label-permutation invariance); (iii) null hypothesis: ARI(detector,B) > ARI(seeded-random-permutation,B) over a corpus sample.
- **Cross-split consistency**: assert gate pass-rates on `splits.json` train vs test don't diverge beyond a recorded band.
- Acceptance: every mutant caught, null rejected, oracle matched. Operators 1-3+5 can land right after Phase 1 if Phase 2 is in flight.

## Phase 4 — I2 band over 7 Tier-0 + 1 Tier-2; promote acceptance.yaml (M, ~2-3d)

- Generate frozen `traced.svg` fixtures (VTracer 0.6.12 pinned, traced offline, committed) for the remaining 6 Tier-0 entries + **petal-N-ring N=6** (documented default Tier-2 pick: canonical known-good face emission), as `calibration/i2/slice-N-*/`.
- Per-slice witness tests following `tests/test_i2_trace_divergence.py`; measurements appended to `calibration/i2/README.md` (oracle-in-record).
- **Create `calibration/i2/acceptance.yaml`** — I2-G1 (every raster-visible ref shape type-matches), I2-G2 (`extra==0` post-filter), I2-G3 (param-drift band derived from the 8 measurements). Evaluate via the existing `qiyas.closeout.gates` machinery (template: `calibration/i1/acceptance.yaml`); if diff-record schema doesn't fit, add thin `i2_gates.py` following `src/qiyas/identity/f2_gates.py`.
- Real-photo slice explicitly **out of scope** (no ground-truth path yet — that's the I2 roadmap's named open question, separate decision).
- Acceptance: 8/8 slice tests green; gate-evaluator run recorded; review-portal verdict recorded for the band promotion (tenet 27).

## Phase 5 — Trust contract + replay linkage (S-M, ~1-2d)

- **Create `docs/trust-contract.md`**: table mapping each claim — determinism / visibility-correct cross-format / adversarial catch + null rejection / I2 calibrated band / replay integrity — to its attesting suite, exact pytest command, and acceptance.yaml gate IDs.
- **Create `tests/test_review_replay_e2e.py`**: annotation verdict=`wrong` → backlog-stub emission end-to-end over `src/qiyas/review/replay.py` (the untested linkage); assert `score/replay.py` `ranking_pairs` violations surface as failures.
- Re-attest R1–R4 in the routing doc with this work's evidence.

## Verification (end-to-end)

1. After each phase: `make ci-local-fast`; full `uv run pytest` where scores/baselines shift (Phases 1, 2).
2. After Phase 2: re-run the slice-0 pipeline (`qiyas validate render.svg traced.svg`) — expect composite to rise as the two invisible-circle misses leave the scoreable set; record before/after in `calibration/i2/README.md`.
3. After Phase 4: `qiyas` gate-evaluator run on `calibration/i2/acceptance.yaml` exits 0; the 8 slice witness tests run inside CI's pytest from then on.
4. Tenet 27: portal verdict recorded for the Phase-4 band promotion.

## Documented defaults an owner can veto at review

1. **Phase 2:** regen historical i1 baselines under the new filter policy (tenet 24) rather than annotating them pre/post-filter.
2. **Phase 3:** frozen ARI oracle fixture rather than a scikit-learn dev dependency.
3. **Phase 4:** petal-N-ring N=6 as the Tier-2 witness.
