---
name: collecting-feedback-on-components
description: Maintain the component showcase page for visual validation of declarative pattern building blocks, and process user feedback on individual components.
user_invocable: true
argument: (optional) markdown feedback text to process, or "add <component-name>" to add a new component
---

# collecting-feedback-on-components

Maintain the component showcase page (`site/components/index.html`) and process feedback on declarative pattern components.

For reusable design patterns shared across feedback tools (layout, drag interactions, extraction channels, coordinate normalization), see `feedback-tool-patterns.md` in this directory.

## Invocation

```
/collecting-feedback-on-components
/collecting-feedback-on-components add star-polygon-variant
/collecting-feedback-on-components <pasted markdown feedback>
```

## What This Skill Does

1. **Maintains the showcase page** — When new components or aggregations are added to the declarative language (`declarative-language-guide.md`), this skill adds them to the showcase with a live D3.js rendering, parameter badges, and feedback textarea.

2. **Processes feedback** — When the user pastes markdown feedback (from the "Copy All Feedback" button on the showcase page), this skill parses it and creates actionable items for each component that received feedback.

3. **Tracks validation status** — Keeps a record of which components have been visually validated and which still need review.

## Showcase Page Location

- Source: `site/components/index.html`
- Live URL: `https://art.bytesofpurpose.com/components/`
- Self-contained HTML with inline CSS and D3.js v7 from CDN

## Adding a New Component

When adding a new component to the showcase:

1. Add an entry to the `COMPONENTS` array in `site/components/index.html`:
   ```javascript
   {
     id: "unique-id",
     name: "component-name",
     tag: "primitive|tiling|strapwork|repetition|special|aggregation",
     description: "What this component renders",
     params: { key: "value" },
     render: renderFunctionName
   }
   ```

2. Implement the render function:
   ```javascript
   function renderFunctionName(svg, cx, cy) {
     // cx, cy = center of 400x400 SVG
     // Use polarX(), polarY(), regularPolygonPoints(), starPoints() utilities
     // Follow compile-d3.md for rendering conventions
   }
   ```

3. The render function should demonstrate the component in isolation with representative parameters. Use the gold/dark color scheme (`#c9a84c` on `#0a0a0f` background).

## Component Tags

| Tag | Color | Description |
|-----|-------|-------------|
| `primitive` | Green | Basic geometric elements (star-polygon, polygon, circle, line) |
| `tiling` | Gold | Filled tile decompositions (star-tiling, filled-rosette, interstitial-tiles, girih-tile) |
| `strapwork` | Purple | Edge networks and interlace bands (radial-network, interlace-network, strapwork-band) |
| `repetition` | Teal | Repetition operators (radial-repeat, grid-repeat) |
| `special` | Pink | Special constructions (rosette, flower-of-life, muqarnas-projection) |
| `aggregation` | Yellow | Multi-component compositions |

## Processing Feedback Markdown

When the user provides feedback markdown (copied from the showcase page), it follows this format:

```markdown
# Component Feedback — 2026-03-01

## star-tiling
The kites should be more elongated...

## filled-rosette
Petal tips need to be sharper...
```

For each component with feedback:
1. Identify the component in the declarative language guide
2. Determine if the feedback is about the rendering accuracy, missing features, or visual bugs
3. Create a plan to address the feedback
4. Update the showcase render function if it's a rendering issue
5. Note gaps in the declarative language if the component can't express what's needed

## Keeping In Sync with Declarative Language

When `declarative-language-guide.md` changes:
- Check if any new layer types were added
- Check if existing layer types gained new parameters
- Update the showcase to reflect additions or changes
- Update parameter badges on affected cards

## Current Components (20)

### Primitives (4)
- star-polygon, polygon, circle, line

### Tiling (4)
- star-tiling, filled-rosette, interstitial-tiles, girih-tile

### Strapwork (3)
- radial-network, interlace-network, strapwork-band

### Repetition (2)
- radial-repeat, grid-repeat

### Special (3)
- rosette, flower-of-life, muqarnas-projection

### Aggregations (4)
- star + satellites, full medallion, star + interstitial tiles, girih tessellation
