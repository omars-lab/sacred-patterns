---
title: "Tenet / skill recommendations — image→DSL inverse problem"
date: 2026-06-06
derived_from: docs/retrospectives/2026-06-06-image-to-dsl-retrospective.md
status: APPLIED 2026-06-07 — R1–R5 + §2/§3/§4 leftovers shipped across two sessions (see "Application status" below)
generated_by: retrospect-hard-problem skill
applied: 2026-06-07
---

> **Application status (2026-06-07).** Applied across two sessions, both
> currently in the **working tree, uncommitted** (the decision-memory cascade
> AND this leftovers session are staged-but-unpushed pending owner-authorized
> commit — so commit SHAs are filled at commit time, not here):
>
> - **Decision-memory cascade (2026-06-07, prior session):** R1–R5 → tenets
>   C1–C5 in all three `CLAUDE.md`; `validate_premise_before_options` memory
>   into qiyas + bikar; `present-options` §0 Premise check; `handle-falsification`
>   L0 branch + `dead_end:` step; the typed `DecisionFrontmatter` +
>   `LEDGER.md` ×3 + `LEDGER-XREPO.md` + `check-decision-coherence.sh` +
>   `tags.yaml` + `docs/decision-schema.md`. (Working-tree artifacts:
>   `?? docs/decision-schema.md`, `?? docs/decisions/LEDGER.md`, `M CLAUDE.md`.)
> - **Leftovers session (2026-06-07, this session):** §2 two memory files
>   (`metric_temptation_at_plateau`, `idle_vs_blocked_loop_test`) × 3 repos +
>   indexed; §3 three skill guards (calibration knob-moved assertion in qiyas's
>   `iterate-detector-calibration`; construction triage + qiyas-diff→.bkr map in
>   `iterate-construction-hypothesis`; new `loop-idle-audit` skill); §4
>   `2026-06-07-loop-terminal-condition.md` decision doc (ACCEPTED Option C,
>   coherence-gate green) + training-pipeline task #5 + I2/girih confirmed +
>   routing-doc entry. (Working-tree artifacts:
>   `?? docs/decisions/2026-06-07-loop-terminal-condition.md`,
>   `?? .claude/skills/loop-idle-audit/`,
>   `M .claude/skills/iterate-construction-hypothesis/SKILL.md`.)
>
> **Commit SHAs (filled 2026-06-10):** decision-memory cascade `f62c575`
> (decision-memory layer: schema, ledgers, coherence gate) + `6a380ea`
> (skill guards + loop-idle-audit + retrospect-hard-problem); leftovers
> session artifacts are split across the same two commits plus the CLAUDE.md
> tenet commit that follows them (C1–C5 + tenets 29/30).

> These are PROPOSALS as diffs-in-prose. This skill does NOT apply them. Each
> cites the retrospective §4 mistake it prevents and an evidence tier. Only
> Tier A/B are proposed. The recurring theme: **the strongest tenets still saw
> recurrences — so the fix is an operational check at the moment of temptation
> (plateau, resume, budget-scare, option-authoring), not another aspirational
> sentence.**

# Recommendations

## 1. New / amended tenets

| # | Repo(s) | Tenet (new / amend) | Prevents (retro §4) | Tier |
|---|---------|---------------------|---------------------|------|
| R1 | all 3 (shared) | **NEW: "Validate the premise before authoring options or regenerating artifacts."** | M1 | A |
| R2 | qiyas, bikar (mirror SP) | **NEW (mirror): "Trust but verify inherited claims — re-emit/git-check before load-bearing use."** | M2 | A |
| R3 | all 3 (shared) | **AMEND bias-for-action: add the idle-vs-blocked operational test + GHA-freeze carve-out.** | M4 | A |
| R4 | all 3 (shared) | **AMEND GHA-budget tenet: "burns billable minutes" covers *status polling*, not just pushes.** | M8 | A |
| R5 | all 3 (shared) | **NEW (mechanical): "Read a file before you write/edit it."** | M7 | B |

**Proposed wording (diffs-in-prose):**

- **R1 (shared tenet):** *"Validate the framing premise before you author
  options or regenerate any artifact. A decision doc's premise ('N items are
  missing', 'the DSL can't express X', 'shape_id is the identity'), and any SHIP
  verdict, must be checked against the actual codebase/corpus/committed tree —
  not the task text — before options are enumerated or a corpus is regenerated.
  The premise-check is the cheapest step and the one most often skipped."*
  Because: F2 `shape_id` shipped + 258-file regen then falsified; the
  rotate-block "can't express neighbor indexing" doc self-falsified within an
  hour; iter-5/6/7 SHIP ran on an uncommitted tree (retro §4 M1). This is the
  single highest-value change. `[A]`

