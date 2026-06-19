#!/usr/bin/env python3
"""Strip the colour, keep the weave — then diff our weave against the reference's.

Plain-English purpose (2026-06-19, owner request): the field weave we render is
wrong (white blobs + scattered grey confetti where the reference has a continuous
white basket-weave lattice framing every tile). But we keep diagnosing it by eye
against the COLOURED reference photo, and the colour fights the eye — it's hard to
tell whether our white straps trace the same paths as the reference's white straps
when both pictures are dominated by reds, teals, golds.

The owner's fix: "from our original image, demote/remove all the coloured pieces,
keep the weaves, then compare and contrast the weaves between shapes." Strip BOTH
images down to just the weave, then the comparison is weave-line vs weave-line with
nothing else in the frame. A side-by-side plus an overlay diff makes the gap
(missing straps, wrong crossings, blobs where there should be ribbons) jump out.

Why our side is EXACT and the reference side is not:
  - Our render is an SVG whose weave is already a SEPARATE, TAGGED layer — colour
    faces sit in <g data-layer="N">, the weave sits in <g class="strapwork-*">. So
    isolating our weave is a structural SVG filter (`weave_only_svg`) — lossless,
    deterministic, no thresholding.
  - The reference is a photo with no layer tags — colour and weave are baked into
    pixels. Isolating its weave needs an IMAGE operation: a whiteness threshold
    (keep high-lightness + low-saturation pixels = the white straps; demote colour
    to black). This is the only lossy / tunable step.

Three stages:
  A. strip the reference to its weave  -> ref-weave-only.png   (magick HSL threshold)
  B. isolate OUR weave from the SVG    -> our-weave-only.png    (weave_only_svg, exact)
  C. compare: side-by-side + overlay   -> weave-diff/*          (qiyas pixel-diff)

The one-command entry point runs A -> B -> C and opens the four-up quad with `open`
(do the mechanical owner-facing step ourselves, the surfacing workstyle).

Storage rule (session-artifact-storage): this script is authored code -> git
(tools/). Every rendered artifact it writes -> the Dropbox render dir.

Plan: bikar/.claude/plans/weave-only-compare.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

# --- Paths (mirror layout: authored here, renders -> Dropbox) ----------------
SESSION = "bikar-medallion-10"
DROPBOX_ROOT = Path(
    os.environ.get(
        "BIKAR_DROPBOX_ROOT",
        "/Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns",
    )
)
SESSION_DIR = DROPBOX_ROOT / SESSION
REFERENCE_JPG = SESSION_DIR / "input" / "reference.jpg"
OUT_DIR = SESSION_DIR / "weave-only-compare"

STUDIO_URL = os.environ.get("BIKAR_STUDIO_URL", "http://localhost:8765")

# qiyas:dev is unauthorized on this machine (confirmed 2026-06-19) — use :latest,
# which has pixel-diff and is present locally.
QIYAS_IMAGE = os.environ.get("QIYAS_IMAGE", "ghcr.io/naqshcoffee/qiyas:latest")
MAGICK = shutil.which("magick") or "/opt/homebrew/bin/magick"

# The weave lives in these SVG groups (svg-renderer.ts). The witness test pins
# these names — if the renderer renames a group the test goes red, not the diff
# silently empty.
STRAPWORK_GROUP_RE = re.compile(r'class="(strapwork-[a-z]+)"')

# Reference-strip defaults. The white straps are the brightest region of the
# photo — BUT a pure lightness threshold can't separate strap-white from the
# white BACKGROUND, because the straps connect to the disc edge (flood-fill from
# a corner floods right through the straps and erases them; verified 2026-06-19).
# The fix that works: a silhouette mask. Close the COLOURED tiles (dark/saturated
# pixels) into one solid pattern blob, then intersect that blob with the bright
# pixels — the bright pixels inside the pattern are the straps; the bright pixels
# outside (the background) fall away because they're not inside the silhouette.
# Tuned against reference.jpg (the L55/Close8 winner of the 2026-06-19 sweep):
# Close:5 fragments the straps into rings, L60 erodes the strap shoulders.
DEFAULT_REF_WHITE_MIN = 55   # % lightness floor — pixels darker than this are tile/outline
DEFAULT_REF_CLOSE = 8        # morphology Close Disk radius — fuses tiles into the silhouette


# === Stage B (our side — EXACT) ==============================================

def weave_only_svg(svg: str) -> str:
    """Keep ONLY the weave groups from a bikar weave SVG; drop everything else.

    The whole point of this filter is that our weave is already a tagged layer,
    so isolating it is lossless — a structural whitelist, not a pixel threshold.

    KEEP:   the <svg ...> wrapper + every <g class="strapwork-*"> group.
    DROP:   the background <rect>, every <g data-layer="N"> colour-face group
            (and blueprint data-layer="-1"), and the free <path data-edge-index>
            tile-edge hit-targets at the tail.

    To mirror the reference strip (white straps on black), the kept straps are
    recoloured white and a black background rect is prepended.

    Example (shape, not exhaustive):
        in : <svg ...><rect .../><g data-layer="1">...</g>
             <g class="strapwork-over"><path stroke="#FCFDFD" .../></g>
             <path data-edge-index="7" stroke="transparent"/></svg>
        out: <svg ...><rect ... fill="#000000"/>
             <g class="strapwork-over"><path stroke="#FFFFFF" .../></g></svg>
    """
    # 1) the <svg ...> open tag (preserve viewBox/width/height verbatim).
    svg_open = re.search(r"<svg\b[^>]*>", svg)
    if not svg_open:
        raise ValueError("input is not an SVG (no <svg> tag)")
    head = svg_open.group(0)

    # 2) a black background rect sized to the original (mirror the ref strip).
    rect = re.search(r"<rect\b[^>]*/>", svg)
    if rect:
        bg = re.sub(r'fill="[^"]*"', 'fill="#000000"', rect.group(0))
    else:
        bg = '<rect x="-289" y="-289" width="578" height="578" fill="#000000" />'

    # 3) pull out each <g class="strapwork-*"> ... </g> block verbatim. The
    #    renderer emits them flat (no nesting), so a non-greedy span to the next
    #    </g> is exact. We recolour the visible strap fill to pure white; the
    #    casing/outline (the interlace shadow + dark rail) keep their own colour
    #    so the over/under reads in isolation too.
    groups: list[str] = []
    for m in re.finditer(r'<g class="strapwork-[a-z]+">.*?</g>', svg, flags=re.DOTALL):
        block = m.group(0)
        # near-white strap fills -> pure white so they pop on black.
        block = re.sub(r'stroke="#F[0-9A-Fa-f]{5}"', 'stroke="#FFFFFF"', block)
        groups.append(block)

    if not groups:
        raise ValueError(
            "no <g class=\"strapwork-*\"> groups found — the SVG carries no weave "
            "(is style=field/crossing set, and did the variant actually weave?)"
        )

    body = "\n".join(groups)
    return f'{head}\n  {bg}\n{body}\n</svg>\n'


def fetch_our_weave_svg(params: dict) -> str:
    """Source our weave SVG from the running studio's /api/preview-svg route.

    The studio (wave-plan-server.py) owns the transient-variant build
    (build_weave_variant) + bikar-CLI render seam; we reuse it over HTTP rather
    than duplicating the variant logic here. Requires the studio on :8765.
    """
    body = json.dumps({"params": params}).encode()
    req = urllib.request.Request(
        f"{STUDIO_URL}/api/preview-svg",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.read().decode()
    except Exception as e:  # noqa: BLE001 — surface a plain-language hint
        raise SystemExit(
            f"could not reach the weave studio at {STUDIO_URL}/api/preview-svg "
            f"({e}). Is it running? (PID on :8765 — relaunch with the Dropbox "
            f"session_dir + --session-json sessions/{SESSION}/session.json)"
        ) from e


RSVG = shutil.which("rsvg-convert") or "/opt/homebrew/bin/rsvg-convert"


def rasterize_svg(svg_path: Path, png_path: Path, size: int = 1024) -> None:
    """SVG -> PNG, rsvg-convert-first.

    Counter to the full-weave render's magick-first lesson: that lesson is
    clipPath-specific (rsvg drops outer arc-CLIPPED faces at high path counts).
    The weave-only SVG carries NO clipPaths — it's pure strokes — and there
    magick mis-handles the explicit width="578" + density and renders an
    effectively 1x1 (all-black) frame, while rsvg-convert renders the strokes
    correctly (verified 2026-06-19: magick mean ~0.01 vs rsvg mean ~14). So for
    the stroke-only weave-only render we prefer rsvg-convert; magick is the
    fallback only if rsvg is absent."""
    if shutil.which("rsvg-convert"):
        subprocess.run(
            [RSVG, "-w", str(size), "-h", str(size),
             "-b", "black", str(svg_path), "-o", str(png_path)],
            check=True, capture_output=True, text=True,
        )
        return
    subprocess.run(
        [MAGICK, "-background", "black", "-density", "200",
         str(svg_path), "-resize", f"{size}x{size}", str(png_path)],
        check=True, capture_output=True, text=True,
    )


def stage_b_our_weave(params: dict, size: int = 1024) -> Path:
    """Fetch our weave SVG, filter to weave-only (exact), rasterize."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw = fetch_our_weave_svg(params)
    only = weave_only_svg(raw)
    svg_out = OUT_DIR / "our-weave-only.svg"
    png_out = OUT_DIR / "our-weave-only.png"
    svg_out.write_text(only)
    rasterize_svg(svg_out, png_out, size)
    return png_out


