# Refined-A Phase 3 (qiyas#226) — spec gap surfaced before contract step

**Status:** RESOLVED 2026-05-06 — owner picked C3.
**Discovered:** 2026-05-06 during autonomous /loop after qiyas#225 SHIP.
**Discovered by:** Claude (autonomous).
**Decided:** 2026-05-06 by owner (omareid). Picked **Option C3**:
restrict the contract step to face_class-populated corpus, keep a
legacy function for Phase 1.A, file a milestone-tied deletion ticket
on the legacy function. Rationale (per web-research robustness ranking):
C3 is the only option with prior-art endorsement for its exact shape
(Interface Refactoring Catalog, API-versioning literature), with one
well-named mitigable risk (legacy-method drift). C2 had direct
anti-pattern hits; C1's annotate-blind workflow is the failure mode
the ground-truth-reproducibility literature flags.
**Hard-stop trigger (per /loop input):** "Spec divergence: if
implementation reveals a spec is wrong, STOP. Surface the divergence
as a doc edit proposal under .claude/plans/ and wait."

## Layman summary

The cascade reached the deletion step (qiyas#226) for the multiset
class-keying branch in `derive_fused_partition_v2`. The parent
decision (`docs/decisions/2026-05-06-iter-8-face-class-vs-multiset.md`
Option A) said: "delete the multiset branch AND the temporary
fallback in the same shipment." But applying that as written breaks
the Phase 1.A SHIP (iter-5 ARI = 1.000 on medallion10/star10/star7),
because Phase 1.A constructions don't author `.className` directives
in their `.bkr` source — `face_class` is legitimately null on every
shape in those fixtures, and falling through to `A::` (visual label)
collapses 261 medallion10 shapes into ~14 classes instead of
preserving the multiset-derived 261-cluster equivalence relation.

This is not a parity gap between paths; both paths agree that those
275 shapes should NOT collapse to 14 classes. The gap is between the
parent decision's "delete multiset everywhere" instruction and the
empirical state of Phase 1.A fixtures, which still need a
class-keying mechanism that face_class can't supply.

## What iter-9 actually showed

`calibration/i1/iter-9-refined-a-parity.py` proved that legacy and
expanded paths produce identical partitions on every entry of the
9-entry corpus (`ARI(legacy, expanded) = 1.000` everywhere). The
SHIP verdict is real — the *expand* step is semantically equivalent
to legacy. But the *contract* step (next) is not just "remove the
expand fallback path"; it's "remove the multiset branch the parent
decision named, which is also the path that produces correct
partitions for face_class-null fixtures."

Concretely, Phase 1.A namespaces (legacy = expanded under iter-9):

- medallion10-iter14: `{A: 14, P: 261}` — 261 shapes class-keyed by
  multiset.
- star10: `{A: 1, P: 31}` — 31 shapes class-keyed by multiset.
- star7: `{A: 1, P: 29}` — 29 shapes class-keyed by multiset.

If qiyas#226 deletes the `P::` (multiset) branch as the parent
decision instructs, those 321 shapes drop to `A::<visual_label>` —
which collapses each fixture's partition to ~1–14 classes,
breaking iter-5's recorded `fused_v3 ARI = 1.000` against B-partition.

## Why the parent decision didn't anticipate this

Looking at the parent decision §"What changes" lines 86–89:

> `qiyas/src/qiyas/identity/provenance.py` gains a `face_class` branch
> in `derive_fused_partition_v2` (when present, key on `face_class`;
> fall back to multiset only when absent — *temporary*, removed in
> the same shipment).

The "temporary fallback" framing assumed face_class would be
populated *everywhere* on the regenerated corpus — i.e., the only
reason multiset-fallback exists is to bridge the regen window. That
was true for Phase 1.B petal-N-2ring (where Phase 0 #223 regen
populated face_class on petal faces), but it was *false* for Phase
1.A: the sub-decision in
`docs/decisions/2026-05-06-refined-A-parity-scope.md` §"Phase 0.5
outcome" recorded after the parent that:

> "face_class is uniformly null on every shape" on Phase 1.A
> regenerated fixtures, "because Phase 1.A constructions predate
> the face_class authoring system, so their `.bkr` source files
> don't use `.className` directives."

The sub-decision noted this as a parity-test refinement (Tier 1.A
= vacuous, Tier 1.B = empirical) but did not propagate the implication
back to the contract step. The contract step, as parent-decision-
written, can't proceed unmodified.

## Three options the owner can pick from

### Option C1 — Add `.className` directives to Phase 1.A `.bkr` source

**What changes:**
- Edit `medallion10.bkr`, `Star-10.bkr`, `Star-7.bkr` (in bikar) to
  annotate every face-emitting block with appropriate
  `.className` directives so face_class populates.
- Re-run bikar build; re-emit Phase 1.A pattern.gt.json files.
- Re-run iter-5 to confirm fused_v3 ARI still = 1.000 on regenerated
  files (Tenet 6 re-verification on the new authoring).
- Then proceed with #226 as parent-decision-written.

**Web research:**
- Hand-authored ground-truth class labels are the ML literature's
  canonical "objective standard" — but the same literature warns
  that retroactive labeling is *measurably* less reproducible than
  derived labels under replication
  ([ICLR submission: Are Ground Truth Labels
  Reproducible?](https://ml-eval.github.io/assets/pdf/GroundTruthReproducibilityICLRSubmitted.pdf)).
  The paper measures inter-annotator agreement well below 1.000 on
  tasks where humans are asked to author class names from scratch
  on objects with no prior class vocabulary — which is exactly C1's
  task (medallion10's 14 visual-class structure has never been
  hand-named).
- Backfill via re-running the source pipeline with new annotations
  is the standard pattern when fixtures predate a schema field
  ([AWS active-learning pipelines for label
  backfill](https://aws.amazon.com/blogs/machine-learning/build-an-active-learning-pipeline-for-automatic-annotation-of-images-with-aws-services/)) —
  but the canonical workflow assumes annotators *review* model-
  proposed labels rather than authoring blind. C1 is annotate-blind
  (the multiset *is* the pre-existing label, but C1 explicitly
  declines to use it as the seed).

**Cost:** ~3/4 day. Requires understanding medallion10's 14
visual-class breakdown well enough to author class names that
preserve multiset-equivalent groupings, on a 261-shape pattern.

**Tenet alignment:** Tenet 8 passes (face_class becomes the truly
universal mechanism); Tenet 2 passes (root-cause fix, not a
fallback); Tenet 6 passes (re-verifies iter-5 SHIP under hand-
authored class names).

**Risk:** the `.className` authoring may not exactly reproduce the
multiset partition. The ground-truth reproducibility literature
above suggests this risk is non-trivial: hand-authoring the same
14 classes a second time, by the same person, doesn't reliably
land on the same partition. If the hand-authored partition
disagrees with multiset on even one shape, iter-5 SHIP retracts.

### Option C2 — Keep `A::<visual_label>` as the no-face_class fallback; delete multiset

**What changes:**
- #226 deletes the multiset branch but keeps the `A::` fallback for
  shapes where face_class is null.
- This semantically *changes* what Phase 1.A's partition looks like:
  multi-class shapes that share a visual label collapse together.
- iter-5's SHIP record on Phase 1.A retracts to "`fused_v3` ARI =
  1.000 was a property of the multiset path; the contracted
  face_class-only path produces a different (visual-label-keyed)
  partition that is no longer 1.000 vs B."

**Web research:**
- The expand/contract pattern (parent decision's framing,
  [Hodgson](https://blog.thepete.net/blog/2023/12/05/expand/contract-making-a-breaking-change-without-a-big-bang/),
  also called [Parallel
  Change](https://martinfowler.com/bliki/ParallelChange.html)) is
  explicit about contraction's contract: "remove the obsolete
  parts only once the new structures are fully adopted." C2 violates
  the precondition — contraction is only safe when the new structure
  *can* express what the old structure expressed. C2 ships a
  contraction where the new structure (face_class-only) is provably
  *less expressive* than the old (multiset) on Phase 1.A.
- The migration-safety literature is direct on this:
  contraction-without-equivalent-coverage is the recurring failure
  mode. [Defacto's schema-migration
  guide](https://www.getdefacto.com/article/database-schema-migrations)
  notes: "the contract phase requires the new schema to be a
  *superset* of the old in observable behavior; if it's a subset,
  you have a regression, not a migration."
- No canonical precedent found for "delete structured-keying
  mechanism and replace with coarser visual-label fallback." The
  one targeted search for that anti-pattern returned no relevant
  prior art — that absence is signal that this *isn't* a recognized
  migration shape; it's a regression dressed up as a migration.

**Cost:** ~1 hour. Code change is small.

**Tenet alignment:** Tenet 6 fails — retroactively invalidates the
Phase 1.A SHIP. Tenet 2 partially fails — the no-face_class case
*is* a fallback, just dressed up as "visual label fallback."
Tenet 8 fails for the same reason as the parent decision warned
against: face_class is supposed to be the general mechanism, but
the visual-label fallback is a different mechanism that takes over
when face_class doesn't fire.

This is essentially the parent decision's Option B (accept the
SHIP-was-via-deleted-mechanism trap) re-introduced under the
banner "contract step."

### Option C3 — Restrict the contract step to corpus that has face_class populated

**What changes:**
- #226 deletes the multiset branch, makes face_class_for required,
  and Phase 1.A is *excluded* from the function's documented
  domain. Phase 1.A's class-keying becomes the responsibility of
  a separate (legacy-named) function that retains the multiset path.
- iter-5's SHIP record on Phase 1.A holds (via the legacy function);
  Phase 1.B is the only domain the contracted function operates on.
- A new follow-up task is filed to either (a) hand-author Phase 1.A
  `.className` directives (Option C1's path) eventually, or
  (b) declare Phase 1.A out-of-domain permanently and document
  the cascade as "F1.v3 with face_class works for face_class-aware
  constructions; Phase 1.A is honored as a historical SHIP via
  the legacy path."

**Web research:**
- "Variant implementations during refactoring — where the old
  method is implemented in terms of the new API, or kept alongside
  with a delegating shim — is a way to break the migration phase
  into smaller and safer steps" (the
  [Interface Refactoring Catalog](https://interface-refactoring.github.io/)).
  C3 is the inverse: keep the old method intact, and scope the
  *new* method narrower. That's a less common shape but recognized
  as legitimate when the old method's domain is broader than the
  new method's intended domain — exactly the situation here.
- API-versioning literature endorses domain-restricted variants
  when the new design genuinely cannot serve the old domain
  ([API versioning best
  practices](https://proteinshaikh.medium.com/best-practices-for-versioning-api-contracts-to-avoid-breaking-changes-a54fbc6d469d)).
  The trade is "more surface area now" vs "premature unification
  later." C3 takes the surface-area cost on principle.
- The risk the literature flags is **legacy-method drift**:
  parallel implementations diverge over time as the new method's
  invariants tighten and the legacy method's guarantees rot. C3
  must include a milestone-tied deletion ticket on the legacy
  function (e.g., "delete when all Phase 1.A `.bkr` files have
  `.className` directives") or it becomes the long-running parallel
  state both the parent decision and Hodgson's expand/contract
  warn against.

**Cost:** ~half day (function split + naming + caller updates +
documentation).

**Tenet alignment:** Tenet 1 partially fails — keeping a legacy
function around means more surface area, not less. Tenet 2 mixed —
this is a scope limit, not a fallback. Tenet 6 passes — iter-5
SHIP is preserved verbatim against the legacy function. Tenet 8
mixed — the cascade gives up "general problem" framing; it's now
"general except Phase 1.A."

This is the most honest option about what the parent decision
implicitly committed to: face_class is the future, but Phase 1.A
constructions never opted into face_class authoring and aren't
going to without C1's bikar-source effort.

## Recommendation (claude's read)

**No autonomous pick.** All three options change the parent
decision's commitments in ways an owner needs to weigh:

- C1 ships the cleanest end-state but costs the most up-front and
  risks an iter-5 retraction if the hand-authored class names don't
  reproduce multiset.
- C2 is fastest but explicitly violates the parent decision's "must
  not retroactively invalidate SHIP records" commitment.
- C3 is the most honest about scope but adds surface area in a way
  the cascade has been trying to avoid.

The /loop's hard-stop rule applies: "if implementation reveals a
spec is wrong, STOP." The spec (parent decision) implicitly assumed
face_class would be uniformly populated post-regen, and Phase 0.5
falsified that without propagating the implication into the
contract step. That's a load-bearing assumption that turned out
false.

## What I am NOT doing

- Not implementing #226 against any of C1/C2/C3 without owner
  selection.
- Not flipping #226 status — leaving it pending.
- Not editing the parent decision doc; that's an owner action.
- Not retracting iter-9's SHIP — it stands as "the expand step is
  semantically equivalent to legacy on the current corpus." The
  contract step's gap is independent of iter-9's verdict.

## What's needed to unblock

Owner picks C1 / C2 / C3 (or another option I haven't considered).
On selection, I'll either:
- (C1) file a bikar task to author `.className` on Phase 1.A
  templates and re-run iter-5 against regenerated fixtures, then
  proceed with #226 as parent-decision-written.
- (C2) implement #226 as a one-PR shipment with the visual-label
  fallback and the iter-5 SHIP retraction recorded explicitly.
- (C3) implement #226 as a scoped contraction with a new legacy
  function for Phase 1.A and a follow-up decision on its long-term
  fate.

## Resolution (2026-05-06)

Owner picked **C3**. Implementation path:

1. **qiyas#226 (revised scope):** in `derive_fused_partition_v2`,
   delete the multiset-only fallback path; require `face_class_for`
   to be passed. The function's documented domain becomes
   "face_class-aware constructions only." Update all in-domain call
   sites.
2. **New legacy function** (e.g., `derive_fused_partition_v2_legacy`
   or rename current to `_multiset`): retains the multiset-keying
   path verbatim. Phase 1.A iter-5 evaluation calls this; Phase 1.B
   iter-7 evaluation calls the contracted `_v2`.
3. **Milestone-tied deletion ticket on the legacy function**
   (mandatory per web research — legacy-method drift is the named
   risk). Trigger condition: "delete when all Phase 1.A `.bkr`
   templates have `.className` directives authored AND iter-5 has
   re-shipped against regenerated fixtures." File this against the
   broader cascade backlog, not as a #226 sub-task.
4. **Update parent decision doc**
   (`docs/decisions/2026-05-06-iter-8-face-class-vs-multiset.md`)
   with a "Refined 2026-05-06" section noting that the parent's
   "delete multiset everywhere in same shipment" instruction was
   refined into a scoped contraction — pointer to this spec-gap doc
   as the rationale.
5. **Update sub-decision doc**
   (`docs/decisions/2026-05-06-refined-A-parity-scope.md`) §
   "Implication for #225 parity gate" to note that the contract
   step lands as scoped, not universal — so iter-9's Tier-1.A
   parity holds against the legacy function, Tier-1.B holds against
   `_v2`.
6. **iter-10 calibration log** records the C3 implementation as the
   contract step's actual ship, with iter-5 SHIP preserved against
   the legacy function and Phase 1.B SHIP preserved against `_v2`.
