# Sacred Patterns

> *Leveraging Design Patterns through the recreation of Sacred, Geometric Patterns*

A TypeScript library that generates sacred geometric patterns as SVG, built with D3.js. Compose geometric primitives — points, lines, circles, polygons, and stars — into intricate recursive patterns rendered in the browser.

**Live site:** https://art.bytesofpurpose.com/

## Available Patterns

- **Hexagon with Surrounding Nonagons** — hexagonal grid with nonagon overlays and configurable color themes
- **Recursive Circles** — flower-of-life style patterns with configurable recursion depth
- **Chained Stars** — linked five-point stars with elongation
- **Star Grid** — grid arrangements of multi-pointed stars
- **Rotated Stars** — stars with rotational transformations
- **Rotating Circles** — circular arrangements with rotational symmetry
- **Polygon Gallery** — triangle through decagon rendering
- **Star Gallery** — various star point configurations

## Quick Start

```bash
npm install

# Dev mode with watch (compile + bundle + auto-restart server)
make ~run

# Then open http://localhost:3000
```

The app serves an interactive page where you can edit the JSON config to change background and line themes, then click "Regenerate SVG" to re-render. SVGs can be downloaded directly from the browser.

## Development

```bash
# Compile TypeScript + lint
make compile

# Watch TypeScript compilation only
make ~compile

# Webpack bundle only
npm run build
```

## Deployment

The site is deployed to GitHub Pages via the `gh-pages` branch with a custom domain (`art.bytesofpurpose.com`).

```bash
# Build and deploy to gh-pages
make deploy
```

This builds the webpack bundle, copies the output to the `gh-pages` branch, commits, and pushes.

## Docker

```bash
# Build image
make build

# Run container (port 3001 -> 3000)
make run

# Stop container
make stop
```

## Geometry Primitives

The library is built on composable geometry classes in `src/ts/`:

| Module | Key Classes | Purpose |
|--------|------------|---------|
| `points.ts` | `Point` | 2D coordinates, distance, quadrant detection |
| `lines.ts` | `Line`, `Lines` | Line segments, slope, extension, scaling |
| `circles.ts` | `Circle` | Circumference points, surrounding circles, recursive flower patterns |
| `polygons.ts` | `Polygon`, `Triangle`...`Decagon` | Regular polygons with chord/sagitta calculations |
| `star.ts` | `Star`, `FivePointStar`, `ElongatedFivePointStar` | Multi-pointed stars with elongation |

All geometric transforms are immutable — methods return new instances rather than mutating.

## Dependencies

### npm (managed via `package.json`)

| Package | Purpose |
|---------|---------|
| `d3` (v7) | SVG rendering engine — all geometric patterns rendered as D3-generated SVG |
| `lodash` | Functional utilities used throughout geometry primitives |
| `typescript` (v5) | Source language (strict mode) |
| `webpack` (v5) | UMD bundling — D3 and Lodash loaded as externals |
| `ts-loader` | TypeScript compilation within webpack |
| `eslint` + `typescript-eslint` | Code quality and linting |
| `webpack-dev-server` | Local development server with hot reload |
| `html-webpack-plugin` | Generates `site/index.html` from template |
| `jsdom` | DOM environment for regression tests (`npm test`) |

### System dependencies (brew / pip)

| Tool | Install | Purpose |
|------|---------|---------|
| **Node.js** (18+) | `brew install node` | Runtime for npm, webpack, dev server |
| **ImageMagick** | `brew install imagemagick` | Image conversion (JPG→PNG for tracing), timelapse GIF assembly (`magick convert`) |
| **libxml2** (xmllint) | `brew install libxml2` (or pre-installed on macOS) | XML validation of SVG files — used by `tools/validate-svg.sh` |
| **ffmpeg** | `brew install ffmpeg` | Timelapse MP4 assembly for social media (optional — skip if unavailable) |
| **VTracer** | `pip install vtracer` | Reference image tracing — converts raster images (JPG/PNG) to colored SVGs for comparison |
| **Python 3** | `brew install python` (or pre-installed on macOS) | Runs VTracer and SVG extraction scripts |

### Quick setup

```bash
# System dependencies
brew install node imagemagick ffmpeg

# Python dependencies
pip install vtracer

# Project dependencies
npm install
```

## References

See [REFERENCES.md](REFERENCES.md) for a curated catalog of academic papers, open-source implementations, tutorials, and reference materials on Islamic geometric pattern construction and computational generation.

## Tech Stack

- **TypeScript** (strict mode) — source language
- **D3.js v7** — SVG rendering
- **Lodash** — functional utilities
- **Webpack 5** — UMD bundling (D3 and Lodash loaded as externals)
- **Docker** — multi-stage containerized deployment
