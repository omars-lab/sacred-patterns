# Petal-N-2ring rotate-block decomposition is spec-incorrect

**Status:** RESOLVED 2026-05-06 — `for $i in 0..N` (bikar #195) is the answer; rotate-block scope unchanged
**Discovered:** 2026-05-06, while smoke-testing parametric template at K=6
**Resolution doc:** [option-A-self-falsified-by-existing-for-loop.md](option-A-self-falsified-by-existing-for-loop.md)
**Original (superseded) decision doc:** [bikar/docs/decisions/2026-05-06-rotate-block-prev-next-index.md](../../../../bikar/docs/decisions/2026-05-06-rotate-block-prev-next-index.md)

> **Note (2026-05-06):** This plan originally surfaced the divergence as
> "rotate-block can't express petal-N-2ring without a new DSL primitive"
> and led to an Option A decision (extend rotate). Within ~1 hour of the
> decision, the premise was falsified — bikar already shipped `for $i in 0..N`
> parse-time loop unrolling with modulo wraparound (#195, commit 21fd213,
> shipped 2026-05-05). Verified at K=6: `for`-loop render = 7 gt_G shapes
> (matches manual source); rotate-block render = 12 gt_G shapes (the symptom).
> The fix is a template rewrite, not a DSL change. Body preserved below for
> the audit trail.

## Symptom

Authored `qiyas/calibration/phase-1b-corpus/templates/petal-N-2ring.bkr.tmpl`
under the Option D plan, instantiated at K=6 by sed-substituting `{{N}}` → `6`,
rendered with the bikar CLI, and got:

- 12 `gt_G` shapes with `face_class ∈ {.x_petal, .y_petal}` — but the face_class
  and fill_color are **inconsistent** for at least 4 shapes
  (e.g. `gt_G0001: face_class=.x_petal fill=#B8860B`, `gt_G0008: face_class=.y_petal fill=#134074`).
- The manually-unrolled originating source (`/tmp/petal-2ring-2class/Petal-2-Ring-2class.bkr`,
  same K=6, same depth-1 if you ignore the cosmetic depth-2) emits **7 gt_G**
  shapes, all face_class-fill consistent, distribution `{.x_petal: 1, .y_petal: 6}`.

The two should produce *equivalent* gt.json structure (both are K=6 N-2-Ring
constructions with the same class semantics) but they don't. The parametric
template is structurally wrong.

## Root cause

The construction has X-petal lens faces (between C0 and each ring-1 circle)
and Y-petal lens faces (between adjacent ring-1 circles). A ring-1 circle
@0.i has **four** distinguished points on it from the intersect declarations:

- `Xi.cpt0`, `Xi.cpt1` — where it meets C0
- `Yi.cpt0` — where it meets @0.{i+1}
- `Y(i-1).cpt1` — where it meets @0.{i-1}

These four points partition @0.i into four arcs. Two of those arcs bound
x-petal lens faces (the "x-lid" arcs: one between X.cpt0 and Y(i-1).cpt1,
one between X.cpt1 and Yi.cpt0). The other two bound y-petal lens faces
(one to each adjacent ring-1 sibling).

The rotate block (`rotate N around C0.mpt`) evaluates its body **once** and
geometrically rotates the produced arcs. The body has access to only one
sector's intersect anchors — typically `X0` and `Y0`. There is no symbolic
"previous sector's Y" available inside the body; you'd have to either
declare Y_{-1} explicitly (which doesn't exist in this construction) or
reach for `Y5` (which only makes sense at K=6, not parametrically).

So the manual-unrolled source declares all six X-intersects and all six
Y-intersects, then writes 30 explicit arc statements that reference both
Y_i and Y_{i-1} (with K=6 wraparound: Y_{-1} = Y_5). The rotate-block
factoring **cannot** express this without a Y-symbolic-rotation primitive
that bikar's DSL doesn't have.

The bug in the current template is that it uses `Y0.cpt1` where `Y_{-1}.cpt0`
(wraparound) is needed — the rotated copy of `Y0.cpt1` lands geometrically
near where Y_{-1}.cpt0 should be **for some sectors only**, depending on
rotation direction and which arc endpoint is used. This produces a tangled
arc graph that the gt-emitter resolves into 12 unbalanced super-shapes
instead of the 7 balanced ones from the manual source.

## Why the spec was written this way

The Option D plan (`.claude/plans/option-i-per-face-class-resolver.md`)
specified parametric K-sweep templates assuming the geometry factors
into a single-sector rotate-block — that assumption was inherited from
the petal-N-ring (1-ring) precedent (#192/#193), which **does** factor
cleanly because each X-petal touches only its own ring-1 circle (no
neighbour-Y boundary to fence). The 2-ring case introduces the
between-adjacent-ring-1-circles Y-petal that the 1-ring case doesn't
have, and the rotate-block decomposition silently breaks.

## Options

### A. Add a wraparound primitive to the bikar DSL

Extend `rotate N around point` so the body can reference `prev` and `next`
peer indices, e.g. `Y(prev)` resolves to "the rotated Y0 at the previous
sector index". Minimal API: a per-iteration rotation context that exposes
`$index`, `$prev_index`, `$next_index` and lets PointRefs use them.

**Pros:** Fixes the root structural limitation. Future N-ring (N ≥ 2) and
ring-of-rings constructions get cleaner factoring. Aligns with bikar's
existing `repeat ... depth` pattern that already exposes `$index` etc.

**Cons:** Bikar DSL surface change. Touches parser, evaluator, ASTNode types.
Not a minutes-fix. Would need its own design doc + tests.

### B. Drop the rotate-block factoring; manually unroll per-K

Generate K-specific .bkr files via a Python regenerator that emits the same
30-arc-per-K explicit form as the manual source. The "template" becomes
a Python script that builds .bkr text given K, not a .bkr.tmpl with `{{N}}`.

**Pros:** No bikar change needed. Matches what the manual K=6 source already
proved works. Decouples this from bikar DSL roadmap.

**Cons:** Drifts from the petal-N-ring precedent (which is a true .bkr.tmpl).
Two parallel idioms in phase-1b-corpus (`tmpl + sed` for 1-ring, `Python emit`
for 2-ring). The cascade was specced assuming all phase-1b templates are
.bkr.tmpl files.

### C. Reformulate the construction to factor into a 1-anchor rotate

Recompose Y-petals as faces bounded by two C0-relative anchors instead of
two ring-1 anchors. E.g. parameterize the Y-petal's outer arc by its
midpoint angle and a half-sweep, so a single sector's body produces both
arc endpoints from C0-relative computations.

**Pros:** No bikar change. Stays in .bkr.tmpl form.
**Cons:** Requires a non-trivial geometric reformulation that I haven't
worked out and that doesn't match how the originating-divergence corpus
was built. Risks introducing geometric drift that obscures whether the
I-D fix is doing what we expect.

## Recommendation

**B** — Python regenerator emitting per-K explicit .bkr files. It's the
smallest change that ships #207 and unblocks #208-#213, doesn't depend on
bikar DSL work, and matches the manual source 1:1 (so the K=6 instance
exactly reproduces the artifact the I-D fix was originally validated against).
The "two idioms in phase-1b-corpus" concern is real but minor — Python-emit
is just `regenerate.py` plus a per-K f-string, not a new framework.

A is the right long-term answer but blocks the cascade on a bikar DSL
expansion that we don't need to ship #213.

C is the worst of both worlds — it changes the construction we're testing
against, which voids the originating-divergence reference.

## What I am NOT doing

- I'm **not** picking B unilaterally. Per the loop's stop rules, this is a
  spec divergence and an owner decision. The .bkr.tmpl approach is in the
  Option D plan as an explicit deliverable; switching to Python-emit is
  scope renegotiation.
- I'm **not** patching the .bkr.tmpl with `Y5` hardcoded for K=6. That
  works for K=6 only and falsifies the parametric premise.

## Stop status

Per the loop's hard-stop rules: "Spec divergence: if implementation reveals
a spec is wrong, STOP. Surface the divergence as a doc edit proposal under
.claude/plans/ and wait." This file is that surface.

Awaiting owner pick: A, B, or C.
