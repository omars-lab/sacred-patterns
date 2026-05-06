---
name: decision-doc
description: Author a structured decision doc when work surfaces a non-trivial choice with multiple plausible paths. Captures every option (not just the picked one) with web-research-grounded pros/cons, layman summary, key open questions, and a final recommendation. Use this BEFORE recommending a path on any cross-repo, architectural, or root-cause-vs-workaround decision.
user_invocable: true
argument: "<topic-slug-or-issue-link>"
---

# decision-doc

Produce a decision doc that the owner (or future-you) can read cold and audit. The point is not to advocate for the recommended option — it is to capture *what was considered*, *why each option exists*, *what evidence informed the weighing*, and *what would change the picked answer*.

## When to invoke

Trigger this skill when work surfaces:
- A cross-repo design choice (touches qiyas + bikar + sacred-patterns).
- A root-cause-vs-workaround tradeoff (the classic shape covered by CLAUDE.md tenet 2).
- A spec edit vs. a code edit (the failure mode tenet 7 names — "tune until green" is one option, but should never be the *only* option you write down).
- A path choice where one option is "do nothing" or "accommodate at the consumer side."
- Any decision the user is likely to want to audit later — anywhere "why did we pick X over Y" would matter in three months.

**Don't invoke this skill for trivial fixes.** A bug fix with one obvious resolution is not a decision; it's an action. If you can name a single option without inventing alternatives, just do it. This skill exists for the moments when the *first* option that comes to mind isn't obviously the right one.

## When to STOP and write the doc instead of continuing

Mid-implementation, if you hit any of these, halt and apply this skill:
- You catch yourself about to recommend a path without having written the alternatives down.
- You catch yourself about to *not* surface alternatives because the picked one feels obvious.
- The user asks "why this and not X?" and you haven't answered X in writing yet.
- A choice would silently constrain future work (e.g., a threshold, an edge-key strategy, a schema field).

The cost of writing the doc is ~30 minutes. The cost of an unaudited decision is shipped code that the next agent can't safely touch.

## Inputs

- `<topic-slug-or-issue-link>`: a short kebab-case slug (e.g., `bikar-lens-face-emission`) or a path to a related issue / plan doc. The slug becomes the filename: `docs/decisions/YYYY-MM-DD-<slug>.md`.
- The current cascade context: which repos are involved, what just happened, what's being decided.

## Where it lives

- **Default:** `<repo-root>/docs/decisions/YYYY-MM-DD-<slug>.md` in the repo where the *decision* will be applied (not necessarily where the symptom surfaced — Option A might live in bikar even if the falsification happened in qiyas).
- **Cross-repo decisions:** put the canonical doc in the repo that owns the *fix*, and add a one-line cross-reference in the other repos' issue docs. Don't duplicate the body.
- If `docs/decisions/` doesn't exist in the target repo, create it. The first line of the directory's `README.md` (also create) should be: "Decision docs authored via the `decision-doc` skill in sacred-patterns."

## Required sections — in order

The order is load-bearing. Don't reorder; the doc should be readable top-down by someone who hasn't seen the conversation.

### 1. Frontmatter

```markdown
---
status: PROPOSED | ACCEPTED YYYY-MM-DD | REJECTED YYYY-MM-DD | SUPERSEDED-BY <link>
discovered: YYYY-MM-DD
decided: YYYY-MM-DD or "PENDING"
owner: <github handle or "PENDING">
related:
  - issue: <repo>/docs/issues/...
  - plan: <repo>/.claude/plans/...
  - cascade: <repo>/.claude/plans/...
---
```

### 2. Layman summary (two sentences max)

What's broken (or what choice we have) in plain English, no jargon. A non-technical reader should understand *what is at stake* before reading anything else. If you can't write it without using the term `DCEL` or `arc-bearing face`, you don't yet understand the decision well enough to write the doc — go re-read the symptom first.

### 3. Implications of getting this wrong

Three bullets max:
- What blocks downstream if we pick the wrong option?
- What rots silently if we don't pick at all?
- What's hard to undo once shipped?

This is the section that justifies the doc's existence. If none of these bullets is sharp, the decision probably doesn't need a doc.

### 4. Main questions we need answered

The *unanswered* questions, listed as questions, that the picked option hinges on. Every question must have a named target (who answers, or what experiment answers it). Examples:
- "Does CGAL's Arrangement_2 key edges by curve identity? — answer via web-search of CGAL docs."
- "Will the gt-emitter regression suite pass after the edge-key change? — answer by running the suite on a candidate branch."

If a question is unanswered at decision time, the picked option must explicitly tolerate that uncertainty (e.g., "ship behind a flag" or "land with a follow-up fixture").

### 5. Options considered

