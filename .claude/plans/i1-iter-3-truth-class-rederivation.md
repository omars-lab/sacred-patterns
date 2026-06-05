# I1 iter-3 spec — truth-class rederivation (DECISION REQUIRED)

**Status:** PROPOSAL — owner decision needed before any code lands.
**Surfaced:** 2026-05-04 by qiyas#152 iter-2 calibration.
**Blocks:** qiyas#161 (wire pass-3 TF rescue into validate_detector + measure macro lift).

## Plain-English summary

Iter-2 implemented the textbook polygon similarity metric (Arkin-Chew-Kedem
turning-function distance) to replace F1's brittle exact-string matching.
The metric works correctly — 24/24 invariant tests pass and it's been
cross-checked against the canonical 1992 reference C implementation.

But when we calibrated the metric on the medallion10 corpus, we discovered
the metric and the *truth-class partition* disagree. Some "same-class"
pairs are farther apart under TF distance (max 0.461) than many
"different-class" pairs (smallest gap 0.085). No scalar threshold can
separate same-from-different.

This is structural, not a tuning problem. Either the truth-class partition
needs to change, or we need a different signal for truth. Two options
below; both are spec edits, not code tweaks.

## The data

Calibration on medallion10 (37 truth classes, derived from F1 signatures
during corpus annotation):

```
intra-class TF distance: max=0.461  mean=0.066  p95=0.369
smallest inter-class gap: 0.085  (between C2 and C11)
```

10 truth classes have intra-class noise ≥ 0.30:
C15, C12, C17, C14, C16, C9, C6, C10, C7, C8

10 inter-class pairs have gap < 0.11 (would collapse under any threshold
large enough to merge real same-class pairs):
C2↔C11, C1↔C30, C28↔C36, C23↔C25, C29↔C36, C0↔C11, C26↔C35, C24↔C25,
C22↔C23, C1↔C13.

The classes iter-2's hypothesis explicitly named as the "0.5°-apart truth
classes we want to preserve" (C2↔C11, C1↔C30) sit *inside* the noise
floor of other intra-class pairs.

## Why this can't be patched with a threshold

Tenet 7: don't tune constants when the same fixture both calibrates and
judges the algorithm. The medallion10 corpus is the only Phase 1.A
fixture for the threshold; tuning it to absorb this overlap would
silently weaken the metric across the rest of the corpus and any future
construction.

The signal-vs-noise overlap is not numerical — it's that the F1
partition (which polygons are the "same shape") was derived under a
different metric (exact-string match on quantized per-vertex angles)
than the metric we're now using to judge it (TF distance integrating
over the boundary). Any partition derived from one signature need not
be coherent under another signature.

## Two options

## Prior-art check (web search 2026-05-04)

Three findings from searching MPEG-7 CE-Shape-1 methodology, cluster
validity for non-convex distance metrics, and synthetic vs human-labeled
ground truth:

1. **MPEG-7 CE-Shape-1** — the canonical shape-retrieval benchmark — uses
   *human-curated* class definitions (70 classes × 20 instances) with
   deliberate intra-class variability. The metric is judged against a
   partition that was NOT derived from the metric. Our F1-derived
   37-class partition is what the benchmark literature would call
   "metric-internal" and treat as inadmissible for judging a different
   metric. Source: dabi.temple.edu MPEG-7 page; tc18.org/Latecki
   bullseye-rating description.

