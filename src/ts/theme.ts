/**
 * Theme shapes that drawing entry points accept to style a rendered
 * pattern — answers "what is the exact, typed contract a caller passes
 * to recolor a drawing's canvas background and its line/fill strokes,
 * without the call site having to know D3's `.style()` key vocabulary?".
 *
 * These replace the prior `unknown` parameters on the draw functions
 * (tenets 15/16 — model the variant, never launder it through `unknown`).
 * `BackgroundTheme` is iterated key-by-key into `svg.style(k, v)`, so any
 * CSS property is valid; `background` is the one always-present key.
 * `LineTheme` mirrors exactly the three keys `appendPolygon` reads via
 * `_.get(metadata, ...)`: `stroke`, `stroke-width`, `fill`.
 */

/**
 * Canvas-level style bag applied to an `<svg>` via `svg.style(key, value)`
 * — `background` is required (every drawing has a backdrop); additional
 * CSS keys (e.g. `opacity`, `filter`) are forwarded verbatim. Example:
 * `{ background: "RGBA(0,0,0,0.9)" }` paints the near-black hero backdrop.
 */
export type BackgroundTheme = { background: string } & Record<string, string>;

/**
 * Per-polyline stroke/fill overrides consumed by `appendPolygon` — the
 * keys map one-to-one onto the `_.get(metadata, ...)` reads in that
 * function, so an empty `{}` yields the function's built-in defaults
 * (black stroke, width 1, no fill). Example:
 * `{ stroke: "url(#svgGradient)", "stroke-width": "1" }` draws the
 * gradient strapwork lines; `{ fill: "RGBA(118,215,196,0.5)" }` tints faces.
 */
export interface LineTheme {
  stroke?: string;
  "stroke-width"?: string;
  fill?: string;
}
