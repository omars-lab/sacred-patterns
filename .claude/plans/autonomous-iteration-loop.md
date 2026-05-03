# Autonomous iteration loop — driving sacred-patterns + qiyas to convergence without a human

## What we're building

A skill (or thin orchestrator) that takes a `learn-new-pattern` session
already initialized — `input/reference.jpg`, `input/baseline.json`,
`iterations/N/pattern.bkr` (the seed) — and runs the iteration cycle
**autonomously** until one of three terminal states:

1. **`go_no_go == "converged"`** — composite ≥ 0.85, structural N == M,
   topology complete, pixel ≥ 80. Success.
2. **Stagnation** — 3 consecutive iterations where `composite_score`
   doesn't improve by ≥ ε (e.g. 0.005). Hand back to a human with a
   diagnosis report.
3. **Budget exhaustion** — N iterations (default 30, configurable). Same
   hand-back.

Each cycle is the existing iteration discipline (render → orchestrator
→ read `warnings[0]` → edit DSL) but with the *agent's role* automated:
the loop is just code calling skills, not a human reading retrospectives
between iterations.

This is what the design has been pointing at all along — the iteration
agent reads `warnings[0]`, qiyas already ranked it, the
`counterfactual_rationale` already prescribes the fix, the BIKAR
`iterate-pattern-from-qiyas-warnings` skill already encodes the
warning→DSL-edit translation table. The human in the loop today is a
process-discipline overseer (gates, deliverables, sanity check), not a
creative contributor. **If the design holds, the loop should converge
without the human.**

## Why this is the right test

Tenet 1 says don't build speculatively. This isn't speculative —
it's the natural verification of the entire qiyas + iteration design.
The design's promise is "warnings rank by score lift; agent translates
warning→edit; convergence happens." We've never run the loop end-to-end
without human steering. Running it autonomously is the experiment that
proves whether the design works.

Tenet 4 says verify before claiming done. The design has been *claimed*
done since the catch-22 unblock. Autonomous convergence is the
verification.

When this works: every new pattern is a one-shot session. When it
doesn't: the failure modes tell us exactly which V2.* items (#74 iter-
analyze, #75 net-delta optimizer, #76 construction hints) are actually
load-bearing vs nice-to-have. **This is the calibration data #75 has
been waiting for.**

## What already exists (don't rebuild)

This is a thin orchestration on top of skills that already work. The
load-bearing pieces are all in place:

- `sacred-patterns/tools/iteration-validate.sh` — render → orchestrator
  → `validation.json` with populated `overall.warnings[0]` (verified
  against bikar-medallion-10 iter 11 fixture on 2026-05-02).
- `bikar/.claude/skills/iterate-pattern-from-qiyas-warnings/SKILL.md` —
  the warning-id → DSL-edit translation table, with worked examples.
  This skill is the *contents* of one cycle's edit step.
- `bikar/packages/core` — `compileDSL(bkr) → svg` is a single function
  call from Node, no human or browser in the path.
- `qiyas baseline emit` — auto-emits `baseline.json` when human-verified
  isn't available. Lets us bootstrap a session from just `reference.jpg`.

What's missing is the **driver** that runs all of these in a loop with
a stop condition.

## Where it lives

**Sacred-patterns side, as a new skill:** `.claude/skills/auto-iterate/`.

Reasons:
- The session lives in sacred-patterns Dropbox tree (`session-name/`).
- The orchestrator is sacred-patterns's tool; the *contract*
  (`validation.json`) is sacred-patterns's contract.
- The hard gates G1-G5 are sacred-patterns's gates and the loop must
  enforce them.
- The BIKAR side already has the per-iteration edit skill — that's the
  right division of labor (sacred-patterns owns the loop, BIKAR owns the
  edit translation when the pattern is in BIKAR DSL).

It's invoked as a sibling to `learn-new-pattern`, not nested inside it,
because:
- `learn-new-pattern` is a *human-driven* workflow with conversational
  steps (Step 1 init, Step 2 zone analysis, Step 1.5 interpret-pattern
  human review).
- `auto-iterate` is a *post-init* autonomous driver. It assumes the
  session is already initialized and starts at iter N+1.
- Trying to fold autonomy into `learn-new-pattern` would force every
  human step to have an "auto-mode bypass" branch — that's the
  defensive-code antipattern (tenet 2/3).

