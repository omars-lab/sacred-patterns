/**
 * Visual regression check — compares current SVG output against the reference baseline.
 * Run after any dependency/build changes to verify output is unchanged.
 *
 * Compares geometry (polyline points, circle positions, element count)
 * rather than exact string match, to tolerate serialization differences
 * between D3 versions.
 *
 * Usage: node test/regression/check.js
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const REFERENCE_PATH = path.join(__dirname, 'reference.svg');

if (!fs.existsSync(REFERENCE_PATH)) {
  console.error('ERROR: reference.svg not found. Run capture-baseline.js first.');
  process.exit(1);
}

const reference = fs.readFileSync(REFERENCE_PATH, 'utf8');

// Set up jsdom
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  pretendToBeVisual: true,
  url: 'http://localhost',
});

const { window } = dom;
global.window = window;
global.document = window.document;
global.navigator = window.navigator;
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

const bundleCode = fs.readFileSync(bundlePath, 'utf8');
const script = new (require('vm').Script)(bundleCode);
script.runInThisContext();

const sacredPatterns = window.sacredPatterns || global.sacredPatterns;
if (!sacredPatterns) {
  console.error('ERROR: sacredPatterns not found after loading bundle.');
  process.exit(1);
}

const radius = 100;
const maxLevels = 2;
const size = maxLevels * 3;
const background_theme = { background: 'RGBA(0,0,0,0.9)' };
const line_theme = { stroke: 'url(#invertedSvgGradient)', 'stroke-width': '1' };

sacredPatterns.drawHexagonWithSurroundingNonagons('d6', radius, size, background_theme, line_theme);

const svgElement = window.document.getElementById('d6');
if (!svgElement) {
  console.error('ERROR: SVG element #d6 not found in DOM.');
  process.exit(1);
}

const current = svgElement.outerHTML;

// Extract geometry for comparison
function extractGeometry(svgString) {
  const pointsRegex = /points="([^"]+)"/g;
  const points = [];
  let match;
  while ((match = pointsRegex.exec(svgString)) !== null) {
    points.push(match[1]);
  }
  return points.sort();
}

function countElements(svgString, tag) {
  const regex = new RegExp(`<${tag}[ />]`, 'g');
  return (svgString.match(regex) || []).length;
}

const refPoints = extractGeometry(reference);
const curPoints = extractGeometry(current);

let passed = true;

// Check polyline count
if (refPoints.length !== curPoints.length) {
  console.error(`FAIL: Polyline count differs (reference: ${refPoints.length}, current: ${curPoints.length})`);
  passed = false;
} else {
  console.log(`  Polyline count: ${curPoints.length} (matches)`);
}

// Check all polyline points are identical
for (let i = 0; i < Math.min(refPoints.length, curPoints.length); i++) {
  if (refPoints[i] !== curPoints[i]) {
    console.error(`FAIL: Polyline ${i} geometry differs!`);
    console.error(`  Reference: ${refPoints[i].substring(0, 80)}...`);
    console.error(`  Current:   ${curPoints[i].substring(0, 80)}...`);
    passed = false;
    break;
  }
}
if (passed) {
  console.log('  All polyline coordinates match');
}

// Check element counts
for (const tag of ['polyline', 'circle', 'linearGradient', 'stop', 'defs']) {
  const refCount = countElements(reference, tag);
  const curCount = countElements(current, tag);
  if (refCount !== curCount) {
    console.error(`FAIL: <${tag}> count differs (reference: ${refCount}, current: ${curCount})`);
    passed = false;
  } else {
    console.log(`  <${tag}> count: ${curCount} (matches)`);
  }
}

if (passed) {
  console.log('PASS: SVG geometry matches reference baseline.');
  process.exit(0);
} else {
  const currentPath = path.join(__dirname, 'current.svg');
  fs.writeFileSync(currentPath, current, 'utf8');
  console.error(`Current output saved to ${currentPath}`);
  process.exit(1);
}
