---
name: analyze-geometric-patterns
description: Analyze a reference image of an Islamic geometric pattern, producing a detailed structural analysis without the full iteration pipeline.
user_invocable: true
argument: image_path - Path to a reference image (jpg/png) of a geometric pattern
---

# analyze-geometric-patterns

Standalone pattern analysis skill. Examines a reference image and produces a comprehensive analysis of its geometric structure, color palette, and construction — without running the full iteration/replication pipeline.

Use this when you want to understand a pattern quickly, or when the retrospective loop in `learn-new-pattern` needs to re-examine a reference.

## Invocation

```
/analyze-geometric-patterns /path/to/image.jpg
```

## Workflow

### Step 1: Load Reference

1. Read the image at the provided path
2. If there's an existing session, note it but analyze independently
3. Load `learnings/common-mistakes.md` for known pitfalls

### Step 2: Analyze

Follow the analysis guide at `.claude/skills/learn-new-pattern/analysis-guide.md`.

Cover all sections:
1. Symmetry type (dihedral group, rotational order, mirror axes)
2. Base polygon & star pattern ({n/k} notation)
3. Tiling method
4. Construction geometry (normalized radii)
5. Tile shapes & angles
6. Interlace & strapwork
7. Arabesque elements
8. Calligraphic zones
9. Muqarnas projections
10. Color & material
11. Programmatic construction steps

### Step 3: Identify Palette

Consult `.claude/skills/learn-new-pattern/color-palettes.md` to match the reference to a known tradition. Extract hex values.

### Step 4: Present

Present the analysis to the user with:
- Summary of key findings
- Color palette swatches (describe hex values)
- Construction overview
- Confidence in the analysis
- Any ambiguous elements that need user input

### Step 5: Save (Optional)

If the user wants to save the analysis:
- Write to a specified location
- Or create a minimal session folder at `/Users/omareid/Dropbox/Data/sacred-patterns/session-{name}/` with just `input/` and `analysis.md`

## Shared Resources

This skill reuses guides from `learn-new-pattern`:
- `.claude/skills/learn-new-pattern/analysis-guide.md`
- `.claude/skills/learn-new-pattern/color-palettes.md`
- `/Users/omareid/Dropbox/Data/sacred-patterns/learnings/common-mistakes.md`

## Differences from learn-new-pattern

| Aspect | analyze-geometric-patterns | learn-new-pattern |
|--------|---------------------------|-------------------|
| Scope | Analysis only | Full pipeline |
| Output | Markdown analysis | HTML + GeoGebra + dashboard |
| Iteration | None | Up to 5 iterations |
| Library changes | None | May extend src/ts/ |
| Duration | Quick (1-2 minutes) | Extended (10+ minutes) |
