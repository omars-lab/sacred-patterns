#!/usr/bin/env python3
"""Build per-wave reference CROPS: the original photo zoomed to just this wave's
shapes, with those shapes ringed so it's obvious WHICH shapes this wave rebuilds.

Plain English (owner, 2026-06-15): the default picture on each wave card should be
"a cropped version of your original photo's steps, focused on the shapes being
recreated" — not the whole photo, not a grey ghost, but the real reference photo
zoomed in on exactly the shapes this wave adds.

How: wave-plan.json shapes[] carry pixel x/y (reference-photo coords) and area_px.
For wave N we take the bbox of its shapes (each shape's half-extent ~ sqrt(area)/2),
pad it, crop reference.jpg to that box, and draw a soft ring around each shape so the
eye lands on the rebuilt shapes. Square-ish output so the cards line up.

Output: wave-N-crop.png next to the ghosts. Re-run after the wave plan changes.
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

B = Path("/Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns/bikar-medallion-10")
ITER = sys.argv[1] if len(sys.argv) > 1 else "71"
OUT = B / "iterations" / ITER / "wave-ghosts"

RING = (227, 78, 16, 255)   # warm orange — the "this is the shape" highlight
RING_HALO = (255, 244, 214, 235)  # pale halo drawn under the ring so it pops
                                  # against the busy blue pattern at any zoom
MARGIN_FRAC = 0.35          # pad the bbox by 35% of its larger side
MIN_BOX = 90                # never crop tighter than this (tiny inner waves)
OUT_PX = 512                # square output, upscaled so small crops read big


def shape_radius(s: dict) -> float:
    # Half-extent estimate: a shape of area A read as a disk has r=sqrt(A/pi),
    # but the medallion shapes are stars/petals, so sqrt(A)/2 is a steadier
    # half-width that doesn't under-ring spiky shapes.
    return math.sqrt(max(s.get("area_px", 0), 1)) / 2.0


def main() -> None:
    wp = json.loads((B / "input" / "reference-analysis" / "wave-plan" / "wave-plan.json").read_text())
    ref = Image.open(B / "input" / "reference.jpg").convert("RGB")
    W, H = ref.size

    for w in wp["waves"]:
        n = w["wave"]
        shapes = w.get("shapes", [])
        if not shapes:
            continue
        xs = [s["x"] for s in shapes]
        ys = [s["y"] for s in shapes]
        rads = [shape_radius(s) for s in shapes]
        x0 = min(x - r for x, r in zip(xs, rads))
        x1 = max(x + r for x, r in zip(xs, rads))
        y0 = min(y - r for y, r in zip(ys, rads))
        y1 = max(y + r for y, r in zip(ys, rads))

        # Pad, then square the box around its center so every card is the same
        # aspect (a row of mixed-aspect crops reads as ragged).
        side = max(x1 - x0, y1 - y0, MIN_BOX)
        pad = side * MARGIN_FRAC
        side += 2 * pad
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        bx0, by0 = cx - side / 2, cy - side / 2
        bx1, by1 = cx + side / 2, cy + side / 2
        # Clamp into the photo (shift, don't shrink, so it stays square).
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

        crop = ref.crop((round(bx0), round(by0), round(bx1), round(by1)))
        # Ring each shape in crop-local coords, scaled up to the output size.
        scale = OUT_PX / max(crop.width, crop.height)
        out = crop.resize((round(crop.width * scale), round(crop.height * scale)))
        draw = ImageDraw.Draw(out, "RGBA")
        # Ring width scales with the output so it reads on both a 1-shape tight
        # crop and a 44-shape full-frame crop; a pale halo underneath lifts the
        # orange off the blue pattern.
        rw = max(2, round(OUT_PX / 170))
        for s, r in zip(shapes, rads):
            lx = (s["x"] - bx0) * scale
            ly = (s["y"] - by0) * scale
            lr = max(r * scale, 7)
            draw.ellipse([lx - lr, ly - lr, lx + lr, ly + lr],
                         outline=RING_HALO, width=rw + 3)
            draw.ellipse([lx - lr, ly - lr, lx + lr, ly + lr],
                         outline=RING, width=rw)
        out.save(OUT / f"wave-{n}-crop.png")
        print(f"wave-{n}-crop: {crop.width}x{crop.height} crop, {len(shapes)} shapes ringed")
    print("DONE")


if __name__ == "__main__":
    main()
