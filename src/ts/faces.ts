import {Line} from "./lines";
import {Point} from "./points";

/**
 * `FaceConstruct` — the shared face-list vocabulary this library now
 * speaks, converged onto bikar's surface A (`FaceConstruct` in
 * `bikar packages/core/src/viz/face-constructs.ts`). A face is identified
 * by `index` (its data-join key — `faceKey(f)` is `String(f.index)`),
 * bounded by `polygon` (a closed ring of pattern-unit points whose last
 * entry returns to the first), centred at `centroid`, and painted by
 * `classes`.
 *
 * `ring` is the OPTIONAL concentric-styling index and carries the K10
 * transfer condition from the convergence design (§9,
 * `3d-models:docs/vocabulary-convergence-design.md`): it is populated
 * ONLY where a genuine concentric index exists (a `Circle` ring). This
 * library builds faces from polygons and stars — never from concentric
 * circle rings — so nothing here synthesises `ring`; it stays undefined.
 * Modelled as a typed interface, not a `Record` bag (tenet 15).
 */
export interface FaceConstruct {
    readonly index: number;
    readonly polygon: readonly Point[];
    readonly centroid: Point;
    readonly classes: readonly string[];
    readonly ring?: number;
}

/**
 * A geometry primitive that exposes its boundary as connected `Line`s —
 * every `Polygon`/`Star` subclass already satisfies this via its `.lines`
 * getter, so `faceConstructs` adapts them without a new method.
 */
export interface HasLines {
    readonly lines: Line[];
}

/**
 * `polygonFromLines` — the closed point ring of a boundary, byte-identical
 * to the vertex sequence `appendPolygon` renders (`canvas.ts`): one point
 * per line start, then the final line's end (which, for a closed boundary,
 * is the first point again). Pure; it reuses the `Line`s' own `Point`
 * instances verbatim so a rendered coordinate string is bit-for-bit what
 * the prior `<polyline points=...>` produced.
 */
export function polygonFromLines(lines: readonly Line[]): readonly Point[] {
    if (lines.length === 0) {
        return [];
    }
    const last = lines[lines.length - 1];
    return [...lines.map(l => l.p1), last.p2];
}

/**
 * `centroidOf` — the arithmetic mean of a ring's distinct vertices (the
 * repeated closing point is dropped so it does not double-weight the first
 * vertex). Face metadata only; it never feeds the rendered path, so it
 * cannot perturb pixel output.
 */
export function centroidOf(polygon: readonly Point[]): Point {
    const ring = polygon.length > 1 ? polygon.slice(0, -1) : polygon;
    const n = ring.length || 1;
    const sx = ring.reduce((a, p) => a + p.x, 0);
    const sy = ring.reduce((a, p) => a + p.y, 0);
    return new Point(sx / n, sy / n);
}

/**
 * `faceConstructs` — the `faceConstructs()`-analog (bikar surface A): map a
 * collection of boundary-bearing shapes to a `FaceConstruct[]` in emission
 * order. `index` is the ordinal that becomes the join key; `classes`
 * defaults to `["face"]`. Shapes with no boundary are dropped so the face
 * count matches the prior per-shape `<polyline>` count (`appendPolygon`
 * no-oped on empty lines). Pure and immutable — no shape is mutated and no
 * module-level state is touched (tenet 10).
 */
export function faceConstructs(
    shapes: readonly HasLines[],
    classes: readonly string[] = ["face"],
): readonly FaceConstruct[] {
    return shapes
        .filter(s => s.lines.length > 0)
        .map((s, index) => {
            const polygon = polygonFromLines(s.lines);
            return {index, polygon, centroid: centroidOf(polygon), classes};
        });
}
