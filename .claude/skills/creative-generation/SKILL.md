---
name: creative-generation
description: Auto-generate timelapse GIF, MP4, and social media copy from a completed learning session.
user_invocable: true
argument: session_name (optional — auto-discovers completed sessions if omitted)
---

# creative-generation

Generate timelapse animations and social media copy from a completed learning session's iteration screenshots.

## Invocation

```
/creative-generation session-abc
```

If no session name is given, scan `$SESSIONS_DIR/session-*/session.json` for sessions with status `completed` that lack `final/timelapse.gif`.

## Workflow

### Step 1: Discover

1. Read `session.json` from the session folder
2. Locate all `iterations/*/screenshot.png` files, sorted by iteration number (zero-padded folders sort correctly via glob)
3. Verify at least 1 screenshot exists
4. Ensure `final/` directory exists

### Step 2: Assemble GIF

```bash
magick convert -delay 100 -loop 0 -resize 800x800 \
    iterations/*/screenshot.png final/timelapse.gif
```

If `magick` is not available, fall back to generating a browser slideshow HTML or using the `gif_creator` MCP tool from Claude in Chrome.

### Step 3: Assemble MP4

```bash
ffmpeg -framerate 1 -pattern_type glob \
    -i 'iterations/*/screenshot.png' \
    -vf "scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:-1:-1:color=black" \
    -c:v libx264 -pix_fmt yuv420p -y final/timelapse.mp4
```

If `ffmpeg` is not available, skip MP4 generation and note it in the output.

### Step 4: Generate Social Copy

Write `final/social-posts.md` using metadata from `session.json` and `analysis.md`. See `social-copy-guide.md` for templates.

Three platforms:
- **Instagram:** visual description + iteration count + confidence + hashtags
- **Twitter/X:** 3-4 tweet thread (hook -> process -> result -> link)
- **TikTok:** short caption with trending hashtags

### Step 5: Update Dashboard

The dashboard template includes timelapse and social copy sections. When generating the dashboard, include:
- `timelapse_gif_path` in the sessionData JSON blob (relative path to `timelapse.gif`)
- `timelapse_mp4_path` in the sessionData JSON blob (relative path to `timelapse.mp4`)
- `social_posts` object: `{ instagram: "...", twitter: ["...", "..."], tiktok: "..." }`

These fields drive the timelapse player, download links, and social copy tabs in the dashboard.

## Outputs

| File | How Made | Purpose |
|------|----------|---------|
| `final/timelapse.gif` | `magick convert` | Web/gallery, social media |
| `final/timelapse.mp4` | `ffmpeg` | TikTok/Reels/Stories (1080x1080) |
| `final/social-posts.md` | Claude generates | Instagram, Twitter/X, TikTok captions |

## Guide Files

| File | Purpose |
|------|---------|
| `timelapse-guide.md` | ImageMagick and ffmpeg command details, fallbacks |
| `social-copy-guide.md` | Platform templates with variable placeholders |
