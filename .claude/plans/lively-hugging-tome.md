# Plan: Sacred-Patterns gh-pages frontend overhaul — interactive gallery of all 8 patterns

## Context

The live site (https://blog.bytesofpurpose.com/sacred-patterns/, served from `/site`, deployed to gh-pages via `make deploy`) looks hackish. The page opens with a raw git commit hash, then a raw JSON config dump (`background_theme`/`line_theme`), then three plain unstyled text links (Regenerate / Download SVG / Download Inverted SVG), then a single rendered pattern. Only **1 of 8** available pattern generators is rendered — the other 7 are commented out in `templates/index.tpl`.

The hero asset is genuinely beautiful (thin gold/silver strapwork on near-black) — the chrome around it is the problem.

**Intended outcome** (per owner direction this session):
1. A polished, distinctive frontend (frontend-design skill aesthetic; palette built from the hero pattern).
2. **A gallery of ALL 8 patterns**, each an **interactive card** with per-card theme controls (background + line palette), Regenerate, and Download SVG.
3. The git-hash / config JSON / global download links collapse into a **hover-over debug menu pinned bottom-right** — not dumped at the top.
4. **A new skill** documenting how to visually review the site (Claude-in-Chrome MCP, Playwright automated visual tests, etc.).

## Verified facts (de-risk)

- **The regression test does NOT depend on body-append.** `test/regression/check.js` loads `site/bundle.js` into JSDOM, calls `drawHexagonWithSurroundingNonagons('d6', 100, 6, bg, line)`, then `getElementById('d6')`, asserting on sorted polyline `points` + element counts — never on the parent node. A default `mountSelector = "body"` preserves it byte-for-byte. The test loads the **bundle**, not the HTML, so the template rewrite cannot break it; only `src/ts` geometry changes can.
- **eslint is strict** (`eslint.config.js`): `no-explicit-any: error`, `jsdoc/require-jsdoc` (every exported fn/type needs a WHY-style JSDoc), `complexity max 10`, `jsdoc/no-blank-blocks`. tsconfig adds `noUnusedParameters`/`noImplicitReturns`/`strict`. Every new export carries an intent JSDoc + a real type — `unknown` for themes is out (matches tenets 15/16).
- **`appendPolygon(onto, lines, metadata={})`** reads `_.get(metadata,"stroke"|"stroke-width"|"fill")` via `.style()`. A `LineTheme = {stroke?; "stroke-width"?; fill?}` maps exactly — body unchanged.
- **`appendSVGToDOM` (src/ts/index.ts:71)** hardcodes `d3.select("body").append("svg")` — **the one structural blocker** for a multi-card gallery.
- No Playwright/Puppeteer today; `npm test` is a JSDOM geometry regression. Skills follow `.claude/skills/<name>/SKILL.md` with frontmatter `name`/`description`/`user_invocable`/`argument`.

## The 8 generators

| id | fn | returns | themed? | special |
|----|----|---------|---------|---------|
| d0 | `drawChainedStars(id, r, size)` | IO | no | `appendText` labels |
| d1 | `drawDifferentPolygons(id, r, size)` | IO | no | emits **N svgs** (loop) |
| d2 | `drawStarGrid(id, r, size)` | IO | no | |
| d3 | `drawRotatedStar(id, r, size)` | IO | no | |
| d4 | `drawDifferentStars(id, r, size)` | IO | no | emits **N svgs** |
| d5 | `drawRotatingCircles(id, r, size)` | IO | no | `setInterval` animation |
| d6 | `drawHexagonWithSurroundingNonagons(id, r, size, bg, line)` | d3SVG | yes (`unknown`) | **test pins this** |
| d7 | `drawCirclesRecursively(id, r, size, maxLevels)` | IO | no | extra `maxLevels` |

---

## CHUNK 1 — Theme types + `appendSVGToDOM` mount-target (no UI yet)

Land the structural enablers; keep existing page + test green.

**1a. Real theme types** (new `src/ts/theme.ts`), each with a WHY JSDoc:
```ts
export type BackgroundTheme = { background: string } & Record<string, string>;
export interface LineTheme { stroke?: string; "stroke-width"?: string; fill?: string; }
```
- Retype `drawHexagonWithSurroundingNonagons(... bg: BackgroundTheme, line: LineTheme)` (was `unknown`). Body unchanged; drop the "deliberate unknown" note from its JSDoc.
- Widen `appendPolygon(onto, lines, metadata: LineTheme = {})` in `canvas.ts`. `_.get` still type-checks. Leave `appendText` metadata as-is (varied keys) to limit blast radius.

**1b. Optional mount selector** on `appendSVGToDOM`:
```ts
export function appendSVGToDOM(id, width, height, mountSelector = "body"): d3SVG {
  const svg = d3.select(mountSelector).append("svg") ...
}
```
Thread an optional trailing `mountSelector = "body"` through all 8 draw fns → forward to `appendSVGToDOM`. **For d6, append `mountSelector` AFTER bg/line** so the test's positional 5-arg call still binds and gets the default.

**Verify:** `make compile` (jsdoc + no-explicit-any + noUnusedParameters), `npm run build`, `npm test` MUST pass (geometry untouched).

---

## CHUNK 2 — Retrofit the 7 void generators to typed themes (geometry identical)

Uniform target: `drawX(id, r, size, bg: BackgroundTheme = {background:"transparent"}, line: LineTheme = {}, mountSelector = "body"): d3SVG`.

- **Return the svg** (`IO`→`d3SVG`) so Download/Regenerate can read `.node().outerHTML` like d6. Additive — current call sites ignore the return.
- Factor a helper (WHY JSDoc) to stay under complexity gate:
```ts
export function applyBackground(svg: d3SVG, bg: BackgroundTheme): void {
  _.forOwn(bg, (v, k) => svg.style(k, v));
}
```
  Call after `appendSVGToDOM`; pass `line` as the metadata arg to every `appendPolygon` (today they pass none → default black).
- **Scope note (in each JSDoc):** `line` governs polylines. Circle-based draws (`drawRotatingCircles`, `drawCirclesRecursively`) style circles via per-instance metadata; pass `line` for uniformity but it mainly affects polylines there.
- **Per-fn:** `drawChainedStars` — leave `appendText` styling alone. `drawDifferentPolygons`/`drawDifferentStars` — apply bg+line per emitted svg, unique ids (`svg-d1-<i>`), return last. `drawRotatingCircles` — animation unchanged. `drawCirclesRecursively` — keep `(id, r, size, maxLevels, bg, line, mountSelector)` ordering; special-case in registry; document the extra-arg exception.

**Verify:** `make compile`; `npm run build`; `npm test` (d6 untouched → PASS); `make serve` confirms old template still works.

---

## CHUNK 3 — Gallery shell (rewrite `templates/index.tpl`) + card wiring

Rewrite the wired template, borrowing the CSS shell from `templates/components/index.html` (existing polished dark-theme showcase, gold `#c9a84c` accent) but driving the **real** `sacredPatterns.draw*` generators.

**Aesthetic (anti-AI-slop):**
- Palette from hero pattern: bg `#0a0a0f`/`#08080c`, card `#14141e`, gold `#c9a84c`/`#e8d5a3`, silver `#c0c0c0`, hairline `#2a2a3a`. Keep `svgGradient`/`invertedSvgGradient` as line-palette options.
- Typography: **not** Inter/system — pair a high-contrast display serif (Cormorant Garamond / Spectral) for headings with a technical mono (IBM Plex Mono / Space Mono) for ids + params. One Google Fonts `<link>`; keep d3 + lodash CDN tags.
- Motion: staggered fade/translate-up on load via CSS keyframes + per-card `animation-delay`; guard `@media (prefers-reduced-motion: reduce)`.
- Grid: `repeat(auto-fill, minmax(440px,1fr))`, collapse to 1 col under ~520px.

**Card registry** (JS array, one entry per generator):
```js
{ id:"d6", title:"Hexagon + Nonagon 6-Point Star", tag:"strapwork",
  draw:(mountSel,bg,line)=>sacredPatterns.drawHexagonWithSurroundingNonagons("svg-d6",100,6,bg,line,mountSel) }
```
Each card: serif title + mono id chip + tag pill; a `.render` div with a stable mount id (`#mount-d6`) the draw fn targets via `mountSelector`; the svg keeps a distinct id (`svg-d6`) so Regenerate can `getElementById('svg-d6').remove()` then redraw; two `<select>`s (Background + Line palette) populated from the `background_theme[]`/`line_theme[]` arrays (the data formerly dumped as raw JSON, now one JS const); Regenerate + Download SVG buttons (existing btoa/outerHTML pattern, generalized to `svg-<id>`).

**Special cards:** d1/d4 emit N svgs → `.render { display:flex; gap; overflow-x:auto }` scroll strip, unique ids; download the first (note limitation). d5 animated → on regenerate old interval orphans (harmless detached) — flagged minor leak. d7 passes `maxLevels=2` in its closure.

**Verify:** `npm run build` → `make serve` → Claude-in-Chrome MCP (navigate, screenshot, console, resize): 8 cards render, no console errors, selects/regenerate/download work, motion plays. `npm test` still PASS.

---

## CHUNK 4 — Bottom-right hover debug menu

Fixed `bottom:16px; right:16px; z-index:200` chip (gold hairline) expanding on **hover and click** (click for touch + keyboard a11y). Expanded panel holds: relocated `<%= VERSION %> / <%= COMMITHASH %> / <%= BRANCH %>` EJS tags; the config JSON in a `contenteditable`/`<textarea>` (preserves edit-then-regenerate); the global Download SVG / Download Inverted SVG links (existing btoa logic, retargeted). Add `aria-expanded`, focusability, `prefers-reduced-motion`. Top of the page becomes clean — no hash/JSON/link dump.

**Verify:** Claude-in-Chrome MCP `hover` → screenshot expanded; confirm contents present and page top is clean.

---

## CHUNK 5 — New skill: `review-site-visually`

New `.claude/skills/review-site-visually/SKILL.md` (+ a `playwright/` subdir for the automated path). Frontmatter matches repo convention (`name`/`description`/`user_invocable: true`/`argument`). Documents two complementary review paths:

**Path A — interactive (Claude-in-Chrome MCP):** the loop used in this session — `make serve`, `tabs_context_mcp` → `navigate` → `computer screenshot` / `get_page_text` / scroll, then compare against a written-down expectation (tenet 26: state expected visual BEFORE viewing). Checklist: 8 cards present, no console errors, controls functional, debug menu hover, responsive at narrow width. For ad-hoc review and debugging.

**Path B — automated (Playwright):** add `@playwright/test` as a devDependency; a `playwright/visual.spec.ts` that (1) serves `/site`, (2) asserts 8 `.pattern-card` mounts each contain a non-empty `<svg>`, (3) asserts zero console errors, (4) exercises one Regenerate + one Download, (5) captures full-page + per-card screenshots as snapshots (`toHaveScreenshot`) for regression. Wire `npm run test:visual`. Pin browser + viewport for determinism (per the CI-platform-portability memory — screenshots diverge across arch; document that snapshots are advisory unless pinned to the CI runner arch). Keep it OUT of the gating `npm test` (which must stay the fast headless geometry check) — `test:visual` is opt-in / a separate CI job with `paths-ignore` + `concurrency` + `timeout-minutes` per the GHA-budget tenet.

The skill names when to use which: Path A for "does this look right / debug a divergence," Path B for "lock in a regression so a future refactor can't silently break the gallery" (tenet 18 — codify the witness).

**Verify:** `npx playwright test` runs green locally; the skill's checklist is followed once end-to-end against the built site.

---

## CHUNK 6 — Full verification + deploy

1. `make compile` — tsc + eslint clean (jsdoc on every new export; no `any`/`unknown` for themes; complexity ≤ 10).
2. `npm run build`.
3. `npm test` — **the gate**: d6 geometry + element counts unchanged.
4. `npm run test:visual` (new) — 8 cards, controls, no console errors.
5. `make serve` + Claude-in-Chrome MCP visual QA (desktop + narrow): gallery, controls, debug menu, motion, zero console errors.
6. `make deploy` (**only when owner asks** — push to gh-pages is owner-gated): copies `bundle.js` + `index.html` to the gh-pages worktree; also copies `templates/components` (keep showcase reachable).

## Risk register

1. **Reordering d6 params** breaks the test's positional 5-arg call → append `mountSelector` AFTER bg/line. *(mitigated)*
2. **Default `mountSelector` ≠ `"body"`** orphans `getElementById('d6')` → keep `"body"`. *(mitigated)*
3. **Touching `appendPolygon` point math** shifts coords → only the metadata *type* changes; body untouched. *(mitigated)*
4. **eslint jsdoc / no-explicit-any** — every new export needs a WHY JSDoc + real type. *(designed in)*
5. **d1/d4 multi-svg into one id** → unique ids + flex strip.
6. **d5 setInterval leak** on regenerate (no stop handle) — known minor leak; full fix is a follow-on.
7. **Playwright snapshot flakiness across arch** — pin viewport/browser; mark snapshots advisory unless run on CI arch (per memory).
8. **Scaling convention** — radii stay origin-relative (`radius*size/2`); themes are style-only, no new magic constants, no geometry change.

## Critical files

- `src/ts/theme.ts` *(new — theme types)*
- `src/ts/index.ts` *(appendSVGToDOM mount-target; retrofit all 8 draw fns; applyBackground helper)*
- `src/ts/canvas.ts` *(appendPolygon metadata → LineTheme)*
- `templates/index.tpl` *(full gallery rewrite)*
- `templates/components/index.html` *(CSS/shell reference — not edited)*
- `test/regression/check.js` *(the gate — read-only, must stay green)*
- `.claude/skills/review-site-visually/SKILL.md` + `playwright/visual.spec.ts` *(new skill)*
- `package.json` *(add `@playwright/test` devDep + `test:visual` script)*
