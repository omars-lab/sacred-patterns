# Bikar: symmetry-preserving strapwork crossing modes

## Status update — 2026-05-03 (post iter-16 falsification)

PR1 (`crossing over`/`crossing under`) shipped end-to-end (tokens, parser, kernel branch, 6 tests, full suite green). Iter-16 used `crossing over` as the confirmatory experiment for the plan's central hypothesis: "uniform over-strands are rotationally invariant → A2 cv stays under 0.08."

**Hypothesis FALSIFIED.** Iter-16 results:
- A2 cv 0.067 → **0.2671** (worse than iter-15 even)
- A2 status: BROKEN (was OK at iter-14)
- composite 0.7842 → **0.6089** (−0.175 vs iter-14)
- 247 extras (worse than iter-15's 185)

**Why the prediction was wrong:** the plan modeled the symmetry break as living entirely in the `isOver` toggle. It does not. `assignStrands` walks the edge graph in graph-order and assigns strand IDs based on neighbor visit order; that order is not rotationally invariant when crossings span multiple sectors. Setting `isOver = true` everywhere removes one source of symmetry breakage without touching the dominant one (strand-grouping itself). The 247 extras come from sector-varying band-path geometry, not from over/under choice.

**Implications for PR2/PR3:**
- PR2 (`crossing rotational`) was framed as "fix the over/under decision per geometric orbit." If grouping itself is non-invariant, this is solving the wrong layer. PR2 should be re-scoped to *also* canonicalize the strand-walk before doing per-orbit policy. Until that's done, PR2 will fail the same way.
- PR3 (`crossing weave`) inherits the same problem — synchronization across symmetric strands requires that "symmetric strands" be a stable concept, which today they aren't.

**Revised next move (replaces "ship PR2 next"):**
1. Add a kernel test in bikar that renders a medallion-10 strapwork with `crossing over` and asserts 10-fold rotational equivalence of the resulting strand IDs (canonicalize by polar angle, group by sector, check group equality).
2. If that test fails (expected): root-cause is in `assignStrands` graph-walk order. Fix is to sort/canonicalize edges by polar angle before walking. This is **the actual prerequisite** for PR2 working.
3. Only after the kernel test passes for `crossing over` should PR2 (`rotational`) be implemented — and PR2 should be re-validated against the medallion-10 iter-17+ corpus.

PR1 itself stays — `crossing over` and `crossing under` are correct, well-tested, and useful for non-strapwork-symmetric contexts. They're just not the medallion-10 fix.

## Problem

Bikar's strapwork DSL accepts only `crossing alternating` (verified `bikar/packages/core/src/dsl/parser.ts:1139`, `tokens.ts:41`). The alternating mode is global toggle-driven — `detectCrossings` in `bikar/packages/core/src/kernel/strapwork.ts:182` increments `overToggle` per-crossing as it walks nodes, and `assignStrands` (line 287) flips `isOver` at every crossing along each strand.

This breaks rotational symmetry for any odd n-fold (and many even folds): which crossing gets the `over` decision depends on graph-walk order, not on the crossing's geometric position. For n=10 (verified with bikar-medallion-10/iter-15) the result was A2 cv 0.067 → 0.1325, A2 status BROKEN.

**Side proof the fix is cheap:** the renderer (`svg-renderer.ts:289–339`) already partitions strands into `under` and `over` groups and renders them in z-order. The infrastructure for *any* crossing-mode is already there. The only thing missing is the policy that decides which strand crosses over at each node.

Even cheaper: **the `_crossingMode` parameter is already plumbed through the API and ignored.** `computeStrapwork(graph, width, _crossingMode)` at `strapwork.ts:381` underscore-prefixes the parameter — it's threaded all the way from parser to kernel and dropped on the floor. The DSL value is captured into `evaluator.ts:445`'s `env.strapworkConfig.crossing`. Half the wiring is already done.

## Why iter-15 of bikar-medallion-10 needed this

Concrete evidence (see `iterations/15/evaluation.md`):
- Adding strapwork advanced A5 BROKEN→PARTIAL (one notch up, real gain).
- Same edit collapsed A2 cv from 0.067 to 0.1325 (UNEVEN got more uneven).
- Net composite −0.124, REVERTED.

Without a symmetry-preserving crossing mode, strapwork cannot be added to *any* odd-fold pattern (the entire bikar-medallion-N family) without surrendering A2.

## Design space — crossing modes

Five candidate modes, in order of complexity:

| Mode | Decision rule | Symmetry | Notes |
|---|---|---|---|
| `alternating` (current) | global toggle as graph is walked | broken (walk-order-dependent) | already shipped |
| `over` | every crossing: pair-0 over | preserved (rotationally invariant) | trivial — flat policy |
| `under` | every crossing: pair-0 under | preserved | trivial |
| `rotational` | crossing's pair-0 angle decides over/under | preserved (because the rule is geometric) | clean answer for n-fold patterns |
| `weave` | classical over-under-over-under along each strand, but **synchronized at symmetric crossings** | preserved | requires identifying symmetric crossing-orbits |

`over` and `under` are correctness baselines — they prove the mode parameter works end-to-end and they preserve symmetry. They look visually flat (no interlace illusion) but they're the right starting point for testing.

`rotational` is the natural mode for sacred-geometry medallions where every crossing in an n-fold orbit should make the same over/under choice. Rule: at each crossing, sort the two strand-pairs by their incidence angle, and the pair whose first edge has angle in [0, π/n) goes over (the orbit equivalence class is then preserved under rotation by 2π/n).

`weave` is the visually-traditional Islamic-strapwork interlace — but to preserve symmetry, the toggle along each strand must be synchronized so symmetric strands get the same over/under sequence. The synchronization needs the n-fold orbit information (an orbit-finder pass over crossings). Most complex; defer.

## DSL syntax

```
strapwork
  width 5
  crossing over
```

```
strapwork
  width 5
  crossing rotational
```

```
strapwork
  width 5
  crossing alternating  # current behavior, default
```

Backwards-compatible: existing patterns continue to work; the parser change adds new keywords without removing the old one.

## Changes

### Parser (`packages/core/src/dsl/parser.ts:1139`, `tokens.ts:41,188`)

**Current:**
```ts
} else if (t.type === TokenType.Crossing) {
  this.advance();
  crossing = this.expect(TokenType.Alternating).value;
```

**New:** accept any of `Alternating | Over | Under | Rotational | Weave` (add tokens). Validate the captured string is one of the supported modes; emit a clear error for unknown modes. Keep the AST field as `crossing: string` — no type-narrowing needed at the AST layer.

### Tokens (`packages/core/src/dsl/tokens.ts`)

Add `Over`, `Under`, `Rotational`, `Weave` to the `TokenType` enum and the keyword map. Five-line change.

### Kernel (`packages/core/src/kernel/strapwork.ts`)

The `_crossingMode` param at line 384 stops being underscore-prefixed and starts being read. Two functions need to branch:

1. **`detectCrossings`** (line 180) — currently sets `overPairIndex: overToggle % 2` per crossing. New behavior:
   - `over`: `overPairIndex = 0` always
   - `under`: `overPairIndex = 1` always (or whichever index represents the "other" pair)
   - `rotational`: compute the sort-angle of pair-0's first edge; `overPairIndex = floor(angle / (π / n_fold)) % 2` — but `n_fold` isn't known at this layer, so the rule must be expressed without it. Cleaner alternative: `overPairIndex = (atan2(...) >= 0) ? 0 : 1` — preserves 2-fold symmetry trivially, preserves arbitrary n-fold because the half-plane decision is rotationally consistent within each orbit half. Verify experimentally with n=10 medallion.
   - `alternating`: keep current toggle behavior (default / backwards-compat).
   - `weave`: defer — emit an explicit `Error('weave mode not yet implemented')` so users get a clear signal.

2. **`assignStrands`** (line 256) — currently flips `isOver` at each crossing along the strand walk. For `over`/`under` this stays correct (the flip preserves the consistent over/under assignment because both crossings on the strand share the same overPairIndex). For `rotational` the same logic also works because the per-crossing decision is geometric, not order-dependent. For `weave` the synchronized-toggle logic needs orbit information — defer with the kernel.

### Evaluator (`packages/core/src/dsl/evaluator.ts:445`)

No change — already passes `env.strapworkConfig.crossing` through.

### Renderer (`packages/core/src/render/svg-renderer.ts:289`)

No change — already partitions on `isOver` and renders under-then-over.

## Test fixtures

Three new test cases in `packages/core/test/strapwork/`:

1. `crossing-over.test.ts` — render an n=10 hexagram-like pattern with `crossing over`, assert all crossings render pair-0 above (visual + JSON-graph assertion).
2. `crossing-rotational.test.ts` — render the same n=10 pattern with `crossing rotational`, assert that crossings in the same orbit (same radius from center, ±2π/10 rotation apart) all have the same over/under decision.
3. `crossing-symmetry-preservation.test.ts` — render a known-symmetric pattern with each mode, encode it through qiyas (or a stand-in symmetry checker), assert `alternating` produces `cv > 0.10` and `over`/`under`/`rotational` produce `cv < 0.05`.

The third test uses bikar-medallion-10 reference data as the integration target — keeps sacred-patterns and bikar honest about each other.

## Sequencing

Two PRs.

**PR 1 (kernel + parser, half-day):** `over` and `under` modes only. Touches tokens, parser, kernel branching, two new tests. Ship the trivial cases first to prove the policy plumbing works.

**PR 2 (geometric mode, half-day):** `rotational` mode + the symmetry-preservation test. Iterate on the geometric rule until n=10 medallion-bikar-10 strapwork preserves A2 (validated against qiyas svg-audit, not just visual).

**PR 3 (deferred, days-to-week):** `weave` mode with orbit-synchronized toggles. Only ship if traditional interlace turns out to be load-bearing for sacred-patterns convergence (it might — but `over`/`rotational` may be enough to unblock #85).

After PR 1 + PR 2: re-attempt iter-15-equivalent on bikar-medallion-10 with `crossing rotational`. Predicted: A5 PARTIAL preserved, A2 cv stays ≤ 0.07, composite ≥ iter-14's 0.7842.

## What we shouldn't do

- **Don't add `weave` first.** It's the visually-richest mode but requires orbit detection; that's a separate problem and shouldn't gate the unblocker for #85.
- **Don't change `alternating`'s behavior** even if it's symmetry-broken. It has shipped behavior; existing patterns may rely on it. Add new modes alongside.
- **Don't compute `n_fold` inside `strapwork.ts`.** Keep the kernel agnostic of pattern n-fold; the rotational rule should be expressible from local crossing geometry alone (atan2 of pair-0). If it can't, the rule needs to be reconsidered before being added.

## Cross-repo dependencies

- bikar: parser + tokens + kernel + tests (~half-day per PR × 2)
- sacred-patterns: nothing required from the bikar side; just a one-line edit to the iter-16 pattern.bkr (`crossing alternating` → `crossing rotational`) once shipped
- qiyas: nothing required; A2 audit already detects the difference

Add to `docs/cross-repo-dependencies.md` under "bikar strapwork crossing modes" once PR 1 lands.

## Verification

After PR 1+2 land:
1. Re-fork iter-15-equivalent from iter-14: same `strapwork width 5` block but `crossing rotational`.
2. Render and validate via the orchestrator.
3. Expected: composite ≥ 0.79 (vs iter-15's 0.6604), A2 status PARTIAL or PASS (vs UNEVEN), A5 PARTIAL preserved.
4. If composite ≥ 0.83 (above iter-14 baseline), KEEP. If 0.79–0.82, KEEP and continue. If < 0.79, file qiyas-side issue (rotational-mode rendered correctly but the score didn't move — something else is dominating).