- **R2 (mirror into qiyas/bikar):** sacred-patterns already has
  `feedback_adjudicate_missing_items_via_git_before_loadbearing.md` and the
  Tenet-6 "inherited claims are snapshots" rule; qiyas/bikar agents don't load
  SP's memory. Either promote to a shared CLAUDE.md tenet or mirror the memory
  file. Because: iter-6 "arc_bearing=0" false claim propagated; doc frontmatter
  ACCEPTED contradicting its own body (retro §4 M2). `[A]`

- **R3 (amend bias-for-action):** add — *"In an autonomous loop, before idling
  or declaring 'converged/owner-gated', name (a) the specific artifact you are
  blocked on and (b) one fresh angle you have NOT tried; if you cannot name a
  real external blocker, you are not blocked — act. A GHA-budget freeze blocks
  **pushes**, never local work; never hold N commits idle across ticks waiting
  for budget."* Because: 15-tick idle holding 58 commits; 11+ ticks
  re-asserting converged-idle; one-shot "authorization blocker" (retro §4 M4).
  `[A]`

- **R4 (amend GHA tenet):** add one clause — *"This budget is consumed by CI
  *runs*, which `Monitor`/status-poll loops trigger indirectly; do not poll CI
  status on a tight loop. Check once, schedule a long fallback, move on."*
  Because: excessive `status now?` polling cited by owner during the budget
  squeeze (retro §4 M8). `[A]`

- **R5 (mechanical guard):** add — *"Read a file before writing or editing it —
  including CLAUDE.md mirrors and decision docs. Before authoring a new decision
  doc, grep `docs/decisions/` for an existing doc on the same problem."*
  Because: 6× "File has not been read yet"; duplicate §1 headers; duplicate
  decision doc #400 vs an existing one (retro §4 M7). Best enforced as a
  pre-commit/hook check, not just prose. `[B]`

## 2. New memory files (un-codified recurring mistakes)

| Proposed file | Fact | Why it recurred | Tier |
|---------------|------|-----------------|------|
| qiyas + bikar `memory/feedback_validate_premise_before_options.md` (mirror of an SP one) | Before enumerating options / regenerating artifacts, check the premise against code/corpus/committed tree | The lesson is folklore + 3 SP-only files; qiyas/bikar agents never load it | A |
| `memory/feedback_metric_temptation_at_plateau.md` (all 3) | When a score plateaus, the reflex to raise counts / tune a constant / over-fit a fixture is exactly the moment Tenet 7 governs — stop and fix the cause | M6 recurred *despite* the tenet; the tenet names the rule but not the trigger-moment | B |
| `memory/feedback_idle_vs_blocked_loop_test.md` (all 3) | The operational test for "am I idling or genuinely blocked" (R3 wording) | M4 recurred across many ticks; no operational test existed | A |

> Note the structural finding: **sacred-patterns has 87 auto-memory files
> (`~/.claude/projects/.../sacred-patterns/memory/`); qiyas and bikar have 4
> each.** (These are per-machine auto-memory, not checked-in repo `memory/`
> dirs — so they are invisible across repos *and* across machines. If a lesson
> is meant to be durable + shared, a CLAUDE.md tenet or a checked-in doc is the
> right home, not auto-memory.) qiyas/bikar push lessons into CLAUDE.md tenets
> and decision docs instead. That is a legitimate choice, but it means SP's rich process
> lessons (premise-check, git-adjudication, oracle-in-record) are invisible to
> qiyas/bikar sessions. **Decide deliberately: either mirror the load-bearing
> process lessons cross-repo, or accept the asymmetry knowingly.**

## 3. New / edited skills

| Skill | Guard to add | Prevents | Tier |
|-------|--------------|----------|------|
| `present-options` | A mandatory **"Premise check"** section at the top: state the premise, name where you verified it against code/corpus, before any option. | M1 | A |
| `handle-falsification` | When falsified, explicitly ask: *was the picked option wrong, the enumeration wrong, or **the premise/framing wrong**?* — and feed that back. (Partly there; make the premise branch explicit.) | M1, M2 | A |
| `iterate-construction-hypothesis` | Add the **qiyas-diff → deterministic .bkr edit** mapping + the per-iteration **construction-issue vs qiyas-bug vs bikar-DSL-gap** triage checklist the loop kept asking for. | §5 open alternative | B |
| `iterate-detector-calibration` | Add a "**did the knob actually move?**" assertion (the tolerance-sweep no-op witness) — verify the constant changed before trusting a sweep. | M6 / qiyas#18 | A |
| (new) `loop-idle-audit` or a `learn-new-pattern` guard | The idle-vs-blocked test from R3, run at each idle tick. | M4 | A |

