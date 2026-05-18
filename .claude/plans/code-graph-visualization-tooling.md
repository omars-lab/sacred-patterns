# Code-graph visualization tooling — design micro-check

## Question

User asked 2026-05-18: *"should we be using something like graphipfy [sic] to
track what we've implemented, how things connect, what we test for each method,
etc, to make our debugging process more effective?"*

The user is naming a real failure mode — repeated debugging sessions where the
agent can't quickly answer "what calls this function?", "what tests cover
it?", "is there already something that does X?". The question is whether
*tooling* is the right lever for that failure mode, or whether convention +
existing infra already covers it.

## What "Graphify" probably means

"Graphify" isn't a recognizable product. The user likely means one of:

- A code-graph visualizer (call graphs, dependency graphs, type-to-test maps)
- A LSP-driven indexer (Sourcegraph, Glean, Stack Graphs)
- A custom AST-walk that builds a hyperlinked map of the codebase

The category is *code intelligence tooling*. Treat the user question as "should
we adopt code intelligence beyond what we have?"

## What we already have

Surveyed 2026-05-18:

| Repo            | Tool             | What it shows                                | Status                    |
|-----------------|------------------|----------------------------------------------|---------------------------|
| bikar           | madge 8.0.0      | Module import graph + circular-dep detection | Wired into `pnpm import-graph` (per #349) |
| bikar           | knip             | Unused exports                                | Wired (per #348)          |
| qiyas           | vulture          | Dead code                                    | Wired (per #348)          |
| qiyas           | ruff C901        | Cyclomatic complexity                        | Wired (per #348)          |
| qiyas + bikar   | import-linter    | Layered architecture contracts                | Queued #391 — not shipped |
| qiyas + bikar   | codespell        | Spell-check identifiers                      | Wired (per #349)          |
| sacred-patterns | madge (TS)       | Module import graph                          | Wired (per #349)          |
| all             | pytest-cov / vitest coverage | Line/branch coverage                | Wired (per #343 queued/done) |

**What we DON'T have:**

- Function-level call graph (only module-level via madge)
- Test-to-method mapping (only line-coverage; doesn't tell you "which test
  exercises function X")
- Cross-repo dependency visualization (each repo's madge is local)
- Symbol-level "find references" beyond editor/LSP (transient, not artifacted)

## Concrete debug failures from the recent record

Picking real cases from the last ~30 days where a different debug experience
would have helped, and asking: *would code-graph tooling actually have
prevented or accelerated this?*

### Case 1 — bikar#333 source-tag-path discovery (2026-05-18)

What happened: Option E implementation surfaced an unexpected interaction
with `assignSourceTagClasses` after-the-fact, not at decision-doc time.

Would a tool have helped? **Yes, marginally.** A function-level call graph
showing the three callers of `face.sources` (`assignSourceTagClasses`,
`applyArcRegionClasses`, and `assignSelectorClasses`) all writing to
`faceClasses` would have made the three-path structure visible without
having to read 2000 lines of evaluator.ts. But: the bug was structural
(the third path interacts with class tags via source-tag inheritance) —
the *call graph* shows the paths but doesn't show that one of them
inherits class tags through edge-source plumbing. So the tool would have
shortened the discovery time, not prevented the bug.

**Verdict:** call-graph would have saved ~30 min of code reading.

### Case 2 — Tenet 11 violation cascade (iter-1 to iter-15)

What happened: `validate_detector` shipped in iter-1, but iters 2-15
shipped parallel ARI cross-check scripts that measured different things;
the macro-fidelity contract rotted silently because nothing surfaced
that `validate_detector`'s downstream callers had quietly stopped using
it for the load-bearing metric.

Would a tool have helped? **Yes, significantly.** A call-graph diff between
"who depends on `validate_detector`" at iter-1 vs iter-15 would have
shown the fan-out collapse loudly. import-linter contracts (queued #391)
would catch this if we authored a contract like "calibration scripts
must call validate-detector, not bespoke ARI computations" — but only if
someone *thought* to author the contract. A passive call-graph would
have surfaced the drift without that authoring step.

**Verdict:** call-graph + diff would have caught this much earlier. This
is the *highest-leverage* use case in the recent record.

### Case 3 — Tenet 5 violations (read existing shape before adding new)

What happened: multiple cases where a new helper got added when an
existing one would have served — e.g., `_param_int` / `_param_float`
in qiyas (closed by #366), the duplicate edge-key logic in bikar
gt-emitter (closed by #197).

Would a tool have helped? **Marginally.** A symbol-search-with-similarity
("functions in this codebase that take `dict[str, object]` and an
integer-typed key") would catch some, but most of these are caught by
the *agent's own search* when it follows tenet 5. The tool would lower
the threshold for searching — make "is there already something like
this?" a cheap query instead of a multi-grep deliberation.

**Verdict:** search-quality improvement, not graph-tooling per se.

### Case 4 — Test-to-method coverage (the actual user question)

What happened: when a function breaks, the agent currently has to grep
for tests that import the module, then read each test to figure out
which exercises the specific function. The user's question targeted
exactly this: "what tests cover this method?"

Would a tool have helped? **Yes, directly.** `pytest --collect-only` plus
coverage.py's per-test-line data can produce a JSON map "function X is
exercised by tests A, B, C." This is reachable from existing infra
(pytest-cov, already wired per #343) — needs a small post-processing
script, not new tooling.

**Verdict:** existing infra + 50-line post-processor would close this.

## Options considered

### Option A — adopt a heavier symbol-level indexer (Sourcegraph local, ts-graph, pyan)

**What:** stand up a daemon (Sourcegraph srcgraph CLI, ts-graph as a
build artifact, pyan3 as a one-shot) that produces a clickable HTML
call graph per repo, regenerated in CI.

**Pros:**
- Best UX for "find references", "who calls this", "what's the type
  of this expression"
- Cross-repo if we set up a single Sourcegraph instance

**Cons:**
- Sourcegraph local is heavyweight (Docker, ~2GB image, scheduled
  index runs) — overkill for a 3-repo monorepo-equivalent
- pyan3 / ts-graph are static — no live "find references"; just produce
  graphs the agent has to read
- Adoption cost: new infra to learn, new failure mode (stale index)
- Doesn't address case 2 (call-graph diff over time) without custom
  scripting

**Cost:** 2-3 days standup + ongoing maintenance

### Option B — extend existing madge / vulture / coverage to produce one rolled-up "code health" artifact per repo

**What:** small Makefile target `make code-graph` in each repo that:

1. Runs `madge --json` (TS) or `pydeps --json` (Python) for module graph
2. Runs `pytest --collect-only --quiet` + coverage.py JSON to build
   test-to-function map
3. Runs `vulture` / `knip` to surface dead code
4. Emits a single `code-graph.json` to `docs/generated/code-graph.json`
   that the agent can grep for "callers of X" / "tests for Y"

**Pros:**
- Uses 100% existing tooling — no new dependencies
- Closes Case 4 directly (test-to-function map)
- Closes Case 2 partially (diffable artifact in git history; can
  compare two commits' code-graph.json)
- Each repo can adopt independently; no cross-repo coordination
- Output is plain JSON — agent-readable without HTML/UI tooling

**Cons:**
- Closes Case 1 only weakly (module-level, not function-level call
  graph)
- Test-to-function map for Python needs coverage.py's `--contexts`
  flag (light extra setup but standard)
- Function-level call graph for TypeScript would still need
  ts-graph or similar — bikar/sacred-patterns half-solution

**Cost:** ~half day per repo, three repos = ~1.5 days total

### Option C — function-level call graphs via dedicated AST tools (pyan + ts-graph)

**What:** add `pyan3` (Python) and `ts-call-graph` or `arkit`
(TypeScript) as Tier 3 build artifacts. Generate dot/graphml output;
keep latest in `docs/generated/` for the agent to read.

**Pros:**
- Closes Case 1 directly (function-level call graph would have shown
  the three paths into `faceClasses`)
- Closes Case 2 fully (diff two commits' call graphs)
- Pure AST analysis — no runtime hooks needed

**Cons:**
- pyan3 is unmaintained (last release 2019); `code2flow` is the active
  alternative but produces only single-function neighborhoods, not
  whole-graph
- TS function-level call graphs are notoriously unreliable for dynamic
  dispatch / higher-order patterns common in our code
- Adds two new dependencies whose output quality varies — may be
  noisy
- Doesn't help Case 4 (test-to-method) — that's coverage data, not
  call-graph data

**Cost:** 1 day standup + ongoing maintenance burden

### Option D — defer; current grep + LSP is sufficient

**What:** do nothing. Continue relying on Read+Grep+agent's working
memory. Document the failure modes (Cases 1, 2, 4) and revisit if they
keep recurring.

**Pros:**
- Zero adoption cost
- Honors Tenet 1 (simplicity) — don't add infra unless need is proven

**Cons:**
- Case 2 (Tenet 11 drift) is a recurring failure mode; deferring means
  next cascade will repeat it
- Case 4 (test-to-method) is the user's actual question; deferring
  signals we read it as rhetorical, not a real ask
- The cost of *one* future cascade that a code-graph would have caught
  is plausibly >> the cost of Option B

**Cost:** 0 now; pay-later in future debug sessions

## Recommendation

**Option B** — extend existing tooling to produce a per-repo
`code-graph.json` artifact, regenerated by a Makefile target and
committed to `docs/generated/`. Ship per-repo independently. Defer
Option C (function-level call graphs) until we hit a debug case where
Option B's module-level graph + test-to-function map proves
insufficient.

Reasoning:

1. **Closes the user's actual question (Case 4)** — the
   test-to-function map is the most useful single artifact, and
   pytest-cov / vitest coverage already produce the underlying data.
2. **Addresses the highest-leverage debug failure (Case 2)** —
   diffable git-tracked `code-graph.json` makes Tenet 11 drift visible
   over commits without per-cascade vigilance.
3. **Reuses existing infra** — no new dependencies, no new failure
   modes. Honors Tenet 1.
4. **Defers function-level call graphs (Option C)** until proven
   needed. Tenet 1 says don't build for hypothetical futures; if Case
   1 keeps biting at the function level, we revisit C with concrete
   evidence.
5. **Rejects Option A** as overkill — Sourcegraph for 3 repos is the
   wrong leverage point. **Rejects Option D** because Case 4 is a real
   user ask and Case 2 is a recurring pattern.

## What would change this recommendation

- If Case 1 (the bikar#333 type of function-level interaction
  discovery) happens again within 30 days with material cost, escalate
  to Option C for the affected repo.
- If `code-graph.json` ends up >10MB or noisy enough to be unreadable
  by the agent, scope it down or switch to query-on-demand instead of
  artifacted.
- If a real cross-repo dependency visualization becomes load-bearing
  (e.g., when implementing #69's cross-repo task linkage at scale),
  revisit Option A for the cross-repo angle only.

## Implementation slices (if Option B is approved)

Filed as follow-on tasks only after owner ack:

1. **Slice 1** — qiyas: `make code-graph` target producing
   `docs/generated/code-graph.json` with module dependencies (pydeps),
   test-to-function map (pytest --collect-only + coverage.py contexts),
   dead-code list (vulture).
2. **Slice 2** — bikar: same target producing the TS equivalent
   (madge --json, vitest coverage --reporter=json, knip).
3. **Slice 3** — sacred-patterns: same (madge --json, no test suite to
   speak of yet so test-to-function map is empty/deferred).
4. **Slice 4** — CI gate: regenerate-and-diff `code-graph.json` on PRs;
   surface the diff in the PR description automatically. *Defer* until
   Slices 1-3 prove the artifact is useful in practice (≥1 cascade
   where the agent consults `code-graph.json` and gains a debug
   win).
5. **Slice 5** — agent skill update: add a 1-line note to qiyas + bikar
   CLAUDE.md "Read `docs/generated/code-graph.json` before grep for
   call-graph or test-coverage queries."

## Open items

- The pydeps / coverage / madge invocations need verification on each
  repo before committing to the exact CLI. Slice 1's first hour is a
  smoke check.
- pytest's `--contexts` flag for per-test-function attribution requires
  coverage.py 5.0+; verify qiyas's `[tool.coverage]` config supports
  it.
- The test-to-function map is per-source-file granularity by default;
  per-function granularity needs a coverage plugin or AST
  post-processing. Defer the per-function precision to a separate
  decision once the per-file version is in hand.
