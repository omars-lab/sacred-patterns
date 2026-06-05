# iter-8 SHIP'd via the multiset path that #215 was supposed to delete

**Status:** SUPERSEDED 2026-05-06 by [qiyas/docs/decisions/2026-05-06-iter-8-face-class-vs-multiset.md](../../../qiyas/docs/decisions/2026-05-06-iter-8-face-class-vs-multiset.md) — that doc is the canonical record (PROPOSED, awaiting owner pick of Option A/B/C/D). This file is retained as the original surface note; do not edit further.
**Discovered:** 2026-05-06, while picking up #213 ("qiyas iter-8 re-run with face_class")

## Symptom

Two facts that should not both be true at once:

1. Task **#215** ("Delete multiset class-matching branch; face_class is
   sole class-selector path") is marked **completed**.
2. `qiyas/src/qiyas/identity/provenance.py` still contains
   `derive_fused_partition_v2` keyed on `multiset_to_idx` (multiset
   equality on `source_primitives`); no qiyas-side commit since iter-5
   (`9d4d63d`, 2026-05-04) has touched the file.

And, separately:

3. The renders I emitted today for `petal-N-2ring-{e0bcb697,bb3b4a41}`
   (K=4 and K=6) carry `face_class: null` on every `gt_G` face. bikar
   source has the `face_class` field (commit `f6525c9` and `383391d`),
   but the bundled `bikar/packages/cli/dist/index.js` used by
   `regenerate.py` predates those commits — so the renders were emitted
   without the per-face class resolver.
4. iter-8's "fused_v3 ARI = 1.000 on petal-N-2ring" SHIP verdict
   (#210) was therefore obtained via the **multiset path** in
   `derive_fused_partition_v2`, not via `face_class`. The multiset
   path is exactly the path #215 (and the parent Option I I-D
   decision) committed to deleting.

## Why this matters

- The cascade slice 6 deliverable's SHIP verdict is technically true
  (the numbers in the JSON are correct given the code that ran), but
  it was demonstrated through a mechanism the cascade is mid-removing.
  Re-running the same driver after the multiset deletion lands could
  produce a different result, and we'd not know without explicitly
  re-validating.
- Task #213 (which is what I'd pick up next) reads "qiyas iter-8 re-run:
  petal-N-2ring template + per-K SHIP verdict **using face_class**".
  That re-run is currently impossible: (a) the renders don't carry
  `face_class`, and (b) qiyas has no `face_class`-aware fused-partition
  function to call.
- Task #215 being marked completed is at minimum a tracking error and
  at most a stale claim that masks remaining work. Per Tenet 6, an
  inherited "this is done" claim has to be checked against the
  artifact before it's relied on.

## What's actually missing

To make #213 executable as written, three pre-conditions must be true:

1. **Renders carry `face_class`.** Either the corpus is regenerated
   against a rebuilt bikar dist (the source has the resolver since
   `f6525c9`; the dist binary is older), or the existing renders are
   patched with a one-shot post-processor that walks each `gt_G`
   shape and assigns `face_class` from the dominant `.x_petal` /
   `.y_petal` source-primitive tag.
2. **qiyas has a face_class-aware fused-partition function.** Either
   `derive_fused_partition_v2` gains a face_class branch (preferred:
   when present, use face_class as the equivalence key; fall back to
   multiset only when absent), or a new `derive_fused_partition_v3`
   ships that uses face_class only and the iter-8 driver imports
   from there.
3. **#215 actually lands.** The multiset path either gets deleted in
   the same commit that adds the face_class path, or the deletion
   happens after a parity test confirms the two paths agree on a
   `face_class`-emitting corpus. Per the cascade's "move, don't copy"
   discipline (mirrored from sacred-patterns Phase 2/3), the
   replacement and deletion ship together, not in a long-running
   parallel state.

## Options for the owner

### Option A — Rebuild bikar dist + re-run #210 with face_class

