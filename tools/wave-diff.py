#!/usr/bin/env python3
"""wave-diff.py — diff ONE wave's region: the per-wave gate visual + number.

Plain English: the agreed wave plan drives iteration wave-by-wave, and the
rule is "never steer by the whole-image diff" — each structure iteration is
judged ONLY on the wave it targets. This tool masks the comparison to one
wave's shapes: it registers our render onto the reference photo (same
auto-detection as the planner, run on both images), cuts out the wave's
region from each, and reports how much of the wave's tile area our render
actually inks.

Usage (qiyas venv python):
    /Users/omareid/Workspace/git/qiyas/.venv/bin/python tools/wave-diff.py \
        <session-dir> <wave-number> --render iterations/40/render.png

Outputs (under <render-dir>/wave-diff/wave-<k>/):
    ref-wave.png      reference cropped to the wave's region, wave shapes
                      bright, everything else dimmed
    render-wave.png   our render, registered to the reference frame, same
                      crop, the wave's reference outlines drawn on top in
                      gold so the eye sees exactly where shapes SHOULD be
    sbs.png           the two side by side (the gate visual — look at this)
    wave-diff.json    {wave, coverage, iou, shape_count, ...}

The number: `coverage` = fraction of the wave's reference tile pixels where
the registered render also has ink (non-background). `iou` adds a penalty
for ink we put NEXT to the wave's shapes (inside the wave's dilated
envelope but outside its shapes). Both are 0..1; the gate is the EYEBALL on
sbs.png (Tenet 24/25) — the numbers exist to track trend and catch
regressions, not to substitute for the look.

Example: medallion-10 wave 1 (the single navy center star, shape id 200)
against iter-39's render -> wave-diff/wave-01/sbs.png shows the reference
star beside whatever our render put at the center, gold outline marking the
target; coverage 1.0 would mean every reference-star pixel is inked in our
render.

Registration: both images get the planner's medallion detection (mass
center + larger bbox extent); the render is scaled so its medallion
diameter matches the reference's and translated so the centers coincide.
No rotation — both are upright by construction (Tenet 8: deterministic
renders).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


def load_tool(tools_dir: Path, name: str):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), tools_dir / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def detect_medallion(a: np.ndarray, ar) -> tuple[np.ndarray, float, float, float]:
    """Medallion mask + (cx, cy, diameter) — the planner's detection, reused.

    Input: HxWx3 uint8 RGB. Output: (mask, cx, cy, diameter) where diameter
    is the LARGER bbox extent (the photo frame may clip one axis).
    """
    near_white = (a >= 200).all(axis=2)
    mask = ar.medallion_mask(near_white)
    ys, xs = np.nonzero(mask)
    diameter = float(max(xs.max() - xs.min() + 1, ys.max() - ys.min() + 1))
    return mask, float(xs.mean()), float(ys.mean()), diameter


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("session_dir", type=Path)
    ap.add_argument("wave", type=int, help="1-based wave number from the agreed plan")
    ap.add_argument("--render", type=Path, required=True,
                    help="our render (PNG/JPG, white background), relative to session dir or absolute")
    ap.add_argument("--pad", type=int, default=24, help="crop padding around the wave bbox, px")
    args = ap.parse_args()

    tools_dir = Path(__file__).resolve().parent
    ar = load_tool(tools_dir, "analyze-reference")
    pw = load_tool(tools_dir, "plan-waves")

    plan_path = (args.session_dir / "input" / "reference-analysis" / "wave-plan"
                 / "wave-plan.json")
    plan = json.loads(plan_path.read_text())
    waves = {w["wave"]: w for w in plan["waves"]}
    if args.wave not in waves:
        raise SystemExit(f"wave {args.wave} not in plan ({plan['n_waves']} waves)")
    wave = waves[args.wave]
    wave_ids = {s["id"] for s in wave["shapes"]}

    # --- reference side: re-run the planner's exact segmentation so label
    # ids line up with the plan's shape ids (same constants, same algorithm).
    ref_img = Image.open(args.session_dir / "input" / "reference.jpg").convert("RGB")
    ref = np.asarray(ref_img)
    near_white = (ref >= pw.NEAR_WHITE_MIN).all(axis=2)
    medallion = ar.medallion_mask(near_white)
    tiles = medallion & ~near_white
    four = ndimage.generate_binary_structure(2, 1)
    cores = ndimage.binary_erosion(tiles, structure=four, iterations=pw.ERODE_ITERS)
    seed_labels, n = ndimage.label(cores, structure=four)
    _, (iy, ix) = ndimage.distance_transform_edt(seed_labels == 0, return_indices=True)
    labels = np.where(tiles, seed_labels[iy, ix], 0)
    wave_mask = np.isin(labels, list(wave_ids))
    if not wave_mask.any():
        raise SystemExit(
            f"wave {args.wave}: no pixels matched its shape ids — the photo "
            "or segmentation constants changed since the plan was built; "
            "re-run plan-waves.py first"
        )
    ys_r, xs_r = np.nonzero(medallion)
    ref_c = (float(xs_r.mean()), float(ys_r.mean()))
    ref_d = float(max(xs_r.max() - xs_r.min() + 1, ys_r.max() - ys_r.min() + 1))

    # --- render side: same detection, then scale + translate onto the
    # reference frame (no rotation — both upright by construction).
    render_path = args.render if args.render.is_absolute() else args.session_dir / args.render
    rnd_img = Image.open(render_path).convert("RGB")
    rnd = np.asarray(rnd_img)
    _, rcx, rcy, rnd_d = detect_medallion(rnd, ar)
    scale = ref_d / rnd_d
    new_size = (round(rnd_img.width * scale), round(rnd_img.height * scale))
    scaled = rnd_img.resize(new_size, Image.LANCZOS)
    registered = Image.new("RGB", (ref.shape[1], ref.shape[0]), (255, 255, 255))
    registered.paste(scaled, (round(ref_c[0] - rcx * scale), round(ref_c[1] - rcy * scale)))
    reg = np.asarray(registered)

    # --- the numbers. Ink = non-near-white in the registered render.
    ink = ~(reg >= pw.NEAR_WHITE_MIN).all(axis=2)
    coverage = float((ink & wave_mask).sum() / wave_mask.sum())
    # IoU over the wave's dilated envelope: ink poured NEXT to the shapes
    # (filling the lattice, spilling into neighbours) costs, ink elsewhere in
    # the image is some other wave's business.
    envelope = ndimage.binary_dilation(wave_mask, structure=four, iterations=8)
    inter = float((ink & wave_mask).sum())
    union = float((wave_mask | (ink & envelope)).sum())
    iou = inter / union if union else 0.0

    # --- the gate visual: crop both to the wave bbox, dim the reference's
    # non-wave content, outline the wave's target shapes in gold on BOTH.
    ys_w, xs_w = np.nonzero(wave_mask)
    x0 = max(0, xs_w.min() - args.pad); x1 = min(ref.shape[1], xs_w.max() + args.pad)
    y0 = max(0, ys_w.min() - args.pad); y1 = min(ref.shape[0], ys_w.max() + args.pad)

    gray = (0.3 * ref + 0.7 * 255 * np.ones_like(ref)).astype(np.uint8)
    ref_vis = np.where(wave_mask[..., None], ref, gray)
    outline = ndimage.binary_dilation(wave_mask, structure=four, iterations=2) & ~wave_mask

    out_dir = render_path.parent / "wave-diff" / f"wave-{args.wave:02d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    panels = []
    for vis, name in ((ref_vis, "ref-wave.png"), (reg.copy(), "render-wave.png")):
        vis = vis.copy()
        vis[outline] = (193, 128, 10)
        im = Image.fromarray(vis[y0:y1, x0:x1])
        im.save(out_dir / name)
        panels.append(im)

    gap = 12
    sbs = Image.new("RGB", (panels[0].width + panels[1].width + gap,
                            max(panels[0].height, panels[1].height)), (255, 255, 255))
    sbs.paste(panels[0], (0, 0))
    sbs.paste(panels[1], (panels[0].width + gap, 0))
    sbs.save(out_dir / "sbs.png")

    result = {
        "wave": args.wave,
        "where": wave["where"],
        "color": wave["color"],
        "shape_count": wave["shape_count"],
        "coverage": round(coverage, 4),
        "iou": round(iou, 4),
        "render": str(render_path),
        "registration": {
            "ref_center": [round(ref_c[0], 1), round(ref_c[1], 1)],
            "ref_diameter": ref_d,
            "render_center": [round(rcx, 1), round(rcy, 1)],
            "render_diameter": rnd_d,
            "scale": round(scale, 5),
        },
        "crop": [int(x0), int(y0), int(x1), int(y1)],
    }
    (out_dir / "wave-diff.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"wave {args.wave} ({wave['shape_count']} shapes, {wave['where']}): "
          f"coverage {coverage:.1%}, iou {iou:.1%}")
    print(f"gate visual: {out_dir / 'sbs.png'}")


if __name__ == "__main__":
    main()
