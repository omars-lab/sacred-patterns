---
name: review-site-visually
description: Visually review the rendered gh-pages gallery — either interactively (Claude-in-Chrome MCP, for debugging "does it look right?") or as an automated regression (Playwright, to lock in that all 8 cards render and the controls work). Use before declaring any frontend/template change shipped.
user_invocable: true
argument: (optional) "interactive" | "automated" — defaults to interactive
---

# review-site-visually

The site is a D3 gallery: `templates/index.tpl` → webpack → `site/index.html` + `site/bundle.js`, served locally with `npx serve site` and deployed to gh-pages. Its output is **geometry rendered to pixels** — a green build and a passing geometry regression (`npm test`) are necessary but NOT sufficient, because the failure modes that survive both (a card that renders nothing, a control that throws, a pattern absorbed into the wrong canvas) are exactly the ones the eye catches in seconds (cross-repo Tenets 26/27).

This skill is the **acceptance gate for any change to `templates/index.tpl`, `src/ts/index.ts` draw functions, or `src/ts/canvas.ts` rendering**. Two paths — pick by intent.

## When to use which path

| Intent | Path |
|--------|------|
| "Does this look right? / debug a visual divergence" | **A — interactive** (Claude-in-Chrome) |
| "Lock in a regression so a future refactor can't silently break the gallery" | **B — automated** (Playwright) |

Path A is the diagnostic loop (you're confused, you look). Path B is the durable witness (Tenet 18 — the smoke that found the bug becomes the test that prevents its return). A substantial change does **both**: debug with A, then freeze the result with B.

---

## Path A — interactive review (Claude-in-Chrome MCP)

1. **Build + serve:**
   ```bash
   npm run build
   npx serve site -l 4178 > /tmp/sp-serve.log 2>&1 &
   curl -s -o /dev/null -w "%{http_code}" http://localhost:4178/   # expect 200
   ```
2. **State the expected visual BEFORE viewing** (Tenet 26 — write it down first, so a divergence is a signal, not a rationalization). E.g. *"8 cards in a grid, each with a serif title, a rendered pattern, two palette dropdowns, Regenerate + Download; gold debug chip bottom-right."*
3. **Load the Chrome tools and navigate:**
   - `mcp__claude-in-chrome__tabs_context_mcp` (get a tab; create one if empty)
   - `mcp__claude-in-chrome__navigate` → `http://localhost:4178/`
   - `mcp__claude-in-chrome__computer` action `screenshot` (scroll through the whole grid)
   - `mcp__claude-in-chrome__read_console_messages` with `onlyErrors: true` — **zero errors is part of the gate**.
4. **Run the checklist** (below). Compare each item against the expectation you wrote in step 2.
5. **Exercise the controls:** change a Background/Line select on one card, click Regenerate, click the debug chip — confirm each does what it should and throws nothing.

### Visual checklist
- [ ] Masthead renders (serif title, mono tagline, gold rule).
- [ ] **All 8 cards present**: d6 hexagon-nonagon, d0 chained-stars, d2 star-grid, d3 rotated-star, d7 flower-of-life, d5 rotating-circles, d1 different-polygons (strip), d4 different-stars (strip).
- [ ] Each card's SVG is non-empty and the pattern is recognizable (not a blank canvas, not absorbed/clipped).
- [ ] Single-pattern cards share a uniform render height (grid rows align).
- [ ] Strip cards (d1/d4) lay out horizontally, not stacked.
- [ ] Per-card Background + Line selects change the render on `change`.
- [ ] Regenerate redraws; Download produces a `<id>.svg` file.
- [ ] Debug chip (bottom-right) expands on click/hover → shows build provenance + editable config + the two global export links.
- [ ] **Zero console errors.**
- [ ] Narrow viewport (`resize_page` to ~420px wide): grid collapses to one column, nothing overflows.

If any item fails, that's the divergence — write it down before re-reading the template or bundle, then fix and re-review.

---

## Path B — automated review (Playwright)

A headless regression that asserts the structural invariants the eye checks in Path A, plus screenshot snapshots. Kept **out of** the gating `npm test` (which must stay the fast JSDOM geometry check) — it runs as `npm run test:visual`.

### One-time setup
```bash
npm i -D @playwright/test
npx playwright install chromium
```

### Run
```bash
npm run build            # test:visual asserts against the built site/
npm run test:visual
```

The spec (`.claude/skills/review-site-visually/playwright/visual.spec.ts`) asserts:
1. All 8 `#mount-<id>` containers each hold a non-empty `<svg>`.
2. Zero `console.error` / pageerror during load.
3. Changing a select + clicking Regenerate keeps the svg non-empty.
4. The debug panel opens and contains the provenance + config + export links.
5. A full-page screenshot snapshot (`toHaveScreenshot`) for regression.

### Snapshot caveat (read before trusting a snapshot diff)
Screenshot bytes diverge across CPU arch / font-rendering (see the CI-platform-portability memory). Treat `toHaveScreenshot` diffs as **advisory** unless the baseline was captured on the same arch as the runner. The **structural** assertions (1–4) are the load-bearing gate; the snapshot is a bonus regression signal, not a hard fail on its own. Pin viewport + browser (the spec does) and, if wiring to CI, capture baselines on the CI arch, not the dev box.

### CI wiring (if/when added)
Put `test:visual` in its own job with `on.push.paths-ignore: ['**.md', 'docs/**', '.claude/**']`, `concurrency` + `cancel-in-progress` (PR-only), and `timeout-minutes` — per the GHA-budget tenet. It needs the chromium download cached or it will re-fetch every run.

---

## Stop rule (before declaring a frontend change shipped)
Name (a) which path you ran, (b) what you confirmed against what expectation, (c) the verdict (incl. console-error count). A green `make compile` + `npm test` alone does NOT clear this gate — the render is the artifact, the metric is a lossy projection of it.
