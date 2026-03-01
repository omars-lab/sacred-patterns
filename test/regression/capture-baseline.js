/**
 * Captures the baseline SVG output for visual regression testing.
 * Run ONCE before any dependency changes to establish the reference.
 *
 * Usage: node test/regression/capture-baseline.js
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const REFERENCE_PATH = path.join(__dirname, 'reference.svg');

// Set up jsdom with a minimal HTML document
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  pretendToBeVisual: true,
  url: 'http://localhost',
});

const { window } = dom;

// Expose globals that the UMD bundle expects
global.window = window;
global.document = window.document;
global.navigator = window.navigator;
global.HTMLElement = window.HTMLElement;
global.SVGElement = window.SVGElement;

// Load lodash first (the bundle expects it as external)
const _ = require('lodash');
window._ = _;
global._ = _;

// Load D3 (the bundle expects it as external)
const d3 = require('d3');
window.d3 = d3;
global.d3 = d3;

// Load the bundle
const bundlePath = path.join(__dirname, '..', '..', 'site', 'bundle.js');
if (!fs.existsSync(bundlePath)) {
  console.error('ERROR: site/bundle.js not found. Run `npm run build` first.');
  process.exit(1);
}

// The UMD wrapper references `window`, so we need it available
const bundleCode = fs.readFileSync(bundlePath, 'utf8');
const script = new (require('vm').Script)(bundleCode);
script.runInThisContext();

const sacredPatterns = window.sacredPatterns || global.sacredPatterns;
if (!sacredPatterns) {
  console.error('ERROR: sacredPatterns not found after loading bundle.');
  process.exit(1);
}

// Call the main drawing function with fixed parameters (matching templates/index.tpl)
const radius = 100;
const maxLevels = 2;
const size = maxLevels * 3;
const background_theme = { background: 'RGBA(0,0,0,0.9)' };
const line_theme = { stroke: 'url(#invertedSvgGradient)', 'stroke-width': '1' };

const svg = sacredPatterns.drawHexagonWithSurroundingNonagons('d6', radius, size, background_theme, line_theme);

// Serialize the SVG
const svgElement = window.document.getElementById('d6');
if (!svgElement) {
  console.error('ERROR: SVG element #d6 not found in DOM.');
  process.exit(1);
}

const svgHTML = svgElement.outerHTML;
fs.writeFileSync(REFERENCE_PATH, svgHTML, 'utf8');
console.log(`Baseline SVG captured to ${REFERENCE_PATH}`);
console.log(`Size: ${svgHTML.length} characters`);
