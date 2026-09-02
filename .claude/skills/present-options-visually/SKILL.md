---
name: present-options-visually
description: Build an interactive decision-picker HTML page for a batch of owner decisions — every option described in BOTH plain terms and technical language, visuals where the choice is geometric, recommendations pre-selected, and a copy-button that assembles a paste-back prompt which applies the picks through the decision-memory machinery. Use when ≥2 owner decisions are queued, or when the owner asks to see/pick options visually.
---

# Present options visually — the decision-picker recipe

Turn a queue of owner decisions into one self-contained HTML page where the
owner clicks picks and copies back a single prompt that, pasted into Claude
Code, applies everything through the decision-memory machinery (frontmatter
→ ledgers → follow-on work). Canonical worked example:
`docs/decision-picker.html` + `docs/decision-picker-assets/` (the
2026-06-10 queue).

## When to use

- ≥2 owner-gated decisions have queued up (the batch-drain pattern — one
  owner sitting clears the board; proven 2026-05-24 in prose, upgraded to
  this UI 2026-06-10).
- The owner asks to "see the options," pick visually, or wants a copyable
  outcome.
- A single decision with strongly visual options (geometric choices)
  also qualifies — one card is fine.

Companions: `present-options` authors the underlying decision DOCS (the
four-option weighing lives there; this page never replaces the doc);
`summarize-progress-visually` is the after-the-work mirror of this
before-the-work surface. The prose digest (`docs/owner-decision-queue.md`
style) can coexist — the page is the interactive layer on top.

## Hard rules

1. **Dual register on every option — no exceptions.** Each option carries
   `plain` (what it means for the project, zero jargon, consequences in
   everyday terms — the Tenet-29 grandma bar) AND `tech` (the precise
   engineering statement a future agent executes against). One without the
   other fails review: plain-only loses executability, tech-only loses the
   owner.
2. **Visuals as needed (Tenet 26/27).** Whenever a choice is geometric or
   visual, render a small real image per distinguishable option (e.g. the
   line-primitive card: "line cuts → two colored pieces" vs "line as
   decoration → one piece"). Generate from real renders or minimal SVG you
   author for the comparison; view each image yourself before shipping.
3. **Recommendation pre-selected, never hidden.** Mark exactly one option
   `rec: true` per card (★ in the UI) and pre-select it — the owner edits
   disagreement, not a blank form. A "Reset to recommendations" button
   restores defaults.
4. **The paste-back prompt is the contract.** The generated prompt must:
   name the source page + date; list each pick as `tag (doc-path): PICK id
   — label` + verbatim owner note; and end with the standing apply
   instructions (frontmatter `status_token`/`picked_option` updates,
   owner-pick addendum quoting the prompt, per-repo ledger regen +
   coherence gate, LEDGER-XREPO regen, dependency-ordered application,
   follow-on filing, per-doc outcome report). Picks arriving via this
   prompt ARE owner picks — record them as such.
5. **Data-driven page.** All content lives in one `DECISIONS` JSON array at
   the top of the inline script; regenerating for a new queue = swapping
   the JSON (source it from `docs/decisions/LEDGER-XREPO.md` open rows +
   per-doc option extraction). No build step, inline CSS/JS, relative
   asset refs — the `tools/analysis/` convention.
6. **Screenshot-verify before shipping** (Playwright `npx playwright
   screenshot --full-page file://… out.png`, then Read it) and commit page
   + assets together.

## Option schema (the example)

```js
{
  tag: "line-primitive", repo: "bikar",
  doc: "bikar/docs/decisions/2026-05-26-line-primitive-cascade-D1-D2-D3.md",
  q: "When you draw a line across a shape, should it actually CUT the shape in two?",
  qTech: "Enroll line-family primitives in the face-walker vs render-only; default face_class for unclassified sub-faces.",
  unblocks: "The whole line cascade; every future straightedge construction.",
  options: [
    { id: "E", rec: true, label: "Cut, and nothing gets lost",
      img: "decision-picker-assets/line-cuts.png",
      plain: "Like a real compass-and-straightedge: the line slices the square into two real pieces you can color and count — and any piece you forgot to name still shows up instead of silently vanishing.",
      tech: "Hybrid A+C: face-walker enrollment + default face_class for unclassified sub-faces (closes the gt-emitter silent-drop hazard)." },
    // ... every option: plain + tech, img when visual
  ],
}
```

Also support a "Bucket A" style checkbox for pre-authorized batch items
(reconciliations the loop ships under existing authority) so the owner can
wave those through in one click.

## Output contract

- `docs/decision-picker.html` (or `<topic>-picker.html`) + assets dir,
  committed in the cross-repo home (sacred-patterns) unless the queue is
  single-repo.
- Tell the owner the one-line `open <path>` command and what the paste-back
  will do.
