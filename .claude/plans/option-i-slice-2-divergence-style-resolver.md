---
status: RESOLVED 2026-05-06 — decision doc filed (Option F / I-D selected)
discovered: 2026-05-06
discovered_by: claude during /loop slice 2 implementation (qiyas iter-8 re-run on face_class)
parent: option-i-per-face-class-resolver.md
related:
  - parent-escalation: petal-2ring-q3-actual-face-count-divergence.md
  - bikar-commit: f6525c9 (slice 0 — face_class resolver landed)
  - decision: bikar/docs/decisions/2026-05-06-face-class-style-resolver-wiring.md
---

> **Resolved 2026-05-06.** This document surfaced the divergence and presented
> Options I-A/B/C inline. The authoritative decision (with full options A–F,
> web-search citations, tenet alignment per option, and final ACCEPTED
> selection of Option F = "I-D, delete multiset fallback") lives at
> `bikar/docs/decisions/2026-05-06-face-class-style-resolver-wiring.md`.
> The I-A/B/C inline section below is preserved as the original surface but
> superseded by the decision doc.

# Slice 2 spec divergence — `face_class` is a label nobody renders against

## What slice 0 promised

Slice 0 (committed in bikar `f6525c9`) added a `face_class` field on
every face shape: a single canonical class label, computed by
`resolveFaceClass()` from per-edge tags using the dominant-arc combiner.
The slice 2 plan said: "qiyas iter-8 re-derives B-partition from
`face_class`; per-K SHIP verdicts measured."

For slice 2's ARI to mean anything, `face_class` must:
1. Be present on every face shape ✅ (slice 0 delivered this)
2. Distinguish the X-class faces from the Y-class faces in the rendered
   pattern, so the B-partition has multiple non-trivial classes to align
   against the A-clustering ❌ (slice 0 did NOT verify this end-to-end)

## What the smoke test reveals (Tenet 4 — verify before claiming done)

Running slice 0's resolver against the original divergence-surface
artifact `/tmp/petal-2ring-2class/Petal-2-Ring-2class.bkr` (the bikar
construction whose 6 mixed-class lens faces motivated all of Option I):

- `pattern.gt.json` schema 1.15 ✅
- `face_class` field populated ✅
- **Total `gt_G` face shapes: 1** (not 6 as the parent escalation
  predicted, not 12 as iter-8's ideal premise required)
- That one face: `face_class: ".y_petal"`, `face_count: 18` (i.e., the
  union-find merged 18 same-color sub-faces into one super-shape)
- `source_primitives`: only `.y_petal` tags appear (12× `.y_petal`,
  zero `.x_petal`)
- Rendered SVG fill colors: only `#134074` (petal_x_color) — `#B8860B`
  (petal_y_color) does not appear in the SVG at all

The smoke test contradicts the slice 0 expectation **even though
slice 0's unit + integration tests all pass**. The unit tests use
synthesized `Ring` data with controlled per-edge sources; the
integration test uses Petal-1-Ring 2-class which is a degenerate
single-face-per-class case. Neither exercises the path Petal-2-Ring's
mixed-class lens faces actually take.

## Root cause

`packages/core/src/theme/style-resolver.ts` lines 75-77:

```ts
if (selector.type === 'class') {
  return classes?.has(selector.className) ?? false;
}
```

The style resolver matches a face against `.className` rules by checking
if the face's per-edge **class multiset** contains that class. Petal-2-Ring's
lens faces have BOTH `.x_petal` and `.y_petal` in their multiset (because
their boundaries are made of X-arcs AND Y-arcs). So the FIRST matching
rule in source order wins (CSS cascade without specificity, per the
comment at line 28). In the .bkr file the `.x_petal` rule comes first,
so every lens face gets `petal_x_color` — including the ones whose
`face_class` resolver would have picked `.y_petal`.

Then `gt-emitter.ts`'s same-color union-find merges all 6 same-colored
faces into one super-shape, and the resolver runs on that union.

## Why slice 0's tests didn't catch it

Slice 0's integration test renders Petal-1-Ring 2-class. In Petal-1-Ring,
each lens face has only 2 boundary arcs — one X-arc and one Y-arc. The
multiset has both classes, so the same FIRST-match-wins ambiguity is
present, but Petal-1-Ring's geometry only produces 6 lens faces (not 18
sub-faces colored down to 6 painted regions), so the union-find does
not collapse them to a single super-shape, and qualitative inspection
("each face has a non-null face_class") passes regardless of which class
the FIRST-match rule actually picked. The integration test asserts
`face_class is not null` and `face_class in {.x_petal, .y_petal}` —
it does not check distribution, and it does not check whether
`face_class` agrees with `style-resolver`'s fill choice.