# === Stage A (reference side — LOSSY whiteness threshold) ====================

def ref_strip_command(src: Path, dst: Path, white_min: int, close_radius: int) -> list[str]:
    """The magick pipeline that isolates the white strap lattice (silhouette mask).

    Two masks, ANDed:
      bright    = lightness >= white_min                (white straps AND white bg)
      silhouette= Close(Disk:close_radius) of the dark/coloured tiles
                  (the tiles fused into one solid pattern blob — the straps are
                   the thin gaps INSIDE this blob; the white bg is OUTSIDE it)
      result    = bright AND silhouette                 (straps only — bg drops out)

    Why not a pure lightness threshold + flood-fill: the straps connect to the
    white background at the disc edge, so flood-filling the bg floods through the
    straps and erases them (mean -> 0). The silhouette mask separates strap-white
    from bg-white by REGION (inside vs outside the pattern), not by colour.

    Both knobs are visibly threaded into the command (the witness test asserts
    both reach it — guards a silent default drift like the field-defaults bug).
    """
    return [
        MAGICK, str(src),
        # silhouette: dark/coloured tiles -> white, Close to fuse into a solid blob.
        "(", "-clone", "0", "-colorspace", "HSL",
             "-channel", "B", "-separate", "+channel",          # Lightness plane
             "-threshold", f"{white_min}%", "-negate",          # tiles (dark) -> white
             "-morphology", "Close", f"Disk:{close_radius}",    # fuse tiles -> silhouette
        ")",
        # bright: straps + background -> white.
        "(", "-clone", "0", "-colorspace", "HSL",
             "-channel", "B", "-separate", "+channel",          # Lightness plane
             "-threshold", f"{white_min}%",                     # bright -> white
        ")",
        "-delete", "0",
        "-compose", "multiply", "-composite",                   # AND: straps inside blob
        str(dst),
    ]