The user can run either:
- `learn-new-pattern` end-to-end (manual, exploratory, learning)
- `learn-new-pattern` for init/baseline only, then hand to
  `auto-iterate` (one-shot generation)

## The skill's contract

### Input

A session directory satisfying the existing `learn-new-pattern`
post-Step-1.5 invariants:

```
session-name/
  input/
    reference.jpg               # required
    baseline.json               # required (from interpret-pattern OR qiyas baseline emit)
    pattern-config.json         # optional (zones definition)
  iterations/
    <N>/
      pattern.bkr OR output.html  # the seed; current best
      validation/validation.json  # if N has been validated; optional
```

Plus a small skill arg block:

```yaml
session_dir: <path>
max_iterations: 30                     # budget (G2 conservatism)
stagnation_window: 3                   # consecutive no-improvement iters before hand-back
stagnation_epsilon: 0.005              # min composite delta to count as improvement
edit_skill: iterate-pattern-from-qiyas-warnings  # which skill drives the edit
                                       # (the only one shipped today; future: d3-edit skill)
dry_run: false                         # if true, write deliverables but don't apply edits
```

### Output

After exit:
- One new `iterations/<K>/` directory per cycle with `pattern.bkr`,
  `render.svg`, `validation/validation.json`, and the G3 deliverables
  filed against the *previous* iteration.
- A session-root `auto-iterate-run.md` summarizing the run: terminal
  state, iterations consumed, composite trajectory, top warnings
  consumed, predicted-vs-actual deltas (the calibration data #75
  needs).
- Exit code: 0 on convergence, 1 on stagnation, 2 on budget exhaustion,
  3 on uncaught error in any sub-step.

### The cycle (one iteration)

```
loop while not terminal:
    N = current_best_iteration_number
    K = N + 1

    # 1. Read warnings[0]
    val = load(iterations/N/validation/validation.json)
    if val.overall.go_no_go == "converged":
        terminal = "converged"; break
    if val.overall.go_no_go == "broken":
        # G1 exception: only fix-broken-render edits. Apply minimal fix.
        edit = derive_broken_render_fix(val)
    else:
        warning = val.overall.warnings[0]
        if warning is None:
            terminal = "no-warnings-but-not-converged"; break  # tool gap
        edit = invoke_edit_skill(
            session_dir, N, warning, baseline=input/baseline.json)

    # 2. Apply edit → produce iterations/K/pattern.bkr
    write iterations/K/pattern.bkr (after copying iter N's bkr as base)
    apply edit to iter K's bkr

    # 3. Render
    compile_dsl(iterations/K/pattern.bkr) → iterations/K/render.svg
    if validate-svg fails:
        # Render-broken; record and force next iter into G1-fix mode
        log + continue with iter K marked broken

    # 4. Validate
    iteration-validate.sh --svg iter K render.svg ... --out iter K validation/
    val_K = load(iterations/K/validation/validation.json)

    # 5. File G3 deliverables for iter N (the just-rendered one)
    #    — written after we have val_K so retrospective can reference predicted-vs-actual
    write iter N evaluation.md, retrospective.md, guidance.md
    append to auto-iterate-run.md: predicted Δ vs actual Δ for warning consumed

    # 6. Stagnation check
    if last `stagnation_window` iters all have |composite_K - composite_K-1| < epsilon:
        terminal = "stagnation"; break

    # 7. Budget check
    if K - start_iter >= max_iterations:
        terminal = "budget"; break

    # loop continues with N := K
```

The whole loop is ~150 lines of Python or bash. The intelligence is in
the skills it composes.

### Autonomous edit invocation — the one real design question

The cycle calls `invoke_edit_skill(...)` to translate `warnings[0]` into
a DSL edit. The existing `iterate-pattern-from-qiyas-warnings` skill is
written for an LLM agent to read and execute — it has a translation
table, worked examples, and free-text instructions. It is **not** a
mechanical function.

Two options:

