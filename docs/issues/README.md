# `sacred-patterns` issues archive

One markdown file per discovered issue. The directory exists so issues
get **named, options-listed, decided, and dated** rather than buried in
chat history or tracked only in TaskList descriptions. Parallel structure
to `qiyas/docs/issues/` and `bikar/docs/issues/` — file in whichever repo
owns the *fix*, even if the symptom surfaced elsewhere.

## When to file

File an issue here when *any* of:

- A non-trivial issue surfaces with more than one plausible fix (parity
  divergence between sacred-patterns and qiyas/bikar, iteration-loop
  policy challenged by evidence, orchestrator contract under stress).
- An assumption baked into the iteration loop, interpret-pattern skill,
  or pattern-construction code is challenged by real-world evidence.
- A user-facing decision is forced by a discovery mid-iteration.

Do **not** file here for: trivial bugs (just fix them), scope deferrals
(track in TaskList or `.claude/plans/`), or open design questions before
any work has started (use `.claude/plans/`).

## File naming

`YYYY-MM-DD-short-slug.md` — sortable, dated, scannable.

## Required structure

Every issue file MUST include (per `CLAUDE.md` → "Workflow Conventions"):

1. **Status** — `OPEN`, `RESOLVED YYYY-MM-DD`, or `WONTFIX YYYY-MM-DD`.
2. **Discovered** — when, by whom, what surfaced it.
3. **Symptom** — concrete observation with reproducer where possible.
4. **Root cause** — established by investigation, not speculation.
5. **Options considered** — every option with pros / cons / cost,
   including the option you didn't take. This section is load-bearing:
   the point of filing is so future readers can see what was weighed,
   not just what was picked.
6. **Decision** — which option, why, who decided.
7. **Follow-ups** — task IDs, backlog entries.

Don't delete resolved issues; they're the archive.

## Cross-repo issues

When an issue belongs to a sibling repo (e.g., a qiyas detector bug
surfaced during a sacred-patterns iteration), file it in that repo's
`docs/issues/` directory. Cross-reference both ways: the local task in
TaskList should mention `qiyas#NN` or `bikar#NN` so the linkage is
grep-able (see CLAUDE.md → "Cross-repo task linkage").
