# Dashboard Guide

How to generate per-session dashboards and the gh-pages gallery index.

## Per-Session Dashboard (`dashboard.html`)

A self-contained HTML page that visualizes the complete session journey. All images are embedded as base64 data URIs so the file works standalone.

### When to Generate

During finalization (Step 5), after the final iteration is selected.

### Content Sections

1. **Header** — session name, status badge, pattern type, symmetry group
2. **Side-by-Side Comparison** — reference image (left) vs final output (right)
3. **Analysis Summary** — key findings from `analysis.md`, color palette swatches
4. **Iteration Timeline** — thumbnails of each iteration with:
   - Confidence score badge
   - Key changes bullet points
   - Retrospective insight (what was corrected)
5. **Library Extensions** — any TypeScript classes added during this session
6. **Learnings** — session-specific insights from `learnings.md`

### Building the Dashboard

1. Read `session.json` for metadata
2. Read `analysis.md` for pattern details
3. Read each `iterations/{nn}/evaluation.md` for scores and notes
4. Read each `iterations/{nn}/retrospective.md` for insights
5. Encode reference image and all screenshots as base64
6. Use the dashboard template (`templates/dashboard-template.html`)
7. Fill in the template with session data
8. Save as `dashboard.html` in the session root

### Image Embedding

Convert images to base64 for self-contained HTML:

```bash
base64 -i input/reference.jpg | tr -d '\n'
```

Then embed as:
```html
<img src="data:image/jpeg;base64,{base64_data}" alt="Reference">
```

For PNG files, use `data:image/png;base64,...`.

### Dashboard Template

Use `templates/dashboard-template.html` as the base. The template uses marked.js for rendering markdown sections and inline CSS for styling (no external stylesheets).

---

## Gallery Index Page

A responsive card grid at `site/gallery/index.html` showing all completed sessions.

### Structure

```
site/gallery/
  index.html                    # Card grid page
  session-abc/
    index.html                  # Copy of session dashboard.html
  session-8-fold/
    index.html                  # Copy of session dashboard.html
```

### Card Content

Each session card shows:
- Thumbnail (final output, embedded as base64)
- Pattern name
- Symmetry group badge (e.g., "D8")
- Confidence score (as a percentage)
- Link to the full session dashboard

### Building the Gallery

1. Scan all `session-*` directories in `/Users/omareid/Dropbox/Data/sacred-patterns/`
2. Read each `session.json` to get metadata
3. Use the final output screenshot as the card thumbnail
4. Generate `site/gallery/index.html` from `templates/gallery-template.html`
5. Copy each session's `dashboard.html` to `site/gallery/session-{name}/index.html`

### Integration with `make deploy`

The gallery build is triggered by `make deploy`:
1. Normal site build (`npm run build`)
2. Gallery build (scan sessions, generate gallery index, copy dashboards)
3. Push to gh-pages branch

The gallery is additive — it sits alongside the existing sacred patterns viewer at `site/index.html`.
