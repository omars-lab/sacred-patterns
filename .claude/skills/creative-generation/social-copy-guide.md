# Social Media Copy Guide

## Available Variables

From `session.json`:
- `{name}` — session name (e.g., `8-fold-rosette`)
- `{pattern_type}` — rosette, medallion, tessellation, etc.
- `{symmetry_group}` — D8, D12, etc.
- `{symmetry_order}` — numeric (8, 12, etc.)
- `{confidence_score}` — 0.0–1.0 (display as percentage)
- `{iteration_count}` — `current_iteration` value
- `{tags}` — array of tags
- `{palette_name}` — `color_palette.name`

From `analysis.md`:
- `{key_features}` — notable geometric features described in analysis
- `{construction_summary}` — brief construction method

From iteration retrospectives:
- `{key_retrospective_insight}` — most interesting correction from any `retrospective.md`

## Platform Templates

### Instagram

```
{pattern_name} — {symmetry_group} symmetry

{iteration_count} iterations from blank canvas to {confidence}% match.
Built with Sacred Patterns.

#islamicgeometry #geometricart #sacredgeometry #generativeart #codeart #vibecodeart #patterndesign #mathematicalart #islamicart #d3js
```

**Guidelines:**
- Lead with the pattern name and symmetry — visually-oriented audience
- Include iteration count and confidence — shows the AI learning process
- 2200 character max, but shorter performs better
- 10-15 hashtags in the post body (not comments)
- Pair with the timelapse GIF or MP4 as the media

### Twitter/X Thread

```
1/ Building a {pattern_type} with {symmetry_group} symmetry from scratch.
Watch {iteration_count} iterations of AI learning to draw Islamic geometric art.

2/ Each iteration corrects what the previous got wrong — a visual feedback loop.
{key_retrospective_insight}

3/ Final: {confidence}% match.
art.bytesofpurpose.com/gallery/session-{name}/

#islamicgeometry #generativeart #sacredgeometry
```

**Guidelines:**
- Tweet 1: hook with the visual process (attach GIF or MP4)
- Tweet 2: insight into the learning process — what went wrong and was corrected
- Tweet 3: result + link to the full dashboard
- 280 characters per tweet; threads of 3-4 tweets
- 1-2 hashtags on the final tweet only
- Attach the timelapse GIF to tweet 1

### TikTok

```
Watch AI learn Islamic geometry in {iteration_count} steps

#islamicart #geometricart #sacredgeometry #aigenerated #vibecodeart #timelapse #satisfying #artprocess
```

**Guidelines:**
- Very short caption — TikTok is video-first
- Trending hashtags matter more than description
- Upload the MP4 directly (1080x1080 square format)
- Use the timelapse MP4 as the video content

## Output Format

Write `final/social-posts.md` with this structure:

```markdown
# Social Media Posts — {session_name}

## Instagram

[full Instagram post text]

## Twitter/X

### Tweet 1
[tweet text]

### Tweet 2
[tweet text]

### Tweet 3
[tweet text]

## TikTok

[caption text]
```

Also populate the `social_posts` field in `sessionData` for the dashboard:
```json
{
  "instagram": "full Instagram post text",
  "twitter": ["tweet 1 text", "tweet 2 text", "tweet 3 text"],
  "tiktok": "caption text"
}
```

## Tone

- Educational but not academic
- Emphasize the process (iteration, correction, learning)
- Celebrate the intersection of math, art, and code
- Avoid hyperbole — let the visuals speak
