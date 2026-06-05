# Option A self-falsified — `for $i` already does what A.1 proposed

**Status:** STOP — owner decision needed
**Discovered:** 2026-05-06, ~1 hour after picking A.1
**Trigger:** Reading commit 21fd213 (#195) to model A.1 after the existing `for` precedent

## The falsification

The decision doc `bikar/docs/decisions/2026-05-06-rotate-block-prev-next-index.md`
(decided 2026-05-06, A.1 picked) was written on the premise:

> "the rotate-block factoring **cannot** express this without a Y-symbolic-rotation
> primitive that bikar's DSL doesn't have"
> — `.claude/plans/petal-N-2ring-rotate-decomposition-divergence.md` line 53

But `for $i in start..end` (#195, commit 21fd213, shipped 2026-05-05) IS a
Y-symbolic-rotation primitive. Its commit message even names the use case:

```
for $i in 0..6
    intersect X{$i} C0 @0.{$i}
    connect arc X{$i}.cpt0 -> X{($i + 1) % 6}.cpt0 on C0
```

That is exactly the pattern petal-N-2ring needs. Modulo wraparound + Identifier
interpolation gives both `prev_index = ($i + N - 1) % N` and `next_index = ($i + 1) % N`
without any AST/evaluator/parser changes — they were shipped a day ago.

## Verification (just ran)

Three-way render comparison at K=6:

| Template | gt_G count | Verdict |
|---|---|---|
| Manual `/tmp/petal-2ring-2class/Petal-2-Ring-2class.bkr` | 7 | reference |
| Rotate-block `petal-N-2ring.bkr.tmpl` (the broken one) | 12 | the original symptom |
| `for`-loop `/tmp/petal-2ring-2class-forloop/petal-2ring-forloop-K6.bkr` (new) | **7** | **PARITY** |

The `for`-loop template is at `/tmp/petal-2ring-2class-forloop/petal-2ring-forloop-K6.bkr`.
Renders cleanly, no errors, matches manual K=6 topology.

## What this means

- **Option A is unnecessary.** No bikar DSL change. No parser/evaluator/test work.
- **A.1 sub-decision is moot.** The "minimal substitution" path was already shipped
  (and it wasn't even called Option A.1 — it was task #195 in the bikar repo).
- **Cost drops 1 day → ~5 minutes** (rewrite `petal-N-2ring.bkr.tmpl` to use `for`
  instead of `rotate`, regenerate, ship).

## What I missed

The original divergence write-up was authored before #195 shipped (or while it
was being authored), but I didn't re-check the bikar DSL surface before writing
the decision doc today. Tenet 6: trust but verify inherited claims — the
"rotate-block can't express this" claim was inherited from my own day-old
plan, and I didn't verify it against current bikar HEAD.

## Proposal

1. **Mark the decision doc SUPERSEDED-BY this plan** (status: SUPERSEDED 2026-05-06).
   Preserve the full body for the audit trail per decision-doc skill rules; don't
   delete the rejected options.
2. **Replace `qiyas/calibration/phase-1b-corpus/templates/petal-N-2ring.bkr.tmpl`**
   with a `for`-loop version (substitution: `{{N}}` for the loop bound and modulo).
3. **Close #216-#219 as obsolete** (the parser/evaluator/test/docs work for
   Option A).
4. **Resume #207** (author petal-N-2ring parametric template) using `for`.
5. **Update `.claude/plans/petal-N-2ring-rotate-decomposition-divergence.md`** —
   add a note that the divergence is resolved by `for`, not by extending rotate.

## Awaiting

Owner: confirm supersession + steps 1-5 above. The verification artifacts at
`/tmp/petal-2ring-2class-forloop/` will get cleaned up if not used; the 5-minute
rewrite is gated on this confirmation.

A subtle point worth naming: the decision doc skill explicitly says rejected
options "are the load-bearing record." The doc isn't *wrong* in the sense of
having considered the options badly — Option A was a reasonable proposal in the
absence of `for`. The doc is wrong in its premise (`for` exists), and that's
the part to record. Future readers should be able to see "Option A picked,
then within an hour the premise was falsified — `for` was the answer."
