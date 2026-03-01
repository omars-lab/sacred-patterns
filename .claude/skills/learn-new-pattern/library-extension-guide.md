# Library Extension Guide

When and how to extend the sacred-patterns TypeScript library (`src/ts/`) with new geometric primitives.

## When to Extend

Extend the library when:
1. A `pattern.json` layer type has no corresponding TypeScript class
2. The primitive will be reused across multiple sessions
3. The geometry is non-trivial (not just a simple polygon with different side count)

Do NOT extend for:
- One-off shapes that can be expressed as point arrays in the D3.js output
- Styling or color concerns (handle in the D3 compiler, not the geometry library)
- Layout/composition (handle in the pattern.json layer system)

## Conventions to Follow

These conventions are derived from the existing codebase. Follow them exactly.

### File Structure

Create a new `.ts` file in `src/ts/`:

```typescript
import { Point } from './points';
import { Line } from './lines';
import { Lines } from './lines';
import { Circle } from './circles';

export class NewPrimitive {
    readonly center: Point;
    readonly size: number;

    constructor(center: Point, size: number) {
        this.center = center;
        this.size = size;
    }

    get lines(): Line[] {
        // Return edges for rendering via appendPolygon
        return Lines.fromPoints(this.points);
    }

    get points(): Point[] {
        // Return vertices
        return [];
    }

    get outerCircle(): Circle {
        // Bounding circle for positioning
        return new Circle(this.center.x, this.center.y, this.size);
    }

    rotate(radians: number): NewPrimitive {
        // Return a NEW instance (immutable)
        return new NewPrimitive(this.center, this.size);
    }

    adjacent(x_shift: number, y_shift: number): NewPrimitive {
        // Return a NEW instance at offset position
        return new NewPrimitive(
            new Point(this.center.x + x_shift, this.center.y + y_shift),
            this.size
        );
    }
}
```

### Key Conventions

1. **Constructor signature:** `(center: Point, size: number, ...additionalParams)` — matching the Polygon pattern
2. **Expose `get lines(): Line[]`** — enables rendering via `appendPolygon` in canvas.ts
3. **Expose `get points(): Point[]`** — enables direct vertex access
4. **Expose `get outerCircle(): Circle`** — enables circle-based positioning (surroundingCircles, etc.)
5. **Immutable transforms** — `rotate()`, `adjacent()`, `translate()` return NEW instances, never mutate
6. **Use Point, Line, Circle** — build on existing primitives, don't reimplement coordinate math
7. **Lodash (`_`)** is available as a global — use it for functional operations

### Export Registration

Add exports to `src/ts/index.ts`:

```typescript
// At the top, add import
import { NewPrimitive } from './new-primitive';

// In the exports (the file uses direct exports, not a namespace)
export { NewPrimitive };
```

The existing index.ts re-exports specific items. Follow the same pattern — import then export.

### Verification

After creating/modifying files:

```bash
make compile    # Runs: npx tsc && npx eslint . --ext .ts,.tsx
```

Both TypeScript compilation AND ESLint must pass. Common issues:
- Unused imports (ESLint error) — remove any imports you don't use
- Unused parameters (strict mode) — prefix with `_` if intentionally unused
- Missing return types — TypeScript strict mode requires explicit returns on public methods
- No `any` type — use proper types or generics

## Planned Extensions

These files are likely to be needed as sessions study more complex patterns:

### `src/ts/star-polygon.ts` — StarPolygon

The {n/k} star polygon, connecting every k-th vertex of a regular n-gon.

```typescript
export class StarPolygon {
    readonly center: Point;
    readonly size: number;        // outer radius
    readonly n: number;           // number of vertices
    readonly k: number;           // step size
    readonly radial_shift: number;

    constructor(center: Point, size: number, n: number, k: number, radial_shift: number = 0);

    get points(): Point[];        // n vertices on outer circle
    get lines(): Line[];          // edges connecting every k-th vertex
    get innerRadius(): number;    // radius where edges cross
    get outerCircle(): Circle;
    rotate(radians: number): StarPolygon;
}
```

**Key formula:** Inner radius = `size * cos(k * PI / n) / cos((k-1) * PI / n)`

**Difference from existing Star class:** The existing `Star` class creates a star by alternating between an outer circle and inner circles' circumference points. `StarPolygon` uses the {n/k} notation which produces stars by skipping vertices — this is the standard notation in Islamic geometric art.

### `src/ts/rosettes.ts` — Rosette

An n-fold petal pattern (characteristic of Islamic rosette motifs).

```typescript
export class Rosette {
    readonly center: Point;
    readonly n: number;           // number of petals
    readonly innerRadius: number; // petal base radius
    readonly outerRadius: number; // petal tip radius
    readonly petalShape: 'pointed' | 'rounded' | 'ogee';
    readonly radial_shift: number;

    constructor(center: Point, n: number, innerRadius: number, outerRadius: number,
                petalShape?: string, radial_shift?: number);

    get points(): Point[];        // 2n points alternating inner/outer
    get lines(): Line[];          // petal outlines
    get petalPaths(): Point[][];  // array of point arrays, one per petal
    get outerCircle(): Circle;
    rotate(radians: number): Rosette;
}
```

