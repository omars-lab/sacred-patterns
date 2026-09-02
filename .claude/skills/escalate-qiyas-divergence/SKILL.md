---
name: escalate-qiyas-divergence
description: Invoke when the iteration agent is about to build a local workaround for behavior that should live in qiyas. Captures a fixture, files a qiyas issue with the reproducer, links via cross-repo-dependencies, and decides wait-vs-workaround with a deletion deadline.
user_invocable: false
---

# escalate-qiyas-divergence

## When to invoke this skill

Trigger this skill when iteration work is about to produce ANY of:

- A local Python/shell script that replicates analytical behavior already
  in qiyas's scope (encoding, diff, audit, score, fixture comparison).
- A patch to `tools/iteration-validate.sh` that branches around a qiyas
  call instead of forwarding its output.
- A hand-rolled JSON post-processor sitting between `qiyas <cmd>` and
  the orchestrator that "corrects" qiyas's output before downstream
  consumption.
- An inline `if pattern == "medallion-10": ...` style special case in
  any sacred-patterns tool that exists because qiyas misbehaves on
  that pattern.
- A "DO NOT DELETE — works around qiyas bug X" comment without a
  filed qiyas issue link.

Also trigger when reading code surfaces an *existing* workaround that
doesn't have a tracked deletion deadline — that's a silent debt the
skill exists to surface (Tenet 6: trust but verify; inherited "we'll
clean this up later" markers go stale).

**Do NOT invoke for:** legitimate sacred-patterns-side fixes
(rendering, DSL, geometric construction, iteration UX, validate-svg
preflight). Those are sacred-patterns's job — qiyas owns analysis,
not construction. The boundary is in
`qiyas/docs/sacred-patterns-integration.md`.

## Why this skill exists

`qiyas/docs/sacred-patterns-integration.md` §"Divergence policy" is
explicit: when qiyas and any local checker disagree, **we fix qiyas.**
Local workarounds are allowed only with deletion deadlines. The
policy is documented but unenforced — strategic gap #6 in qiyas's
roadmap is "divergence has policy but no enforcement." This skill is
the enforcement mechanism: every workaround the iteration agent
considers triggers the capture-file-link-decide loop *before* the
workaround code lands.

Without this skill, the failure mode is silent parallel tooling —
the exact pattern that the `tools/svg-diff.sh` / `tools/zone-audit.py`
deletion cascade was designed to prevent. Tenet 2 (root cause, don't
add a fallback) applies cross-repo: the local "fallback" *is* the
divergence, and shipping it without an upstream issue is how qiyas's
roadmap rots.

## Inputs

- **`divergence_description`** (required): one sentence on what qiyas
  did vs what we expected, e.g. *"qiyas svg-audit reports A2 cv 0.27
  on bikar-medallion-10 iter-16 but visual inspection shows
  10-fold symmetry is intact."*
- **`fixture_path`** (required): absolute path to the SVG / PNG /
  encoding.json input that triggers the divergence. Must be a file
  that survives outside the current session — not a `/tmp` artifact.
- **`expected_output`** (required): one sentence on what qiyas
  *should* have produced.
- **`actual_output`** (required): one sentence on what qiyas
  *did* produce, with the relevant JSON path (e.g.
  `audits.A2.cv == 0.27`).

## Mechanical steps

### 1. Capture the fixture into qiyas's tracked corpus

```bash
qiyas fixtures capture <fixture_path> \
  --label <slug> \
  --reason "divergence: <one-line>"
```

The `qiyas fixtures capture` sub-command (qiyas/src/qiyas/cli.py
`fixtures_capture`) copies the input into qiyas's frozen corpus
under `tests/fixtures/<label>/` and records a manifest entry with
the reason. This guarantees the reproducer survives the iteration
session — without it, the divergence becomes unprovable once the
session's Dropbox directory rotates.

Verify the fixture landed:
```bash
ls qiyas/tests/fixtures/<label>/
```

### 2. File a qiyas issue with the reproducer

Issue path: `qiyas/docs/issues/YYYY-MM-DD-<slug>.md`. Required
structure (mirrors `sacred-patterns/CLAUDE.md`:82 "Issue
documentation"):

```markdown
---
status: OPEN
discovered: YYYY-MM-DD — <by whom, what surfaced it>
owner: PENDING
related:
  - fixture: qiyas/tests/fixtures/<label>/
  - sacred-patterns task: #NN (the iteration this surfaced in)
  - sacred-patterns session: <path under ~/Dropbox/Data/sacred-patterns/>
---

## Symptom

<concrete observation; the divergence_description verbatim, then
the exact command that reproduces it:>

```bash
qiyas <cmd> qiyas/tests/fixtures/<label>/input.<ext>
# expected: <expected_output>
# actual:   <actual_output>
```

## Root cause

UNKNOWN — investigation pending. The skill files the issue; the
qiyas-side root-cause work is a separate task.

## Options considered

(Left for the qiyas-side investigator to fill in after root cause is
established. The point of filing OPEN with options-pending is that
this issue exists in qiyas's roadmap and counts against the
strategic-gap-#6 metric.)

## Decision

PENDING.

## Follow-ups

- qiyas-side: investigate root cause, file fix as #NN
- sacred-patterns-side: see decision below in §"Wait or workaround"
```

### 3. Link via cross-repo-dependencies

Two updates, both required:

**(a) sacred-patterns task** (the iteration task that surfaced the
divergence): append to its description:
```
blocked by qiyas issue: docs/issues/YYYY-MM-DD-<slug>.md
```

**(b) qiyas/docs/cross-repo-dependencies.md**: add a row under
§"Active dependencies" with the qiyas issue path and the
sacred-patterns task ID. Mirror the same row into
`sacred-patterns/docs/cross-repo-dependencies.md` (if it has the
table; if not, the task-description link from (a) suffices —
grep-driven discovery still works).

### 4. Decide: wait for upstream fix, or local workaround with deletion deadline

Two branches. Pick based on the iteration's blocking urgency, NOT on
"what's faster to type."

**Branch A — wait for upstream fix.**

Preferred default. The iteration task stays open and blocked by the
qiyas issue; pick a different iteration task to make forward
progress. Cross-repo authority (memory:
`feedback_cross_repo_authority.md`) means switching to qiyas or
bikar work while sacred-patterns waits is the right move.

Action: confirm the task is `blocked by` the issue path; pick
unblocked work; loop.

**Branch B — local workaround with deletion deadline.**

Only when the iteration is on the critical path AND the upstream fix
is days out. The workaround MUST satisfy all of:

1. **Single-purpose.** The workaround does ONLY the one thing the
   divergence requires; no scope creep into other analytical work.
2. **Tagged in code.** A comment at the top of every workaround file
   / function:
   ```python
   # WORKAROUND for qiyas divergence — see qiyas/docs/issues/YYYY-MM-DD-<slug>.md
   # DELETE when qiyas issue closes. Last verified blocking: YYYY-MM-DD.
   ```
3. **Has a sacred-patterns deletion task.** Create a sacred-patterns
   task with subject `[escalate-qiyas-divergence] delete workaround
   for qiyas#NN` and `blocked by` the qiyas issue path. This task is
   what enforces deletion when the upstream fix lands.
4. **Output divergence is named, not silenced.** The workaround must
   emit a `validation.json` warning of source `divergence_workaround`
   citing the qiyas issue path, so downstream consumers see that the
   reported metric is locally-computed, not qiyas-computed.

If you cannot satisfy all four, pick Branch A — the workaround isn't
ready to ship.

## Verification (before declaring escalation complete)

- [ ] `qiyas fixtures capture` produced a fixture directory and a
  manifest entry — verify by `ls qiyas/tests/fixtures/<label>/` and
  `git status` in qiyas.
- [ ] `qiyas/docs/issues/YYYY-MM-DD-<slug>.md` exists with frontmatter
  status: OPEN.
- [ ] The fixture path in §Symptom of the issue is reproducible by
  running the exact command shown — verify by running it.
- [ ] The sacred-patterns iteration task description includes
  `blocked by qiyas issue: <path>`.
- [ ] (Branch B only) The workaround comment cites the issue path and
  the deletion task exists with `blocked by` set.

## Success metric

The roadmap §V2.F success metric: *number of qiyas issues filed
BEFORE the corresponding local workaround lands ≥ 1*. Each invocation
of this skill that completes Branch A (no workaround) or Branch B
with all four guards in place increments that count. Each workaround
that lands WITHOUT this skill's escalation is a metric regression
and should be retroactively escalated.

## Cross-references

- `qiyas/docs/sacred-patterns-integration.md` §"Divergence policy" —
  the policy this skill enforces.
- `qiyas/docs/sacred-patterns-integration.md` §"A5 contingency" —
  the canonical worked example of Branch B (deletion deadline
  against a qiyas milestone).
- `sacred-patterns/CLAUDE.md` Tenet 2 (root cause, don't add a
  fallback) — cross-repo extension: the local workaround *is* the
  fallback; skipping the upstream filing is what makes it rot.
- `sacred-patterns/CLAUDE.md` Tenet 6 (inherited claims are
  snapshots) — applies to existing workaround comments without
  filed issues; this skill is also how those debts get surfaced.
- `qiyas/.claude/skills/iterate-detector-calibration/SKILL.md` —
  sibling skill on the qiyas side; this skill files the issues that
  feed that skill's calibration loop.
- `sacred-patterns/.claude/skills/learn-new-pattern/iteration-guide.md`
  — cross-references this skill at "consider workaround" decision
  points (see Step 12 and the convergence decision tree).
