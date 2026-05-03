#!/usr/bin/env python3
"""qiyas-diff.py — Thin Docker wrapper around `qiyas validate`.

Replaces the bash version (`qiyas-diff.sh`). Python is friendlier on macOS
(no bash-3 footguns like `${var,,}`) and gives clearer error messages.

Encodes a reference image and our reconstruction, diffs them via Hungarian
shape matching, and emits an interactive HTML report. This is one of the
signals in the iteration loop's validation orchestrator (alongside qiyas
pixel-diff, qiyas svg-audit, and qiyas score).

Usage:
    ./tools/qiyas-diff.py <recon.svg|png|jpg> <reference.svg|png|jpg> [output-dir]

Outputs (under output-dir, default: <recon-dir>/qiyas/):
    ref.encoding.json    qiyas Stage 5 encoding for reference
    recon.encoding.json  qiyas Stage 5 encoding for our SVG
    diff.json            Hungarian shape pairing + per-shape error
    report.html          Tier 3 interactive workbench
    ref.png, recon.png   rasterized inputs (so qiyas sees consistent format)

Why we rasterize: qiyas's SVG fast-path rejects clipPath elements, and our
patterns rely on clipPath heavily. Rasterizing to PNG forces qiyas's raster
pipeline (Hough + findContours), which works on our outputs.

Prerequisites: docker, rsvg-convert (or ImageMagick `magick`)
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

QIYAS_IMAGE_DEFAULT = "ghcr.io/naqshcoffee/qiyas:v0.1.1"
RENDER_SIZE_DEFAULT = 1200
TIER_DEFAULT = 3

# ANSI colors (no-op when stdout isn't a TTY)
def _color(code: str) -> str:
    return code if sys.stdout.isatty() else ""

RED = _color("\033[0;31m")
GREEN = _color("\033[0;32m")
CYAN = _color("\033[0;36m")
NC = _color("\033[0m")


def die(msg: str, exit_code: int = 1) -> None:
    print(f"{RED}{msg}{NC}", file=sys.stderr)
    sys.exit(exit_code)


def rasterize(src: Path, dst: Path, render_size: int) -> None:
    """SVG -> PNG via rsvg-convert (preferred) or ImageMagick `magick`.
    Non-SVG (PNG/JPG) -> resized PNG via `magick`."""
    suffix = src.suffix.lower()
    if suffix == ".svg":
        if shutil.which("rsvg-convert"):
            cmd = [
                "rsvg-convert",
                "-w", str(render_size), "-h", str(render_size),
                "--background-color=white",
                str(src), "-o", str(dst),
            ]
        elif shutil.which("magick"):
            cmd = [
                "magick",
                "-background", "white",
                "-density", "150",
                str(src),
                "-resize", f"{render_size}x{render_size}",
                str(dst),
            ]
        else:
            die("Need rsvg-convert or ImageMagick `magick` for SVG rasterization")
    else:
        if not shutil.which("magick"):
            die("Need ImageMagick `magick` to rasterize non-SVG inputs")
        cmd = [
            "magick", str(src),
            "-resize", f"{render_size}x{render_size}",
            "-background", "white",
            "-alpha", "remove", "-alpha", "off",
            str(dst),
        ]
    subprocess.run(cmd, check=True)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Thin Docker wrapper around `qiyas validate`.",
    )
    p.add_argument("recon", help="Reconstruction (SVG/PNG/JPG)")
    p.add_argument("reference", help="Reference image (SVG/PNG/JPG)")
    p.add_argument("output_dir", nargs="?", default=None,
                   help="Output directory (default: <recon-dir>/qiyas/)")
    p.add_argument("--qiyas-image", default=os.environ.get("QIYAS_IMAGE", QIYAS_IMAGE_DEFAULT),
                   help=f"Docker image (default: {QIYAS_IMAGE_DEFAULT})")
    p.add_argument("--render-size", type=int,
                   default=int(os.environ.get("QIYAS_RENDER_SIZE", RENDER_SIZE_DEFAULT)),
                   help=f"Rasterize-to size in px (default: {RENDER_SIZE_DEFAULT})")
    p.add_argument("--tier", type=int,
                   default=int(os.environ.get("QIYAS_TIER", TIER_DEFAULT)),
                   help=f"qiyas validate tier (default: {TIER_DEFAULT})")
    args = p.parse_args()

    recon = Path(args.recon).resolve()
    reference = Path(args.reference).resolve()

    if not recon.is_file():
        die(f"Recon input not found: {recon}")
    if not reference.is_file():
        die(f"Reference input not found: {reference}")

    out_dir = Path(args.output_dir).resolve() if args.output_dir else recon.parent / "qiyas"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"{CYAN}qiyas validate{NC}")
    print(f"  Recon:     {recon}")
    print(f"  Reference: {reference}")
    print(f"  Output:    {out_dir}")
    print(f"  Image:     {args.qiyas_image}")
    print()

    # ============================================================
    # Rasterize inputs
    # ============================================================
    recon_png = out_dir / "recon.png"
    ref_png = out_dir / "ref.png"

    print(f"Rasterizing inputs to {args.render_size}x{args.render_size} PNG...")
    try:
        rasterize(recon, recon_png, args.render_size)
        rasterize(reference, ref_png, args.render_size)
    except subprocess.CalledProcessError as e:
        die(f"Rasterization failed: {e}")

    # ============================================================
    # Run qiyas validate
    # ============================================================
    print(f"Running qiyas validate (tier {args.tier})...")

    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{out_dir}:/work",
        args.qiyas_image,
        "validate",
        "/work/ref.png",
        "/work/recon.png",
        "--output-dir", "/work",
        "--tier", str(args.tier),
    ]

    log_path = out_dir / "qiyas-stdout.log"
    with log_path.open("w") as logf:
        proc = subprocess.run(
            docker_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        # Tee to both terminal and log
        if proc.stdout:
            print(proc.stdout, end="")
            logf.write(proc.stdout)

    if proc.returncode != 0:
        die(f"qiyas validate failed (exit {proc.returncode}); see {log_path}")

    # ============================================================
    # Verify outputs
    # ============================================================
    required = [
        out_dir / "ref.encoding.json",
        out_dir / "recon.encoding.json",
        out_dir / "diff.json",
        out_dir / "report.html",
    ]
    missing = [str(f) for f in required if not f.exists()]
    if missing:
        for m in missing:
            print(f"{RED}Missing expected output: {m}{NC}", file=sys.stderr)
        return 1

    print()
    print(f"{GREEN}qiyas diff complete{NC}")
    print(f"  Encodings: {out_dir}/{{ref,recon}}.encoding.json")
    print(f"  Diff:      {out_dir}/diff.json")
    print(f"  Report:    {out_dir}/report.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
