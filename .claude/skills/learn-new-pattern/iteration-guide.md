# Iteration Guide

Core workflow for iteratively replicating a reference pattern. Each iteration produces a self-contained D3.js HTML file, evaluates it against the reference, and applies corrections.

## Iteration Folder Structure

Each iteration lives in `iterations/{nn}/` (zero-padded: 01, 02, etc.):

```
iterations/01/
  pattern.json          # Pattern definition for this iteration
  output.html           # Self-contained D3.js v7 HTML
  screenshot.png        # Browser screenshot
  evaluation.md         # Structured comparison
  retrospective.md      # Why did analysis lead to this output?
  guidance.md           # What to change next
  library-changes.md    # Any TS library changes (if applicable)
```

## The Loop

### A. Generate

1. Read the current `pattern.json` from the session root (or from the previous iteration's guidance)
2. Apply any corrections from the previous iteration's `guidance.md`
3. Save the updated `pattern.json` to `iterations/{nn}/pattern.json`
4. Compile to D3.js HTML following `compile-d3.md`
5. Save as `iterations/{nn}/output.html`

**HTML Requirements** (matching session-abc/test.html format):
- D3.js v7 loaded from CDN: `https://d3js.org/d3.v7.min.js`
- Single `<div id="pattern">` container
- 800x800 SVG canvas (configurable via pattern.json)
- Dark background applied to SVG, not body
- Pattern centered in SVG
- NO ES6 template literals (use string concatenation)
- All images embedded as base64 data URIs
- File must be fully self-contained (no external resources except D3 CDN)

### B. Render & Capture

1. Open the HTML file in browser:
   - Use `mcp__chrome-devtools__navigate_page` with `file:///` URL, OR
   - Use `mcp__claude-in-chrome__navigate` with the file path
2. Wait for rendering to complete (D3 operations are synchronous, but wait 1-2 seconds)
3. Take a screenshot:
   - Use `mcp__chrome-devtools__take_screenshot` and save to `iterations/{nn}/screenshot.png`, OR
   - Use `mcp__claude-in-chrome__computer` with `action: "screenshot"`
4. Read the screenshot to verify it rendered correctly

### C. Evaluate

Compare the screenshot against the reference image. Score each criterion:

| Criterion | Score | Description |
|-----------|-------|-------------|
| Symmetry Order | MISSING / PARTIAL / PRESENT / ACCURATE | Is the n-fold symmetry correct? |
| Element Count | MISSING / PARTIAL / PRESENT / ACCURATE | Are all stars, polygons, rosettes present? |
| Radial Proportions | MISSING / PARTIAL / PRESENT / ACCURATE | Do ring ratios match the analysis? |
| Star Geometry | MISSING / PARTIAL / PRESENT / ACCURATE | Are {n/k} star shapes correct? |
| Interlace/Strapwork | MISSING / PARTIAL / PRESENT / ACCURATE | Over-under weaving present and correct? |
| Color Palette | MISSING / PARTIAL / PRESENT / ACCURATE | Colors match reference? |
| Color Distribution | MISSING / PARTIAL / PRESENT / ACCURATE | Radial/zonal coloring correct? |
| Overall Composition | MISSING / PARTIAL / PRESENT / ACCURATE | Does it "look right" as a whole? |

**Scoring rules:**
- MISSING (0.0) — element is completely absent
- PARTIAL (0.4) — element is present but wrong (wrong count, wrong proportions, wrong colors)
- PRESENT (0.7) — element is present and approximately correct
- ACCURATE (1.0) — element closely matches the reference

**Confidence score** = mean of all applicable criterion scores (skip N/A criteria like interlace if the reference has none).

Write `evaluation.md` with:
```markdown
# Iteration {nn} Evaluation

## Scores
| Criterion | Score | Notes |
|-----------|-------|-------|
| Symmetry Order | ACCURATE | 8-fold symmetry correctly rendered |
| Element Count | PARTIAL | Missing 4 of 8 satellite stars |
| ... | ... | ... |

## Confidence: 0.XX

## Summary
[2-3 sentences on overall quality]
```

### D. Retrospect

**This is the core learning mechanism.** When any criterion scores MISSING or PARTIAL:

1. **Re-examine the reference image** focusing specifically on the failing area
2. **Compare** what `analysis.md` says about that area vs what was actually rendered
3. **Identify the misinterpretation** — what did the analysis get wrong?

Common types of misinterpretation:
- **Count errors** — "I counted 8 satellites but there are 12"
- **Proportion errors** — "r4 should be 0.65, not 0.55"
- **Type errors** — "These are {8/3} stars, not {8/2}"
- **Structural errors** — "The interlace is concentric, not radial"
- **Missing elements** — "I didn't notice the inner rosettes between the stars"
- **Color errors** — "The gradient goes warm-to-cool, not bright-to-dark"

4. **Update `analysis.md`** and `construction.md` with corrections (mark changes with `[CORRECTED iteration {nn}]`)
5. **Record in `retrospective.md`**:

```markdown
# Iteration {nn} Retrospective

## What went wrong
[Describe what was incorrect in the output]

## Root cause
[What did the analysis say that led to this? Why was it wrong?]

## Correction
[What is the corrected understanding?]

## Files updated
- analysis.md: [what changed]
- construction.md: [what changed]
```

6. **Update cross-session learnings** — if this is a generalizable mistake (e.g., "always verify star polygon step size by tracing connections"), add it to `learnings/common-mistakes.md`

### E. Decide

Based on the evaluation:

| Condition | Action |
|-----------|--------|
| Confidence >= 0.85 AND no MISSING | **Complete** — proceed to finalization |
| Confidence >= 0.70 | **Ask user** — show screenshot vs reference, ask if acceptable |
| Confidence < 0.70 | **Iterate** — apply retrospective corrections |
| Iteration count >= 5 | **Ask user** — show progress, ask whether to continue or accept current best |

When iterating, write `guidance.md`:
```markdown
# Guidance for Iteration {nn+1}

## Changes needed
1. [Specific change to pattern.json]
2. [Specific change to pattern.json]

## Analysis corrections applied
- [What was corrected in analysis.md]

## Priority
[Which criterion to focus on improving]
```

### F. Library Extension Check

Before each iteration, check if the `pattern.json` requires primitives not yet in the sacred-patterns TypeScript library:

1. Review the layer types used in `pattern.json`
2. Check if corresponding TypeScript classes exist in `src/ts/`
3. If a gap is found:
   - Follow `library-extension-guide.md` to create the new file
   - Run `make compile` to verify
   - Document in `iterations/{nn}/library-changes.md`
   - Add to `learnings/library-extensions-log.md`

**Auto-create policy:** When a library gap is identified, auto-create the new file and exports, run `make compile`, then note what was added in the iteration summary. No pause needed for library creation.

**Note:** The D3.js HTML output is generated directly from `pattern.json` (not from the TS library). Library extensions are for the reusable TypeScript library — they make the primitives available for the webpack-bundled site, future sessions, and the `generate-drawing` skill.

## Iteration Summary Template

At the end of each iteration, present to the user:

```
## Iteration {nn} Summary

**Confidence:** X.XX ({previous} → {current})
**Status:** [Iterating / Asking user / Complete]

### What changed
- [Change 1]
- [Change 2]

### What's still off
- [Issue 1]
- [Issue 2]

### Retrospective insight
- [What was misunderstood and corrected]

### Next steps
- [What will change in next iteration]
```