2. **Silhouette has a known shortcoming for non-convex clusters**
   (Nature Biotech 2025, "Shortcomings of silhouette in single-cell
   integration benchmarking"). TF-distance space is not a Euclidean
   blob; silhouette will mis-rank cluster cuts. Recommended discipline:
   combine an *internal* index (silhouette, Davies-Bouldin) with an
   *external* one (ARI against an independent partition). The external
   partition is exactly what Option B provides.

3. **Procedural / synthetic ground truth has documented advantages over
   human-labeled** when human inter-rater agreement is fair-to-moderate
   (and our F1-partition annotators were essentially us-with-a-broken-
   signature). The "Ground Truth Correspondence Measure" framing for
   synthetic shape benchmarks supports Option B's premise: when the
   construction primitives are known, they ARE the ground truth.

Implication: A and B aren't substitutes — they're a layered design
where B is the truth signal and A is an *independent witness* that
validates the TF metric itself.

### Option A — Re-derive truth classes from the TF-distance matrix

Compute pairwise TF distance for every detector outline in the corpus.
Cluster (single-linkage with cut, or DBSCAN) at a threshold chosen by
silhouette / cluster-count. The resulting partition becomes the new
truth signal; detector recall is measured against it.

**Pros:**
- No new code beyond the calibration script.
- Self-consistent: same metric calibrates and judges.
- Handles whatever idiosyncratic noise the detector outlines carry.

**Cons:**
- Trades semantic ground-truth (what the construction *meant* the shape
  to be) for metric-internal consistency. Two physically-different
  petals might collapse if their TF distance is small — exactly the
  failure mode MPEG-7 was designed around.
- Threshold for the cluster cut is itself a free parameter, AND
  silhouette is unreliable on non-convex distance manifolds (Nature
  Biotech 2025) — partially defers the same problem and *adds* a
  second one.
- The new partition is opaque to downstream consumers (the C2
  annotation tool, BIKAR, sacred-patterns iteration loop).
- Same-fixture-calibrates-and-judges fails the MPEG-7 standard for an
  admissible benchmark.

### Option B — Re-derive truth classes from construction ground truth

bikar emits `pattern.gt.json` alongside every render — that file already
names the construction primitives (bands, petals, satellites, etc.) and
their parameters. The C2 annotation tool consumes this. Use the
construction ground truth as the partition; measure detector recall
against shapes that came from the *same construction primitive*
regardless of TF distance.

**Pros:**
- Aligned with the parent issue
  (`docs/issues/2026-05-04-no-shape-identity-detection.md`) — identity
  is grounded in construction, not in detector signature.
- Survives any future signature change.
- Re-uses bikar's existing `pattern.gt.json` (no annotation re-work).
- Matches the MPEG-7-style discipline (the partition is independent of
  the metric being judged).
- Procedural ground truth has documented precision advantages over
  human-labeled in shape-recognition benchmarks.

**Cons:**
- We still need a threshold for "is this detector outline close enough
  to the construction-ground-truth outline" — but now the threshold has
  a meaning (detector noise tolerance) and a clean witness pair (truth
  outline vs detector outline derived from the same construction
  primitive).
- Requires expanding qiyas/D3 to consume `pattern.gt.json` directly
  rather than the annotation answer-key.
- Needs Phase 1.A corpus to have `pattern.gt.json` for all three
  patterns (medallion10-iter14, star10, star7). Status of this is
  unknown — needs verification before estimating.

### Option C — Layered: B as truth signal, A as TF-metric witness (RECOMMENDED)

Do both, with specific roles:

- **B is the partition.** Construction primitives from `pattern.gt.json`
  define which detector outlines should match each other.
- **A becomes a diagnostic, not a partition.** Cluster the TF-distance
  matrix at the silhouette-optimal cut. Compute ARI between A's
  clustering and B's partition.

**The ARI is the load-bearing signal:**
- **High ARI** (≥ 0.7, "strong" by silhouette convention) → TF metric
  agrees with construction → ship the threshold derived from B's
  intra-class spread; the metric is sound and the partition is
  semantically grounded.
- **Low ARI** (≤ 0.4) → TF metric is *itself* unsound for this corpus,
  not just the partition → spec decision goes deeper than truth-class
  rederivation. Likely paths: (i) richer signature (turning function +
  per-vertex angle list), (ii) construction-parameter distance instead
  of boundary distance, (iii) per-construction-primitive metrics.
- **Mid ARI** (0.4–0.7) → identify the disagreeing pairs; they are the
  ambiguous-shape catalogue. Decide per-pair (collapse vs split) with
  human review, then re-measure.

**Pros:**
- Two independent witnesses (tenet 8): partition derived from one
  signal, metric validated against another.
- Owner decision becomes binary on a measurable signal (high/low ARI),
  not a pre-commitment to A or B blind.
- Both fail and succeed paths produce information: high ARI ships;
  low ARI surfaces a deeper spec problem we'd otherwise ship past.
- MPEG-7-aligned (B is the partition) AND silhouette-best-practice
  aligned (A's internal validity is checked by an external index).

**Cons:**
- Two implementations instead of one. But Option A's marginal cost is
  small ("no new code beyond the calibration script" per its own
  description); B's `pattern.gt.json` consumption is the real work
  either way.
- Adds a stop-condition (low ARI) that could block iter-3 from
  shipping a number. This is a feature, not a bug — see tenet 7.

## Recommendation

**Option C (layered).** B is the partition; A is the TF-metric witness.
The ARI between them is the single number that decides whether iter-3
ships a threshold or surfaces a deeper spec problem.

If owner picks A or B alone, name which one and why; both are valid in
isolation but neither produces the cross-check that the prior-art
discipline calls for.

## Hard stop on this work

- Iter-3 implementation does not start until owner names A, B, or C.
- The TF metric implementation (qiyas#159) is correct and stays as-is.
- pass-3 wiring into validate_detector (qiyas#161) is blocked until
  iter-3 spec lands.
- No threshold is calibrated, no constants tuned, no per-pattern
  exceptions added. Tenet 7 stop rule is in force.

## Files relevant to the decision

- `qiyas/calibration/i1/iter-2.md` — calibration result section.
- `qiyas/calibration/i1/tally.json` — `stuck_gaps.f1_partition_unsound_under_tf_distance`.
- `qiyas/src/qiyas/identity/turning_function.py` — TF metric (cite Ressler 1992).
- `qiyas/calibration/i1/iter-2-calibrate.py` — re-runnable evidence.
- `qiyas/docs/issues/2026-05-04-no-shape-identity-detection.md` — parent issue.
- `bikar/.../pattern.gt.json` (Option B) — construction-ground-truth schema.
