---
name: handle-falsification
description: Run after an attempted implementation of a decision-doc recommendation gets falsified (test failure, regression, dropped invariant, owner-rejected behaviour). Reopens the doc with a structured falsification log, introspects whether the picked option was wrong vs. the option enumeration was wrong vs. the doc's framing question itself was wrong, runs fresh web-search for options the original doc missed, captures the meta-lesson as cross-repo memory, and decides whether to author a new option locally or escalate to the owner. Companion to `present-options` and `decision-doc`.
user_invocable: true
argument: "<decision-doc-path-or-slug>"
---

# handle-falsification

A decision doc records *what was considered*; this skill records *what we learned when the picked option didn't work*. Falsification is the most expensive evidence a session produces — losing it (or treating it as just "try harder") is the failure mode this skill exists to prevent.

The shape of the failure this skill names: an option ships, breaks something, gets reverted, the agent reaches for a 2nd variant of the same option, that breaks too, and only then does someone notice the original doc's framing was wrong. The bikar#426 Option C cascade (2026-05-19, Variants 1 and 2 falsified the same day before the audit gap was diagnosed) is the canonical example.

## When to invoke

Trigger this skill the moment an implementation of a decision-doc recommendation gets falsified. Concretely:

- A test fails that the doc's "verification" or "what would change this recommendation" section said would pass.
- A corpus sweep shows a regression the doc didn't anticipate.
- An owner rejects the shipped behaviour or pauses it for redesign.
- A second variant of the picked option fails for the same root reason as the first (tenet 7 stop rule fired).
- A consumer audit / impact analysis the doc relied on turns out to have missed a contract surface.

**Don't invoke this skill for:**
- Trivial bug fixes inside a picked option's implementation (a typo, a missing edge case) that don't change the option's *premise*. Fix and ship.
- Falsification of an *exploratory* probe that was never proposed as the recommendation. The probe served its purpose.

The trigger is: the doc said X would work, X didn't work, and the question of "what now" is non-trivial.

## When to STOP and apply this skill instead of continuing

Mid-session, if you hit any of these, halt and run this protocol:

- You're about to try a 3rd variant of the same option after two have falsified.
- You're about to author a "small tweak" to make the picked option green that wasn't in the doc.
- You're about to write the lesson as a one-line task description and move on.
- You catch yourself thinking "the doc was basically right, I just need to..."

The cost of running this skill is ~30-60 minutes. The cost of skipping it is the next agent rediscovering the same dead-end from scratch, or shipping a tuned-to-fit fix that calcifies the wrong framing.

## Inputs

- `<decision-doc-path-or-slug>`: the falsified decision doc (e.g. `bikar/docs/decisions/2026-05-19-face-extractor-origin-coincidence-fix.md`).
- The current falsification context: what was tried, what broke, what evidence surfaced.

## The protocol — 6 steps

Steps 1-3 are mandatory. Steps 4-6 depend on step 3's introspection verdict.

### Step 1 — Reopen the doc with structured frontmatter

Update the frontmatter:

```yaml
status: REOPENED YYYY-MM-DD — <Option-Letter> falsified (<one-phrase reason>)
decided: PENDING
owner: PENDING  # if owner direction is required; otherwise keep prior owner
```

Append a new top-level section to the body:

```markdown
## Falsification log

### YYYY-MM-DD — Option <Letter> falsified

**What was tried:** <concrete implementation, 1-3 sentences>

**How it failed:** <the test/symptom/regression, with the load-bearing measurement>

**Root reason (current best understanding):** <why the option couldn't work — be honest, not optimistic>

**What this falsifies in the doc:**
- [ ] The picked option's mechanism (Option <Letter> §<subsection>)
- [ ] The option enumeration (a viable Option <Letter+1> was missing)
- [ ] The doc's framing question (§4 asked the wrong thing)
- [ ] The audit / impact analysis the doc relied on (§<subsection>)

**Falsification artifacts:** <commit hash of the revert, links to test output, probe scripts>
```

The checkbox quadrant in "what this falsifies" is the introspection — step 3 fills it in. Until then, leave it unchecked.

Also update `docs/decisions/README.md` to reflect the REOPENED status.

### Step 2 — Codify the falsifying witness as a test

If the falsification surfaced a witness (a hand-run command, a probe script, a smoke comparison), it must become a vitest/pytest test *before* the next variant is attempted. This is tenet 18 (codify every debug witness as a test) applied to the falsification side.

The test asserts the *invariant the witness probed*, not the symptom narrative. Example: if Option C dropped X-petal lens faces from 6 → 0, the test asserts "petal-N-ring N=4 emits N lens faces," not "petal-N-ring N=4 doesn't regress."

If the witness requires non-trivial scaffolding, file a tracked task `blockedBy` the next-variant attempt, and name the task ID in the falsification log entry. **The witness must outlive this session even if the test ships in a follow-on PR.**

### Step 3 — Introspect: which layer of the doc is wrong?