- **Option A: Wrap the existing skill in an Agent call.** The driver
  spawns a subagent with: "Read these files, apply the
  iterate-pattern-from-qiyas-warnings skill, return the modified
  pattern.bkr." The subagent reads the skill, performs the edit, returns
  the new file. This preserves all the LLM judgment that makes the
  translation table robust to unknown warning ids (the skill's "Unknown
  id" row).
- **Option B: Lift the translation table into a deterministic Python
  function.** `apply_warning_to_bkr(bkr, warning) → bkr'` with one
  branch per warning id. Faster, no LLM call per cycle, but brittle on
  unknown ids and on warnings whose `counterfactual_rationale` requires
  semantic interpretation (most of them).

**Pick A.** Reasons:
- The whole point of the experiment is to test whether the LLM-driven
  translation works end-to-end. Replacing the LLM with a switch
  statement would be a different experiment.
- The translation table acknowledges its limits explicitly (the
  "Unknown id" row says read the rationale verbatim) — that's a
  judgment call, not a mechanical lookup.
- One Agent call per iteration on a 30-iter budget is ~30 calls — not
  expensive; well within Sonnet/Opus throughput.
- Deterministic translation is the V2.D "construction hints"
  exploration's destination, not this skill's. If A succeeds, B becomes
  attractive as an optimization. If A fails, B doesn't help — the
  failure mode is upstream of translation.

The driver's edit step is concretely:

```
Agent({
  description: "Translate warnings[0] to BIKAR DSL edit",
  subagent_type: "general-purpose",
  prompt: f"""
    You are running iteration K = {K} of the auto-iterate loop on
    session {session_dir}.

    Apply the BIKAR `iterate-pattern-from-qiyas-warnings` skill at
    {bikar_skill_path} to:

    Inputs:
    - Current pattern: {session_dir}/iterations/{N}/pattern.bkr
    - Validation: {session_dir}/iterations/{N}/validation/validation.json
        (read overall.warnings[0] for the directive)
    - Baseline: {session_dir}/input/baseline.json
    - Reference image: {session_dir}/input/reference.jpg

    Output:
    - Write {session_dir}/iterations/{K}/pattern.bkr (the edited DSL).
    - Write a one-paragraph rationale to stdout: which warning consumed,
      verbatim counterfactual_rationale, what DSL statement(s) changed.

    Constraints:
    - Apply G1 (do not modify iter {N}'s files).
    - Apply G2 (if structural < 1.0, the edit MUST target a structural
      warning, not coloring).
    - The new pattern.bkr must compile via `compileDSL` (the driver
      will fail the iteration if it doesn't).

    Do NOT run the orchestrator or render — the driver handles those.
    Only produce pattern.bkr and the rationale.
  """
})
```

The driver parses the rationale into the run log. This is the
predicted-vs-actual calibration record.

## Phasing — small chunks, each independently shippable

Tenet 1: don't build the whole thing in one PR. Three phases, each
ends with a working artifact, each is independently mergeable.

### Phase 0 — manual dry run (no skill yet)

**Deliverable:** A 30-line bash script `tools/auto-iterate-dryrun.sh`
that runs ONE cycle: read latest validation.json, print warnings[0],
exit. No edit, no loop. Just confirms the data plumbing works on a
live session.

Validation: run on session-1 (which now has iter 92 validation) and on
bikar-medallion-10 iter 13. Confirm the script reads the right warning
in both cases.

This is the smoke test before any real automation. If the data isn't
there in the shape we expect, we learn now.

### Phase 1 — driver shell, manual edit

**Deliverable:** `tools/auto-iterate.py` implementing the full loop
EXCEPT the edit step. The edit step prints the warning and prompts
the user "apply edit and press enter; the loop will resume." This is
a half-automated mode: loop, render, validate, summarize, stagnation
check, budget check — all automatic. Edit — human.

Validation: run on bikar-medallion-10 starting from iter 12. Drive 3
iterations through the half-auto loop. Confirm:
- Each iter's `validation.json` lands.
- G3 deliverables get written automatically.
- `auto-iterate-run.md` accumulates the predicted-vs-actual deltas.
- Stagnation/budget checks fire when expected.

This proves the harness without depending on the Agent-call step.

### Phase 2 — autonomous edit via Agent call

**Deliverable:** Replace Phase 1's "wait for human edit" with the
Agent invocation described in "Autonomous edit invocation" above. Now
the loop is fully closed.

Validation: run on a fresh session. Pick a pattern that has reasonable
existing convergence runway (e.g. clone the bikar-medallion-10 input/
into a new session-dir, start from iter 1). Set max_iterations=30,
let it run.

Three success criteria:
1. The loop terminates (doesn't crash, doesn't hang).
2. The composite trajectory either converges OR plateaus visibly
   (stagnation hand-back fires).
3. The run-log captures predicted-vs-actual deltas for every iteration
   — calibration data for V2.B.

Failure modes to expect (each is signal, not bug):
- Translation produces invalid DSL → iteration K is broken-render →
  forced into G1 fix mode. Track how often this happens; if >20%, the
  translation skill needs hardening.
- Loop oscillates (warning A → fix → warning B → fix → warning A) →
  this is exactly what V2.B is for. Document the oscillation pattern;
  it becomes V2.B's first concrete use case.
- Loop converges to a wrong-but-locally-optimal state → V2.D
  (construction hints) territory. Document the local optimum; it
  becomes V2.D's motivating example.

Each "failure" is a calibration data point that turns one of the
deferred V2.* items from speculative to grounded.

## Output: the run log

The `auto-iterate-run.md` doc isn't an afterthought — it's the actual
deliverable for the post-resurrection-roadmap. Format:

```markdown
# Auto-iterate run — <session> — <date>

Terminal state: converged | stagnation | budget | error
Iterations: <start> → <end>
Wall time: <duration>

## Trajectory

| Iter | composite | structural | pixel | top_warning | predicted Δ | actual Δ |
|------|-----------|------------|-------|-------------|-------------|----------|
| ...  |           |            |       |             |             |          |

## Edit log per iteration

### Iter K
- warning consumed: <id> (delta <X>)
- rationale (verbatim): "..."
- DSL change: <one-line summary>
- compile result: ok | failed
- next-iter composite delta: <Y>
- predicted-vs-actual error: <X-Y>

...

## Failure modes observed

(empty if converged; otherwise: oscillation pattern, local optimum,
translation failure rate, etc.)
```

This file is the artifact that justifies (or kills) every V2.* item.

## Open questions (don't block Phase 0)

- **Does the driver need its own Docker context?** The orchestrator
  shells to qiyas Docker; the BIKAR core is pure Node; the Agent call
  needs LLM access. The simplest answer is "no — the driver is just a
  Python script that orchestrates these. The user runs it from their
  shell." Revisit if the Agent-call surface needs a sandbox.
- **D3-authored sessions.** Today the edit skill is BIKAR-only. If a
  session uses D3 (`output.html` instead of `pattern.bkr`), the auto-
  iterate skill should error out cleanly with "no D3 edit skill yet
  — see Phase 4." Don't try to hand-roll D3 editing; building a D3
  iteration skill is a separate scope and deserves its own plan.
- **Cost/budget signaling.** Should the driver push a notification
  every N iterations? Probably yes for runs ≥10 iters, since they
  take wall-clock time. Implement in Phase 2 once we know the wall-
  time profile.

## What this plan deliberately doesn't do

- Build a "smart" optimizer (V2.B). The driver consumes warnings as
  ranked; better ranking is V2.B's job, post-data.
- Build construction hints (V2.D). The driver translates warnings;
  generating constructions from intent is V2.D's job, also post-data.
- Build iteration memory (V2.A). The driver keeps a run log; making
  qiyas itself iteration-aware is V2.A's job. The run log is the
  bridge until V2.A lands.
- Auto-init sessions. The driver assumes a session has already been
  set up with input/. Setup is `learn-new-pattern`'s job (or a shell
  one-liner using `qiyas baseline emit`).

These are all downstream of the calibration data this loop generates.
Build them when this plan's Phase 2 produces the data, not before.

## Cross-references

- `bikar/.claude/skills/iterate-pattern-from-qiyas-warnings/SKILL.md`
  — the per-iteration edit skill the driver invokes
- `sacred-patterns/.claude/skills/learn-new-pattern/iteration-guide.md`
  — the human-driven version of this loop; auto-iterate is the
  autonomous sibling
- `sacred-patterns/CLAUDE.md` "HARD GATES" — G1-G5 the driver enforces
- `sacred-patterns/CLAUDE.md` "Engineering Tenets" — the lens this
  plan applies (especially #1 chunked phasing, #4 verify-before-claim)
- `qiyas/docs/product-vision.md` — the "iteration agent is *the*
  user" framing that justifies building this at all
- `sacred-patterns/.claude/plans/post-resurrection-roadmap.md` — the
  triage that ranked this work as "drive next" via #85 + the
  V2.* gating signals
