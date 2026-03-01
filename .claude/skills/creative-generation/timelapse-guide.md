# Timelapse Generation Guide

## Frame Source

Iteration screenshots at `iterations/*/screenshot.png` are the raw frames. Zero-padded folder names (`01/`, `02/`, ...) ensure glob ordering matches iteration order.

## GIF Assembly (ImageMagick)

```bash
magick convert -delay 100 -loop 0 -resize 800x800 \
    iterations/*/screenshot.png final/timelapse.gif
```

### Flags

| Flag | Value | Meaning |
|------|-------|---------|
| `-delay` | `100` | 100 centiseconds (1 second) between frames |
| `-loop` | `0` | Infinite loop |
| `-resize` | `800x800` | Constrain to 800px, maintaining aspect ratio |

### Quality Optimization

For better GIF quality with smaller file size:

```bash
magick convert -delay 100 -loop 0 -resize 800x800 \
    -dither FloydSteinberg -colors 128 \
    iterations/*/screenshot.png final/timelapse.gif
```

- `-dither FloydSteinberg` — reduces banding in gradients
- `-colors 128` — limits palette for smaller file size (increase to 256 if quality suffers)

### Timing Variations

- Faster playback: `-delay 50` (0.5s per frame)
- Slower final frame (pause on result): use `-delay 100` for all frames, then `-delay 300` on the last frame via a two-step process:
  ```bash
  magick convert -delay 100 -loop 0 -resize 800x800 \
      iterations/*/screenshot.png \
      -delay 300 iterations/$(ls -1d iterations/*/ | tail -1)screenshot.png \
      final/timelapse.gif
  ```

## MP4 Assembly (ffmpeg)

```bash
ffmpeg -framerate 1 -pattern_type glob \
    -i 'iterations/*/screenshot.png' \
    -vf "scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:-1:-1:color=black" \
    -c:v libx264 -pix_fmt yuv420p -y final/timelapse.mp4
```

### Flags

| Flag | Value | Meaning |
|------|-------|---------|
| `-framerate` | `1` | 1 fps (1 second per iteration) |
| `-pattern_type glob` | — | Use shell glob for input |
| `-i` | `'iterations/*/screenshot.png'` | Input frames (glob) |
| `-vf scale=...` | — | Scale to fit 1080x1080 square, pad with black |
| `-c:v libx264` | — | H.264 codec (universal compatibility) |
| `-pix_fmt yuv420p` | — | Pixel format for maximum device compatibility |
| `-y` | — | Overwrite output without asking |

### Social Media Specs

- **TikTok/Reels/Stories:** 1080x1080 (square) or 1080x1920 (portrait)
- **Twitter/X:** 1280x720 minimum, max 512MB
- **Instagram feed:** 1080x1080 (square)

The default 1080x1080 square works across all platforms.

### Bitrate for Quality

For higher quality uploads (at larger file size):

```bash
ffmpeg -framerate 1 -pattern_type glob \
    -i 'iterations/*/screenshot.png' \
    -vf "scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:-1:-1:color=black" \
    -c:v libx264 -b:v 5M -pix_fmt yuv420p -y final/timelapse.mp4
```

## Fallbacks

### If `magick` is not available

1. **Browser slideshow HTML:** Generate a self-contained HTML file that cycles through base64-encoded screenshots using JavaScript `setInterval`:
   ```html
   <img id="frame" src="data:image/png;base64,...">
   <script>
   var frames = [/* base64 strings */];
   var i = 0;
   setInterval(() => { document.getElementById('frame').src = frames[++i % frames.length]; }, 1000);
   </script>
   ```

2. **Claude in Chrome `gif_creator`:** Use `mcp__claude-in-chrome__gif_creator` to record the slideshow playback.

### If `ffmpeg` is not available

Skip MP4 generation. Note in output that MP4 was skipped. The GIF serves as the primary timelapse asset.

## Verification

After generation:
1. Check `final/timelapse.gif` exists and file size > 0
2. Check `final/timelapse.mp4` exists and file size > 0
3. Open GIF in browser to verify frame order and timing
