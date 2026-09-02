# I1 iter-12 slice 3 — spec divergence: target regime no longer exists in corpus

**Status:** OPEN — owner sign-off needed before slice 3 work proceeds.
**Discovered:** 2026-05-07 during slice 3 implementation prep.
**Surfaces:** task #238 / qiyas#152 / iter-8 driver wiring.

## What was planned

**Slice 3 (#238)** as scoped in this session: wire SMI into the iter-8
driver, apply a metric-by-balance roll-up rule (balanced refs use ARI;
imbalanced refs use SMI), re-run on petal-N-2ring K∈{2,3,4,6}, write
iter-12 record.

## What I found when reading the existing iter-8 state

The corpus and the decision doc disagree on which K-instances exist:

| Source | K values | Note |
|---|---|---|
| Decision doc `2026-05-06-petal-2ring-k3-ari-saturation.md` | K=3 is the load-bearing case at ARI=0.756 | Framed as "the saturation that justifies Option G" |
| Corpus `phase-1b-corpus/corpus.json` | K∈{4, 6} only | K=2 errors on tangent geometry; K=3 produces a degenerate single-class output (per `petal-N-2ring-K-range-refinement.md` cited in iter-8.md L46-48) |
| Latest iter-8 results | K=4: fused_v3 ARI=1.000 / K=6: fused_v3 ARI=1.000 | petal-N-2ring already SHIPS at ARI=1.000 on every K in the corpus |

The K=3 instance the decision doc treats as the load-bearing case
**does not exist in the current corpus**. It was excluded during the
K-range refinement *after* the original iter-8 attempt that observed
the 0.756 saturation, on the grounds that K=3 produces a degenerate
single-class output (the X-petal class collapses).

## Why slice 3 as planned is a no-op

1. **No K instance in the corpus needs SMI.** K=4 and K=6 already
   reach ARI=1.000. Substituting SMI doesn't change the verdict.
2. **The petal-6-full HARD-STOP is structural, not small-N.** It's a
   singleton-heavy B partition (15 fused-v3 clusters trying to match
   21 B classes). SMI doesn't address the asymmetry between A and B
   granularities; it's a different problem class.
3. **The Option G decision was made against a premise that's already
   been refined out of the corpus** — Tenet 6 (inherited claim went
   stale): the decision doc was written assuming K=3 would remain in
   the corpus, but a corpus refinement *prior to* iter-8 SHIP removed
   it. The decision doc didn't get updated.

## Options

### Option α — Re-add K=3 to the corpus and run slice 3 as originally scoped

**What changes:** add K=3 to `phase-1b-corpus/regenerate.py`, regenerate,
re-run iter-8 to confirm the saturation (ARI=0.756), then run iter-12
with SMI substituted in to confirm SMI lifts that case to a clear
above-chance verdict.

**Pros:**
- Validates SMI on the regime it was picked for.
- Keeps the decision doc's premise live in the corpus.
- Clean experimental witness for "SMI > AMI on small-N imbalanced K."

**Cons:**
- The K=3 instance was excluded for being a *degenerate single-class
  output* — re-adding it might mean SMI gets a "single A-cluster vs
  multiple B-classes" comparison that reduces to the petal-6-full
  asymmetric-granularity problem, not a small-N noise problem. We'd
  be confirming SMI works on a fictional regime.

**Cost:** half day. Owner-touchable.

### Option β — Mark slice 3 satisfied and pivot SMI to petal-6-full

**What changes:** declare slice 3 (as originally scoped) satisfied by
slices 1+2 (SMI shipped, pre-check confirms it works on the N=24 6/12/6
regime). Open a new investigation: does SMI *also* address petal-6-full's
fused_v3=0.945 hard-stop?

**Pros:**
- Slice 3 as a "wire into iter-8 driver" task is implementation, not
  research. If the load-bearing K=3 instance doesn't exist, the
  wiring isn't earning anything we can measure.
- petal-6-full IS a current hard-stop. SMI might or might not help
  there, but it's the actual unfinished business.

**Cons:**
- petal-6-full's problem (15 vs 21 clusters) is asymmetric-granularity,
  not small-N noise. Romano 2014 doesn't claim SMI fixes that. Likely
  a wasted experiment.
- Doesn't close the loop on the decision doc's stated premise.

**Cost:** quarter day to write a probe; high probability of negative
result that surfaces as a *separate* iteration record.

### Option γ — Mark slice 3 satisfied; close the SMI work; re-frame iter-12 as "library-ready, no current consumer"

**What changes:** declare slices 1+2 the deliverable. SMI is in qiyas's
identity layer with tests + chance-noise calibration. The "wire it
into iter-8" step happens *if and when* a future K-instance lands at
the small-N imbalanced regime SMI was picked for.

Update the decision doc with a note: "Option G's *implementation*
shipped 2026-05-07 (iter-12 slices 1+2); the K-instance the doc
treated as the load-bearing case was refined out of the corpus prior
to iter-8 SHIP. SMI is available as the imbalanced-ref metric for any
future corpus addition that lands in the σ-comparable-to-signal
regime."

**Pros:**
- Honest. Doesn't pretend slice 3 did meaningful work it can't do.
- Preserves the value of slices 1+2 (a working SMI module + N=24
  calibration data) for future use.
- Matches tenet 1 (smaller solution that does the job): we built the
  literature's named fix; the consumer can pick it up when there's a
  consumer.
- Tenet 8 alignment: SMI in the codebase is the general fix; the
  current K-instances don't need it, but the next one might.

**Cons:**
- Leaves a half-decided thread: the decision doc's "K=3 saturates,
  Option G is the fix" reasoning becomes archival rather than
  active. Future readers might want clarity on why we shipped SMI
  but didn't switch the iter-8 driver to use it.

**Cost:** ~30 min (update decision doc, mark #238, write a one-line
note in the iter-12 record).

## Web research findings (added 2026-05-07)

Three searches were run after this doc's first draft to ground each
option's pros/cons in the literature, per the decision-doc skill.

1. **Romano 2014's stated regime** — the paper recommends SMI "when
   the number of records is small compared to the number of clusters
   considered," and emphasizes that "standardization is particularly
   important to correct for selection bias when the number of objects
   N is small."
   ([Romano et al. 2014, ICML](https://proceedings.mlr.press/v32/romano14.html);
   [Romano et al. 2016 follow-on, JMLR](https://jmlr.csail.mit.edu/papers/volume17/15-627/15-627))
   This grounds Option γ: shipping SMI as the library tool aligns
   with the paper's framing — the consumer materializes when a
   small-N/K instance lands in the corpus.

2. **K=3 degenerate-partition risk (Option α)** — chance-corrected
   metrics including AMI and SMI are chance-correction tools, *not*
   algorithm-correction tools. AMI "takes a value of 1 when the two
   partitions are identical and 0 when MI between two partitions
   equals the value expected due to chance alone"
   ([AMI, Wikipedia](https://en.wikipedia.org/wiki/Adjusted_mutual_information)).
   If K=3 produces a single-class A-output (the documented reason
   K=3 was excluded), that's a clustering-algorithm degeneracy. SMI
   would still report the chance-corrected MI between a 1-class
   partition and a 3-class partition, but this **doesn't validate
   SMI on a meaningful regime** — it validates SMI's behavior on a
   degenerate partition pair. **Option α falsified.**

3. **Petal-6-full asymmetric-granularity (Option β)** — the literature
   names a different named fix for this regime, not SMI. *"If the
   cluster sizes differ, measures like the Jaccard index and the
   Hubert-Arabie adjusted Rand index tend to mainly reflect the
   degree of agreement between the partitions on the large clusters.
   The indices provide little to no information on the smaller
   clusters."*
   ([Warrens & Hennig 2022, "Understanding the Adjusted Rand Index"](https://link.springer.com/article/10.1007/s00357-022-09413-z)).
   The named fixes for asymmetric granularity are **asymmetric Wallace
   indices** (cited in Warrens & Hennig 2022) and **Normalised
   Clustering Accuracy** ([Gagolewski 2024](https://link.springer.com/article/10.1007/s00357-024-09482-2)),
   not SMI. **Option β theoretically misaligned.**

## Recommendation

**Option γ.** The web search collapses the option set:

- **α falsified** — K=3 was excluded for being a single-class
  degenerate output. SMI cannot rescue a clustering algorithm whose
  output partition has 1 cluster; the chance-correction is doing
  the wrong job on the wrong problem.
- **β theoretically misaligned** — petal-6-full's 15-vs-21 cluster
  asymmetry is the regime where ARI loses information about small
  clusters; the named fixes in the literature are asymmetric Wallace
  / NCA, not SMI.
- **γ aligned with Romano 2014's stated regime** — ship SMI as the
  library tool for small-N/K instances; document that the current
  corpus doesn't contain such an instance after the K=3 exclusion;
  the iter-8 driver continues to use ARI on every current corpus
  entry.

If the petal-6-full hard-stop becomes load-bearing on its own, that
spawns a *new* decision (asymmetric Wallace vs NCA vs accept the
asymmetric-granularity penalty), independent of this iter-12
cascade.

The /loop hard-stop rule (spec divergence) names exactly this
moment: stop, surface, wait for owner sign-off — but with the
literature now named, the picked option is no longer judgment-call;
it's the only option not falsified by the searches.

## What would change this recommendation

- If the user confirms that re-adding K=3 to the corpus is desired
  (Option α), slice 3 has a real target.
- If the user wants to investigate SMI on petal-6-full despite the
  poor theoretical fit (Option β), slice 3 pivots scope.
- If the user agrees with Option γ, slices 1+2 close out the iter-12
  cascade and #238 is marked completed-as-noop with a pointer here.

## Open question for owner

After the web research above, the original "intentional vs accidental"
exclusion question is settled: K=3 was excluded for being a degenerate
single-class output, which SMI cannot rescue. So the only remaining
question is whether to accept γ as-stated, or to spawn a separate
decision doc for the petal-6-full asymmetric-granularity hard-stop
(asymmetric Wallace vs NCA vs accept the penalty).

Awaiting sign-off on:
1. Adopt γ — close iter-12 with library shipped; mark #238 as
   noop-against-current-corpus and point at this doc.
2. Whether to file a follow-up decision doc on petal-6-full
   (separate from iter-12) for the 0.945 hard-stop.

## Sources

- [Romano et al. 2014 — Standardized Mutual Information for Clustering Comparisons (ICML)](https://proceedings.mlr.press/v32/romano14.html)
- [Romano et al. 2016 — Adjusting for Chance Clustering Comparison Measures (JMLR)](https://jmlr.csail.mit.edu/papers/volume17/15-627/15-627)
- [Adjusted Mutual Information (Wikipedia)](https://en.wikipedia.org/wiki/Adjusted_mutual_information)
- [Vinh, Epps & Bailey 2010 — Information Theoretic Measures for Clusterings Comparison (JMLR)](https://jmlr.csail.mit.edu/papers/volume11/vinh10a/vinh10a.pdf)
- [Warrens & Hennig 2022 — Understanding the Adjusted Rand Index and Other Partition Comparison Indices Based on Counting Object Pairs (Journal of Classification)](https://link.springer.com/article/10.1007/s00357-022-09413-z)
- [Gagolewski 2024 — Normalised Clustering Accuracy: An Asymmetric External Cluster Validity Measure (Journal of Classification)](https://link.springer.com/article/10.1007/s00357-024-09482-2)
