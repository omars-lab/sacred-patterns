#!/usr/bin/env python3
"""Build per-wave ADDITIVE reference-photo ghosts: the real photo with everything
faded to faint grey EXCEPT the shapes belonging to waves 1..N, which stay full color.

Plain English (owner, 2026-06-15): the big picture at the top of each wave card pairs
"our build" (left, which grows wave by wave) with "your photo" (right). The photo side
was the WHOLE photo at once — so it wasn't additive: wave 1 already showed the whole
burst. This makes the photo side additive too: on wave N, only the shapes from waves
1..N are in real color; everything the build hasn't reached yet is dimmed to a grey
ghost. Left and right now reveal together, one wave at a time — "an additive view just
like /waves".

How: wave-plan.json shapes[] carry pixel x/y (reference-photo coords) and area_px,
grouped by wave. For wave N we build a CUMULATIVE mask = the union of soft disks over
every shape in waves 1..N (disk radius from sqrt(area)/2, inflated so adjacent same-band
shapes merge into a connected region rather than 426 isolated dots). Inside the mask we
keep the photo's true colour; outside we desaturate + lighten toward #DBDBDB (the same
ghost grey the render-side ghosts use) so the two ghost families read alike. Then crop
to the pattern's bounding circle so the framing lines up with wave-N-build.png.

Output: wave-N-photo.png next to the other ghosts (512px, white background). The mask is
monotonic by construction (wave N's mask ⊇ wave N-1's) — asserted post-build (Tenet 18).
Re-run after the wave plan changes (alongside build_wave_ghosts.py / build_wave_crops.py).
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

B = Path("/Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns/bikar-medallion-10")
ITER = sys.argv[1] if len(sys.argv) > 1 else "71"
OUT = B / "iterations" / ITER / "wave-ghosts"

# Pattern framing in reference-photo pixels (matches the portal --center/--diameter).
CX, CY, DIAM = 386.0, 361.0, 738.0
R = DIAM / 2.0

GHOST_RGB = (0xDB, 0xDB, 0xDB)   # same faint grey as the render-side ghosts
GHOST_MIX = 0.82                 # how far un-revealed pixels move toward grey (0..1)
GHOST_DESAT = 0.85               # how much colour to drain from un-revealed pixels
DISK_INFLATE = 1.9               # blow up each shape disk so same-wave neighbours merge
DISK_MIN = 9.0                   # never smaller than this (tiny inner/outer shapes)
MASK_BLUR = 4.0                  # soft mask edge so the reveal isn't hard-cut
OUT_PX = 512


def shape_radius(s: dict) -> float:
    # Same half-extent estimate the crop script uses (sqrt(A)/2 — steadier than the
    # disk r=sqrt(A/pi) for spiky star/petal shapes), then inflated so a wave's
    # shapes fuse into a band instead of reading as scattered dots.
    return max(math.sqrt(max(s.get("area_px", 0), 1)) / 2.0 * DISK_INFLATE, DISK_MIN)


def main() -> None:
    wp = json.loads((B / "input" / "reference-analysis" / "wave-plan" / "wave-plan.json").read_text())
    ref = Image.open(B / "input" / "reference.jpg").convert("RGB")
    W, H = ref.size

    # A fully-grey, fully-desaturated version of the whole photo, computed once;
    # each wave image is photo-where-revealed, ghost-where-not, blended by the mask.
    grey_full = Image.new("RGB", (W, H), GHOST_RGB)
    desat = ref.convert("L").convert("RGB")
    # un-revealed look = desaturate the photo, then pull it toward flat grey
    ghosted = Image.blend(ref, desat, GHOST_DESAT)
    ghosted = Image.blend(ghosted, grey_full, GHOST_MIX)

    waves = sorted(wp["waves"], key=lambda w: w["wave"])
    cum_mask = Image.new("L", (W, H), 0)   # cumulative reveal, grows each wave
    prev_white = 0

    for w in waves:
        n = w["wave"]
        # Add THIS wave's shape disks to the running cumulative mask.
        draw = ImageDraw.Draw(cum_mask)
        for s in w.get("shapes", []):
            x, y, r = s["x"], s["y"], shape_radius(s)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=255)

        # Soft edge so the colour reveal feathers into the ghost.
        soft = cum_mask.filter(ImageFilter.GaussianBlur(MASK_BLUR))
        frame = Image.composite(ref, ghosted, soft)

        # Crop to the pattern bounding box (square) so framing matches wave-N-build.
        bx0, by0 = CX - R, CY - R
        bx1, by1 = CX + R, CY + R
        # Clamp into the photo, shifting (not shrinking) to stay square.
        if bx0 < 0:
            bx1 -= bx0; bx0 = 0
        if by0 < 0:
            by1 -= by0; by0 = 0
        if bx1 > W:
            bx0 -= bx1 - W; bx1 = W
        if by1 > H:
            by0 -= by1 - H; by1 = H
        bx0, by0 = max(0, bx0), max(0, by0)
        bx1, by1 = min(W, bx1), min(H, by1)
        crop = frame.crop((round(bx0), round(by0), round(bx1), round(by1)))
        out = crop.resize((OUT_PX, OUT_PX))
        out.save(OUT / f"wave-{n}-photo.png")

        white = sum(1 for p in cum_mask.getdata() if p > 0)
        # Tenet 18: the cumulative mask must never shrink (additive reveal).
        assert white >= prev_white, f"wave {n} mask shrank ({white} < {prev_white})"
        prev_white = white
        frac = 100.0 * white / (W * H)
        print(f"wave-{n}-photo: {len(w.get('shapes', []))} shapes this wave, "
              f"cumulative reveal {frac:.1f}% of frame")
    print("DONE")


if __name__ == "__main__":
    main()