def stage_a_reference(white_min: int, close_radius: int, size: int = 1024) -> Path:
    """Strip reference.jpg to ref-weave-only.png (white straps on black)."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not REFERENCE_JPG.exists():
        raise SystemExit(f"reference not found: {REFERENCE_JPG}")
    out = OUT_DIR / "ref-weave-only.png"
    cmd = ref_strip_command(REFERENCE_JPG, out, white_min, close_radius)
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    # normalize to the comparison size (square) so pixel-diff aligns cleanly.
    subprocess.run(
        [MAGICK, str(out), "-resize", f"{size}x{size}", str(out)],
        check=True, capture_output=True, text=True,
    )
    return out


# === Stage C (compare) =======================================================

def stage_c_compare(ref_png: Path, our_png: Path) -> dict:
    """qiyas pixel-diff -> four-up quad (ref/ours/diff/overlay) + score json.

    Reference is IMG_A (the target), ours is IMG_B; the overlay composites ours
    over the reference at 50% so white-on-white = matched strap, lone-colour =
    strap present in only one. magick rasterizer (stroke-heavy)."""
    diff_dir = OUT_DIR / "weave-diff"
    diff_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "docker", "run", "--rm", "-v", f"{OUT_DIR}:/work",
        QIYAS_IMAGE, "pixel-diff",
        f"/work/{ref_png.name}", f"/work/{our_png.name}",
        "--out", "/work/weave-diff",
        "--rasterizer", "magick",
        "--overlay-opacity", "50",
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    score_path = diff_dir / "pixel-diff.json"
    return json.loads(score_path.read_text()) if score_path.exists() else {}


def open_quad(diff_dir: Path) -> None:
    """Open the diff visual for the owner (the surfacing workstyle)."""
    for name in ("diff-overlay.png", "diff-visual.png"):
        p = diff_dir / name
        if p.exists():
            subprocess.run(["open", str(p)], check=False)
            return


# === Entry point =============================================================

def parse_params(query: str) -> dict:
    """Parse a studio query string (style=field&width=10&...) into a params dict,
    matching the studio's URL_KEYS typing (ints/floats where the studio expects)."""
    params: dict = {}
    for pair in query.lstrip("?").split("&"):
        if not pair or "=" not in pair:
            continue
        k, v = pair.split("=", 1)
        v = urllib.parse.unquote(v)
        # mirror the studio's numeric coercions; leave strings (style, color) as-is.
        if k in ("width", "field_angle", "field_ray", "step", "suppress_tol",
                 "suppress_beyond"):
            try:
                params[k] = float(v) if "." in v else int(v)
            except ValueError:
                params[k] = v
        elif k in ("field_wave_lo", "field_wave_hi"):
            params[k] = int(v)
        elif k in ("shadow", "network", "suppress"):
            params[k] = v in ("1", "true", "True")
        else:
            params[k] = v
    return params


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Strip colour, keep weave, diff our weave vs the reference's.",
    )
    ap.add_argument(
        "--params",
        default=("style=field&width=10&color=%23FCFDFD&field_angle=36"
                 "&field_ray=8&field_wave_lo=17&field_wave_hi=17"),
        help="studio query string for OUR weave variant (default: bounded field weave).",
    )
    ap.add_argument("--ref-white-min", type=int, default=DEFAULT_REF_WHITE_MIN,
                    help="lightness%% floor for the reference strap mask (Stage A).")
    ap.add_argument("--ref-close", type=int, default=DEFAULT_REF_CLOSE,
                    help="morphology Close Disk radius — fuses tiles into the "
                         "pattern silhouette so strap-white separates from bg-white.")
    ap.add_argument("--size", type=int, default=1024, help="square comparison size.")
    ap.add_argument("--stage", choices=["a", "b", "c", "all"], default="all",
                    help="run a single stage (a=ref strip, b=our weave, c=diff) or all.")
    ap.add_argument("--no-open", action="store_true", help="don't open the quad.")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    params = parse_params(args.params)

    ref_png = OUT_DIR / "ref-weave-only.png"
    our_png = OUT_DIR / "our-weave-only.png"

    if args.stage in ("a", "all"):
        print(f"[A] stripping reference -> weave-only "
              f"(white_min={args.ref_white_min}%, close=Disk:{args.ref_close})")
        ref_png = stage_a_reference(args.ref_white_min, args.ref_close, args.size)
        print(f"    -> {ref_png}")

    if args.stage in ("b", "all"):
        print(f"[B] isolating OUR weave (exact SVG-layer filter): {params}")
        our_png = stage_b_our_weave(params, args.size)
        print(f"    -> {our_png}")

    if args.stage in ("c", "all"):
        if not ref_png.exists() or not our_png.exists():
            print("[C] need both ref-weave-only.png and our-weave-only.png "
                  "(run stages a+b first).", file=sys.stderr)
            return 1
        print("[C] comparing (qiyas pixel-diff: side-by-side + overlay)")
        score = stage_c_compare(ref_png, our_png)
        diff_dir = OUT_DIR / "weave-diff"
        sim = score.get("similarity_pct")
        cov = score.get("coverage", {})
        print(f"    -> {diff_dir}/  (similarity: {sim}%)")
        # The coverage breakdown IS the weave compare-and-contrast: only_a = the
        # reference's straps we're MISSING, only_b = straps we drew that the
        # reference has NOT (our spurious blobs / confetti). Plain verdict so the
        # owner reads the gap without opening the JSON.
        if cov:
            print(f"    shared straps:   {cov.get('shared_pct')}%  (match)")
            print(f"    MISSING (ref-only): {cov.get('only_a_pct')}%  "
                  f"<- straps the reference has and we don't")
            print(f"    EXTRA (ours-only):  {cov.get('only_b_pct')}%  "
                  f"<- straps we drew that aren't in the reference")
        if not args.no_open:
            open_quad(diff_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
