---
status: REOPENED 2026-05-25 — Option A falsified, Option G shipped + fixture verdict surfaced Option I (qiyas detector + sliver cleanup, NOT Option E/F clip semantic change); PENDING owner re-decision
status_token: REOPENED
picked_option: null
tag: arc-lens-partial
dead_end:
  approach: ship the full 3-piece extend+clip cascade (Option A) for partial-shape rendering
  verdict: REFUTED
  use_instead: Option G (qiyas detector + sliver cleanup), not an Option E/F clip semantic change
  killed_by: docs/decisions/2026-05-07-partial-shape-rendering-via-construction.md
discovered: 2026-05-07
decided: 2026-05-07 (original), PENDING (re-decision)
owner: omar (sacred-patterns owner)
related:
  - plan: sacred-patterns/.claude/plans/partial-shapes-via-construction.md
  - task: sacred-patterns#106 (parent), #254-#260 (cascade), #539 (falsification)
  - cross-repo: qiyas (encoder + A6 verdict), bikar (DSL primitives)
  - falsification-iters: bikar-medallion-10 iter-19 (extend validated, ceiling), iter-20 (clip(C0) -0.13), iter-21-probe (clip(C0+S0..S9) -0.029)
---

# Partial-shape rendering via construction

## Layman summary

The reference medallion has half-shapes at every interior boundary — where two
satellite stars meet, the tips that would extend into the neighbor's territory
are drawn as half-stars clipped along the shared chord. Our renderer draws only
whole shapes inside their natural circle, leaving bare gaps where the reference
has structure. We need to decide whether to fix the construction language so it
can express "extend beyond, then clip to a boundary," and whether the audit tool
should call out the gap explicitly or stay silent.

## Implications of getting this wrong

- **Wrong → blocks convergence.** medallion-10 has been stuck at ~74% pixel
  similarity for 14 iterations because 30-40% of bare-region pixels can't be
  closed by any tile-shape edit; only construction-extent edits close them. If
  we pick an option that doesn't add the construction primitive, that ceiling
  stays.
- **No-pick → silent rot.** A6 keeps reporting `MISSING vertex_count=8` for
  shapes that *are* present in the reference but as partial polygons. The
  iteration agent reads `MISSING`, treats it as "construction missing
  entirely," and either gives up or builds a redundant whole-shape that the
  void detector then over-paints. The signal is structurally wrong — it's not
  that we forgot to draw a star, it's that the star reaches further than our
  primitives let it reach. (Tenet 3 violation if we let it stand.)
- **Hard to undo.** New DSL primitives are commitment surface. Once `extend`,
  `boundary`, and `clip pattern` ship in bikar, every existing pattern
  inherits them — fixing a bad grammar later means migrating gt.json fixtures
  and the qiyas detector calibration corpus. The grammar shape needs to be
  right on first land.

## Main questions we need answered

1. **Does the bikar DSL shape mirror an existing canonical surface?** — answer
   via web research below (CGAL `Boolean_set_operations_2`, Asymptote `clip`,
   Kaplan PhD thesis on Islamic-pattern boundary handling).
