# Build-time code validation cascade

## Status

**PROPOSED** 2026-05-16 by Claude (loop sweep + owner directive).

Parent task: **qiyas#342**. Slice tasks: **qiyas#335 (mypy)**, **#338–#341 (mypy slices + docstrings)**, **#343–#352 (tier 1–5)**.

Cross-repo: identical plan applies to sacred-patterns and bikar; sibling copies
live at `sacred-patterns/.claude/plans/build-time-validation-cascade.md` and
`bikar/.claude/plans/build-time-validation-cascade.md` (mirror this doc when
adopted).

## Layman summary

Every defect class that *can* be caught before runtime *should* be caught
before runtime, via a CI-blocking gate. Today qiyas's toolchain catches
maybe 30% of the catchable surface — ruff for some style/lint, pytest for
runtime. The rest (type errors, security issues, dead code, missing docs,
property violations, secrets, CVEs) ships silently. This plan tiers the
remaining work by yield-per-hour so we ship the highest-leverage gates
first.

## Implications of getting this wrong

- **Silent defects compound across the iteration loop.** A type error
  that mypy would catch in 30s gets caught in iter-N+5 via a confusing
  validation failure that costs an hour to debug.
- **Per-PR friction stays high without pre-commit hooks.** Reviewers
  catch what should be linters' job.
- **Secret leakage is non-recoverable.** A single committed API token
  invalidates the credential and (depending on what it accessed) costs
  real money. Even after revocation, the token is in git history forever.

## Main questions we need answered

1. **Will strict-mypy land in one shipment or per-module?** — Decided in
   #338/#339 sub-slicing: per-module, starting with a baseline that
   doesn't immediately green (150 errors). Per tenet 2 (no fallback),
   each `[[tool.mypy.overrides]]` relaxation needs a WHY-comment.
2. **What's the docstring coverage starting point and target?** — 59
   missing docstrings on public APIs today (24 classes, 17 functions,
   13 methods, etc.). Target: 100% on public APIs, enforced by ruff
   D101–D107.
3. **Does property-based testing actually catch geometry defects in
   our codebase?** — High prior YES (the memory cites a 30-second
   property-test catch of the F1 turning-function bug). To answer:
   ship #350 slice 1 (one property test on `rotate(p, θ)` invariants)
   and measure how long until it surfaces a real defect.
