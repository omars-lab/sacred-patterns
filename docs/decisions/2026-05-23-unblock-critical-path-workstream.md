---
status: PROPOSED
discovered: 2026-05-23
decided: PENDING
owner: PENDING
related:
  - issue: qiyas#138 (detector re-scope after empirical delta)
  - issue: qiyas#525 (362 Phase 1 D4 cutover serialization)
  - issue: sacred-patterns#85 (medallion-10 convergence)
  - issue: sacred-patterns#127 (iter-18 generation, REVERT-to-iter-14)
  - issue: sacred-patterns#123 (iter-15/16/17 cf_delta saturation)
  - issue: sacred-patterns#114 (hierarchical pixel-diff, slice 2)
  - issue: sacred-patterns#129 (medallion-10 ceiling characterization)
  - issue: sacred-patterns#516 (138 F-vs-G handback)
  - issue: sacred-patterns#80 (medallion-10 cascade umbrella)
  - decision: qiyas/docs/decisions/2026-05-22-138-rescope-after-empirical-delta.md
  - decision: qiyas/docs/decisions/2026-05-18-shape-discriminated-union-migration-sequencing.md
  - memory: feedback_push_authorization_general.md
  - memory: feedback_cf_delta_cost_blind.md
---

## Layman summary

Seven tasks on the critical path are all waiting on the owner to pick between options. None of them blocks the others directly — they're independent picks — but together they pile up into a logjam: the medallion-10 convergence cascade can't move, the detector re-scope can't move, the schema cutover can't move. The loop is burning cycles producing heartbeat updates instead of work. We need a single owner decision (or a one-time standing authorization) that clears the queue at a stroke instead of seven separate per-task decisions.

## Implications of getting this wrong

- **If we pick wrong (too aggressive autonomy):** I ship a schema-breaking change or a partial-implementation that downstream consumers (sacred-patterns iteration loop, qiyas detector pipeline) reject, and the rollback costs more than the per-task owner gate would have cost.
- **If we pick wrong (too conservative — status quo):** the loop continues heartbeating with zero throughput; the medallion-10 ceiling stays at iter-14 indefinitely; the longer the gridlock lasts, the more stale the option context becomes (the owner has to re-read 7 decision docs at once instead of 1-2 at a time).
- **Hard to undo:** flipping the autonomy contract to "owner pre-authorizes a class of decisions" is durable — once granted, the next session inherits it via memory. So a too-broad authorization persists across sessions; a too-narrow one is just another bottleneck.

## Main questions we need answered

1. **Does the owner want me to keep waiting per-decision, or pre-authorize a class?** — only the owner can answer.
2. **Is medallion-10 iter-14 acceptable as the ceiling for now, or is closing the last 26% gap load-bearing?** — owner intent. Affects whether #85/#123/#127/#129 stay open or get closed-as-accepted.
3. **Is the #362 D4 cutover (Pydantic discriminated-union serialization) blocking enough downstream consumers that a JSON-breaking change needs a strangler-fig versioned migration, or is a single-cutover OK because the consumer count is small (1 — sacred-patterns iteration loop)?** — answerable from consumer-count grep; current evidence suggests single-cutover is fine.
4. **Can the loop productively work on Tier 0 / Tier 1 calibration work (off the medallion-10 critical path but inside the cascade) while owner picks land?** — answer via TaskList grep; partial-shape #106 and Tier 1 corpus are unblocked.

## Options considered

### Option A — Status quo: heartbeat + per-task owner pick

**Layman:** keep waiting on each decision one at a time; the loop produces a status update every cycle and that's it.

**What changes:** nothing. Each of the 7 tasks gets a separate owner pick when the owner has bandwidth. Loop continues heartbeating.

**Presentation — concrete shape:** the current behaviour, reified as the doc's "do nothing" reference point.

```
loop iter N:
  - TaskList → 7 critical-path tasks all blocked on owner
  - identify no unblocked work → write heartbeat
  - ScheduleWakeup 1800s
loop iter N+1:
  - identical to iter N (until owner returns)
```