This is the Tenet 8 failure on slice 0: the unit fixtures were "regular
n-gon-only" (Tenet 8 anti-pattern); the asymmetric witness — running
against the actual originating-divergence construction — was not on the
slice 0 acceptance check. The slice plan's acceptance step 1 ("Build
bikar locally; render `/tmp/petal-2ring-2class/Petal-2-Ring-2class.bkr`")
listed it but I did not verify the **distribution** in step 3 ("3 X-faces
and 3 Y-faces") before declaring slice 0 done.

## Options the owner should consider

### Option I-A — Wire `face_class` into `style-resolver.ts` (recommended)

Extend `style-resolver.ts:75-77` to consult the resolved `face_class`
when choosing among class selectors, with multiset-membership as a
fallback. Concretely:

- Compute `face_class` once per face (via `resolveFaceClass`) before
  iterating style rules.
- When the rule selector is `{type: 'class', className: X}`:
  - If `face_class === X` → match wins immediately.
  - Else if `face_class` is non-null and `face_class !== X` → no match
    (face_class is the canonical label; it overrides multiset).
  - Else (face_class is null because no class tags on this face) →
    fall back to current `classes?.has(X)` behavior.

This makes `face_class` the load-bearing class label end-to-end, fixes
Petal-2-Ring rendering (3 lens faces paint X, 3 paint Y), and the
union-find then correctly merges into 6 super-shapes with 3 X + 3 Y
class distribution as the parent escalation expected.

**Cost:** ~2 hours (small refactor in `style-resolver.ts`, add a
`faceClasses` argument that's the resolved per-face label, update the
2 call sites in `evaluator.ts`, add a regression test that renders
Petal-2-Ring-2class and asserts both palette colors appear in the SVG).

**Risk:** Existing single-class-bearing faces' fill behavior is
unchanged because for those faces `face_class === only-class-tag`, so
the new branch matches identically to the old one.

### Option I-B — Decouple `face_class` from rendering entirely

Keep `face_class` as a metadata-only field that ground-truth consumers
(qiyas's B-partition) can use, but accept that **rendered colors may
disagree with `face_class`**. Slice 2 then becomes: re-author
Petal-2-Ring-2class to declare X and Y rules with explicit attribute
selectors that don't depend on multiset matching — for example
`[face_class .x_petal] fill petal_x_color`.

**Cost:** ~half a day (new `face_class` attribute selector in DSL +
parser + matcher; re-author Petal-2-Ring-2class with the new selector;
re-render and re-smoke).

**Risk:** Two parallel ways of writing class-based fills — the original
`.className { fill }` shorthand and the explicit `[face_class C] { fill }`
form. New template authors will pick the wrong one for multi-class
arc-bearing patterns and re-hit this divergence. Unless we
simultaneously *deprecate* the multiset shorthand for class selectors,
this option introduces tooling divergence.

### Option I-C — Re-author Petal-2-Ring-2class to avoid mixed-class boundaries

Drop the `connect arc` declarations that put X-arcs and Y-arcs on the
same lens face's boundary. Instead, declare each lens face explicitly
via `face` statements (which exist in the DSL for direct face emission)
and tag each face with a single class.

**Cost:** ~half a day (re-author the .bkr; verify gt-emitter handles
direct-face syntax for arc-bounded faces; re-smoke).

**Risk:** This is Option H from the parent escalation (face .className
direct declaration). It papers over the multi-class boundary problem
rather than solving it; future templates with naturally-shared-boundary
lens faces (which is geometrically common — every Flower-of-Life
construction has them) will hit the same wall. Tenet 8 violation:
fixes one instance, doesn't generalize.

## Recommendation

**Option I-A.** It's the smallest fix, it makes `face_class` actually
load-bearing (which was the whole point of slice 0), and it preserves
the multiset-membership fallback for backwards compatibility on
single-class-bearing faces. Slice 2 then proceeds as the original plan
described, against a correctly-rendered Petal-2-Ring corpus.

**Slice plan update needed:** insert a "slice 0.5" between slice 0 and
slice 2: "Wire face_class into style-resolver." Slice 1 (DSL surface
for combiners) was already deferred past slice 2 and stays deferred.

## What this divergence is NOT

- It is NOT a flaw in the resolver itself. `resolveFaceClass()` picks
  the right label given the per-edge tags it receives. The unit tests
  on it stand.
- It is NOT a Tenet 7 violation (tuning constants to make a test green).
  The fix is structural — wire face_class into style matching — not a
  threshold change.
- It is NOT a problem with the slice 0 plan. The plan's acceptance
  steps 2-4 (the per-face-distribution checks) were correct; my error
  was treating the integration test as sufficient evidence and skipping
  the acceptance smoke.

## Hard-stop trigger reference

Per the `/loop` autonomous-loop input verbatim:

> Hard stops (do not proceed past these):
> - Spec divergence: if implementation reveals a spec is wrong, STOP.
>   Surface the divergence as a doc edit proposal under .claude/plans/
>   and wait.

This doc is the surface. Slice 2 (`#213`) is paused. Slice 0 (`#211`)
remains COMPLETE — the resolver function is correct and the schema
extension is sound. What's missing is the consumer wiring.