2. **Can qiyas's encoder reliably distinguish a "would-close-into-N-vertex
   polygon if extended" partial path from random open polylines?** — answer by
   running the proposed detector against the existing iter-14 medallion-10 SVG
   and at least one Phase-1.A fixture (where the answer should be "no partial
   polygons present").
3. **Does Option A's predicted +0.05 to +0.10 composite lift hold up under the
   counterfactual cost model?** — answer via the actual `extend` edit on
   iter-14 (#260 verifies post-implementation; cf_delta-cost-blind memory
   applies).
4. **Will `extend` interact badly with the in-flight strapwork rotation work
   (bikar PR2/#114)?** — open at decision time; mitigation is to land #258
   PR1 (`boundary`) before strapwork PR2 merges so the merge order is forced.

## Options considered

### Option A — Ship the full 3-piece cascade (qiyas detector + bikar primitives + sacred-patterns translation)

**Layman:** add the four DSL primitives in bikar, the new A6 verdict in qiyas,
and the iteration-guide translation row — the full plan as written.

**What changes:**
- bikar: new DSL primitives `boundary`, `extend`, `clip pattern`, `intersect`
  (parser + compiler + scene-graph + gt-emitter); pattern.gt.json schema bump
  to express extended-then-clipped faces.
- qiyas: encoder partial-polygon detector; A6 verdict `CLIPPED-MISSING`;
  counterfactual transformer for the new verdict; weights/sacred-patterns.json
  weight for CLIPPED-MISSING delta.
- sacred-patterns: iteration-guide translation table row; cross-repo-deps
  section update.

**Web research:**
- CGAL's `Boolean_set_operations_2` provides the canonical "regularized
  union/intersection of polygons" semantics — `join(P, Q, R)` returns a
  polygon-with-holes; this is the model the bikar `boundary <name> = union(...)`
  primitive should mirror, not invent. — [CGAL 2D Boolean Set-Operations](https://doc.cgal.org/latest/Boolean_set_operations_2/index.html)
- Asymptote's `clip(picture, path, fillrule)` is the canonical "draw beyond,
  then clip to a region" pattern in declarative graphics — the four primitives
  align directly with how Asymptote programs express the same construction
  ("draw the full unit-circle scaled, then `clip(scale(0.7)*unitcircle)`"). —
  [Asymptote clip documentation](https://www.cs.rit.edu/doc/asymptote/html/clip.html)
- Kaplan's PhD thesis on Islamic star patterns explicitly handles this case:
  *"motif segments around the boundary of the resulting composition can be
  removed, paring it down to a core of whole rosettes"* — i.e., the canonical
  pattern is "construct the full motif, then clip to medallion silhouette,"
  which is exactly what `extend` + `clip pattern` enables. — [Kaplan PhD §3 (Islamic Star Patterns)](https://cs.uwaterloo.ca/~csk/other/phd/kaplan_diss_starpatterns_print.pdf)

**Pros:**
- Closes the structural gap end-to-end. The iteration agent reads
  `CLIPPED-MISSING` and applies a one-line `extend` edit; no hand-translation.
- Aligns with established prior art (CGAL semantics, Asymptote pattern,
  Kaplan's pattern-construction methodology) — we're not inventing.
- Generalizes (tenet 8): every future bikar pattern with internal boundaries
  inherits the primitives. medallion-10 is the witness, not the only target.

**Cons:**
- Largest scope: ~1-2 days qiyas + ~3-5 days bikar + ~1 hr sacred-patterns.
  Sequencing risk: qiyas detector and bikar primitives have to land in some
  order, and the verifier (#260) only runs after both ship.
- Decision binds bikar grammar shape on first land; rework cost is high
  (existing gt.json fixtures + detector calibration corpus would migrate).
- `intersect` primitive is hardest and may slip — the plan flags this as
  "deferrable to follow-up," but that means the cascade ships with 3 of 4
  primitives and the medallion-10 inter-satellite case may not fully close.

**Cost:** 4-7 days across two repos.

**Closes which questions from §4:** Q1 (mirrors CGAL/Asymptote/Kaplan), Q2 (qiyas
detector ships and is tested on iter-14 + Phase-1.A fixtures), Q3 (verified
post-implementation by #260).
**Leaves open which questions:** Q4 (strapwork interaction; mitigated by merge
ordering, not closed in spec).

**Tenet alignment:**
- Tenet 1 (simplicity): mixed. Four primitives is more surface than zero, but
  each primitive does one thing and the alternatives (Option B/C/D) push
  complexity into worse places (manual baseline edits, ad-hoc clip rules).
- Tenet 2 (root cause): yes. `extend` + `clip` is the construction-extent
  primitive that's been missing; this fixes the language, doesn't paper over.
- Tenet 5 (read existing shape): yes. Mirrors CGAL/Asymptote rather than
  inventing.
- Tenet 8 (general problem): yes. Every bikar pattern with internal
  boundaries inherits; medallion-10 is one witness of the class.

### Option B — qiyas-only: emit CLIPPED-MISSING, defer bikar primitives

**Layman:** qiyas detects partial shapes and surfaces the new verdict; bikar
is unchanged. Iteration agent sees the warning but has no mechanical edit to
apply — must hand-extend construction circles or accept the gap.

**What changes:**
- qiyas: same detector + A6 verdict + counterfactual as Option A.
- bikar: nothing.
- sacred-patterns: translation table row says "CLIPPED-MISSING — no
  mechanical fix yet; investigate manually."

**Web research:**
- The pattern of "diagnostic ahead of remediation" is common in compiler
  toolchains — clang ships warnings for code patterns it can't auto-fix, and
  rustc's "consider adding lifetime annotation" diagnostics are explicit
  about leaving the fix to the human. The model is honest if the warning's
  cost is low (silent if benign) and the fix surface is still discoverable. —
  [no specific URL; canonical pattern in compiler diagnostics]
- Penrose (the diagram DSL) has a similar split: the constraint solver
  produces diagnostics about unsatisfiable constraints, but extending the
  Style language is a separate workflow. — [Penrose: from mathematical
  notation to beautiful diagrams](https://penrose.cs.cmu.edu/siggraph20)

**Pros:**
- Smallest scope: ~1-2 days qiyas only.
- Surfaces the gap loudly (tenet 3) without committing to a grammar shape we
  may want to revise.
- Buys time to gather more evidence on what the right bikar primitives are
  before binding the grammar.

**Cons:**
- **Violates tenet 3 in a subtler way:** the warning is "loud-but-not-actionable."
  An iteration agent reading `CLIPPED-MISSING` with no DSL idiom to apply has
  the same downstream effect as the silent `MISSING`-on-a-partial-shape:
  nothing changes. The signal exists in the validation.json but doesn't
  translate to code. (Memory: cf_delta-cost-blind — predicting score lift
  doesn't deliver score lift.)
- Doesn't close the medallion-10 ceiling. The plan's predicted +0.05 to +0.10
  lift requires the `extend` edit; without bikar primitives, the only fix is
  hand-extending construction circles in BKR — which works once but doesn't
  generalize and is exactly the manual-tuning anti-pattern (tenet 7-adjacent).
- Adds a pending-fix backlog item: "CLIPPED-MISSING ships in qiyas, bikar
  doesn't act on it yet." That backlog rots — by month-3 the warning is
  noise.

**Cost:** 1-2 days.

**Closes which questions from §4:** Q2 (detector tested).
**Leaves open which questions:** Q1 (no DSL shape committed), Q3 (no `extend`
edit to verify), Q4 (no strapwork interaction since no primitive).

**Tenet alignment:**
- Tenet 3 (surface, don't hide): partial credit. Surfaces louder than `MISSING`,
  but the warning is unactionable so the noise/signal ratio worsens over time.
- Tenet 8 (general problem): no. Solves the qiyas detection instance but
  leaves the broader "bikar can't express extended-then-clipped" gap open.

### Option C — bikar-only: ship DSL primitives, qiyas keeps reporting MISSING

**Layman:** add the four DSL primitives to bikar. Iteration agents have to
recognize partial-shape opportunities by inspection (looking at the reference
image vs the recon) — qiyas keeps emitting plain `MISSING`.

**What changes:**
- bikar: same four primitives as Option A.
- qiyas: nothing.
- sacred-patterns: iteration-guide note explaining "MISSING vertex_count=N
  near a satellite boundary may indicate a CLIPPED-MISSING — try `extend
  ... clip-to medallion_outline`."

**Web research:**
- TikZ / pgfplots is the prior-art comparison: a powerful declarative language
  with rich clipping/extend semantics, but no static analyzer that points out
  "this construction is missing." Authors learn idioms by reading examples,
  not by tool guidance. The model works for TikZ because it's
  human-authored; it fails our use case because our authors are LLM agents
  reading a JSON warning array. — [no canonical URL; standard observation
  about TikZ/pgfplots toolchain]
- The "language without diagnostic" pattern is the inverse of Option B —
  capable surface, no signal. In compiler terms: like having a powerful type
  system with no error messages.

**Pros:**
- Bikar's grammar gains the right primitives; future patterns can express the
  construction.
- The `extend` edit, once authored manually, closes the medallion-10 gap as
  predicted by the plan.

**Cons:**
- **Violates tenet 8 (solve the general problem):** every iteration agent
  has to re-derive the partial-shape opportunity from visual inspection of
  the reference. The detection is the part that generalizes; without it,
  bikar primitives serve only the patterns where a human (or LLM) already
  knew to apply them.
- Loses the iteration-loop's design contract (`overall.warnings[0]` drives
  the next edit). If the warning still says `MISSING`, the agent applies the
  wrong fix; if it says nothing, the gap stays invisible.
- Asymmetric burden: bikar gets the harder change (3-5 days) and gets none
  of the loop signal; qiyas gets the easier change deferred indefinitely.

**Cost:** 3-5 days.

**Closes which questions from §4:** Q4 (strapwork interaction surfaces during
implementation).
**Leaves open which questions:** Q1 partial (DSL shape committed but without
qiyas-side feedback to validate), Q2 (no detector), Q3 (no automated lift
verification).

**Tenet alignment:**
- Tenet 2 (root cause): partial. Fixes one root cause (DSL gap), leaves the
  other (qiyas can't see partial shapes) open.
- Tenet 8 (general problem): no. Solves the BKR-author-instance, leaves the
  iteration-loop class unsolved.

### Option D — Do nothing in code; expand baseline.json with partial-shape entries by hand

**Layman:** keep the baseline.json human-edited contract and add explicit
partial-shape rows ("expect 4 v8-stars at medallion-outline-clipped
positions"). Renderer and detector unchanged.

**What changes:**
- sacred-patterns: input/baseline.json schema gains partial-shape entries;
  human edits the file per pattern.
- qiyas: A6 evaluates partial-shape rows the same as full rows (count
  match) — no semantic change.
- bikar: nothing.

**Web research:**
- This is a manual-encoding workaround. The canonical Islamic-pattern
  literature (Kaplan, Lee/Adams, Bonner) treats partial shapes as a
  *generative* property of the construction, not a hand-listed inventory —
  Kaplan's "boundary segment removal" is an algorithmic step, not a
  hand-edit. Choosing Option D means we deviate from the established
  methodology for purely scope reasons. — [Kaplan PhD §3](https://cs.uwaterloo.ca/~csk/other/phd/kaplan_diss_starpatterns_print.pdf)

**Pros:**
- Zero code change; zero days.
- Unblocks medallion-10 baseline-shape coverage in the short term (the human
  enumerates what's actually in the reference).

**Cons:**
- **Plan §94 explicitly rejects this:** *"Don't expand baseline.json with
  partial-shape entries — it's qiyas's responsibility to discover them at
  encoding time, not the human's responsibility to enumerate by hand."*
- **Tenet 2 violation:** papers over the qiyas-can't-detect and bikar-can't-
  express gaps with manual data entry. The next pattern's partial shapes get
  the same hand-edit; the rot compounds.
- **Tenet 8 violation:** solves only the patterns we've manually annotated.
  Every new construction starts at zero partial-shape support.
- Re-introduces the "human is the source of truth for shape inventory" model
  that the interpret-pattern skill was designed to *replace* (the skill
  bootstraps baseline.json from qiyas encode + image review, not from a hand
  enumeration of shape types).

**Cost:** zero days for medallion-10 in isolation; unbounded as patterns
accumulate.

**Closes which questions from §4:** none — defers all four.
**Leaves open which questions:** all of Q1-Q4.

**Tenet alignment:**
- Tenet 2 (root cause): violates. Manual data entry to compensate for
  language and detector gaps.
- Tenet 7 (don't tune to fit): violates. Every new pattern's hand-edits are
  per-pattern tuning; the algorithm is whatever we typed last.
- Tenet 8 (general problem): violates explicitly. Per-instance, never
  generalizes.

### Option E — Extend bikar `clip` to intersect-then-drop (CGAL Arrangement_2 DCEL semantic)

**Layman:** change the bikar `clip pattern to <boundary>` primitive so that, before dropping faces wholly outside the boundary, it first splits half-edges at every intersection between the pattern's edges and the boundary's edges, materializing the boundary-incident intersection vertices into the face graph. Faces that *straddle* the boundary then become two faces (one inside, one outside); the inside-fragment is preserved; the outside-fragment is dropped. This is what the cascade plan implicitly assumed `clip` would do.

**What changes:**
- bikar: `clip pattern to <boundary>` in evaluator goes from "drop face if centroid outside boundary" to "intersect every half-edge with the boundary's edge ring, split at intersection points, then drop only faces whose centroid is outside." The half-edge graph gains boundary-incident vertices and the face count changes (faces split into inside/outside fragments at the boundary).
- bikar: no new DSL surface; existing `clip` syntax keeps working, semantics tighten.
- sacred-patterns: re-run iter-21-probe's `boundary outline = union(C0, S0..S9)` + `clip pattern to outline` *unchanged* on top of the new semantic and measure. If predicted +composite recovery materializes (≥0.82, ≥iter-19 ceiling), the cascade closes.
- qiyas: no change.

**Presentation — concrete shape:** evaluator pseudocode for `clip pattern to boundary`:
```
# Before (current):
for face in pattern.faces:
    if centroid(face) outside boundary: drop(face)

# After (Option E):
boundary_segments = extract_edges(boundary)
for halfedge in pattern.halfedges:
    for bseg in boundary_segments:
        for pt in intersect(halfedge, bseg):
            split_halfedge(halfedge, pt)  # subdivides face graph at pt
rebuild_faces(pattern)  # face graph now has boundary-incident verts
for face in pattern.faces:
    if centroid(face) outside boundary: drop(face)
```

**Web research:**
- CGAL's `Arrangement_on_surface_2` package is the canonical pattern: every pair of input curves is intersected, and intersection points are materialized as DCEL vertices that subdivide both curves into half-edges. The arrangement *is* the half-edge subdivision; downstream Boolean operations (`difference`, `intersection`) then operate face-level on the subdivided graph. — [CGAL 2D Arrangements](https://doc.cgal.org/latest/Arrangement_on_surface_2/index.html)
- JTS's `Geometry.intersection(other)` follows the same pattern: the topology-graph overlay computes all edge-edge intersections, inserts them as nodes in both geometries' graphs, then computes the result by labeling each resulting face (in / out / on-boundary). The intersection of a pattern with a boundary preserves all interior intersections by construction. — [JTS Topology Suite overlay](https://locationtech.github.io/jts/javadoc/org/locationtech/jts/operation/overlayng/OverlayNG.html)
- Foster et al. (2019) restate the Greiner-Hormann polygon-clipping algorithm with explicit entry/exit labeling and degenerate-intersection handling — the algorithm's first phase inserts all intersection vertices into *both* polygons' circular doubly-linked lists before the clip output is traced. Same shape: intersection vertices first, clip second. — [Foster, Hormann, Popa — "Clipping Simple Polygons with Degenerate Intersections" (2019)](http://www.inf.usi.ch/hormann/papers/Foster.2019.CSP.pdf)

**Pros:**
- Fixes the cascade plan's root assumption (`extend → clip` would close partial-shape gaps) without changing the cascade plan's DSL shape. The plan's `extend + clip` two-step *does* work — once `clip` does what every canonical impl says it should.
- Aligns with three independent canonical references (CGAL, JTS, Greiner-Hormann). Tenet 5.
- Preserves all 4 cascade primitives' user-facing API; no migration for existing patterns.
- Single primitive change, single mechanism to test; small surface area for a substantial semantic improvement.

**Cons:**
- Half-edge subdivision is the trickiest geometry-kernel change in bikar's history; requires careful handling of degenerate intersections (boundary touches a vertex, two collinear edges, etc.). Foster (2019) is 30 pages on degeneracies for a reason.
- May break existing patterns that *rely* on the current "drop wholly outside" semantic (none known, but the audit is real work).
- The full intersection-then-clip is O((m+n) log(m+n)) for m pattern edges and n boundary edges; current is O(faces). Performance regression possible on dense patterns; needs measurement.
- Requires a Tier 0 composition test (`single-petal + extend + clip` with a known-correct expected face graph) per [[cascade-primitive-semantic-composition]] before any composite-target measurement.

**Cost:** 3-5 days (half-edge subdivision implementation + degenerate-intersection cases + Tier 0 fixture + composite re-measurement on iter-22).

**Closes which questions from §4:** Q1 (mirrors CGAL/JTS/Greiner-Hormann), Q3 (the original predicted lift becomes measurable once `clip` does what it semantically should).
**Leaves open which questions:** Q2 (qiyas detector unaffected — already shipped per Option A cascade), Q4 (strapwork interaction unchanged).

**Tenet alignment:**
- Tenet 2 (root cause): yes. The L2-layer failure of Option A was "the clip primitive doesn't preserve intersection geometry"; this option fixes that root.
- Tenet 5 (read existing shape): strongly yes. CGAL + JTS + Greiner-Hormann all converge on this exact mechanism.
- Tenet 7 (don't tune to fit): yes. Doesn't add a threshold or a special case; tightens the primitive's semantic to match its name.
- Tenet 17 (prove the primitive first): requires a Tier 0 composition fixture as part of the slice; with that, satisfied.
- Cross-repo Tenet 7 (the falsification-aware variant): the new option's mechanism was *not* in the original enumeration (L3 was the right diagnosis); this option corrects the enumeration.

### Option F — Add a separate `intersect <pattern> with <boundary>` primitive, leave `clip` alone

**Layman:** instead of changing `clip`, add a new bikar primitive `intersect <pattern> with <boundary>` that does the half-edge subdivision (Greiner-Hormann entry/exit labeling), materializes intersection vertices, and outputs a new pattern with the inner fragments. The cascade idiom becomes `extend → intersect with outline → clip pattern to outline` (or just `extend → intersect with outline`, since `intersect` alone would produce only the inside fragments).

**What changes:**
- bikar: new DSL primitive `intersect <pattern> with <boundary>`. Parser + evaluator + AST. `clip` semantic unchanged.
- sacred-patterns: cascade plan updated to use `intersect` before `clip`, OR replaces `clip` entirely. iter-22 re-renders with new idiom.
- qiyas: no change.

**Presentation — concrete shape:** DSL fragment in `bikar-medallion-10/iterations/22/pattern.bkr`:
```
pattern decagram_full
  boundary outline = union(C0, S0, S1, ..., S9)
  extend connect every 4 on Sk beyond 1.5 .star_arm
  intersect pattern with outline      # NEW: subdivides at boundary, keeps inside fragments
  voids detect
```

**Web research:**
- Greiner-Hormann (1998 / Foster 2019) describes `intersection`, `union`, `difference` as *three separate operators* over the same first-phase intersection-vertex insertion. The decision of which fragments to output is the second-phase labeling, distinct from the geometric subdivision. — [Foster, Hormann, Popa (2019)](http://www.inf.usi.ch/hormann/papers/Foster.2019.CSP.pdf)
- CGAL's `Boolean_set_operations_2` exposes `intersection(P, Q, OutputIterator)` as a first-class function distinct from clipping a picture. The clearer API is per-operation, not "clip-then-figure-out-what-you-meant". — [CGAL Boolean Set-Operations 2D — Intersection](https://doc.cgal.org/latest/Boolean_set_operations_2/group__boolean__intersection.html)
- Counter-precedent: Asymptote bundles "draw beyond + clip to region" into a single `clip(picture, path)` op — the user doesn't distinguish intersection from clipping. This works for diagram code but rots when downstream consumers need the intersection vertices as first-class geometry (which the cascade plan implicitly required). — [Asymptote clip](https://www.cs.rit.edu/doc/asymptote/html/clip.html)

**Pros:**
- Keeps `clip`'s existing semantic intact — no audit of existing patterns needed.
- The new `intersect` primitive has crisp semantics named after its mathematical meaning (intersection of two regions); easier to reason about than re-defined `clip`.
- Aligns with CGAL/JTS API decomposition (intersection is its own first-class operator).
- The cascade plan's original 4-primitive enumeration *did* list `intersect` as the 4th primitive (the "hardest, deferrable"). This option ships it.

**Cons:**
- Adds DSL surface (Tenet 1 cost). Now there are two near-synonymous primitives (`intersect`, `clip`) and the iteration agent has to learn which to apply when. The cascade plan currently can't distinguish them at the warning level.
- Requires the cascade plan's translation table to update: `CLIPPED-MISSING` verdict now maps to `intersect with` or `extend ... intersect with`, not just `extend ... clip`.
- Same Tier 0 composition-test requirement as Option E.
- Same algorithmic complexity (Greiner-Hormann subdivision); same difficulty.

**Cost:** 3-5 days (new primitive parser+evaluator+AST + half-edge subdivision + Tier 0 fixture + composite re-measurement on iter-22).

**Closes which questions from §4:** Q1 (clean CGAL/JTS mapping), Q3 (lift becomes re-measurable on iter-22 with new idiom).
**Leaves open which questions:** Q2, Q4.

**Tenet alignment:**
- Tenet 1 (simplicity): mixed — net +1 DSL primitive, but each primitive has one clean semantic. Tradeoff vs Option E's "change existing primitive's meaning."
- Tenet 2 (root cause): yes.
- Tenet 5 (read existing shape): yes — CGAL/JTS pattern of per-operation primitives.

### Option G — Cascade-process fix: require Tier 0 composition test BEFORE composite-target measurement on any new cascade plan

**Layman:** the falsification's deeper lesson isn't *which* primitive to add — it's that the cascade plan was authored and ACCEPTED 2026-05-07 without ever validating that the proposed primitive composition (`extend + clip`) actually produced the predicted output on a single-petal fixture. Before any composite-target measurement, every cascade plan composing ≥2 DSL primitives ships a Tier 0 fixture demonstrating the composition works as the plan predicts. Process change, not primitive change.

**What changes:**
- sacred-patterns: `present-options` skill gains a new verification checkbox: "every cascade plan composing ≥2 DSL primitives ships a Tier 0 composition fixture demonstrating the composition produces the predicted output." Same shape as bikar Tenet 17.
- bikar: no DSL change.
- qiyas: no change.
- For cascade #106 specifically: author `single-petal + extend + clip` Tier 0 fixture; measure; whichever primitive change (Option E or F) the fixture validates becomes the next pick.

**Presentation — concrete shape:** new checkbox added to `sacred-patterns/.claude/skills/present-options/SKILL.md` §"Verification" block:
```markdown
- [ ] If the picked option composes ≥2 DSL primitives, a Tier 0 composition
      fixture is filed *as part of the slice plan*, validates the composition
      produces the predicted output, and runs before any composite-target
      measurement. (Per cross-repo tenet on cascade primitive semantic
      composition.)
```

**Web research:**
- Property-based testing literature (Hughes, *QuickCheck*; Claessen) consistently shows that compositional correctness must be tested on minimal inputs before complex ones — the shrinking step exists exactly because composite-failure witnesses don't isolate which composition step broke. — [Hughes, *QuickCheck: Lightweight Tools for Random Testing of Haskell Programs* (2000)](https://www.cse.chalmers.se/~rjmh/QuickCheck/manual.html)
- The bikar codebase already has Tenet 17 ("Prove the primitive before composing it — simple cases first, tiers gate higher tiers"). The cascade-plan authoring layer doesn't currently enforce it. This option closes the enforcement gap.
- No canonical precedent for "cascade plans must include composition fixtures" found in literature (this is a sacred-patterns-specific cross-repo workflow). The shape is novel to this codebase but follows the standard property-testing prior art for *what* to test.

**Pros:**
- Addresses the L4 framing layer (cascade-plan author skipped a composition-validity check that should have been mandatory).
- Cheap to add (one checkbox in the skill); high leverage (every future cascade plan benefits).
- Doesn't bind cascade #106's choice between Option E vs Option F — the Tier 0 fixture *informs* the choice.
- Doesn't block on bikar half-edge subdivision work (which is the longest path in E/F).

**Cons:**
- Doesn't *close* cascade #106. The plan still needs Option E or F to actually ship the primitive fix.
- Adds friction to cascade-plan authoring; cascade plans get longer.
- The Tier 0 fixture for `extend + clip` will validate that the current `clip` doesn't preserve intersections (which we already know from the falsification log) — so the fixture's main value is *future* cascade plans, not this one.

**Cost:** 1 day (skill update + cascade #106 Tier 0 fixture authoring + measurement).

**Closes which questions from §4:** none directly for cascade #106; closes a class of future Q3-style questions ("does the prediction hold?") by mandating empirical validation.
**Leaves open which questions:** Q1, Q3 for cascade #106 specifically.

**Tenet alignment:**
- Tenet 7 (don't tune to fit): the cascade plan was tuned to predict lift without proving the composition produced it; this option closes that loophole.
- Tenet 17 (prove the primitive first): operationalizes the tenet at the cascade-plan authoring layer.
- [[cascade-primitive-semantic-composition]] memory: this option *is* the rule that memory predicts as the mandatory companion.

### Option H — Accept iter-19 (0.8236) as medallion-10's permanent ceiling; route cluster work elsewhere

**Layman:** the cascade plan's prediction (+0.05 to +0.10 composite lift) didn't materialize after 2 variant attempts. Conclude that medallion-10's structural mismatch is bounded by primitives bikar doesn't have, and won't have unless we commit to Option E or F's multi-day half-edge work. Mark iter-19 as the ceiling, close the medallion-10 cluster (#80/#85) at "ceiling reached," and route the cluster's effort to other on-path candidates (#129 detector-calibration cascade, #25/#59/#60 A5 band-network, #74/#75/#77 V2 sub-commands).

**What changes:**
- sacred-patterns: medallion-10 README updated with "ceiling: iter-19, composite=0.8236, structural blocked on bikar `intersect` primitive or `clip` semantic change (see #106 decision doc)." #80 and #85 close as "ceiling reached, not converged."
- bikar: no change.
- qiyas: no change.
- Other repos: no change; the cluster's effort is freed for next-highest-leverage on-path work.

**Web research:**
- Engineering practice on "stop iterating, accept the local optimum" is widely documented in optimization literature: when the search-step cost exceeds the marginal improvement-step cost AND no obvious change of search direction is available, accept and move on. The cascade #106 case has 2 falsified variants and the remaining options (E/F) are 3-5 day commitments — the marginal improvement cost is no longer small. — *General principle, no single canonical URL*.
- Counter-precedent: the broader sacred-patterns design philosophy (per CLAUDE.md) is "patterns drive the engine" — when a pattern can't be expressed with current primitives, the resolution is usually to add the primitive, not to drop the pattern. — `sacred-patterns/CLAUDE.md`

**Pros:**
- Zero cost; immediate route to other work.
- Honest about where the system is.
- Doesn't bind bikar to a multi-day primitive change driven by one medallion's needs.

**Cons:**
- **Tenet 8 (general problem) violation:** medallion-10 is one witness of the partial-shape class; accepting the ceiling means every future pattern in this class hits the same ceiling.
- Leaves the cascade #106 doc's predicted +0.05 to +0.10 lift permanently unredeemed; the decision-doc trail records "accepted but didn't deliver."
- The 2026-05-07 cascade plan was authored partly to address medallion-10; accepting the ceiling effectively reverts that plan.
- Future cascade plans authored in the same spirit (predicted lift from a primitive composition) will face the same falsification risk; without Option G, the lesson doesn't propagate.

**Cost:** 0 days.

**Closes which questions from §4:** none — defers them indefinitely.
**Leaves open which questions:** all of Q1-Q4 permanently.

**Tenet alignment:**
- Tenet 8 (general problem): violates. Per-pattern ceiling acceptance.
- Tenet 19 (bias for action): the action is "stop"; defensible only if the stop is grounded in resource constraints, not in giving up.

## Option G — Tier 0/1 fixture empirical findings (filed 2026-05-25 after fixture ran)

The Tier 0 + Tier 1 fixture (`bikar/packages/core/tests/dsl/evaluator-extend-clip-composition.test.ts`, committed bikar 2026-05-25) ran against current main and produced these concrete numbers:

| Test | Construction | Boundary | Result |
|---|---|---|---|
| **TIER 0 baseline** | hex (r=100) `extend connect every 2 beyond 1.5` | none | 7 boundedFaces |
| **TIER 0 inner clip** | same | `union(Cinner r=40)` (boundary inside extension) | **1 face, 0 partials** — star points dropped wholesale |
| **TIER 0 outer clip** | same | `union(Couter r=130)` (boundary between construction and extension) | **13 faces, 12 partials** — boundary-incident inside-fragments preserved as `partial: true` |
| **TIER 1 multi-circle** | same | `union(C0 r=100, Csat at (100,0) r=50)` | **13 faces, 11 partials** — virtually identical to Tier 0 outer; multi-circle UNION works as expected |

**Empirical conclusion — Option E is probably WRONG.** The cascade plan's predicted mechanism (`extend → clip preserves inside fragments via partial annotation`) DOES work at Tier 0 and Tier 1. Both single-circle and multi-circle UNION boundaries correctly produce boundary-incident partial-annotated faces. This is the OPPOSITE of what the L2-introspection of the falsification log hypothesized.

**Where the falsification's root reason actually sits:** the medallion-10 iter-20/iter-21-probe failures (extra-shapes 30→42 severity error, missing-shapes still 36) must therefore be a **Tier 2/3 scale-dependent issue** — likely:
- (i) sliver-polygon culling at 10-fold rotational symmetry (the 10 satellite circles produce sliver polygons at each pairwise intersection that need a post-clip cleanup pass), OR
- (ii) qiyas detector misclassifying boundary-incident partial-annotated faces as `extra-shapes` because the detector wasn't taught to recognize `partial: true` faces, OR
- (iii) the cascade plan's expected `boundedFaces` count for medallion-10 was wrong from the start — partial annotation produces MORE faces than the reference image has, not fewer.

**Implication for Option E vs F vs new options:**
- Options E and F (clip semantic change + new intersect primitive) are likely **NOT needed**; the primitive works as documented at Tier 0/1.
- A NEW option (call it **Option I**) is now indicated: investigate the qiyas detector's handling of `partial: true` faces from bikar SVG output, AND/OR add post-clip sliver-polygon cleanup pass to bikar evaluator.
- Option G's value already realized: the empirical finding here saved 3-5 days that would have been burned on the wrong primitive change.

## Recommendation

**~~Option G + Option E (sequenced: G first, then E informed by G's fixture).~~** Superseded 2026-05-25 by Option G's fixture verdict (see above).

**Updated recommendation 2026-05-25: Option G (already shipped — Tier 0/1 fixture) + investigate Option I (qiyas detector + sliver-polygon cleanup).**

The falsification's introspection (step 3 of handle-falsification skill) checked L2, L3, *and* L4 — the doc was wrong at multiple layers. A single new primitive option (E or F alone) addresses L2 + L3 but not L4 (the cascade-plan author skipped a composition-validity check). Option G addresses L4 directly and is cheap (1 day) and high-leverage (every future cascade plan inherits).

Once G's Tier 0 fixture is authored and run, it will reveal *which* of Option E or Option F (or some other option not yet enumerated) actually closes the partial-shape gap on the simplest witness. The fixture's verdict — "with current `clip`, `single-petal + extend + clip` produces N faces; with intersect-then-drop `clip` it produces N+k boundary-incident fragments; with separate `intersect with` primitive it produces (M, k) as a 2-tuple" — informs E vs F.

Why not just pick E or F now and skip G:
- We already burned 2 variants of cascade #106 by skipping composition validation. Picking E without first running a Tier 0 fixture risks burning a 3rd 3-5 day commitment on the wrong choice.
- G's cost is rounding error (1 day) vs E/F (3-5 days each); paying G first is cheap insurance.
- G makes the E-vs-F decision *empirical* rather than philosophical — we don't have to weigh "should `clip` change semantic vs add a new primitive" abstractly; we can read the fixture.

Why not Option H:
- Tenet 8 — medallion-10 is one witness; every future pattern in the class hits the same wall.
- The falsification doesn't establish that the gap is uncloseable; it establishes that the *current `clip` primitive* doesn't close it. The cascade plan's broader thesis (`extend + boundary-aware operation` closes partial-shape gaps) survives if we get the boundary-aware operation right.

Why not Option B/C/D (re-considered):
- Option B (qiyas-only) and Option C (bikar-only without qiyas) were rejected at decision time on tenet 8 grounds; falsification doesn't change that.
- Option D (manual baseline edits) was rejected at decision time on tenet 2/7/8; falsification reinforces that.

**The sequence:**
1. Ship Option G (skill checkbox + cascade #106 Tier 0 fixture) — 1 day.
2. Read G's fixture verdict; pick E or F (or a not-yet-enumerated option G surfaces).
3. Ship the picked primitive option — 3-5 days.
4. Re-render iter-22 with the cascade plan's *original* `extend + (boundary-aware op)` idiom unchanged at the cascade-plan level (the change is below the DSL, in the evaluator).

The cost (1 + 3-5 = 4-6 days) is comparable to the original Option A estimate (4-7 days), and the work is sequenced so the high-cost work (E/F) is paid only after G validates it's the right work.

~~**Original recommendation (2026-05-07):** Option A — full 3-piece cascade. Superseded 2026-05-25 by 2 variant falsifications; see Falsification log above.~~

Why:
- Q1 has a clean answer: CGAL `Boolean_set_operations_2` is the canonical
  shape for `boundary <name> = union(...)`, and Asymptote's `clip(picture,
  path)` is the canonical shape for `clip pattern to <boundary>`. We're
  mirroring established prior art, not inventing — tenet 5.
- Q3's predicted +0.05 to +0.10 lift is testable post-implementation (#260),
  which makes the cost worthwhile *and* falsifiable — the kind of bet the
  iteration-loop's counterfactual ranking was designed to evaluate.
- Tenet 8 is decisive: medallion-10 is one witness of "patterns with
  internal boundaries that should clip extended construction." Phase 1.B's
  multi-ring corpus (already authored) is the next class member; future
  decagram-strapwork constructions (#115) will inherit. Option B/C/D each
  solve one slice and leave the class open.
- Cost is real (4-7 days, 2 repos) but the alternatives' total cost is
  higher when amortized: Option D is per-pattern hand-edit forever,
  Option B's unactionable warning rots, Option C asymmetrically burdens
  bikar without closing the loop.

The recommendation is *not* unanimous on cost — Option B is faster — but it
is unanimous on tenet alignment and on closing the structural gap. The cost
input is what makes Option B a real alternative if the cascade owner needs
to defer; it shouldn't make Option B the pick if we have the budget.

## What would change this recommendation

**Updated 2026-05-25 after Option A falsification — Option G+E sequenced recommendation:**

- **If Option G's Tier 0 fixture (`single-petal + extend + clip`) reveals that the gap is closed by a primitive choice not yet enumerated** (e.g., a Sutherland-Hodgman boundary subdivision pass before `clip`, or a `region` primitive that wraps both intersect-and-clip) — author that option as Option I and re-evaluate. The fixture is the empirical input that may surface options local reasoning didn't.
- **If Option G's fixture reveals that even the current `clip` primitive *can* produce the right output when called in a different idiom** (e.g., `clip pattern to outline` applied to *each layer separately* before merging) — then the L2 layer of the falsification was wrong; the primitive works, the cascade plan's *use* of it was wrong, and we ship a cascade-plan fix (no bikar changes) plus Option G.
- **If Option E's half-edge subdivision implementation hits intractable degenerate-intersection cases on real medallion geometry** (boundary touches a satellite at a tangent point, two collinear extended arcs share a satellite circle, etc.) — fall back to Option F (separate `intersect with` primitive); its narrower surface is easier to handle one degenerate at a time.
- **If iter-15 strapwork render (or any subsequent iteration's other improvements) closes the medallion-10 gap to ≥0.85 composite via non-partial-shape means** — partial-shape rendering is no longer the dominant remaining mismatch and the cascade-#106 work can be paused (Option H route). Re-evaluate after #114 strapwork lands and the medallion is re-rendered with strapwork PR2.

**(Original 2026-05-07 entries — now subsumed by the falsification log; kept for audit.)**

- **If the iter-15 strapwork render closes the medallion-10 gap to ≥85%
  pixel similarity** — then partial-shape rendering is no longer the
  dominant remaining mismatch and the cascade can be deferred. Re-evaluate
  after iter-15 + iter-16 ship.
- **If the bikar `intersect` primitive proves intractable** (the plan's
  flagged "hardest, deferrable" warning) — drop it from Option A's scope
  and ship 3-of-4 primitives. The medallion-10 inter-satellite case may not
  fully close, but the inter-satellite *partial-shape* case (the dominant
  one) closes with `extend` + `clip` alone.
- **If the qiyas detector can't reliably distinguish partial-polygon-with-
  zone-boundary-endpoints from random open polylines** (Q2 falsifies during
  #256 implementation) — fall back to Option C: ship bikar primitives,
  defer the verdict-rename to qiyas, take the manual-translation cost in
  the iteration-guide as a known gap with a deletion ticket against the
  qiyas detector improvement.
- **If the strapwork PR (#114) lands first and reveals that
  rotation-canonicalization needs `boundary` semantics already**, we may
  ship `boundary` as a stand-alone bikar PR ahead of the rest of Option A,
  refactor strapwork to use it, and keep the rest of the cascade
  sequenced behind. The grammar shape stays the same; only the merge order
  shifts.
- **If the cascade owner declines the cross-repo coordination overhead** —
  ship Option B with a 6-week deletion ticket on the unactionable warning.
  At 6 weeks, either the bikar primitives have shipped (verdict becomes
  actionable, ticket auto-closes) or we revisit and accept Option D's
  manual fallback as the chosen workaround.

## Final decision

**Status: PENDING re-decision (post-falsification).**

**Original decision (2026-05-07) by owner (sacred-patterns):** Option A — full 3-piece cascade. ~~ACCEPTED~~ **SUPERSEDED 2026-05-25 by Falsification log (2 variants falsified)**.

**Proposed re-decision (PENDING owner):** Option G then Option E (sequenced).

**Proposed rationale:**
- Option G addresses the L4 framing failure (cascade plan skipped composition-validity check) — 1 day, high leverage, every future cascade benefits.
- Option G's Tier 0 fixture (`single-petal + extend + clip`) informs the E-vs-F choice empirically.
- Option E (extend `clip` semantic to intersect-then-drop, per CGAL Arrangement_2 / JTS overlay / Greiner-Hormann) is the canonical-mechanism fix per 3 web-search citations; mirrors established prior art (Tenet 5).
- Sequenced cost (1 + 3-5 days) is comparable to original Option A estimate (4-7 days), with the high-cost work paid only after G validates it's correct.

**Proposed follow-ups (implementation):**
- New task: ship Option G — `present-options` skill update + cascade #106 Tier 0 fixture authoring + measurement.
- New task: ship Option E (or F, if G's fixture surfaces F as the right choice) — bikar `clip` semantic change (or `intersect` primitive) + half-edge subdivision + degenerate-intersection handling + Tier 0 composition test green + iter-22 re-render.
- Existing #540 (cascade #106 re-decision authoring) — completed by this doc revision; close on owner re-decision acceptance.

**Proposed follow-ups (conditional / backlog — track triggers, not work):**
- **If Option G's fixture surfaces Option I (not-yet-enumerated):** file task to author Option I block in this doc; defer E/F shipment pending Option I weighting.
- **If iter-15 strapwork closes the medallion-10 gap to ≥0.85 composite via non-partial-shape means:** file task to mark this cascade Option H (pause) and reroute #80/#85 cluster work.

**Original follow-ups (now superseded):**
- ~~#255 (qiyas spec) — unblocked~~
- ~~#257 (bikar spec) — unblocked~~
- ~~#256, #258, #259, #260 — chained downstream per cascade dependencies~~

## Sources

- [CGAL 2D Boolean Set-Operations: User Manual](https://doc.cgal.org/latest/Boolean_set_operations_2/index.html)
- [CGAL 2D Boolean Set-Operations: Union Functions](https://doc.cgal.org/latest/Boolean_set_operations_2/group__boolean__join.html)
- [Asymptote: clip documentation](https://www.cs.rit.edu/doc/asymptote/html/clip.html)
- [Asymptote: Vector Graphics Language tutorial](https://asymptote.sourceforge.io/intro.pdf)
- [Penrose: from mathematical notation to beautiful diagrams (SIGGRAPH 2020)](https://penrose.cs.cmu.edu/siggraph20)
- [Kaplan, C.S. — *Islamic Star Patterns* (PhD §3)](https://cs.uwaterloo.ca/~csk/other/phd/kaplan_diss_starpatterns_print.pdf)
- [Islamic geometric algorithms: A survey (ResearchGate)](https://www.researchgate.net/publication/358999942_Islamic_geometric_algorithms_A_survey)
- [Application-based principles of Islamic geometric patterns (npj Heritage Science)](https://www.nature.com/articles/s40494-022-00852-w)

## Falsification log

### 2026-05-25 — Option A (extend → clip cascade) falsified, both boundary variants

**Witness path:** `Dropbox/Data/sacred-patterns/bikar-medallion-10/iterations/{19,20,21-probe}/`

**What was tried (Variant 1 — iter-20):** Layer `boundary outline = union(C0) + clip pattern to outline` on top of iter-19's validated `extend connect every 4 on @0.k beyond 1.5` (10 satellites). The cascade plan's prediction was composite +0.02 to +0.04 and structural 3-7/18.

**How it failed (Variant 1):** composite 0.8236 → **0.697** (-0.13, vs -0.02 stop limit). Missing-shapes regressed 32 → 39 (severity warn → error). Symmetry-mismatch resurged at cf=0.0958 (the clip drops boundary-incident edges that were carrying the rotational-order distribution). The plan's `union(C0)` boundary spec is incomplete — the medallion silhouette is `union(C0, satellite_circles)` since satellites at distance 1.0·R reach 1.3·R from origin.

**What was tried (Variant 2 — iter-21-probe):** L1 fix on Variant 1's incorrect boundary. The shipped grammar's `parseBoundaryDeclaration` (parser.ts:1898) only accepts `TokenType.Identifier` in `union(...)`, NOT `@N.k` repeat-addresses, so the satellite `repeat at C0 depth 1` block was refactored into 10 explicit named circles `S0..S9` to make `boundary outline = union(C0, S0, S1, ..., S9)` expressible.

**How it failed (Variant 2):** composite 0.8236 → **0.7947** (-0.029, still over -0.02 stop limit). Partial recovery from Variant 1 (+0.097) confirms the boundary spec was *part* of the issue, but extra-shapes regressed 30 → 42 with severity escalating to **error**, and missing-shapes still at 36 (severity error). Structural still 0/18.

**Root reason (current best understanding):** The `clip pattern to outline` primitive creates **sliver polygons** at the medallion boundary — extension arcs reach beyond the silhouette but the clip leaves tiny boundary-incident fragments rather than dropping them cleanly. Worse, the clip drops faces *wholly* outside the boundary before they can intersect inner-star/rosette geometry, so the partial-shape intersection that the cascade plan predicted (extension tips merging into satellite-adjacent partial polygons) never happens. The cascade plan modeled `extend → clip` as a clean two-step but the actual mechanism is `extend → drop-outside-faces`, missing the `intersect-then-clip` step the plan implicitly required.

**What this falsifies in the doc:**
- [ ] L1 — The picked option's mechanism (no implementation bug found; bikar's `clip` primitive works as documented, the doc's *use* of it was wrong)
- [x] L2 — The picked option itself (`extend + clip` as a two-step is mechanically incomplete; needs `intersect` before clipping OR a different clip semantic that preserves intersection geometry)
- [x] L3 — The option enumeration (the doc considered `extend`, `boundary`, `clip pattern`, `intersect` as 4 separable primitives but didn't enumerate the option where `clip` semantically *includes* intersection-with-inner-geometry-before-drop)
- [x] L4 — The audit / impact analysis (the cascade plan's "predicted +0.05 to +0.10" came from modeling extension geometry as if it would close the partial-shape gap merely by being trimmed; the plan didn't validate that clip semantics preserve the intersections it relied on)

**Falsification artifacts:**
- `bikar-medallion-10/iterations/20/pattern.bkr` (Variant 1 source)
- `bikar-medallion-10/iterations/20/evaluation.md` (Variant 1 verdict)
- `bikar-medallion-10/iterations/21-probe/pattern.bkr` (Variant 2 source)
- `bikar-medallion-10/iterations/21-probe/evaluation.md` (Variant 2 verdict)
- Bikar grammar gap: `parser.ts:1898` `parseBoundaryDeclaration` rejects `@N.k` syntax (forced Variant 2 refactor)
- Witness invariants codified as: TBD (filed as follow-on task — needs a single-primitive fixture demonstrating `extend → clip` slipver-polygon mechanism; deferred for follow-on slice scaffolding)

**Tenet 7 stop rule:** Two variants of cascade #106 clip primitive falsified. Do not author Variant 3 without first running full L2/L3/L4 introspection, fresh web-search of canonical clip-and-intersect implementations (CGAL Arrangement_2 with do_intersect predicates, JTS difference/intersection semantics, Asymptote `clip` vs `intersection`), and authoring new options that surface the `intersect-before-clip` mechanism the cascade plan missed.

**Next directive — local pickup paused per §F mechanical critical-path check:** iter-19 remains the medallion-10 ceiling at composite=0.8236. Pickup a different on-path task (autonomous loop will route per `qiyas/.claude/plans/post-i1-task-routing.md` §A/§C). The cascade re-decision (new Option E / F authoring + fresh web-search) is the next decision-doc work item once falsification protocol's remaining steps (web-search per skill, new option(s), cross-repo memory) are scheduled.
