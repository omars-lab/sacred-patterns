/**
 * Graduation test for the d3 vocabulary convergence — surface C.
 *
 * The sacred-patterns renderer was rebuilt from per-shape `<polyline>`
 * emission onto the shared face-list vocabulary (`faceConstructs` +
 * `joinFaces`) that bikar surfaces A and B already speak. This test is the
 * failing-before / passing-after record of that cutover:
 *
 *   - BEFORE: the render emitted `<polyline>` and there was no
 *     `faceConstructs`/`faceKey` on the public surface — every assertion
 *     below about `<path class="face">`, `data-face-index`, and the
 *     exported mapper fails.
 *   - AFTER: faces render as keyed `<path class="face">` whose coordinate
 *     multiset is byte-identical to the pre-cutover polyline baseline
 *     (`faces-golden.json`) — pixel-identity across the format change.
 *
 * Run under Node >=22 (the bundle harness `require()`s ESM d3), same as
 * `check.js`. Wired into `npm test`.
 */
const fs = require('fs');
const path = require('path');
const assert = require('assert');
const { JSDOM } = require('jsdom');

const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  pretendToBeVisual: true,
  url: 'http://localhost',
});
const { window } = dom;
global.window = window;
global.document = window.document;
global.HTMLElement = window.HTMLElement;
global.SVGElement = window.SVGElement;

const _ = require('lodash');
window._ = _;
global._ = _;
const d3 = require('d3');
window.d3 = d3;
global.d3 = d3;

const bundlePath = path.join(__dirname, '..', '..', 'site', 'bundle.js');
if (!fs.existsSync(bundlePath)) {
  console.error('ERROR: site/bundle.js not found. Run `npm run build` first.');
  process.exit(1);
}
new (require('vm').Script)(fs.readFileSync(bundlePath, 'utf8')).runInThisContext();
const sp = window.sacredPatterns || global.sacredPatterns;
assert.ok(sp, 'sacredPatterns global present after loading bundle');

let failures = 0;
function check(name, fn) {
  try {
    fn();
    console.log(`  ok  ${name}`);
  } catch (e) {
    failures++;
    console.error(`  FAIL ${name}: ${e.message}`);
  }
}

// A structural `HasLines`: a boundary as connected {p1,p2} segments, the
// exact shape `.lines` yields. Lets us exercise the pure mapper without
// pulling in the geometry classes.
function ringLines(pts) {
  const lines = [];
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i];
    const b = pts[(i + 1) % pts.length];
    lines.push({ p1: { x: a[0], y: a[1] }, p2: { x: b[0], y: b[1] } });
  }
  return { lines };
}

// ---- pure mapper: faceConstructs ----------------------------------------
check('faceConstructs: index is the ordinal join key, contiguous from 0', () => {
  const cs = sp.faceConstructs([ringLines([[0, 0], [2, 0], [1, 2]]), ringLines([[3, 3], [4, 3], [4, 4]])]);
  assert.strictEqual(cs.length, 2);
  assert.deepStrictEqual(cs.map(c => c.index), [0, 1]);
  assert.strictEqual(sp.faceKey(cs[0]), '0');
  assert.strictEqual(sp.faceKey(cs[1]), '1');
});

check('faceConstructs: polygon is the closed ring, last vertex == first', () => {
  const [c] = sp.faceConstructs([ringLines([[0, 0], [2, 0], [1, 2]])]);
  const poly = c.polygon;
  assert.strictEqual(poly.length, 4); // 3 starts + closing return
  assert.deepStrictEqual([poly[0].x, poly[0].y], [0, 0]);
  assert.deepStrictEqual([poly[poly.length - 1].x, poly[poly.length - 1].y], [0, 0]);
});

check('faceConstructs: centroid is the mean of distinct vertices', () => {
  const [c] = sp.faceConstructs([ringLines([[0, 0], [3, 0], [0, 3]])]);
  assert.strictEqual(c.centroid.x, 1);
  assert.strictEqual(c.centroid.y, 1);
});

check('faceConstructs: ring is never synthesised (K10 transfer condition)', () => {
  const cs = sp.faceConstructs([ringLines([[0, 0], [1, 0], [0, 1]])]);
  assert.strictEqual(cs[0].ring, undefined);
});

