---
# human-readable (kept; never machine-parsed)
status: ACCEPTED 2026-06-07 — Option C (composite-AND-portal-AND-no-open-gate, with stagnation/budget handbacks)
discovered: 2026-06-07
decided: 2026-06-07
owner: omareid
# structured (machine-read — the contract)
status_token: ACCEPTED
picked_option: C
tag: loop-terminal-condition
supersedes: []
superseded_by: []
related:
  - plan: .claude/plans/autonomous-iteration-loop.md
  - skill: .claude/skills/loop-idle-audit/SKILL.md
  - retrospective: docs/retrospectives/2026-06-06-image-to-dsl-retrospective.md
  - recommendations: docs/retrospectives/2026-06-06-image-to-dsl-recommendations.md
  - memory: feedback_idle_vs_blocked_loop_test.md
---

## 0. Premise check (MANDATORY)

**Premise:** "The autonomous iteration loop has no defined terminal condition,
so it cannot tell *done* from *idling* and repeatedly re-asserts converged-idle
(retro M4)."

**Verified against:** `.claude/plans/autonomous-iteration-loop.md` (read
2026-06-07). The premise is **partially false and that is the finding**: the
plan *does* define three terminal states (1: `go_no_go == "converged"` =
composite ≥ 0.85 + structural N==M + topology complete + pixel ≥ 80; 2:
stagnation = 3 iters without ≥ε composite lift; 3: budget exhaustion = N iters,
default 30). What is *missing* is (a) any reconciliation of those states with the
**Tenet 27 ship gate** (no construction ships without a recorded review-portal
verdict) and the **owner-gate** reality (a converged metric while a decision doc
is PENDING is not "done"), and (b) consolidation into an authoritative decision
the loop and a cold session can both read. The loop has a *metric* terminal
state but not a *ship/acceptance* terminal condition — which is exactly the M4 +
M6 + Tenet-27 seam where "the number is green, declare victory" recurs.

**LEDGER lookup (tag `loop-terminal-condition`):** no prior doc on this tag
(`make ledger` / grep `docs/decisions/*.md` 2026-06-07 — tag newly added to
`tags.yaml` in this commit). The `autonomous-iteration-loop.md` plan is a *plan*,
not a decision doc, and carries no `status_token`; this doc is the first
authoritative decision on the tag and consolidates the plan's metric states.

## 2. Layman summary

The autonomous loop keeps asking "am I done yet?" and has no crisp answer, so it
either stops too early (a green score that hides a topology bug, or a converged
metric while the owner still owes a decision) or never stops (idling tick after
tick re-asserting "converged"). This doc writes down exactly what "done" means —
a metric bar AND a human-eye verdict AND no open owner decision — and what
"hand back to a human" means (stuck or out of budget), so the loop knows which
of those three it's in on every tick.

## 3. Implications of getting this wrong

- **Blocks downstream if wrong:** a loop that declares "converged" on the metric
  alone ships a construction with a topology defect the metric masked (the exact
  Tenet-27 failure) — every downstream consumer (corpus, detector calibration,
  I2 substrate) inherits the bad artifact.
- **Rots silently if we don't pick:** the loop continues the M4 idle churn —
  15-tick / 58-commit idles, 11+ "converged-idle" re-assertions — burning cycles
  producing heartbeats instead of work, because "done" stays a judgment call.
- **Hard to undo:** the terminal condition is load-bearing for the
  `loop-idle-audit` skill and any future autonomous-loop orchestrator; once the
  loop's stop logic keys on these states, changing them is a behavior change
  across every session that inherits the loop.

## 4. Main questions we need answered

1. **Is the metric bar (composite ≥ 0.85 etc.) sufficient for "done," or is a
   recorded review-portal verdict mandatory?** — answerable from Tenet 27 (it is
   mandatory; the metric is necessary-not-sufficient).
2. **Does an open owner-gate (a PENDING decision doc on a tag this pattern
   depends on) block "done"?** — owner-intent, but the decision-pick authority +
   ledger make it checkable: a converged pattern with an unshipped owner-PENDING
   dependency is not done; it is *handed back*, not *converged*.
3. **What distinguishes a legitimate terminal state from an idle tick that only
   looks terminal?** — answered by the `loop-idle-audit` idle-vs-blocked test
   (name the unfired trigger or named blocker).

## 5. Options considered

### Option A — Status quo: metric-only terminal state (the plan as written)

**Layman:** "done" = the plan's `go_no_go == "converged"` metric bar; nothing
about the portal or owner-gates.

**What changes:** nothing. The loop stops on composite ≥ 0.85 + structural N==M
+ topology + pixel ≥ 80, or hands back on stagnation/budget.

**Presentation — concrete shape:**
```
terminal(iter) := go_no_go == "converged"          # metric only
              OR  stagnation(3, ε)                  # handback
              OR  iters >= budget                   # handback
```

**Web research:** No canonical precedent for "metric-only convergence is
sufficient"; the opposite is folklore in the ML literature (a held-out metric
overfits; a green number is a lossy projection).

**Pros:** zero work; already implemented in the plan.
**Cons:** violates Tenet 27 (ships on the metric without a portal verdict);
ignores owner-gates (declares done while a dependency is PENDING); this is the
M6/M4 recurrence the retrospective named.
**Cost:** half day (none — status quo).
**Closes which questions from §4:** none cleanly.
**Leaves open:** Q1, Q2, Q3.
**Tenet alignment:** violates Tenet 27 (no ship without portal verdict) and the
metric-temptation lesson; mis-serves Tenet 4 (verify before claiming done).

### Option B — Portal-gated terminal state (metric AND portal verdict)

**Layman:** "done" = the metric bar AND a recorded review-portal verdict.

