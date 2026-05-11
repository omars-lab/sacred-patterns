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

**Presentation — concrete shape:** the actual artifact this option produces,
shown in a form the reader can audit. Pick the form that matches the
decision class:
  - Schema/contract decisions: a JSON/code block showing the exact field
    shape (key names, types, example values).
  - Algorithm decisions: pseudocode or a 5–10 line sketch of the core loop.
  - Architecture decisions: a tree/diagram of files+modules+arrows.
  - Process decisions: the smallest concrete example run end-to-end.
This section is NOT a re-paraphrase of "What changes" — it's the *artifact
the reader would see in a diff* if this option were picked. The reader
must be able to compare Option A's shape against Option B's shape
side-by-side and tell them apart at a glance.

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

## Web search discipline — HARD PRECONDITION for the Recommendation

**No Recommendation section may be written before web search is complete for every option.** This is a gate, not a guideline. The recommendation that comes out of local reasoning alone is the recommendation most likely to flip after the user asks "did we websearch this?" — which has happened, and which is the failure mode this gate exists to prevent.

For each option, run at least one web search BEFORE writing §6 (Recommendation) and cite the result. The search should target:
- **Canonical implementations** of the option's pattern (e.g., "how do mainstream computational geometry libraries handle X", "RFC for JSON canonicalization", "PROV canonical form").
- **Prior-art critiques** of the workaround options (e.g., "why is goal-seeking calibration considered an anti-pattern in ML", "metadata as ground truth pitfalls").
- **Independent witnesses** of the cost estimate (e.g., "how long does a typical DCEL edge-key migration take in similar codebases").

**Why this gate exists:** local reasoning systematically under-weights options that match a canonical pattern named in literature, because the canonical pattern's *advantages* aren't visible from inside the codebase — they're visible in the citations that converge on the same shape. The 2026-05-11 `pattern-identity-signature-shape` decision is the case in point: the first draft recommended Option A from local reasoning; after three WebSearch calls surfaced RFC 8785, Peel et al. 2017, and PROV Canonical Form, the recommendation flipped to Option C — same evidence base, different ranking, because prior art changed which costs were load-bearing.

If a search returns nothing relevant, say so in the doc — that absence is signal. **Don't fabricate citations.** If you can't find prior art for an option, the doc should record "no canonical precedent found"; that's information.

Use the `WebSearch` tool. Include the URLs as markdown hyperlinks in the option's "Web research" section. Aggregate sources at the bottom of the doc in a `Sources:` section.

**Self-check before writing §6:** for each option, can you cite at least one source (or an explicit "no prior art found")? If any option still has empty Web research, return to WebSearch — do not advance.

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

## Post-ACCEPT — keep the mental model current

When (and only when) status flips to `ACCEPTED`, update the relevant
repo's mental-model doc with a one-paragraph **principle** + link to
the full decision. This is what makes the decision *operational* — the
mental model is what future agents read on day one; the decision doc
is the audit trail they consult on day N when something looks
arbitrary.

Target docs:
- qiyas → `qiyas/docs/dev-mental-model.md` §"Decisions that shaped this codebase"
- sacred-patterns → `sacred-patterns/docs/dev-mental-model.md` (create the section if missing — same shape)
- bikar → `bikar/docs/dev-mental-model.md` (same)

What the entry must contain:
1. A short H3 heading naming the *durable rule* in imperative or
   declarative form. Not the option letter, not the symptom, not the
   pattern — the rule. ("`face_class` is the sole class-selector"
   beats "iter-8 face_class vs multiset.")
2. One paragraph (3–6 sentences) on what the rule means and why it
   generalizes beyond the originating instance. Distill, don't copy.
3. Trailing `→ [date — slug](decisions/YYYY-MM-DD-slug.md)` link.

If a previously-ACCEPTED decision is **superseded**, mark the entry
`(SUPERSEDED by [...])` rather than deleting it — the audit trail
includes the superseded principle for future readers wondering why
something *isn't* the case anymore.

## Verification

Before considering the skill done, check:
- [ ] Layman summary readable by a non-technical reader.
- [ ] At least 3 options, including a "do nothing" or "accommodate" option.
- [ ] Every option has at least one web-search citation OR an explicit "no prior art found."
- [ ] Tenet alignment named explicitly per option.
- [ ] Recommendation references §4 questions and §5 tenets, not just intuition.
- [ ] "What would change this recommendation" section is non-empty.
- [ ] Frontmatter `status` reflects whether owner has decided.
- [ ] **If status is ACCEPTED:** mental-model doc updated with a principle entry per "Post-ACCEPT" above.

If any check fails, the doc is not ready. Don't ship it just to clear the task.