check('faceConstructs: empty-boundary shapes are dropped (count parity with appendPolygon)', () => {
  const cs = sp.faceConstructs([ringLines([[0, 0], [1, 0], [0, 1]]), { lines: [] }]);
  assert.strictEqual(cs.length, 1);
  assert.strictEqual(cs[0].index, 0);
});

// Origin-relative (CLAUDE.md line 158): scaling every input coordinate by
// k scales every output polygon coordinate by k — the mapper injects no
// absolute constant of its own.
check('faceConstructs: origin-relative — scaling the input by k scales the polygon by k', () => {
  const base = [[10, 20], [40, 20], [25, 50]];
  const k = 2.5;
  const [c1] = sp.faceConstructs([ringLines(base)]);
  const [ck] = sp.faceConstructs([ringLines(base.map(([x, y]) => [x * k, y * k]))]);
  assert.strictEqual(c1.polygon.length, ck.polygon.length);
  for (let i = 0; i < c1.polygon.length; i++) {
    assert.ok(Math.abs(ck.polygon[i].x - c1.polygon[i].x * k) < 1e-9, `x[${i}] scales by k`);
    assert.ok(Math.abs(ck.polygon[i].y - c1.polygon[i].y * k) < 1e-9, `y[${i}] scales by k`);
  }
});

// Cross-surface parity: an A-shaped face and a B-shaped face of the same
// index key identically (the convergence invariant, mirroring bikar's own
// faceKey graduation test).
check('faceKey: A-shaped and B-shaped faces of the same index key identically', () => {
  const a = { index: 7, polygon: [], centroid: { x: 0, y: 0 }, classes: ['face'] };
  const b = { index: 7, status: 'matched' };
  assert.strictEqual(sp.faceKey(a), sp.faceKey(b));
  assert.strictEqual(sp.faceKey(a), '7');
  assert.notStrictEqual(sp.faceKey({ index: 3 }), sp.faceKey({ index: 4 }));
});

// ---- rendered surface: the join emits keyed <path class="face"> ---------
sp.drawHexagonWithSurroundingNonagons('d6', 100, 6, { background: 'RGBA(0,0,0,0.9)' }, { stroke: 'url(#invertedSvgGradient)', 'stroke-width': '1' });
const svg = window.document.getElementById('d6');
const html = svg.outerHTML;

check('render: faces are <path class="face">, not <polyline>', () => {
  const paths = (html.match(/<path[ />]/g) || []).length;
  const polylines = (html.match(/<polyline[ />]/g) || []).length;
  assert.ok(paths > 0, 'at least one path.face');
  assert.strictEqual(polylines, 0, 'no polyline survives the cutover');
  assert.strictEqual((html.match(/class="face"/g) || []).length, paths, 'every path carries class="face"');
});

check('render: data-face-index is the join key, contiguous 0..n-1', () => {
  const idx = [...html.matchAll(/data-face-index="(\d+)"/g)].map(m => Number(m[1]));
  const paths = (html.match(/<path[ />]/g) || []).length;
  assert.strictEqual(idx.length, paths, 'every path has data-face-index');
  const sorted = [...idx].sort((a, b) => a - b);
  for (let i = 0; i < sorted.length; i++) assert.strictEqual(sorted[i], i, `index ${i} present`);
});

check('render: coordinate multiset is byte-identical to the pre-cutover polyline golden', () => {
  const golden = JSON.parse(fs.readFileSync(path.join(__dirname, 'faces-golden.json'), 'utf8')).pairs;
  const re = /(-?[\d.]+),(-?[\d.]+)/g;
  const cur = [];
  let m;
  while ((m = re.exec(html)) !== null) cur.push(`${m[1]},${m[2]}`);
  cur.sort();
  assert.strictEqual(cur.length, golden.length, `pair count (${cur.length}) == golden (${golden.length})`);
  for (let i = 0; i < golden.length; i++) {
    assert.strictEqual(cur[i], golden[i], `pair ${i} matches golden`);
  }
});

if (failures > 0) {
  console.error(`\nFAIL: ${failures} face-vocabulary assertion(s) failed.`);
  process.exit(1);
}
console.log('PASS: face-list vocabulary (surface C) — join, keys, and pixel-identity all hold.');
