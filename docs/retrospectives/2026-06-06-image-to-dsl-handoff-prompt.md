# Handoff prompt — validate retrospective, audit decisions, plan the hardening

> Paste everything in the fenced block below into a fresh session (run it from
> the sacred-patterns repo, which has cross-repo access to qiyas + bikar).
> Nothing gets applied — Phases 1–2 produce reports; Phase 3 plans the edits and
> stops for approval.

````
Task: Validate the image→DSL retrospective via prior art, AUDIT our decision-doc corpus for coverage + contradictions, then plan how to harden CLAUDE.md tenets + memories so we remember key decisions/dead-ends and never silently re-decide or contradict ourselves.

Read first:
- sacred-patterns/docs/retrospectives/2026-06-06-image-to-dsl-retrospective.md — findings, §3 dead-ends, §4 repeated mistakes
- sacred-patterns/docs/retrospectives/2026-06-06-image-to-dsl-recommendations.md — proposed edits (all PROPOSED, nothing applied)
- sacred-patterns/.claude/skills/retrospect-hard-problem/ — the pipeline + its artifacts/{qiyas,bikar,sacred-patterns}/ground_truth.json (already-indexed: 61 decision docs w/ status+rationale+cross-refs)

Phase 1 — Prior-art validation:
/deep-research
  Question: "For recovering a parametric/generative DSL of an Islamic geometric pattern from an image (the inverse problem): is our producer-checked round-trip approach (retro §1) consistent with published prior art, and are our recorded dead-ends (retro §3/§5 — girih hand-authoring, derotation-by-shape-count, raster-fold-as-honest, clip-primitive variants, I2 photo cascade) genuinely dead or solved elsewhere (Lu-Steinhardt substitution, turning-function/graph matching, synthetic-GT training)?"
  -> save to sacred-patterns/docs/retrospectives/2026-06-06-image-to-dsl-priorart.md; mark each finding/dead-end Confirmed / Refuted / Open-in-field. Curate sources into each repo's docs/citations.md.

Phase 2 — Decision-coherence audit (the gap the retrospective skipped — DEEP-READ the docs, not just status):
- Cover ALL 61 decision docs (qiyas/docs/decisions 40, bikar 18, sacred-patterns 3). The retrospective only status-indexed them; this phase reads bodies.
- For each topic cluster sharing a problem-tag (known offenders: face-class x7, petal/ring x4, scope x5, shape x3), determine: are the multiple ACCEPTED docs coherently LAYERED, or do any CONTRADICT each other (one says X, a later one assumes not-X without superseding it)?
- Flag every doc whose frontmatter status contradicts its own body (retro §4 M2 found >=1: ACCEPTED-in-frontmatter / PENDING-in-body), and every reversal that was NOT marked SUPERSEDED/REOPENED (only 3 of 61 are marked — suspiciously low).
- Output: sacred-patterns/docs/retrospectives/2026-06-06-decision-coherence-audit.md = a table of {topic, docs, verdict: coherent | contradictory | stale-status | duplicate, the authoritative doc, what to reconcile}.

Phase 3 — Plan the hardening (enter plan mode; nothing applied until approved):
Address ALL of: (a) are key decisions remembered? (b) full decision coverage? (c) contradictory decisions? plus the dead-end-memory problem.
- A durable, consultable DEAD-ENDS + DECISIONS ledger: decide its home (auto-memory is per-machine/invisible cross-repo — SP has 87, qiyas/bikar 4 each; checked-in beats it for shared facts) and format. It must let any future session check "has this been tried/decided/falsified?" BEFORE re-deciding — directly attacking retro §4 M1/M2.
- A decision-doc hygiene mechanism so contradictions can't accrue silently: a supersede-on-reversal rule, a "one authoritative doc per problem-tag" index, and/or a pre-commit/hook check that frontmatter-status matches body + that a new doc on an existing tag must cite/supersede the prior one.
- The tenet diffs (per CLAUDE.md, shared wording), the skill guards (present-options/handle-falsification get a premise-check + "search the ledger for prior decisions/dead-ends" step), each tied to a retro §4 mistake AND a Phase-1 prior-art verdict + a Phase-2 audit finding.

Out of scope: applying any edits (plan only); re-running the full retrospect pipeline unless a finding needs deeper transcript evidence.

Success criteria:
- Prior-art report tags every dead-end Confirmed/Refuted/Open.
- Coherence audit covers all 61 docs and names every contradiction/stale-status/duplicate + the authoritative doc per topic.
- Approved plan answers, concretely: "are we remembering key decisions + dead-ends, did we cover them all, do we contradict ourselves" — each with the mechanism that fixes it going forward.
````