### `src/ts/interlace.ts` — Interlace System

The hardest part — Islamic art's defining visual feature of continuous bands weaving over and under.

```typescript
export class StrapworkBand {
    readonly path: Point[];       // centerline of the band
    readonly width: number;       // band width
    readonly layer: number;       // z-order for over-under

    get offsetPaths(): [Point[], Point[]];  // parallel paths (left/right edges)
    get svgPath(): string;                   // SVG path data string
}

export class InterlaceNetwork {
    readonly bands: StrapworkBand[];

    get crossings(): CrossingPoint[];       // all intersection points
    get renderedBands(): RenderedBand[];     // bands split at crossings with z-order

    // At each crossing, alternation: (segment_index + band_index) % 2
    static alternateWeave(crossings: CrossingPoint[]): void;
}

export class ConcentricRingBands {
    // Generate bands following concentric polygon/circle guides
    static fromPolygon(sides: number, radius: number, center: Point,
                       bandWidth: number, rotation?: number): StrapworkBand;
    static fromCircle(radius: number, center: Point,
                      bandWidth: number): StrapworkBand;
}

export class RadialConnectorBands {
    // Generate bands connecting between concentric rings
    static between(innerRadius: number, outerRadius: number,
                   center: Point, count: number,
                   bandWidth: number): StrapworkBand[];
}
```

**Rendering notes:**
- Bands need SVG `<path>` output (not just `<line>`) since they have width
- Use `d3.line()` with stroke-width for simple bands
- For proper over-under: render each band in segments, with crossing segments ordered by their `layer` value
- At crossings, the "under" band gets a subtle shadow via a parallel dark path offset by 1-2px

### `src/ts/arabesque.ts` — Arabesque Motifs

Curvilinear vegetal motifs (vine paths, palmettes, leaf shapes).

```typescript
export class Vine {
    readonly spine: Point[];      // control points for the vine's path
    readonly leafPositions: number[]; // parameter values along spine where leaves attach

    get svgPath(): string;        // cubic bezier SVG path
    get leaves(): Leaf[];         // leaf shapes at each position
}

export class Palmette {
    readonly center: Point;
    readonly size: number;
    readonly lobes: number;       // number of lobes (typically 3, 5, or 7)

    get svgPath(): string;        // symmetric palmette shape
}
```

### `src/ts/girih.ts` — Girih Tiles

The 5 girih tile shapes with their internal strap-line generation rules.

```typescript
export class GirihTile {
    readonly center: Point;
    readonly edgeLength: number;
    readonly shape: 'decagon' | 'pentagon' | 'bowtie' | 'rhombus' | 'hexagon';
    readonly rotation: number;

    get points(): Point[];
    get lines(): Line[];
    get strapLines(): Line[];     // internal decoration lines (girih strap patterns)
    get outerCircle(): Circle;
}
```

### `src/ts/tiling.ts` — Tessellation Helpers

```typescript
export class RadialTiling {
    static repeat<T>(element: T, count: number, radius: number,
                     center: Point, rotateElements?: boolean): T[];
}

export class GridTiling {
    static repeat<T>(element: T, cols: number, rows: number,
                     spacingX: number, spacingY: number,
                     origin: Point, offsetAlternateRows?: boolean): T[];
}
```

### `src/ts/palettes.ts` — Color Palettes

```typescript
export interface ColorPalette {
    name: string;
    colors: Record<string, string>;
    distribution: 'radial' | 'zonal' | 'per-tile' | 'material';
}

export const PALETTES: Record<string, ColorPalette>;
// Ottoman Blue, Moroccan, Persian, Alhambra, Mamluk, Mughal, Dark/Digital
```

## Key Files to Modify

| File | When | What |
|------|------|------|
| `src/ts/index.ts` | Always | Add export for new class |
| `src/ts/polygons.ts` | Rarely | Only if extending base Polygon behavior |
| `src/ts/star.ts` | Rarely | Only if extending existing Star; prefer star-polygon.ts |
| `src/ts/canvas.ts` | Sometimes | If new rendering functions needed (e.g., appendPath for bands) |

## Documentation

When extending the library, create `iterations/{nn}/library-changes.md`:

```markdown
# Library Changes — Iteration {nn}

## New file: src/ts/star-polygon.ts
- `StarPolygon` class implementing {n/k} star polygon notation
- Constructor: (center, size, n, k, radial_shift?)
- Key methods: points, lines, innerRadius, rotate

## Modified file: src/ts/index.ts
- Added export for StarPolygon

## Verification
- `make compile` passed: yes/no
- Tested with: [how it was used in this iteration]
```

Also update `learnings/library-extensions-log.md` with the addition.