This is the load-bearing step. The same falsification can mean very different things at different layers:

| Layer wrong | Symptom in the falsification | What to do next |
|-------------|------------------------------|-----------------|
| **L1: Implementation of the picked option** | The option's *mechanism* was right but the code had a bug (off-by-one, wrong variable, missed call site). | Fix the code and re-ship. **This is NOT the failure mode this skill handles.** If you're confident it's L1, leave a one-line note in the falsification log and continue implementation. Do not reopen the doc. |
| **L2: The picked option itself** | The mechanism cannot work as the doc described. The doc's reasoning was wrong on a checkable claim (e.g., the audit said "consumer X has no implicit invariants," but consumer X turned out to have one). | Cross out the option in the doc (don't delete — keep the trail), author Option E with the corrected mechanism per step 5, and re-recommend. Steps 4-6 apply. |
| **L3: The option enumeration** | The mechanism *could* work but isn't the right move; an option not in the original doc is now obviously better (e.g., the doc framed the choice as "fix the consumer or accommodate at the producer," missing "lift the invariant into a higher layer that owns both"). | Author the missing option per step 5. Steps 4-6 apply. |
| **L4: The doc's framing question** | The doc asked the wrong question. The symptom that triggered the doc is a *manifestation* of a deeper question that the doc didn't surface (e.g., doc asked "how do we unify vertex identity in the kernel?" but the deeper question is "is vertex identity a kernel concern or a DSL concern?"). | The doc is structurally wrong. Author a *new* decision doc (don't try to retrofit the old one) per the `present-options` skill, citing the falsified doc as the trigger. Mark the falsified doc `SUPERSEDED-BY <new-doc-link>`. Steps 4-6 apply to the new doc. |

Check the relevant checkbox in step 1's quadrant. **If you check L3 or L4, the prior recommendation isn't just wrong — the prior reasoning process missed something. That's the meta-lesson step 6 captures.**

If you check more than one box, that's fine — falsifications often expose multiple layers at once. The bikar#426 Option C falsification checked L2 (the mechanism couldn't preserve lens construction) *and* the audit subbox (the consumer audit missed upstream construction contracts).

### Step 4 — Fresh web-search for options the original doc missed

Falsification is the trigger to re-search the space, with the new evidence as input. The original doc's web-research was done before the falsification surfaced what was actually load-bearing. Now you know more.

Re-search with at least:
- **The specific failure mode** (e.g., "DCEL multi-curve vertex coincidence policy" — not just "DCEL").
- **Canonical implementations in mainstream libraries** that have likely solved this exact problem (CGAL Arrangement_2, JTS, Mapbox geometry libs, Pydantic discriminated-union patterns, etc.).
- **Counter-precedents** — when canonical libs *chose not* to solve it the way the falsified option proposed, the reason they gave is often the same root cause the falsification just exposed.

The bar: at least 3 web-searches per re-search pass, with at least one canonical-implementation citation and at least one counter-precedent citation. Cite as markdown links in the new option's "Web research" block, same shape as `present-options` §5.

If the search returns "no canonical precedent for this case," that's signal: the falsification may have surfaced genuine novel territory, and the new option needs an explicit decision-doc footer noting this. Don't fabricate citations.

### Step 5 — Author the new option(s) inside the reopened doc

For each new option the introspection + web-search surfaced, append a new option block to the doc's §5 using the same shape as `present-options` (layman, what changes, web research, pros, cons, cost, tenet alignment, closes/leaves-open questions).

**Critically:** the new options must include any of these that apply:
- An option that addresses the L2/L3/L4 layer-wrong root the introspection identified, not just the surface symptom.
- An "escalate to owner" option naming the specific question owner direction would answer. (This is often the right option when L3 or L4 was checked.)
- A "do nothing and revisit when X changes" option with X named (a cascade close, a corpus state, an upstream decision).

Update the doc's §6 (recommendation) and §7 (what would change this recommendation) to reflect the new option set. The old recommendation stays in the doc (for audit) with a `~~strikethrough~~` and a one-line note linking to the falsification log.

### Step 6 — Capture the meta-lesson as cross-repo memory

The falsification taught something about *how the original reasoning went wrong*. That's not a per-repo fact; it's a process correction that applies to future audits, doc authoring, and cascade design across qiyas + bikar + sacred-patterns.

Write a `feedback`-type memory entry (per the auto-memory instructions in the global CLAUDE.md). The entry's body follows the standard feedback structure:

```markdown
---
name: <one-line rule the lesson teaches>
description: <one-line description for relevance matching in future conversations>
type: feedback
---

<The rule itself — one sentence stating what to do or not do>

**Why:** <The incident — name the cascade, the date, the falsification artifact path. Include a quotable detail so future-you can verify the memory against the codebase>

**How to apply:** <When this rule kicks in — what the next agent should check / do / not do>

(optional) **Companion to:** <list relevant tenets or other memories this strengthens>
```

Then add a one-line pointer to `MEMORY.md` per the memory contract.

