# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sacred Patterns is a TypeScript library that generates sacred geometric patterns as SVG using D3.js. It bundles into a UMD module (`sacredPatterns`) viewable in a browser.

## Build & Development Commands

```bash
# Install dependencies
npm install

# Compile TypeScript and run ESLint
make compile

# Bundle with Webpack (outputs to /site)
npm run build        # or: make build

# Watch mode - TypeScript compilation
make ~compile

# Watch mode - dev server with hot reload
make ~run

# Serve the site locally
make serve

# Deploy to GitHub Pages (builds + pushes to gh-pages branch)
make deploy
# Live site: https://art.bytesofpurpose.com/
```

Regression test: `npm test` runs a geometry comparison against a reference SVG.

## Architecture

### Source Layout

All TypeScript source lives in `src/ts/`. Webpack entry point is `src/ts/index.ts`, which re-exports drawing functions that compose the geometry primitives.

### Geometry Primitive Layer (`src/ts/`)

- **`points.ts`** - `Point` class (2D coordinates, distance, quadrant detection)
- **`lines.ts`** - `Line` class (slope, extension, scaling); `Lines` factory
- **`circles.ts`** - `Circle` class (circumference points, surrounding circles, recursive flower patterns); carries metadata (level, fill, stroke)
- **`polygons.ts`** - Base `Polygon` class with subclasses: `Triangle`, `Square`, `Pentagon`, `Hexagon`, `Heptagon`, `Octagon`, `Nonagon`, `Decagon`; chord/sagitta calculations
- **`star.ts`** - `Star` class, `FivePointStar`, `ElongatedFivePointStar`

### Visualization Layer

- **`canvas.ts`** - D3.js SVG rendering functions (`appendCircle`, `appendLine`, `appendPolygon`, `appendText`); gradient definitions; type aliases `d3SVG` and `d3CIRCLE`
- **`index.ts`** - High-level drawing functions that compose primitives into patterns (e.g., `drawCirclesRecursively`, `drawChainedStars`, `drawStarGrid`); SVG DOM creation and color utilities

### Supporting

- **`helpers.ts`** - Functional utilities (`all`, `any`, `isEven`, `isOdd`, `_map_even_odd`, `applyTransformationPipeline`)
- **`types.ts`** - `IO` (void alias), `Optional<T>`

### Build Pipeline

TypeScript (`src/ts/`) → Webpack + ts-loader → UMD bundle (`site/bundle.js`) + HTML from template (`templates/index.tpl`) → static site served from `/site` directory

D3 and Lodash are webpack **externals** (loaded via `<script>` tags, not bundled).

## Key Conventions

- Geometric transforms are **immutable** — methods like `rotate()`, `adjacent()`, `scaleLine()` return new instances
- Objects carry rendering metadata (level, stroke, fill) through transformations
- Circles serve as reference frames for positioning surrounding shapes
- Heavy use of Lodash (`_`) for functional operations
- TypeScript strict mode is enabled
- ESLint uses `@typescript-eslint` parser with recommended presets (flat config, eslint.config.js)
- **Geometric construction from central origin** — All proportions are derived from trigonometric relationships relative to a central circle, not arbitrary scaling factors. Radii come from star polygon edge intersections (`cos(pi*k/n)` formulas), positions from polar coordinates at `360/n` intervals, and distances from additive geometric terms (tip radius + band width + satellite radius). Never use unexplained `R * 0.52`-style constants.
- **Relative-to-origin scaling** — Every coordinate, distance, and size in a pattern MUST be defined as a ratio or function of the originating circle's midpoint `(cx, cy)` and radius `R`. When `R` changes, the entire diagram scales proportionally — no element has an absolute position or size. This mirrors the landing page implementation where `surroundingCircles(6, 1)` places circles at `R` from center with radius `R`, and nonagons are sized at `0.75 * R`. Satellite distances, band widths, tile vertices — all expressions of `R`, never standalone constants.

## Workflow Conventions