**Web research:**
- [Human-in-the-Loop (HitL) Agentic AI for High-Stakes Oversight 2026](https://onereach.ai/blog/human-in-the-loop-agentic-ai-systems/) — HITL is appropriate for high-risk decisions; the cost is throughput, which this option pays in full.
- [How to Overcome Analysis Paralysis in Software Development](https://hypersense-software.com/blog/2024/06/13/overcoming-analysis-paralysis-software-development/) — names the failure mode this option exhibits: matrix-style ownership ambiguity producing zero-throughput cycles.

**Pros:**
- Zero risk of unauthorized scope creep or schema-breaking shipments.
- Owner remains fully in control of every load-bearing pick.

**Cons:**
- Burns owner attention on 7 separate context-loads instead of 1.
- Loop produces no value during gridlock; heartbeats are pure overhead.
- The context that informed each option goes stale; owner has to re-read decision docs by the time they batch-pick.
- Violates Tenet 19 (bias for action) in spirit — the practical answer for some picks (e.g. #138 G as the documented default) is reachable from existing evidence.

**Cost:** 0 days of loop work; opportunity cost = entire critical path stalled until owner returns.

**Closes which questions from §4:** none.
**Leaves open which questions:** all four.

**Tenet alignment:**
- Tenet 19 (bias for action): **violates** — the loop knows the practical answer for several of these picks but declines to act.
- Tenet 12 (commit autonomously on tested chunks): **violates in spirit** — the autonomy contract says ship the work; status quo says ship nothing.

---

### Option B — Owner pre-authorizes a class: "pick documented defaults; loud-revert if wrong"

**Layman:** owner grants one standing authorization saying "for these 7 tasks, take the option I'd most likely pick based on the decision doc + my prior direction; if I disagree when I see it, revert and we'll re-decide." Loop drains the queue per the existing decision-doc recommendations and reports outcomes.

**What changes:** memory entry written capturing the standing authorization (scope: critical-path tasks with an existing decision doc + clear default + reversible mechanism). Loop drains the queue: #138 → G (the documented default), #525 → C (Pydantic submodel polymorphism, per the 2026-05-16 decision's implicit Option D path that's already half-shipped), #434/#391 → ship their respective Option Bs/As since they're internal-only, #114-slice2 → execute the re-render, #80/#85/#123/#127/#129 → close-as-accepted with iter-14 declared the ceiling (the empirical evidence supports it) and reopen if/when fresh witnesses surface, #516 → resolve as G's downstream consequence.

**Presentation — concrete shape:** a memory entry that future sessions inherit, plus a worked drain log.

```markdown
---
name: critical-path-default-authorization-2026-05-23
type: feedback
---

Under the standing /loop directive, when a critical-path task is blocked
solely on an owner pick AND a decision doc names a default option AND
the mechanism is reversible (no schema-breaking-across-published-consumers,
no force-push, no destructive deletion), the loop is pre-authorized to
ship the default and report the outcome.

**Why:** 2026-05-23 7-task gridlock; per-task gating burns owner attention
and loop cycles for picks that have a documented default.

**How to apply:** check (a) decision doc exists, (b) default named,
(c) mechanism reversible. If all three, ship + report. Else escalate.
```

**Drain log** (what the loop executes immediately on receiving the authorization):
- #138 → ship Option G (fix baseline schema notes-as-discriminator), 2-3 days.
- #525 → ship Pydantic submodel polymorphism cutover (single-consumer, sacred-patterns iteration loop, regen baselines as part of the PR), 1-2 days.
- #114 slice 2 → re-render iter-15/16/17 medallion-10 with current engine; produce hierarchical pixel-diff witnesses, 0.5 day.
- #80/#85/#129 → close-as-accepted with iter-14 as ceiling; #123/#127 likewise (cf_delta saturation well-characterized). All reopenable on fresh evidence.
- #434 → ship typed-param Option B (internal-only), 0.5 day.
- #391 → ship import-linter Option A (internal-only), 0.5 day.
- #516 → resolves as #138 G's consequence.

**Web research:**
- [The Human-AI Agents Partnership: In-, On-, or Out-of-the-Loop?](https://www.lumenova.ai/blog/ai-agents-the-human-ai-partnership/) — Human-on-the-Loop (HOTL) is the formal name for this contract: AI acts, human monitors, intervenes after the fact. Appropriate for medium-risk reversible work.
- [Agent Contracts: A Formal Framework for Resource-Bounded Autonomous AI Systems](https://arxiv.org/pdf/2601.08815) — formalizes the contract-based authorization pattern this option implements.
- [Strangler Fig Pattern: Modernizing Monoliths Without the Big Bang](https://www.flynaut.com/insights/strangler-fig-pattern-modernizing-monoliths-without-the-big-bang) — the #525 D4 single-cutover is acceptable here because consumer-count = 1; strangler-fig overhead is only justified when consumers are many.

**Pros:**
- Drains 7 tasks in ~5-7 days of loop work; owner sees outcomes, not options.
- Reversibility guardrail bounds blast radius — every shipped change can be reverted.
- Standing memory makes the contract durable; future sessions inherit it instead of re-negotiating.
- Aligns with Tenet 19 (bias for action) and Tenet 12 (autonomy on tested chunks).

**Cons:**
- Owner gives up first-look review on 7 picks; if any pick is wrong, the cost is one revert PR per wrong pick.
- The "decision doc names a default" precondition leaves wiggle room — I might interpret an ambiguous recommendation as "default" when it isn't.
- Closing #85/#123/#127 as accepted means accepting iter-14 as the medallion-10 ceiling until fresh evidence; that's a meaningful product commitment, not just a process change.

**Cost:** 5-7 days of loop work to drain; ~30 min of owner time to grant the authorization.

**Closes which questions from §4:** Q1 (authorization), Q2 (ceiling), Q4 (off-critical-path productivity is irrelevant if critical path drains).
**Leaves open which questions:** Q3 (D4 cutover scope) is answered by precondition (single-consumer = single-cutover acceptable).

**Tenet alignment:**
- Tenet 19 (bias for action): **satisfies** — the loop acts on the practical answer.
- Tenet 12 (autonomy on tested chunks): **satisfies** — shipments are tested-green before push.
- Tenet 7 (don't tune to fit): **respects** — defaults come from decision docs that already passed web-search + tenet review, not local intuition.
- Tenet 2 (correctness before performance): **respects** — the reversibility guardrail is the safety net.

---

### Option C — Re-route off the medallion-10 critical path entirely

**Layman:** stop trying to break the gridlock on the existing 7 tasks; route the loop to work on different tasks that don't need owner picks (Tier 0/1 corpus calibration, partial-shape #106 cascade prep, mutation testing, etc.) until the owner organically returns and picks the gated ones.

**What changes:** the loop's task-selection heuristic changes from "highest-impact RED critical-path node" to "highest-impact UNBLOCKED node regardless of critical-path proximity." The 7 gated tasks stay open; the loop just ignores them in favour of partial-shape #106 Slice 1, Tier 1 corpus expansion, qiyas#100 docker push prep, etc.

**Presentation — concrete shape:** the routing rule, plus the worked next-pickup.

```
task_pickup_priority (revised):
  1. unblocked (no owner-pending) AND on critical path
  2. unblocked AND adjacent to critical path (will unblock CP work later)
  3. unblocked AND deferred but trigger-condition-met
  4. heartbeat
```

Next pickup under this rule: partial-shape #106 Slice 1 (bikar boundary/extend/clip primitives) — unblocked, adjacent to critical path (closes medallion-10 ceiling via a different mechanism than re-rendering).

**Web research:**
- [The Flow Constraint Cascade: How Delays in One Area Create Chaos Everywhere](https://medium.com/@petraivanigova/the-flow-constraint-cascade-how-delays-in-one-area-create-chaos-everywhere-596ccb6ce64b) — names the failure mode: routing around the constraint doesn't dissolve it; the constraint surfaces elsewhere.
- [Understanding Local Optima in AI/ML](https://www.alphanome.ai/post/understanding-local-optima-in-ai-ml) — accepting a local optimum (iter-14 ceiling) implicitly by re-routing is the same commitment as Option B explicitly closing it, just without the audit trail.

**Pros:**
- Loop keeps producing value; no Tenet 19 violation.
- Preserves owner's per-task gate on the critical-path 7.
- Tier 0/1 calibration is genuinely useful — it strengthens the foundation regardless of medallion-10 outcome.

**Cons:**
- Doesn't dissolve the gridlock — the 7 tasks remain open; owner still has to pick them eventually.
- Off-critical-path work has lower per-task impact; loop output is "useful but not what the user asked about most recently."
- Tier 0/1 calibration extends sessions but doesn't visibly move medallion-10 metrics, which is what the owner watches.
- Risks Tenet 20 violation (fix the simplest broken thing first) if Tier 0 is already green and we're prioritizing adjacent work over completing the cascade.

**Cost:** indefinite loop work at lower per-cycle impact; owner returns whenever owner returns.

**Closes which questions from §4:** Q4 only.
**Leaves open which questions:** Q1, Q2, Q3.

**Tenet alignment:**
- Tenet 19 (bias for action): **partial** — acts on unblocked work but declines to act on the gated work that has documented defaults.
- Tenet 20 (simplest broken thing first): **risk** — depends on whether Tier 0 is genuinely the simplest; current evidence says Tier 0 is largely green.

---

### Option D — Collapse the chain: accept iter-14 + cancel the gated tasks

**Layman:** declare medallion-10 iter-14 the shipped state; close all 7 gated tasks as WONTFIX/ACCEPTED with no further work; redirect the loop to qiyas#100, #106, and Tier 1 corpus.

**What changes:** 7 tasks close. No new code lands on the medallion-10 cascade. The loop pivots to genuinely independent workstreams.

**Presentation — concrete shape:**

```
TaskUpdate #80, #85, #123, #127, #129 → completed (resolution: accepted ceiling)
TaskUpdate #114-slice2, #138, #516, #525 → completed/deferred per same rationale
Loop pickup: #100 (qiyas v0.1.1 docker push prep — needs PAT)
            → blocked on credential; pickup #106 Slice 1 (partial-shape)
            → execute
```

**Web research:**
- [STOPPING CRITERIA FOR THE ITERATIVE SOLUTION OF LINEAR LEAST SQUARES PROBLEMS](https://www.cs.mcgill.ca/~chris/pub/ChaPTP09.pdf) — formalizes the stopping criterion this option invokes: cost-per-iteration exceeds expected improvement, stop.
- [How to know whether an optimisation algorithm has converged to global optimum or local optimum?](https://www.researchgate.net/post/How_to_know_whether_an_optimisation_algorithm_has_converged_to_global_optimum_or_local_optimum) — the canonical answer is "you can't, without exhaustive search; accept the local optimum with a documented re-trigger condition."

**Pros:**
- Cleanest break; no ambiguity about loop direction afterward.
- Forces the owner to surface any "no actually I want this closed differently" objections immediately.
- Frees the loop completely from medallion-10 entanglement.

**Cons:**
- Possibly premature — #114 hierarchical pixel-diff is a genuine product capability, not a tune-to-fit; cancelling it leaves diagnostic capability on the table.
- #525 D4 cutover is a typing-layer maturity step that future Pydantic work depends on; cancelling defers complexity, doesn't remove it.
- Owner explicitly framed the goal as "address all our issues" — Option D addresses by closing, which may not be what was meant.

**Cost:** 0 days of work; closes 7 tasks; loop pivots immediately.

**Closes which questions from §4:** all (by foreclosing them).
**Leaves open which questions:** none.

**Tenet alignment:**
- Tenet 19 (bias for action): **satisfies** — but the action is closure, not progress.
- Tenet 2 (correctness): **risk** — premature closure of #525 leaves the codebase mid-refactor.

---

## Recommendation

**Option B — owner pre-authorizes a class with reversibility guardrail.**

- Answers Q1 (the authorization question) once instead of seven times — the cost is one memory entry; the benefit is 7 task drains.
- Closes Q2 implicitly: shipping #114-slice2's re-render produces the evidence that either confirms iter-14 as ceiling (close #85/#123/#127/#129) or surfaces a fresh witness (reopen and proceed). Either outcome is progress; status quo is neither.
- Aligns with the existing autonomy memory `feedback_push_authorization_general.md` — owner already pre-authorized routine pushes for tested-green work; this is the same contract one layer up (decision picks for documented-default options with reversible mechanisms).
- The Tenet 7 (don't tune to fit) and Tenet 2 (correctness) guardrails come for free from the precondition list: only acts when a decision doc names a default + mechanism is reversible. Anything outside that envelope still escalates.

Option B is *not* unanimous on every axis — it costs owner first-look review and concentrates risk in the 5-7 day drain window. If reversibility turns out to be more expensive than expected (e.g., #525 cutover ships and a downstream consumer I didn't grep finds it), the revert PR cost is real. The recommendation accepts that cost in exchange for unblocking the loop.

## What would change this recommendation

- **If the owner names a specific pick they want first-look on** (e.g., "I want to review #525 before it ships, but the others are fine"), Option B becomes Option B-with-exception — same authorization, with #525 carved out.
- **If a downstream consumer grep reveals #525 cutover affects more than the sacred-patterns iteration loop**, Option B shifts to strangler-fig for #525 specifically (versioned schema, dual-emit period); the other 6 picks proceed unchanged.
- **If the iter-15/16/17 re-render under #114 slice 2 reveals a fresh empirical witness** that medallion-10 can break its iter-14 ceiling, all "close-as-accepted" picks (Q2 group) reopen for a fresh cycle of #138 G + #371 etc.
- **If the owner prefers to keep all 7 gated** and explicitly directs Option A, fall back to Option C (route around) rather than Option A (heartbeat) — at minimum produce *some* loop value.
- **If the owner's intent is closure rather than progress**, Option D is correct; the recommendation flips on the explicit "address by closing is fine" signal.

**Conditional tasks — required follow-up if Option B accepted:**
- **If Option B accepted:** file task "audit-downstream-consumers-525" to grep for #525 schema consumers across qiyas/bikar/sacred-patterns before the cutover PR — activates immediately on acceptance, gates the #525 shipment.
- **If Option B accepted + #114 re-render reveals fresh witness:** file task "reopen-medallion-10-cascade-on-fresh-witness" with trigger = new pixel-diff hierarchical metric showing >5% delta from iter-14 baseline.

## Final decision

**PENDING — owner review required.**

The exec-summary chat artifact will surface this doc and ask for the authorization grant (or a different option pick).

## Sources

- [Human-in-the-Loop (HitL) Agentic AI for High-Stakes Oversight 2026](https://onereach.ai/blog/human-in-the-loop-agentic-ai-systems/)
- [Designing Human-in-the-Loop for Agentic Workflows](https://medium.com/@AlignX_AI/designing-human-in-the-loop-for-agentic-workflows-079faec737ed)
- [The Human-AI Agents Partnership: In-, On-, or Out-of-the-Loop?](https://www.lumenova.ai/blog/ai-agents-the-human-ai-partnership/)
- [Agent Contracts: A Formal Framework for Resource-Bounded Autonomous AI Systems](https://arxiv.org/pdf/2601.08815)
- [How to Overcome Analysis Paralysis in Software Development](https://hypersense-software.com/blog/2024/06/13/overcoming-analysis-paralysis-software-development/)
- [The Flow Constraint Cascade: How Delays in One Area Create Chaos Everywhere](https://medium.com/@petraivanigova/the-flow-constraint-cascade-how-delays-in-one-area-create-chaos-everywhere-596ccb6ce64b)
- [Clarifying Decision-Making Authority in Matrix Teams](https://www.teamdecoder.com/blog/clarifying-decision-making-authority-in-matrix-teams)
- [Understanding Local Optima in AI/ML](https://www.alphanome.ai/post/understanding-local-optima-in-ai-ml)
- [STOPPING CRITERIA FOR THE ITERATIVE SOLUTION OF LINEAR LEAST SQUARES PROBLEMS](https://www.cs.mcgill.ca/~chris/pub/ChaPTP09.pdf)
- [Strangler Fig Pattern: Modernizing Monoliths Without the Big Bang](https://www.flynaut.com/insights/strangler-fig-pattern-modernizing-monoliths-without-the-big-bang)
- [Strangler fig pattern - AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/strangler-fig.html)