**Every option you considered, including the ones you rejected immediately.** If you only considered one option, you didn't do the work of this skill. Minimum: name 3 distinct options, including:
- The "do nothing / accommodate" option (even if obviously wrong — it forces the doc to articulate *why* it's wrong).
- The "fix the root cause" option.
- At least one "workaround" or "smaller scope" option.

For each option:

```markdown
### Option <Letter> — <imperative-verb-phrase>

**Layman:** one sentence on what this option does.

**What changes:** which files, which repos, which surfaces.

**Web research:**
- <claim from web search> — [<title>](<url>)
- ...
(2-4 bullets per option, naming canonical implementations or prior art. If
no relevant prior art exists, say so explicitly: "No canonical precedent
found; this is novel territory.")

**Pros:**
- ...

**Cons:**
- ...

**Cost:** <half day | 1 day | 2 days | unknown>

**Closes which questions from §4:** <list>
**Leaves open which questions:** <list>

**Tenet alignment:**
- Tenet 1 (simplicity): ...
- Tenet 2 (root cause): ...
- Tenet 7 (don't tune to fit): ...
- Tenet 8 (general problem): ...
(Only list the tenets the option touches. If an option violates a tenet,
say so plainly; don't soften.)
```

### 6. Recommendation

One option, named. Then 2-4 bullets on *why this one* — referencing the questions in §4 and the tenets in §5. If the recommendation isn't unanimous across criteria (e.g., it costs more but unblocks more), say so.

### 7. What would change this recommendation

A list of conditions under which a different option becomes correct. Examples:
- "If the bikar regression suite reveals a hidden dependency on vertex-pair edge identity, fall back to Option D."
- "If the cascade owner declines the cross-repo PR review, ship Option C with a 6-week deletion ticket."

This section is what makes the doc *audit-able*: future readers can check whether the conditions still hold.

### 8. Final decision

Either "PENDING — owner review required" or:

```markdown
**Decided:** YYYY-MM-DD by <handle>
**Picked:** Option <Letter>
**Rationale:** <2-3 sentences>
**Follow-ups:** <task IDs filed>
```

After a decision is made, update §1 frontmatter `status` and `decided` fields. Never delete the rejected options — they're the load-bearing record.

## Web search discipline

For each option, run at least one web search and cite the result. The search should target:
- **Canonical implementations** of the option's pattern (e.g., "how do mainstream computational geometry libraries handle X").
- **Prior-art critiques** of the workaround options (e.g., "why is goal-seeking calibration considered an anti-pattern in ML").
- **Independent witnesses** of the cost estimate (e.g., "how long does a typical DCEL edge-key migration take in similar codebases").

If a search returns nothing relevant, say so in the doc — that absence is signal. **Don't fabricate citations.** If you can't find prior art for an option, the doc should record "no canonical precedent found"; that's information.

Use the `WebSearch` tool. Include the URLs as markdown hyperlinks in the option's "Web research" section. Aggregate sources at the bottom of the doc in a `Sources:` section.

## Anti-patterns

- **Single-option doc.** "Here's the option I picked, here are some pros and cons." That's an advocacy memo, not a decision doc. Always name alternatives.
- **Goal-seeking option weighting.** Don't pre-decide and then pad the rejected options with weak cons. The reader should be able to flip to any rejected option and see a fair representation.
- **Burying the workaround tenet violation.** If Option C violates tenet 7, say "violates tenet 7" — don't write "introduces calibration coupling that may need future review." Plain language; tenets are named for failure modes, use the names.
- **Recommending the cheapest option by default.** Cost is one input; root-cause vs. workaround is another; tenet alignment is another. If the recommendation collapses to "cheapest" you've under-weighted the future cost of workarounds.
- **Skipping web search to save time.** The 30 minutes you save authoring the doc costs hours when the next agent can't tell whether the picked option was the canonical one or a local invention.

## Output

A single markdown file at the path defined in §"Where it lives", plus:
- A one-line entry in `docs/decisions/README.md` (create if missing) listing the new doc.
- An update to any related issue doc's "Options considered" section to point at the decision doc rather than re-listing options.
- (If applicable) A task created via TaskCreate for the picked option's implementation.

## Verification

Before considering the skill done, check:
- [ ] Layman summary readable by a non-technical reader.
- [ ] At least 3 options, including a "do nothing" or "accommodate" option.
- [ ] Every option has at least one web-search citation OR an explicit "no prior art found."
- [ ] Tenet alignment named explicitly per option.
- [ ] Recommendation references §4 questions and §5 tenets, not just intuition.
- [ ] "What would change this recommendation" section is non-empty.
- [ ] Frontmatter `status` reflects whether owner has decided.

If any check fails, the doc is not ready. Don't ship it just to clear the task.
