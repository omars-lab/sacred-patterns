# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sacred Patterns is a TypeScript library that generates sacred geometric patterns as SVG using D3.js. It bundles into a UMD module (`sacredPatterns`) served by an Express.js server, viewable in a browser.

## Build & Development Commands

```bash
# Install dependencies
npm install

# Compile TypeScript and run ESLint
make compile

# Bundle with Webpack (outputs to /site)
npm run build        # or: make _build

# Full build including Docker image
make build

# Watch mode - TypeScript compilation
make ~compile

# Watch mode - full dev loop (compile + bundle + server restart)
make ~run

# Start Express server (serves /site on port 3000)
npm run site

# Docker: run container (maps port 3001 -> 3000)
make run

# Docker: stop container
make stop

# Deploy to GitHub Pages (builds + pushes to gh-pages branch)
make deploy
# Live site: https://art.bytesofpurpose.com/
```

There are no tests configured (`npm test` is a placeholder).

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

TypeScript (`src/ts/`) → Webpack + ts-loader → UMD bundle (`site/bundle.js`) + HTML from template (`templates/index.tpl`) → Express serves `/site` directory

D3 and Lodash are webpack **externals** (loaded via `<script>` tags, not bundled).

## Key Conventions

- Geometric transforms are **immutable** — methods like `rotate()`, `adjacent()`, `scaleLine()` return new instances
- Objects carry rendering metadata (level, stroke, fill) through transformations
- Circles serve as reference frames for positioning surrounding shapes
- Heavy use of Lodash (`_`) for functional operations
- TypeScript strict mode is enabled
- ESLint uses `@typescript-eslint` parser with recommended presets
