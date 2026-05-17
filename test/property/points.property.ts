/**
 * Property-based tests for Point (sacred-patterns#350 slice 3).
 *
 * Companion to the existing visual-regression check — that one pins the
 * output of one specific pattern; these pin the *algebraic* invariants of
 * the geometric primitives every pattern is built on.
 *
 * Why this file is the entry point for property testing in sacred-patterns:
 *   Point.distanceBetweenPoints sits underneath every layout calculation
 *   (rosette radii, satellite placement, band width). A silent regression
 *   here — e.g. distance(p, q) !== distance(q, p) under some edge case —
 *   would surface as inscrutable per-pattern geometry drift many layers
 *   up the stack. Pinning the algebra at the leaf is the cheapest catch.
 *
 * Mirrors the qiyas hypothesis pattern (qiyas#350 slice 1) and the bikar
 * fast-check pattern (bikar#350 slice 2): state invariant, generate
 * random witnesses, assert with bounded tolerance.
 *
 * Run: npx tsx test/property/points.property.ts
 */

import fc from 'fast-check';
import { Point } from '../../src/ts/points';

const pointArb = fc.record({
    x: fc.double({ min: -1e6, max: 1e6, noNaN: true, noDefaultInfinity: true }),
    y: fc.double({ min: -1e6, max: 1e6, noNaN: true, noDefaultInfinity: true }),
}).map(({ x, y }) => new Point(x, y));

const translationArb = fc.record({
    dx: fc.double({ min: -1e6, max: 1e6, noNaN: true, noDefaultInfinity: true }),
    dy: fc.double({ min: -1e6, max: 1e6, noNaN: true, noDefaultInfinity: true }),
});

const failures: string[] = [];

function check(name: string, prop: fc.IProperty<unknown>): void {
    try {
        fc.assert(prop, { numRuns: 200 });
        console.log(`  PASS  ${name}`);
    } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        console.error(`  FAIL  ${name}`);
        console.error(`        ${msg.split('\n')[0]}`);
        failures.push(name);
    }
}

console.log('Point — property tests');

// Distance is symmetric: d(a, b) == d(b, a). The function uses Math.hypot
// which is commutative under squaring, so this is a true equality — no
// tolerance needed.
check(
    'distance is symmetric',
    fc.property(pointArb, pointArb, (a: Point, b: Point) => {
        const d1 = Point.distanceBetweenPoints(a, b);
        const d2 = Point.distanceBetweenPoints(b, a);
        if (d1 !== d2) throw new Error(`d(a,b)=${d1} d(b,a)=${d2}`);
    }),
);

// Distance from a point to itself is zero.
check(
    'distance from a point to itself is zero',
    fc.property(pointArb, (p: Point) => {
        const d = Point.distanceBetweenPoints(p, p);
        if (d !== 0) throw new Error(`d(p,p)=${d}`);
    }),
);

// Distance is non-negative. The function returns Math.hypot which can't be
// negative, but this is the property that justifies "distance" as a name.
check(
    'distance is non-negative',
    fc.property(pointArb, pointArb, (a: Point, b: Point) => {
        const d = Point.distanceBetweenPoints(a, b);
        if (!(d >= 0)) throw new Error(`d=${d} (negative or NaN)`);
    }),
);

// Translation invariance: shifting both endpoints by the same offset
// preserves distance. This is the load-bearing invariant for every
// pattern that re-centers a sub-shape (every satellite, every petal).
check(
    'distance is translation-invariant',
    fc.property(pointArb, pointArb, translationArb, (a: Point, b: Point, t: { dx: number; dy: number }) => {
        const d1 = Point.distanceBetweenPoints(a, b);
        const a2 = new Point(a.x + t.dx, a.y + t.dy);
        const b2 = new Point(b.x + t.dx, b.y + t.dy);
        const d2 = Point.distanceBetweenPoints(a2, b2);
        // Floating-point: shifting (1e6, 0) by (1e6, 0) and back loses
        // precision around 1e-10. Tolerance scales with the magnitudes.
        const scale = Math.max(1, Math.abs(a.x), Math.abs(a.y), Math.abs(b.x), Math.abs(b.y), Math.abs(t.dx), Math.abs(t.dy));
        const tol = 1e-9 * scale;
        if (Math.abs(d1 - d2) > tol) {
            throw new Error(`d=${d1} d(translated)=${d2} delta=${Math.abs(d1 - d2)} tol=${tol}`);
        }
    }),
);

if (failures.length > 0) {
    console.error(`\n${failures.length} property test(s) failed.`);
    process.exit(1);
} else {
    console.log('\nAll property tests passed.');
}
