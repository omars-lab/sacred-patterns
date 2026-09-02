---
name: summarize-progress-visually
description: Turn a session's shipped changes into a layman-readable visual story page (before/after image comparisons, real verdict numbers, an honest-gaps wall) built ONLY from real artifacts. Use after shipping changes whose effect can be SHOWN by comparing images — validator behavior changes, render/construction changes, detector capability shifts — or whenever the owner asks "show me what changed."
---

# Summarize progress visually — the picture-story recipe

Turn a working session's outcome into a single self-contained HTML page a
non-technical person (the Tenet-29 "art-savvy grandma") reads in two
minutes and *understands what changed and why it matters*. The canonical
worked example is `qiyas/calibration/i2/progress-story.html` (2026-06-10
trust-the-validator session).

## When to use

- A session shipped changes whose effect is **visible by comparing
  images**: a verdict that changed, a render that changed, a capability
  that appeared/was found missing.
- The owner asks any flavor of "show me the progress / what did we
  actually do?"
- A milestone or cascade closes and the routing doc entry alone won't
  land with a non-technical reader.

**Don't use** for pure-infrastructure sessions with nothing imageable
(CI plumbing, doc reshuffles) — a picture page about invisible work
violates the realness rule below. Summarize those in prose.

## Hard rules (each maps to a tenet)

1. **Every image is a real artifact** — generated from the frozen
   fixtures, corpus renders, or tool outputs the session actually touched.
   Never illustrate, never mock up. If a "before" can no longer be
   produced (the bug is fixed), show the *evidence* of before (the
   recorded numbers) rather than faking the old behavior. (Tenets 4/27.)
2. **Expectation-first viewing** (Tenet 26): before viewing any generated
   image, write one sentence of what it should show; view it with the
   Read tool; a divergence is a finding, not a styling problem.
3. **Grandma bar** (Tenet 29): no metric names, no task IDs, no schema
   vocabulary in anything she reads. Analogies over terminology ("a
   referee whose call changes with the camera angle"). Technical pointers
   live only in the footer.
4. **The honesty section is mandatory.** Every story includes what the
   system still CANNOT do, shown as concretely as the wins — ideally as a
   "wall" of tiles wired to tripwire tests that flip when capability
   lands. A page of pure wins is marketing, not a summary. (Tenet 3.)
5. **Live numbers, labeled as point-in-time.** Verdict cards quote the
   *actual measured values* from the session's recorded runs (diff.json,
   README measurement tables), with the date and the regen pointer in the
   footer. (Tenet 6 — snapshots must say they're snapshots.)

## Recipe

1. **Pick 2–4 chapters.** Each chapter is one before/after contrast or
   one reveal. Good shapes: *same input, two old verdicts → one new
   verdict*; *the hidden thing revealed* (e.g., construction scaffolding
   recolored thick dashed red); *the honest gap wall*.
2. **Generate images from artifacts** into a `story/` dir next to the
   page (cairosvg/CLI renders at ~220–420px). For reveals, transform the
   real source file (e.g., restyle invisible strokes), render, delete the
   intermediate.
3. **Verdict cards**: red "Before" / green "After" boxes; one plain
   sentence each; real numbers in parentheses where they help ("two
   points docked" beats "structural 0.33").
4. **Assemble one self-contained HTML** (inline CSS, relative image
   refs, no build step — same convention as `tools/analysis/`). Footer:
   artifact provenance + regen pointer + technical-record links.
5. **View the page's key images yourself before shipping** (rule 2), then
   commit page + `story/` images together (small PNGs are fine; scratch
   intermediates are not committed).
6. Tell the owner the one-line `open <path>` command.

## Output contract

- `progress-story.html` (or `<topic>-story.html`) + `story/*.png`,
  committed in the repo whose artifacts star in it.
- Page sections: title with date · 2–4 chapters with image rows +
  verdict cards · honesty wall · "so what did this buy us" close ·
  provenance footer.