1. Rebuild `bikar/packages/cli/dist/index.js` from current source.
2. Re-run `regenerate.py petal-N-2ring` to refresh the K=4, K=6
   renders. Verify `face_class` is non-null on every `gt_G`.
3. Implement face_class branch in `derive_fused_partition_v2`
   (or v3).
4. Re-run iter-8 driver. Confirm fused_v3 ARI = 1.000 still holds
   per K — this is the actual cascade slice 6 SHIP verdict.
5. Then delete the multiset path (closes #215 for real).

**Pro:** cleanest path; produces the ship the cascade actually wants;
exposes whether face_class agrees with multiset on this corpus
(parity check).

**Con:** ~3 work units (bikar rebuild + qiyas function + re-run +
delete). Probably half a day.

### Option B — Accept iter-8's current SHIP, defer face_class re-run

Mark #210 as ship-via-multiset (correct verdict, deprecated mechanism)
and split #213/#215 into separate later iters. Document that the
slice 6 deliverable holds for the current code state and will need
re-validation when face_class lands.

**Pro:** minimum churn; the cascade slice 6 contract was "F1.v3
multi-class fusion-delta works on parametric arc geometry" and that
is established (the question was can the principle ship; it can).

**Con:** leaves a known tenet-6 trap for the next agent (record
says SHIP, mechanism is being deleted). Tenet 7's "stop when going
in circles" doesn't apply but tenet 4 ("verify before claiming
done") does — the SHIP claim implicitly relies on the multiset
path, which the cascade is removing.

### Option C — Treat as a cascade reset

#211/#215 work assumed a face_class field that is in source but not
yet in the dist or in qiyas. Treat the iter-8 SHIP-via-multiset as
the *baseline* and re-run iter-8 only after the entire face_class
pipeline lands (bikar dist rebuild + qiyas wiring + multiset
deletion). #213 becomes the integration test for that whole pipeline.

**Pro:** aligns the SHIP narrative with the actual mechanism
shipping.

**Con:** larger scope; pushes the cascade slice 6 close-out further
out.

## Recommendation

**Option A.** It's the smallest path that produces a SHIP verdict
backed by the mechanism the cascade is committing to. Steps 1-2
(bikar dist rebuild + corpus regen) are routine; step 3 is a
1-function qiyas change; steps 4-5 are re-runs against the existing
driver. The work makes #213 and #215 simultaneously executable and
closes the divergence.

I am NOT proceeding without owner sign-off — this is a cascade-shape
question (which mechanism ships first) not a local fix.

## What I am NOT doing

- I'm **not** silently re-running iter-8 with the multiset path
  removed and hoping it still ships. That's goal-seeking under
  tenet 7.
- I'm **not** patching the renders post-hoc with a derived
  face_class. The bikar dist is the source of truth for what
  face_class should be; deriving it qiyas-side reproduces the very
  multiset-vs-resolver debate the cascade was opened to resolve.
- I'm **not** marking #215 back to pending. The owner may have
  intended it as planned-completed (the deletion is queued behind
  the face_class wiring landing). I'm flagging the inconsistency,
  not relitigating the task state.

## Stop status

Per loop hard-stop: "Spec divergence: if implementation reveals a
spec is wrong, STOP. Surface the divergence as a doc edit proposal
under .claude/plans/ and wait." This file is the surface. Waiting
on owner pick of Option A / B / C.

## Cross-refs

- iter-8 record (current SHIP-via-multiset): `qiyas/calibration/i1/iter-8-multiclass-fusion-delta.md`
- bikar face_class commits: `f6525c9` (resolver), `383391d` (wire as sole path)
- qiyas provenance.py: last touched `9d4d63d` (iter-5, 2026-05-04)
- #215 task state: marked completed 2026-05-06 (verify with TaskGet)
- Parent cascade plan: `sacred-patterns/.claude/plans/shape-identity-detection-cascade.md`