## 4. Approach-level recommendations (beyond tenets/skills)

1. **Close the gap between "round-trip validator" and "inference engine."** We
   have built an excellent producer-checked round trip (I1, ARI=1.0) but have
   **never run the actual image→DSL inference (I2, #303/#304)**. Picking up I2 —
   even a thin first slice on one synthetic photo — is what makes the project
   match its own stated goal. Expected payoff: validates the whole premise on a
   real input. Answers retro §1 cap-1 and §5. `[A]`

2. **Lift the medallion-10 girih ceiling producer-side, not detector-side.**
   File/implement the bikar substitution-rule primitive (Lu-Steinhardt table)
   per `girih-substitution-rule-engine.md`; a gap-free render is far easier to
   detect than three hand-authored approximations. Answers retro §3 + §5. `[A]`

3. **Stand up the auto-generated training pipeline** (bikar emits patterns with
   known GT → qiyas verifies at scale, + B-AFF affine matching). Turns
   one-pattern-at-a-time iteration into a measurable corpus-level signal and is
   the natural substrate for I2. Answers retro §5. `[B]`

4. **Define the loop's terminal condition.** The "loop until we address all
   issues" directive had its terminal condition questioned repeatedly. Make
   "loop-until" explicit (e.g. qiyas composite ≥ threshold AND review-portal
   verdict recorded AND no open owner-gate) so the loop knows when it is done vs
   idling. Answers retro §4 M4 + §5. `[B]`

---

## Application checklist (for the owner, after approval)

- [x] R1/R3/R4/R5 tenet edits applied to all three `CLAUDE.md` (shared wording, mirrored). — **Done** as tenets C1–C5 (R1→C1, R2→C2, R3→C3, R4→C4, R5→C5), all three `CLAUDE.md` (verified `grep "C1 —"` ×3, count 5 each).
- [x] R2 + §2 memory files written and linked from each repo's `MEMORY.md` (decide mirror-vs-accept-asymmetry). — **Done.** R2 (`validate_premise_before_options`) shipped in qiyas + bikar by the cascade; this session added `metric_temptation_at_plateau` + `idle_vs_blocked_loop_test` to all three repos' `memory/` + `MEMORY.md`. **Mirror chosen knowingly** (per §2's directive): these are load-bearing process lessons, so they are mirrored, not asymmetric.
- [x] `present-options` + `handle-falsification` premise-check guards added. — **Done** by the cascade (`present-options` §0 Premise check; `handle-falsification` L0 branch + `dead_end:` step). Verified present in the SKILL.md files.
- [x] `iterate-detector-calibration` "did the knob move?" assertion added. — **Done** this session. Note: the skill lives in **qiyas** (`qiyas/.claude/skills/iterate-detector-calibration/SKILL.md`), not sacred-patterns as the handoff assumed; the assertion (the qiyas#18 module-shadowing no-op witness) was added in Step 2 + Trigger 1 there.
- [x] Decide I2 (#303) + girih primitive sequencing on the routing doc. — **Done** this session. I2 #303/#304 confirmed still filed + trigger-gated; girih confirmed filed (`bikar/.claude/plans/girih-substitution-rule-engine.md` + `bikar/docs/decisions/2026-05-28-medallion10-girih-ceiling.md`); both + the training pipeline (task #5) + the new `loop-terminal-condition` decision sequenced in the 2026-06-07 entry of `qiyas/.claude/plans/post-i1-task-routing.md`.
- [x] This doc marked `status: APPLIED <date>` with the commit sha. — **Done** (date 2026-06-07). SHAs deferred to commit time: both the cascade and this session are uncommitted in the working tree (no push without owner OK); the SHA placeholders are in the "Application status" callout at the top of this doc.

### Items deliberately deferred (not part of these two sessions)

- **§4.1 — I2 photo cascade build** — deferred; tracked as I2 #303/#304 (trigger/owner-gated). Confirmed filed, NOT built (the handoff scoped §C to confirm-and-sequence, not build).
- **§4.2 — girih substitution-rule primitive build** — deferred; tracked in `bikar/.claude/plans/girih-substitution-rule-engine.md`. Confirmed filed, NOT built.
- **§4.3 — auto-generated training pipeline build** — deferred; scoped in `bikar-as-training-data-generator.md`, filed as task #5. Captured scope + the "natural substrate for I2" rationale, NOT built.