4. **What's the maintenance cost of mutation testing?** — Unknown.
   Quarterly cadence (#351) is the hypothesis; revisit after first
   quarterly run.

## The tiered plan

Tiers are ordered by **defect-yield per engineering hour**, not
alphabetically. Each tier is a single coordinated shipment across all
three repos (per tenet 11 — no parallel tool paths diverging across
repos).

### Tier 1 — foundational

Highest yield, lowest cost. Already-installed dependencies or trivial
adds.

**Web research:**
- Defects caught in design vs. production: industry consensus is the
  later you catch a defect, the more it costs to fix — figures range
  from "15× during testing" to "100× post-deployment." The widely-cited
  1×→100× ratio originates from IBM training materials and has thin
  primary data, but NIST and Capers Jones' analysis of 12,000+ projects
  support the directional claim. [Cost of software defects (Perforce / IBM SSI)](https://www.perforce.com/blog/pdx/cost-of-software-defects), [NASA error cost escalation](https://ntrs.nasa.gov/api/citations/20100036670/downloads/20100036670.pdf).
- mypy strict adoption: ~65% of Fortune 500 Python teams have adopted
  strict mode for ML/edge apps by 2026; reports cite 60–80% reductions
  in runtime errors. Two-tier (strict per-module + lenient legacy)
  adoption is the dominant migration pattern — exactly the slicing
  approach #338/#339 use. [Eightfold: zero to type-safe](https://eightfold.ai/engineering-blog/static-type-checking-large-scale-python-codebase/), [pydevtools mypy strict guide](https://pydevtools.com/handbook/how-to/how-to-configure-mypy-strict-mode/).

| Workstream | Python (qiyas) | TypeScript (bikar / sp) | Task |
|---|---|---|---|
| Strict type checking | mypy --strict | tsc --strict | #335 |
| Docstring coverage | ruff D101–D107 | eslint-plugin-jsdoc | #341 |
| Coverage gate | pytest-cov --fail-under | vitest --coverage thresholds | #343 |
| Pre-commit hooks | pre-commit framework | husky + lint-staged | #344 |

**Decision:** Tier 1 lands first because it has zero new tooling cost
(everything is install-and-configure) and the highest defect yield.

**Open in Tier 1:** the mypy strict baseline at qiyas is 150 errors in
48 files. Slice #339 will work module-by-module; some modules likely
need per-module overrides with follow-on tickets per tenet 2.

### Tier 2 — security & supply chain

High yield, low-medium cost. These are the gates that prevent
non-recoverable mistakes (leaked secrets, shipped CVEs).

**Web research:**
- gitleaks matches/exceeds Snyk's secret-detection accuracy on common
  credential types in 2026 benchmarks; runs in under a second on
  modest diffs; pre-commit hook integration blocks commits *before*
  push so secrets never reach the remote. Trade-off: higher
  false-positive rate than GitGuardian without custom tuning — manage
  via allowlists. [gitleaks repo](https://github.com/gitleaks/gitleaks), [secrets-scanners comparison 2026 (NomadX)](https://devsecops.ae/secrets-scanners-comparison-2026/).

| Workstream | Tool | Task |
|---|---|---|
| Secret scanning | gitleaks (pre-commit + CI) | #345 |
| Dependency CVEs | pip-audit (qiyas) / npm audit (bikar+sp) | #346 |
| SAST | semgrep (cross-repo) + bandit (qiyas) | #347 |

**Decision:** Tier 2 ships second because the *cost* of a Tier-2-class
mistake (committed credential) is catastrophic and non-recoverable, even
though the *probability* per-PR is low. Cheap insurance.

### Tier 3 — codebase health

Medium yield, low cost. These reduce friction over time but don't
prevent acute failures.

| Workstream | Python | TypeScript | Task |
|---|---|---|---|
| Dead code | vulture | ts-prune / knip | #348 |
| Complexity threshold | ruff C901 | eslint complexity | #348 |
| Import graph | import-linter | madge --circular | #349 |
| Spell-check | codespell | cspell | #349 |

**Decision:** Tier 3 after Tier 2. Codebase health is a tenet-5 enabler
(reading existing shape before adding new) — it pays off when iterating,
not all at once.

### Tier 4 — geometry-specific (HIGH leverage in our domain)

The single highest-leverage addition for our codebase given how
geometry-dense it is.

| Workstream | Python | TypeScript | Task |
|---|---|---|---|
| Property-based testing | hypothesis | fast-check | #350 |
| Mutation testing (quarterly) | mutmut | stryker | #351 |

**Rationale for prioritizing #350 even though it's "Tier 4":** the
memory `feedback_canonical_algo_web_search.md` describes a 30-second
hypothesis test that would have caught the F1 turning-function index
flip. Memory `feedback_geometric_test_asymmetric_witnesses.md` names
the systematic version: every geometric invariant test must include a
scalene/irregular witness. Property-based testing is the canonical
implementation of that rule.

**Web research:**
- Anthropic's red-team work (Jan 2026): an AI agent was set loose with
  hypothesis on 100+ popular Python packages spanning numerical
  computing, parsing, and databases. Of 984 bug reports generated, 56%
  of a 50-bug sample were confirmed real bugs in production libraries.
  This is the strongest available external evidence that hypothesis
  catches real defects in mature numerical/scientific Python code —
  exactly the domain qiyas occupies. [Anthropic: property-based testing with Claude](https://red.anthropic.com/2026/property-based-testing/), [hypothesis repo](https://github.com/hypothesisworks/hypothesis).
- Czumaj & Sohler's "Property Testing in Computational Geometry" line
  of work establishes the theoretical basis: geometric invariants
  (distance preservation, area invariance under isometry, polygon
  vertex-edge counts) are testable in sublinear time. The pragmatic
  upshot for us: property-based testing is the *correct* tool for
  geometry, not just a generic Python testing tool. [Property testing in computational geometry (NJIT)](https://digitalcommons.njit.edu/fac_pubs/15781/), [Springer chapter](https://link.springer.com/chapter/10.1007/3-540-45253-2_15).
- Mutmut/CI integration: in a 2024–2025 IEEE Software benchmark mutmut
  improved fault detection by 35% over coverage-only testing; CI
  overhead ~5 min/PR vs PIT's 12 min. Recommended cadence: weekly,
  applied selectively to high-value modules (10–20% of codebase) —
  which matches our "quarterly on detector/scoring core" framing in
  #351. [mutmut on PyPI](https://pypi.org/project/mutmut/), [Mutmut HN discussion](https://news.ycombinator.com/item?id=44087757), [mutation testing cost/benefit 2026](https://johal.in/mutation-testing-with-mutmut-python-for-code-reliability-2026/).

**Direct ties to existing tenets:**
- Tenet 7 (don't tune to fit): properties exercise the algorithm against
  thousands of inputs, not the one fixture you wrote it against.
- Tenet 8 (general problem): properties phrase invariants in terms of
  the class of valid inputs, not specific witnesses.
- Tenet 4 (verify before claiming done): coverage isn't proof of test
  quality; mutation testing measures whether tests actually exercise
  the code.

**Decision:** Ship #350 slice 1 in parallel with Tier 1 work (it's
independent) — even though it's "Tier 4" in cost-ordered terms, it's
Tier 1 in expected defect catch for our domain.

### Tier 5 — supply-chain hygiene (deferred)

Low immediate yield. Only relevant when projects ship to external
consumers at scale.

| Workstream | Tool | Task |
|---|---|---|
| SBOM generation | syft / cyclonedx | #352 |
| License compliance | pip-licenses / license-checker | #352 |

**Decision:** Deferred. qiyas is `Private :: Do Not Upload`,
sacred-patterns is an art site, bikar is research. Revisit when any of
the three opens an external pipeline. Track as a watch-task, not active
work.

## Cross-repo tenet to author

To be added to all three CLAUDE.md files (per task #337):

> **Tenet N: Catchable defects must be caught at build time, not
> runtime.** Every defect class that has a build-time gate available
> (type errors, missing docstrings, security smells, dead code, secret
> leakage, vulnerable dependencies, complexity blowups) must be guarded
> by a CI-blocking gate. Runtime is reserved for genuinely runtime
> failures (network, I/O, user input). Silent acceptance of a catchable
> defect is the same anti-pattern as silent fallback (tenet 2) and
> silent degradation (tenet 3). **Stop rule:** before any new
> dependency, scanner, or tool category lands, name the defect class it
> catches and the CI gate it enforces. If you can't name both, you're
> shipping decoration, not protection.

Cross-link: see sacred-patterns tenet 10 (FP paradigm), bikar tenet 13
(FP), qiyas (new). Type checking + property testing + immutable data
are the same defense in three forms — surface defects early, before
they become silent.

## Doc relocations

After Tier 1 lands and the cross-repo tenet is authored, the
language-specific implementation details (mypy config rationale,
docstring style rules, pre-commit hook lists) should live in each
repo's own CLAUDE.md or `docs/` — this plan stays canonical for the
*strategy* (tiers, sequencing, rationale), not the per-repo
configuration.

## What would change this plan

- If Tier 1 reveals the strict-mypy baseline is much larger than 150
  errors (e.g., expanding to 500+ once per-module overrides are
  removed), revise #339 into a longer-running per-module cascade rather
  than a single shipment.
- If property-based testing #350 slice 1 catches zero defects in the
  first month, downgrade Tier 4 from "ship in parallel" to "ship after
  Tier 3."
- If the owner adopts a different language at any repo (Rust for
  bikar/core, etc.), the tier table needs a new column.

## Decision

**PENDING owner review.** Tasks already filed and can be worked
sequentially as written. The cross-repo tenet wording in particular
should be reviewed before landing in CLAUDE.md files (#337 covers).

## Follow-ups

- All sub-tasks: #335 (in progress), #338–#341, #343–#352.
- Parent: #342.
- Cross-repo tenet edit: #337.

## Sources

- [The Real Cost of Software Defects (Perforce / IBM SSI)](https://www.perforce.com/blog/pdx/cost-of-software-defects)
- [NASA Johnson Space Center — Error Cost Escalation](https://ntrs.nasa.gov/api/citations/20100036670/downloads/20100036670.pdf)
- [Eightfold — Zero to type-safe with mypy on a large Python codebase](https://eightfold.ai/engineering-blog/static-type-checking-large-scale-python-codebase/)
- [pydevtools — How to configure mypy strict mode](https://pydevtools.com/handbook/how-to/how-to-configure-mypy-strict-mode/)
- [Migrating a Python Codebase to Full Type Safety (Markaicode)](https://markaicode.com/python-type-safety-migration/)
- [gitleaks (GitHub)](https://github.com/gitleaks/gitleaks)
- [Secrets scanners comparison 2026 (NomadX/DevSecOps)](https://devsecops.ae/secrets-scanners-comparison-2026/)
- [Anthropic — Property-Based Testing with Claude](https://red.anthropic.com/2026/property-based-testing/)
- [hypothesis (HypothesisWorks/hypothesis GitHub)](https://github.com/hypothesisworks/hypothesis)
- [Czumaj & Sohler — Property Testing in Computational Geometry (NJIT)](https://digitalcommons.njit.edu/fac_pubs/15781/)
- [Springer — Property Testing in Computational Geometry](https://link.springer.com/chapter/10.1007/3-540-45253-2_15)
- [mutmut on PyPI](https://pypi.org/project/mutmut/)
- [Mutmut Python Mutation Tester — Hacker News discussion](https://news.ycombinator.com/item?id=44087757)
- [Mutation Testing with Mutmut 2026 cost/benefit](https://johal.in/mutation-testing-with-mutmut-python-for-code-reliability-2026/)