**What changes:** the loop's terminal check adds "a portal verdict for this
iteration exists in the session `annotations.json`."

**Presentation — concrete shape:**
```
terminal(iter) := go_no_go == "converged"
              AND portal_verdict_recorded(iter)     # Tenet 27 gate
              OR  stagnation / budget handback
```

**Web research:** matches the "human-in-the-loop acceptance" pattern; no single
canonical citation, but consistent with Tenet 27's own rationale.
**Pros:** closes the Tenet-27 hole (Q1); cheap.
**Cons:** still ignores owner-gates (Q2) — a pattern can be metric+portal green
while a decision doc it depends on is PENDING, which is not "done."
**Cost:** half day.
**Closes which questions from §4:** Q1.
**Leaves open:** Q2.
**Tenet alignment:** satisfies Tenet 27; partial on the autonomy contract.

### Option C — Composite terminal: metric AND portal AND no-open-owner-gate, with explicit handback states (RECOMMENDED)

**Layman:** "done" = the metric bar AND a recorded portal verdict AND no open
owner-gate the pattern depends on. Anything else is either a *handback* (stuck /
out of budget) or *not terminal* (keep working — and if it looks idle, run the
idle-vs-blocked test first).

**What changes:** the loop's terminal logic gains three named states (converged
/ handback / not-terminal) and the converged state ANDs in portal + owner-gate
checks. The `loop-idle-audit` skill governs the not-terminal-but-looks-idle
case.

**Presentation — concrete shape:**
```
# CONVERGED (success — stop, record):
converged(iter) := composite >= 0.85
               AND structural_N == M AND topology_complete AND pixel >= 80
               AND portal_verdict_recorded(iter)              # Tenet 27
               AND no_open_owner_gate(pattern.tags)           # ledger: no PENDING dep

# HANDBACK (hand to human with a diagnosis report):
handback(iter)  := stagnation(3 iters, ε=0.005)               # plateau
               OR  iters >= budget (default 30)               # exhaustion

# NOT-TERMINAL (keep working):
else: pick warnings[0] → edit → render → verify → measure
      # if this tick LOOKS idle, run loop-idle-audit FIRST:
      #   name the unfired trigger OR the named blocker, else act (Tenet 20)
```

**Web research:** "loop-until = quality gate AND acceptance gate AND no open
blocker" is the standard CI/CD release-gate shape (multiple independent gates
ANDed, not a single metric); no single canonical doc, called out as the
conventional release-readiness pattern.
**Pros:** closes Q1 (portal), Q2 (owner-gate), Q3 (idle-vs-blocked via the
skill); makes "done" a conjunction of independent gates so no single green
number can declare victory; reconciles the plan's metric states with Tenets 27 +
the autonomy contract.
**Cons:** slightly more terminal-check logic; requires the loop to read the
ledger for open gates on the pattern's tags (cheap — `make ledger` is generated).
**Cost:** 1 day (to wire portal-verdict + ledger-gate checks into the loop when
the autonomous orchestrator is built; this doc defines the contract now).
**Closes which questions from §4:** Q1, Q2, Q3.
**Leaves open:** none.
**Tenet alignment:** Tenet 27 (portal gate is a required conjunct); Tenet 4
(verify before done — multiple gates); Tenet 19/20 + C3 (the not-terminal branch
defers to bias-for-action via loop-idle-audit); metric-temptation lesson (a green
composite alone is never terminal).

## 6. Recommendation

**Option C.** It is the only option that makes "done" a conjunction of three
independent gates — metric, human-eye (Tenet 27), and no-open-owner-gate — so a
green metric alone can never declare victory (the M6/Tenet-27 recurrence), and it
folds the M4 idle-vs-blocked test into the not-terminal branch via the
`loop-idle-audit` skill. It consolidates the `autonomous-iteration-loop.md`
plan's metric states (which stay correct, as the *converged* conjunct's first
clause) rather than overwriting them, and answers every §4 question.

## 7. What would change this recommendation

- **If the review portal cannot produce a machine-checkable verdict marker** (a
  field the loop can read from `annotations.json`), the portal conjunct degrades
  to a manual gate — Option C still holds but the loop hands back for the portal
  look rather than self-certifying it.
- **If owner-gate checking proves too coarse** (e.g. a pattern's tag has a
  PENDING doc unrelated to *this* pattern's convergence), refine
  `no_open_owner_gate` to depend on the specific decision the pattern's
  construction relies on, not any doc sharing the tag.
- No conditional implementation tasks are filed: the autonomous orchestrator
  that would consume this contract is itself unbuilt (`autonomous-iteration-loop.md`
  is a plan); the terminal-condition wiring is part of that build, tracked there.

## 8. Final decision

**Decided:** 2026-06-07 by omareid (documented default per the decision-pick
authorization — reversible process decision; the contract is consumed only when
the autonomous orchestrator is built, so no artifact is committed against it yet).
**Picked:** Option C.
**Rationale:** "Done" must be a conjunction of independent gates — metric AND
review-portal verdict (Tenet 27) AND no open owner-gate — so that no single green
number can declare convergence; handback states (stagnation / budget) and the
not-terminal branch (governed by `loop-idle-audit`) cover everything else. This
reconciles the existing plan's metric states with the ship-gate and autonomy
tenets the retrospective showed were being skipped.
**Follow-ups (implementation):** none filed now — the terminal-condition wiring
is part of the unbuilt autonomous-orchestrator scope tracked in
`.claude/plans/autonomous-iteration-loop.md`; this doc is the contract that build
will consume.
**Follow-ups (conditional / backlog — track triggers, not work):**
- **If the portal cannot emit a machine-readable verdict marker:** file task
  "add machine-readable portal verdict field to annotations.json" — only
  activates when the autonomous orchestrator is built and needs to self-check the
  portal conjunct.
