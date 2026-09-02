# Handoff prompt — finish the remaining image→DSL retrospective items

> Paste the fenced block into a **fresh, clean session** started from
> `/Users/omareid/Workspace/git/sacred-patterns` (it has cross-repo access to
> `../qiyas` + `../bikar`). This finishes the retrospective's recommendations that
> the 2026-06-06→07 **decision-memory cascade did NOT already ship**. Read the
> "Already done" list first so you don't redo work.

## Context for the operator (not part of the paste)

The decision-memory cascade (2026-06-07) already shipped, from
`2026-06-06-image-to-dsl-recommendations.md`:
- **R1–R5 tenets** → mirrored verbatim as tenets **C1–C5** in all three `CLAUDE.md`.
- **R2 / §2 premise memory** → `feedback_validate_premise_before_options.md` written into qiyas + bikar `memory/` and indexed.
- **§3 `present-options`** → mandatory **§0 Premise check** + structured frontmatter added.
- **§3 `handle-falsification`** → explicit **L0 (premise was wrong)** branch + `dead_end:` step added.
- I2 (#303) and the girih primitive → filed as tracked tasks (NOT built).
- Plus the whole net-new decision-memory layer (typed `DecisionFrontmatter`, generated `LEDGER.md` ×3 + xrepo, CI-blocking `check-decision-coherence.sh`, `tags.yaml`, `docs/decision-schema.md`).

So the block below covers ONLY the leftovers: two more memory files, three skill guards, the approach-level items, and closing out the recommendations doc.

````
Task: Finish the remaining items from the image→DSL retrospective's recommendations doc that the 2026-06-07 decision-memory cascade did NOT already ship. Apply the leftover memory files + skill guards, scope the approach-level items, and mark the recommendations doc APPLIED.

Already done (DO NOT redo — verify briefly, then skip): R1–R5 tenets (shipped as C1–C5 in all three CLAUDE.md); feedback_validate_premise_before_options.md (qiyas + bikar memory/); present-options §0 premise check; handle-falsification L0 branch + dead_end step; I2 (#303) and girih primitive filed as tasks. Confirm these exist (grep the CLAUDE.md files for "C1 —", check the memory/ dirs, check the two skills) so you build on them, then move to the leftovers.

Read first:
- sacred-patterns/docs/retrospectives/2026-06-06-image-to-dsl-recommendations.md — the authoritative list. §2 (memory files), §3 (skills), §4 (approach-level), and the Application checklist at the bottom. Status is still PROPOSED.
- sacred-patterns/docs/retrospectives/2026-06-06-image-to-dsl-retrospective.md — §4 (M4 idle-vs-blocked, M6 metric-temptation) and §5 (open alternatives) for the WHY behind each leftover.
- The global CLAUDE.md auto-memory contract (frontmatter shape: name/description/metadata.type; body with **Why:** / **How to apply:**; index one line in MEMORY.md). Memory dirs are per-repo under ~/.claude/projects/<repo-slug>/memory/.
- docs/decision-schema.md (any repo) — if any leftover wants a decision doc, author it through the now-shipped mechanism (structured frontmatter keys, tag in tags.yaml, passes check-decision-coherence.sh).

LEFTOVERS TO SHIP:

A) §2 — two remaining memory files (the premise one is already done). Author + index in MEMORY.md, in ALL THREE repos' memory dirs (decide mirror-vs-asymmetry knowingly, per the §2 note — recommend mirroring since these are load-bearing process lessons):
   - feedback_metric_temptation_at_plateau.md — "When a score plateaus, the reflex to raise counts / tune a constant / over-fit a fixture is exactly the moment Tenet 7 (don't tune to fit) governs — stop and fix the cause." Why: M6 recurred DESPITE the tenet; the tenet names the rule but not the trigger-moment. How to apply: at any plateau, before touching a threshold, name the root cause you're NOT fixing.
   - feedback_idle_vs_blocked_loop_test.md — the operational idle-vs-blocked test (R3 wording): in an autonomous loop, before idling, name the specific unfired trigger OR the named blocker; "nothing to do" without one of those is a tell you haven't looked. Why: M4 recurred across many ticks with no operational test. How to apply: each idle tick must cite the trigger it's waiting on or the task# blocking it.
   (Cross-link these to the C-tenets and [[validate-premise-before-options]].)

B) §3 — three skill guards (the present-options + handle-falsification ones are already done):
   - sacred-patterns/.claude/skills/iterate-detector-calibration/SKILL.md — add a "did the knob actually move?" assertion: before trusting a tolerance/threshold sweep, verify the constant CHANGED at the call site (the qiyas#18 witness was a no-op sweep that set the tol on a re-exported function object via module shadowing — it measured default behavior and produced a self-inflicted false-green). Add the witness as a stop-rule: after a sweep shows "no movement," first prove the knob is wired before concluding "the knob doesn't matter."
   - sacred-patterns/.claude/skills/iterate-construction-hypothesis/SKILL.md — add the per-iteration triage checklist the loop kept asking for: when qiyas-diff shows a gap, classify it as (construction issue | qiyas detector bug | bikar DSL gap) BEFORE editing, and add the qiyas-diff → deterministic .bkr-edit mapping. (Compose with the existing "Routing — which fix is this?" five-way table; don't duplicate it.)
   - A new loop-idle guard — either a new `loop-idle-audit` skill OR a guard inside the learn-new-pattern orchestrator — that runs the §A idle-vs-blocked test at each idle tick. Pick the lighter-weight home; wire it to the feedback_idle_vs_blocked_loop_test memory.

C) §4 — approach-level items. These are bigger; SCOPE them (don't necessarily build), and for each, file/мupdate a tracked task + a one-line entry on the routing doc (qiyas/.claude/plans/post-i1-task-routing.md or the SP equivalent). I2 (#303) and the girih primitive are already filed — just confirm and add the other two:
   1. Loop terminal condition (§4.4 / M4) — DEFINE it concretely and write it down (a short decision doc, tag e.g. `loop-terminal-condition`, authored through the shipped mechanism): e.g. "loop-until = qiyas composite ≥ threshold AND a review-portal verdict recorded AND no open owner-gate." This one is cheap and high-value — author the decision doc, don't just file a task.
   2. Auto-generated training pipeline (§4.3) — file a scoped task (bikar emits patterns with known GT → qiyas verifies at scale, + B-AFF affine matching). Don't build; capture scope + the "natural substrate for I2" rationale.

D) Close out the recommendations doc:
   - Mark sacred-patterns/docs/retrospectives/2026-06-06-image-to-dsl-recommendations.md `status: APPLIED <today>` with a one-line note + the commit sha(s) of this session and the decision-memory cascade.
   - Tick the Application checklist boxes that are now true; for any deliberately-deferred item, mark it deferred with the task# instead of a blank box.

Hard rules:
- Don't re-ship the already-done items. Verify-then-skip.
- Memory files follow the auto-memory contract exactly (frontmatter + Why/How-to-apply + MEMORY.md index line). Skill edits read the SKILL.md first (don't blind-overwrite).
- Any new decision doc MUST pass check-decision-coherence.sh (structured frontmatter, tag in tags.yaml, run `make ledger` after). Add the tag to tags.yaml in the same change if new.
- Track all of this as tasks. This is docs/skills/memory only — no source under src/ — so the qiyas make ci-local source gates don't apply, but if you author a decision doc, run the decision-coherence gate + `make ledger --check` (or `sh scripts/gen-decision-ledger.sh --check`) before declaring done.
- Don't commit/push unless I ask. When done, report what shipped per A/B/C/D and what was deliberately deferred (with task#s), then stop.

Definition of done:
1. §A: two memory files authored + indexed in all three MEMORY.md (or a knowingly-documented asymmetry decision if you don't mirror).
2. §B: three skill guards added (calibration knob-moved assertion, construction triage checklist, idle-vs-blocked guard).
3. §C: loop-terminal-condition decision doc authored (passes the coherence gate); training-pipeline task filed; I2 + girih confirmed filed; routing doc updated.
4. §D: recommendations doc marked APPLIED with sha(s); checklist reconciled.
5. Report A/B/C/D outcomes + deferrals; stop for my review.
````