**The lesson goes into memory, not into a per-repo lessons doc, when:** the failure mode is process / reasoning / audit-shape, not a code-level invariant. Code-level lessons (a specific SVG sweep-flag gotcha, a face-extractor coincidence quirk) go to the relevant repo's `docs/lessons.md` per that repo's conventions; process lessons go to memory because they're cross-repo by nature.

The bikar#426 falsification produced `feedback_consumer_audit_construction_contracts.md` — that's the shape: a rule about *how to do consumer audits in the future*, not a rule about the face-extractor.

## Escalation gate — when to author a 4th option locally vs hand back to owner

After steps 1-5, you have a reopened doc with new options. The question is whether to attempt the new recommendation in code or to hand back. The gate:

**Attempt locally if all hold:**
- The new option is L2-layer (mechanism correction within the doc's framing question) — i.e., step 3 checked L2 only, not L3 or L4.
- The new option's recommendation aligns with prior owner direction on adjacent decisions (e.g., the owner already established the tradeoff weighting that points to this option).
- Total falsified-variants count so far is ≤ 2 (tenet 7 stop rule: after 2 reversals, escalate).
- The new option can be verified end-to-end in this session (full test suite, not curated sweep).

**Escalate to owner if any hold:**
- Step 3 checked L3 or L4. The framing or option-set was wrong, which means the next move depends on owner intent, not just code correctness.
- Two variants of two different options have falsified in the same cascade. The cascade itself may be miscued.
- The new option requires a tradeoff the doc didn't surface (cost, scope, public-facing impact, cross-repo coupling).
- The new option's recommendation contradicts a prior owner-accepted decision on an adjacent doc.

When escalating, the hand-back is the reopened doc itself plus a `PushNotification` summarizing: which option(s) falsified, which layer was wrong (per step 3), the new options surfaced, and the specific question owner direction would answer. Don't pre-pick; let the owner pick.

## Anti-patterns this skill exists to prevent

- **"Try harder" loops** — attempting Variant 2, 3, 4 of the falsified option without reopening the doc. Each variant burns a session and the next agent has no record of why earlier ones failed.
- **Silent reopens** — fixing the code without updating the doc's status, so the registry still lists ACCEPTED while the implementation is reverted.
- **Meta-lesson loss** — capturing the code-level fix in a commit message and moving on, while the *process* lesson (how the audit missed it) lives nowhere.
- **Goal-seeking introspection** — checking L1 ("just an implementation bug") because L2/L3/L4 would require more rework. The honest verdict is the load-bearing one; if you're not sure, default to the deeper layer.
- **Fabricating Option E** — authoring a "compromise" option to close the doc without doing the web-search step. Compromise options drawn from local reasoning alone repeat the original doc's blind spots.
- **One-doc closeout** — treating the falsification as resolved when the new option ships, without writing the cross-repo memory. The next falsification (different cascade, same shape) won't be prevented.

## Output

After running this skill:

1. The reopened decision doc has the structured falsification log section, status updated, and new options drafted (or `SUPERSEDED-BY` if L4 triggered a new doc).
2. The `docs/decisions/README.md` row reflects the new status.
3. The falsifying witness is a tracked test (committed or filed as a follow-on task).
4. A `feedback`-type memory entry captures the process lesson, indexed in `MEMORY.md`.
5. Either: the next variant is being implemented per the local-attempt gate, OR a `PushNotification` has handed back to the owner with the specific question.

## Verification

Before considering the skill done, check:

- [ ] Decision-doc frontmatter status reflects REOPENED with date + Option letter + reason.
- [ ] Falsification log section has all four subsections filled (what was tried, how it failed, root reason, what it falsifies — with at least one checkbox checked).
- [ ] Falsifying witness is either a test in the repo OR a tracked task ID named in the log.
- [ ] At least one new option block authored (or SUPERSEDED-BY link added).
- [ ] At least 3 web-searches cited across the new option block(s); at least one canonical-implementation citation; at least one counter-precedent citation OR explicit "no precedent found."
- [ ] Cross-repo `feedback`-type memory entry written and indexed in `MEMORY.md`.
- [ ] Either: next-variant work has started locally with the gate's four conditions satisfied, OR an owner handback has been sent.

If any check fails, the skill is not done. Don't ship the new option until the doc, the test, and the memory are aligned.

## Sources / canonical references

- `present-options` skill (sacred-patterns) — the upstream skill this one operates on.
- `decision-doc` skill (sacred-patterns, legacy name) — earlier version of present-options; same protocol.
- Tenets 2 (root cause), 4 (verify before claiming done), 7 (don't tune to fit), 17 (prove the primitive first), 18 (codify every debug witness), 19 (bias for action — and its stop rule for when to escalate).
- The auto-memory contract in global CLAUDE.md governs the memory-write step.
- The bikar#426 Option C cascade (2026-05-19) is the canonical worked example; the doc + falsification log are the reference implementation of this skill's output shape.
