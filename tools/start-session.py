#!/usr/bin/env python3
"""start-session.py — one command from a reference photo to the planning studio.

Plain English: when we want to recreate a NEW image, this is the front door.
Point it at the photo; it builds the session folder, detects the medallion
center and size, plans the waves and flowers, extracts the colour swatches,
and starts the review hub on localhost — the owner's next step is just
"open the printed URL and look".

Usage (qiyas venv python — it carries PIL/numpy/scipy):
    /Users/omareid/Workspace/git/qiyas/.venv/bin/python tools/start-session.py \
        /path/to/photo.jpg --name my-pattern

What it does, in order (each step skipped if its artifact already exists,
so re-running on an existing session is safe):
    1. Creates <base>/<name>/input/ and re-encodes the photo to
       input/reference.jpg (RGB JPEG — the format every downstream tool
       expects, whatever the input was).
    2. Writes a fresh session.json with the stage-gate skeleton
       (structure -> color -> weave; schema per iterate-construction-hypothesis
       SKILL.md -> "The stage ladder").
    3. Edge-extracts input/reference-structure.png (ImageMagick, same fixed
       Canny as tools/structure-diff.sh; skipped with a note if magick is
       missing) and runs analyze-reference.py for the colour-gate swatch
       sheet.
    4. Runs plan-waves.py with AUTO-DETECTED center/diameter (mass center +
       bbox extent of the medallion mask, printed for the owner to confirm
       on the studio's marked-up picture).
    5. Starts wave-plan-server.py and prints the hub URL (`/` lists what
       needs the owner's eyes; `/plan` is the studio; `/palette` the colour
       gate).

Defaults: --base ~/Dropbox/Data/sacred-patterns, --name = photo filename
stem, --port 8765. Protocol home:
.claude/skills/iterate-construction-hypothesis/SKILL.md -> "Stage 1 is
wave-based"; algorithm + witnessed dead ends: docs/wave-planning-design.md.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

from PIL import Image

# Fixed Canny thresholds — must mirror tools/structure-diff.sh (tuned once
# at first execution, then frozen so edge maps stay comparable).
CANNY = "0x1+10%+30%"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path, help="the reference photo to recreate")
    ap.add_argument(
        "--name",
        default=None,
        help="session slug (default: the photo's filename stem)",
    )
    ap.add_argument(
        "--base",
        type=Path,
        default=Path.home() / "Dropbox/Data/sacred-patterns",
        help="where session folders live",
    )
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()

    if not args.image.exists():
        sys.exit(f"no such image: {args.image}")

    name = args.name or args.image.stem.lower().replace(" ", "-").replace("_", "-")
    session_dir = args.base / name
    input_dir = session_dir / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    tools_dir = Path(__file__).resolve().parent
    py = sys.executable

    ref = input_dir / "reference.jpg"
    if ref.exists():
        print(f"reference already in place: {ref} (not overwritten)")
    elif args.image.suffix.lower() in (".jpg", ".jpeg"):
        # Copy JPEGs verbatim — a PIL re-encode adds generation loss, and the
        # jitter is enough to split a wave (witnessed: medallion-10's 39-shape
        # wave split 34+5 after a quality-95 round-trip).
        shutil.copyfile(args.image, ref)
        print(f"reference photo -> {ref}")
    else:
        Image.open(args.image).convert("RGB").save(ref, quality=95)
        print(f"reference photo (re-encoded to RGB JPEG) -> {ref}")

    session_json = session_dir / "session.json"
    if not session_json.exists():
        session_json.write_text(
            json.dumps(
                {
                    "name": name,
                    "status": "planning",
                    "created": date.today().isoformat(),
                    "stage_gates": {
                        "_doc": "Stage-gated loop (structure->color->weave). "
                        "Gate verdicts are recorded by the review surfaces "
                        "(studio agree button, palette agree button). Schema: "
                        "sacred-patterns iterate-construction-hypothesis "
                        "SKILL.md -> 'The stage ladder'.",
                        "structure": {
                            "approved_at_iter": None,
                            "skeleton_sha256": None,
                            "approved_date": None,
                            "wave_plan": {"agreed": False},
                        },
                        "color": {
                            "approved_at_iter": None,
                            "palette_agreed": False,
                            "approved_date": None,
                        },
                        "weave": {"approved_at_iter": None, "approved_date": None},
                    },
                },
                indent=2,
            )
            + "\n"
        )
        print(f"session skeleton -> {session_json}")

    edge = input_dir / "reference-structure.png"
    if not edge.exists():
        if shutil.which("magick"):
            subprocess.run(
                ["magick", str(ref), "-colorspace", "Gray", "-canny", CANNY,
                 "-negate", str(edge)],
                check=True,
            )
            print(f"edge map -> {edge}")
        else:
            print(
                "ImageMagick (magick) not on PATH — skipping the edge map; "
                "the colour-gate swatch sheet will be missing until you "
                "install it and re-run this command."
            )

    swatch = input_dir / "reference-analysis" / "swatch-sheet.png"
    if edge.exists() and not swatch.exists():
        subprocess.run(
            [py, str(tools_dir / "analyze-reference.py"), str(session_dir)],
            check=True,
        )

    # The planner auto-detects center/diameter from the medallion mask and
    # prints them; the studio's marked-up picture is where the owner confirms.
    subprocess.run([py, str(tools_dir / "plan-waves.py"), str(session_dir)], check=True)

    print(f"\nSession ready: {session_dir}\nStarting the review hub…\n")
    result = subprocess.run(
        [py, str(tools_dir / "wave-plan-server.py"), str(session_dir),
         "--port", str(args.port)]
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