- **Task tracking** — When the user issues a command (implement, fix, refactor, create, etc.), track progress with tasks naturally. When the user asks a question or wants to discuss something, engage in conversation first — don't create tasks until a course of action is agreed upon.
- **Feature documentation** — User-facing features for interactive tools (toolbar buttons, keyboard shortcuts, selection modes, etc.) are documented in `docs/features.md`. Update this file when adding or changing UI features.
- **Issue documentation** — When work surfaces a non-trivial issue with more than one plausible fix (parity divergence, dependency gap, design assumption challenged by evidence), file it as a markdown doc under `docs/issues/` (or, when the issue belongs to a sibling repo like qiyas, under that repo's `docs/issues/`). Required structure: **Status** (OPEN / RESOLVED YYYY-MM-DD / WONTFIX), **Discovered** (when, by whom, what surfaced it), **Symptom** (concrete observation with reproducer), **Root cause** (established by investigation, not speculation), **Options considered** (every option with pros/cons/cost — including the one not picked), **Decision** (which option, why, who decided), **Follow-ups** (task IDs, backlog entries). Filename: `YYYY-MM-DD-short-slug.md`. The "Options considered" section is load-bearing — the point of filing is so future readers can see what was weighed, not just what was picked. Don't delete resolved issues; they're the archive. Skip this for trivial bugs (just fix), scope deferrals (track in backlog docs), or open design questions before any work has started (use plans).
- **Cross-repo task linkage** — When a sacred-patterns task blocks or is blocked by work in qiyas or bikar, mention it in the task description as `qiyas#NN` or `bikar#NN` (grep-able). Active cross-repo dependencies live in `docs/cross-repo-dependencies.md` (mirror of the same file in qiyas and bikar). Prune resolved rows once both sides ship.

## Construction Learnings

General construction knowledge lives in `.claude/skills/generate-drawing/learnings/` (git-tracked). This includes:
- `rosette-construction.md` — Lee/Adams traditional compass-and-straightedge method
- `construction-antipatterns.md` — common mistakes applicable to all pattern construction
- `rabbit-hole-checklist.md` — early warning signs for wasted iterations
- `construction-techniques.md` — reusable algorithms discovered across sessions
- `color-palettes-learned.md` — palettes discovered from reference images
- `patterns-catalog.md` — catalog of studied patterns

Session-specific learnings (iteration logs, session-specific mistakes) stay in the Dropbox session directories. When a new general technique is discovered during iteration work, add it to the git-tracked skill learnings.

## Pattern Interpretation (`interpret-pattern` skill)

Before iteration work begins, the interpret-pattern skill (`.claude/skills/interpret-pattern/`) produces a `baseline.json` — user-verified shape expectations that ground the A6 architectural audit. The workflow:

1. Claude generates a shape inventory from visual analysis of the reference image
2. Claude generates `input/pattern-interpretation.html` — interactive D3 overlay tool
3. User reviews and corrects detected shapes in the browser (edit properties, drag vertices, add/delete shapes)
4. Claude extracts corrected data and writes `input/baseline.json`

The baseline gates Step 2 (Analyze Pattern) and is consumed by `qiyas svg-audit --baseline` every iteration.

**Keeping docs in sync** — When modifying the interpretation template (`templates/pattern-interpretation.html`) or `tools/extract-shapes.py`, update four things: (1) `docs/features.md` with any UI or CLI changes, (2) the SKILL.md regression test script to cover new behavior, (3) run the regression test in-browser to verify, (4) **regenerate session HTML** via `make interpret SESSION=<session-dir>` so the live file picks up template and shapes.json changes. See the "End-to-End Regression Test" section in SKILL.md.

## Geometric Analysis Tools (`tools/analysis/`)

Self-contained D3.js HTML tools for pattern decomposition and geometric analysis. Deployed to `https://art.bytesofpurpose.com/tools/analysis/`.

- **Grow organically** — When iteration work reveals a generally useful geometric computation (intersection mapping, parallel detection, tile vertex computation), extract it into a reusable tool in `tools/analysis/`. Don't build tools speculatively — build them when a real need emerges from iteration work.
- **Self-contained** — Each tool is a standalone HTML file with inline JS/CSS, D3 v7 CDN, and URL query parameters. No build step.
- **Deploy with the site** — The Makefile copies `tools/analysis/` into gh-pages during `make deploy`. After adding/updating tools, run deploy and verify with `curl -s -o /dev/null -w "%{http_code}" https://art.bytesofpurpose.com/tools/analysis/<filename>.html`.
- **Document in showcase** — Update `tools/analysis/showcase.html` with screenshots and descriptions when adding new tools. Update `tools/analysis/README.md` with parameter reference.

Current tools: `star-intersection-map.html`, `sector-decomposition.html`, `tile-decomposition.html`, `construction-overlay.html`, `showcase.html`.

## CLI Tools (`tools/`)

**Primary entry point** — call this once per iteration; it runs every other signal and emits a single `validation.json`:

- **`iteration-validate.sh`** — Validation orchestrator. Runs validate-svg, qiyas pixel-diff (vs traced SVG and vs reference image), qiyas svg-audit, qiyas-diff, and `qiyas score run` (rollup sub-command of the `qiyas score` group; sibling sub-commands `qiyas score replay` and `qiyas score explain` are for weight-tuning, not per-iteration use) in one shot. Reads each tool's output and emits `<out>/validation.json`. Schema split: `qiyas/docs/validation-envelope.md` (shared envelope) + `docs/validation-overall.md` (sacred-patterns `overall.*` rollup). The iteration loop reads `overall.go_no_go` for go/no-go; humans drill into per-tool subdirectories for diagnosis. Usage: `./tools/iteration-validate.sh --svg PATH --reference PATH [--reference-traced PATH] [--baseline PATH] --out DIR [--skip-qiyas]`.

**Underlying signals** (called by the orchestrator; only invoke directly when debugging one tool in isolation):

- **`validate-svg.sh`** — XML preflight. Checks xmlns, well-formed XML, visual elements, no markdown wrappers. Exit 0 = valid.
- **`qiyas pixel-diff`** (Docker) — Pixel-based image diff. Renders both inputs to bitmaps, produces visual overlay, heatmap, and numeric similarity score. Owned by qiyas; called from the orchestrator via `docker run ghcr.io/naqshcoffee/qiyas:v0.1.0 pixel-diff ...` with `--rasterizer magick` for stroke fidelity. Pixel similarity is regression-detection only, NOT the convergence goal (see "Convergence Philosophy").
- **`qiyas svg-audit`** (Docker) — Architectural convergence audit (A1/A2/A4/A5 + A6 when `--baseline` is provided): semantic census, N-fold symmetry, coverage completeness, band-network integrity, baseline shape validation. Two-step: orchestrator first runs `qiyas encode SVG` to produce `encoding.json` (forced raster path because our SVGs use clipPath), then `qiyas svg-audit encoding.json`. Replaces the deleted `tools/arch-audit.py`.
- **`qiyas-diff.py`** — Python Docker wrapper around `qiyas validate`. Encodes reference + recon, runs Hungarian shape matching, emits interactive Tier-3 HTML report at `qiyas/report.html` and structured pairings at `qiyas/diff.json`. Rasterizes SVG inputs to PNG first (qiyas's SVG fast-path rejects clipPath). Replaces the bash version (now removed) — Python avoids macOS bash-3 footguns.
- **`qiyas zone-audit`** (Docker) — Per-zone radial diff. Concentric ring match quality, broad zone summaries, strapwork gap analysis. Owned by qiyas; not currently called by the orchestrator but available for standalone debugging via `docker run ghcr.io/naqshcoffee/qiyas:dev zone-audit ...`.
- **Reference tracing** — Use VTracer (`pip install vtracer`) to trace reference images into colored SVGs. See SKILL.md "Reference Image Tracing" for the standard procedure and parameters.

## HARD GATES — Iteration Rules (learn-new-pattern skill)

These rules are ENFORCED as hard gates during iteration work. They survive conversation summarization because they live here in CLAUDE.md.

### G1. Iteration Immutability

**Once `iterations/{N}/output.html` renders successfully in the browser (no JavaScript console errors), that folder is FROZEN.** Any further code change — no matter how small — MUST go in `iterations/{N+1}/output.html`.

**Pre-edit checklist (MUST run before editing ANY output.html):**
1. Has this file already rendered successfully? Check: did I take a screenshot or see console output from this file?
2. If YES → STOP. Create `iterations/{N+1}/`, copy output.html there, edit the COPY.
3. If NO (first render attempt, or fixing JS errors on a broken render) → proceed with edits.

**The ONLY exception:** Fixing JavaScript errors that prevent the file from rendering at all (blank screen, console errors). Once it renders visual output, it is frozen.

### G2. Architecture Before Pixels

If the structural audit score is < 100% (ANY element MISSING or MALFORMED), the next iteration MUST target a structural improvement. Pixel-focused iterations (color tweaks, opacity adjustments, proportion tuning) are ONLY permitted when structural score = 100%.

### G3. Mandatory Deliverables Per Iteration

Every iteration MUST produce these files BEFORE starting the next iteration:
- `evaluation.md` — Structured comparison against reference
- `retrospective.md` — What worked, what didn't, why
- `guidance.md` — What to change in the next iteration

**Never skip straight from render to code changes.** The evaluate→reflect→plan cycle is what prevents repeated mistakes.

### G4. Reference-Grounded Verification

The structural audit MUST be grounded in the reference image, not self-defined labels. For every element:
1. Look at the specific zone in the REFERENCE first
2. Then look at the same zone in the OUTPUT
3. If they don't match, the element is MALFORMED — even if the output has "something" in that zone

### G5. Skill-Prefixed Task Naming

When creating tasks for iteration work, always prefix the task subject with `[learn-new-pattern]` to associate it with the skill and survive conversation summarization.

## Convergence Philosophy — Shape Before Pixels

Pattern convergence is measured by **structural and geometric fidelity**, not pixel-similarity metrics. After 90+ iterations on the first pattern, we learned that VTracer/JPG similarity percentages plateau early while significant architectural differences remain. Metrics can be gamed by color/coverage without matching actual shapes.

### Convergence Hierarchy (evaluate in this order)

1. **Topology** — Correct number and connectivity of structural elements (star, kites, petals, satellites, interstitial tiles, strapwork, interlacing). Tracked via the C1 structural audit (7/7 for this pattern).
2. **Geometry** — Individual tile shapes match the reference (correct vertex count, angles, proportions). Compare per-element: overlay one tile type at a time against the reference.
3. **Proportions** — Relative sizes, distances, and ratios match (rosette-to-satellite ratio, band width, star tip depth). Verify with geometric analysis tools.
4. **Coloring** — Last priority. Once shapes are correct, match reference colors.

### Architectural Convergence Audits (A1-A6)

Every iteration must report these structural metrics (defined in iteration-guide.md):

- **A1. Structural Census** — SVG element counts + arrangement metrics from console logs. Track deltas.
- **A2. N-fold Symmetry** — Verify all sectors are identical (EXACT/APPROXIMATE/BROKEN).
- **A3. Tile Shape Distribution** — Classify faces by vertex count, compare to reference expectations.
- **A4. Coverage Completeness** — Is the medallion fully tiled? (FULL/PARTIAL/SPARSE).
- **A5. Band Network Integrity** — 10 continuous bands, correct crossings, consistent width (COMPLETE/GAPS/BROKEN).
- **A6. Baseline Shape Validation** — Do shapes match user-verified expectations? (PASS/PARTIAL/MISSING per shape). Requires `--baseline input/baseline.json` (produced by the interpret-pattern skill). When A6 reports MISSING or PARTIAL, the G2 gate forces the next iteration to target that shape.

These audits measure shape convergence directly, unlike pixel metrics which conflate color, coverage, and structure.

### Pixel Metrics as Regression Detection

- **`qiyas pixel-diff`** scores are useful for detecting regressions (did this change make things worse?) but NOT for guiding structural work
- A change that adds correct structure may temporarily decrease the similarity score
- Never optimize for the metric — optimize for visual/structural match against the reference
- The primary progress indicators are: `validation.json` → `overall.warnings[0].counterfactual_score_delta` (predicted next-step score lift, ranked) and `overall.structural_score` (A6 PASS count). Pixel similarity is diagnostic-only.

### Iterations Are Driven by `overall.warnings[0]`

Every iteration's priority comes from `validation.json`'s `overall.warnings[0]` — qiyas has already ranked the warnings by predicted score lift (`counterfactual_score_delta`). The iteration agent translates `warnings[0]` into a code change; it does not re-derive priorities from screenshots. Each warning carries `context.counterfactual_rationale` ("if X were Y, score would improve by Z") — that rationale IS the proposed fix. See `iteration-guide.md` sections C0 (Read warnings) and E2 (Mechanical edit derivation).

## Self-Healing Principles

These patterns prevent wasted iterations and catch problems early:

1. **Verify before evaluating** — After rendering output in the browser, always check the console for JavaScript errors (`mcp__chrome-devtools__list_console_messages` with `types: ["error"]`). Never evaluate blank or broken output — fix the render first.

2. **Diagnose before retrying** — When output is wrong, understand WHY before rewriting. Read the previous retrospective. Identify the root cause (wrong approach, missing variable, wrong geometry) rather than making the same structural mistake with different code.

3. **Simplify on failure** — If a complex algorithmic approach produces wrong results, step back to a simpler, more direct approach. Over-engineered solutions are harder to debug and more likely to have subtle bugs.

4. **Compare per-element** — Don't evaluate everything at once. Compare one element at a time (central star, satellites, interstitial tiles, strapwork) against the reference. Fix the highest-impact element first.

5. **Track changes explicitly** — Every iteration must clearly state what changed and why (`guidance.md`). This prevents regression where fixing one thing breaks another.

6. **Consult learnings first** — Before starting work, read existing learnings and common mistakes. Many errors are recurring patterns that can be avoided.

7. **Validate SVG artifacts** — When extracting SVG from D3.js renders (via `document.querySelector('svg').outerHTML`), the SVG requires post-processing. After saving, always run `./tools/validate-svg.sh output.svg` which checks: starts with `<svg`, ends with `</svg>`, has `xmlns`, valid XML, contains visual elements, no wrapper artifacts. Key fixes:
   - **Add `xmlns`**: `sed -i '' 's/<svg /<svg xmlns="http:\/\/www.w3.org\/2000\/svg" /' output.svg`
   - **Strip wrapper text**: If tool output has markdown/JSON wrappers, extract the raw SVG string first.
   - **Curved lines are circles**: Any curve in a geometric pattern is an arc of a circle. Identify the center and radius, express as `f(R, n, k)`, and draw with exact circular arcs — never Bezier approximations.
