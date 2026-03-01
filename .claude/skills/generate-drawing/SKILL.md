---
name: generate-drawing
description: Create original Islamic geometric patterns using learned primitives and the declarative pattern language.
user_invocable: true
argument: prompt - Creative brief describing the desired pattern (e.g., "a 12-fold pattern with gold on navy")
---

# generate-drawing

Creative skill that composes original Islamic geometric patterns from learned primitives. Works in tandem with `learn-new-pattern` — as that skill adds new capabilities to the declarative language, this skill uses them creatively.

## Invocation

```
/generate-drawing a 12-fold pattern with gold on navy
/generate-drawing combine rosettes with an octagonal grid in Persian turquoise
```

## Workflow

### Step 1: Gather Context

1. Read the declarative language guide: `.claude/skills/learn-new-pattern/declarative-language-guide.md`
2. Read available palettes: `.claude/skills/learn-new-pattern/color-palettes.md`
3. Read learned palettes: `/Users/omareid/Dropbox/Data/sacred-patterns/learnings/color-palettes-learned.md`
4. Read construction techniques: `/Users/omareid/Dropbox/Data/sacred-patterns/learnings/construction-techniques.md`
5. Read patterns catalog for inspiration: `/Users/omareid/Dropbox/Data/sacred-patterns/learnings/patterns-catalog.md`

### Step 2: Design

1. Interpret the user's creative brief
2. Choose a symmetry group and base structure
3. Select a color palette (from known palettes or user-specified)
4. Plan the layer composition using available primitives
5. Prioritize recently-added primitives to exercise new capabilities

### Step 3: Generate

1. Create a `pattern.json` using the declarative language
2. Compile to a self-contained D3.js v7 HTML following `.claude/skills/learn-new-pattern/compile-d3.md`
3. Save to the drawings directory

### Step 4: Render & Present

1. Open HTML in browser
2. Take a screenshot
3. Present to the user
4. Describe the composition choices

### Step 5: Iterate

Based on user feedback:
- Adjust colors, proportions, elements
- Add or remove layers
- Try different symmetry groups
- Re-render and present

### Step 6: Save

Save the final drawing to:

```
/Users/omareid/Dropbox/Data/sacred-patterns/drawings/{drawing-name}/
  prompt.md                     # User's creative brief
  pattern.json                  # Declarative definition
  output.html                   # Self-contained D3.js rendering
  thumbnail.png                 # Screenshot
```

## Output Directory

All drawings are saved to `/Users/omareid/Dropbox/Data/sacred-patterns/drawings/`.

Drawings also appear in the gh-pages gallery alongside learning sessions.

## Design Philosophy

- **Use what's available** — compose from the current set of declarative language primitives
- **Exercise new primitives** — when `learn-new-pattern` adds new capabilities (rosettes, interlace, etc.), use them in drawings to validate they work well in creative compositions
- **Feedback loop** — if a primitive is awkward to compose or produces unexpected results, note it. This feedback improves the declarative language design
- **Respect tradition** — even in creative compositions, follow the principles of Islamic geometric art (symmetry, proportion, harmony)
- **Color with intention** — use established palettes or thoughtful variations, not random colors

## Differences from learn-new-pattern

| Aspect | generate-drawing | learn-new-pattern |
|--------|-----------------|-------------------|
| Input | Creative prompt | Reference image |
| Goal | Original composition | Faithful replication |
| Analysis | None (starts from intent) | Deep image analysis |
| Iteration | User-driven feedback | Automated evaluation |
| Output dir | `drawings/` | `session-{name}/` |
| Library changes | None | May extend src/ts/ |
