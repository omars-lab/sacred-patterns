"""Regression: the weave-only isolation is EXACT (lossless) and the reference
threshold knobs actually reach the magick command.

Plain-English purpose (2026-06-19): the weave-only compare tool strips a render
down to just its weave so we can diff our straps against the reference's straps
without colour fighting the eye. Our side is supposed to be EXACT — the weave is
already a tagged SVG layer (<g class="strapwork-*">), so isolating it is a
structural whitelist, not a pixel threshold. This test pins that exactness:

  1. weave_only_svg KEEPS every strapwork-* group and DROPS everything else —
     the colour-face <g data-layer> groups, the background rect, and the free
     <path data-edge-index> tile edges. If the filter ever starts leaking colour
     faces into the weave-only render, the "exact" claim is a lie and this goes
     red. It also pins the strapwork-* group NAMES — if svg-renderer.ts renames a
     weave group, the filter would silently drop the weave; this catches it.

  2. The reference strip's two knobs (--ref-white-min / --ref-sat-max) are
     threaded into the magick command. Guards against a silent default drift like
     the field-defaults split-brain bug (server fixed, client stale).

Witness frozen per Tenet 18.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]

# weave-only-compare.py has a hyphen, so import it by path.
_spec = importlib.util.spec_from_file_location(
    "weave_only_compare", TOOLS_DIR / "weave-only-compare.py"
)
assert _spec and _spec.loader
woc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(woc)


# A minimal SVG with the exact shape svg-renderer.ts emits for a weave render:
# background rect, blueprint + colour-face data-layer groups, the four strapwork
# groups, and the free data-edge-index tail.
SAMPLE_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="-289 -289 578 578" width="578" height="578">
  <rect x="-289" y="-289" width="578" height="578" fill="#FFFFFF" pointer-events="none" />
  <g data-layer="-1" style="display:none">
    <circle cx="0" cy="0" r="100" data-circle-index="0" />
  </g>
  <g data-layer="1">
    <path d="M0,0 L1,1" fill="#C0392B" data-face-index="3" data-layer="1" />
  </g>
  <g data-layer="2">
    <path d="M2,2 L3,3" fill="#2C5C5C" data-face-index="4" data-layer="2" />
  </g>
  <g class="strapwork-outline">
    <path d="M10,10 L20,20" fill="none" stroke="#6B7176" stroke-width="14" data-strand="0" />
  </g>
  <g class="strapwork-under">
    <path d="M10,10 L20,20" fill="none" stroke="#FCFDFD" stroke-width="10" data-strand="0" />
  </g>
  <g class="strapwork-casing">
    <path d="M14,14 L16,16" fill="none" stroke="#888888" stroke-width="12" data-strand="0" />
  </g>
  <g class="strapwork-over">
    <path d="M30,10 L20,20" fill="none" stroke="#FCFDFD" stroke-width="10" data-strand="1" />
  </g>
  <path d="M0,0 L5,5" fill="none" stroke="transparent" stroke-width="10" data-edge-index="42" />
</svg>
"""


class WeaveOnlyIsolationExact(unittest.TestCase):
    def setUp(self) -> None:
        self.out = woc.weave_only_svg(SAMPLE_SVG)

    def test_keeps_every_strapwork_group(self) -> None:
        # All four weave groups survive — pins the group names against a renderer
        # rename that would silently empty the weave.
        for grp in ("strapwork-outline", "strapwork-under",
                    "strapwork-casing", "strapwork-over"):
            self.assertIn(f'class="{grp}"', self.out, f"{grp} dropped")

    def test_drops_colour_face_groups(self) -> None:
        # The lossless invariant: NO colour-face groups or face paths leak through.
        self.assertNotIn("data-layer=", self.out)
        self.assertNotIn("data-face-index=", self.out)
        self.assertNotIn("#C0392B", self.out)  # the red tile fill must be gone
        self.assertNotIn("#2C5C5C", self.out)  # the teal tile fill must be gone

    def test_drops_free_edge_paths(self) -> None:
        # Tile-edge geometry is not weave — it must not survive isolation.
        self.assertNotIn("data-edge-index=", self.out)

    def test_drops_white_background_and_adds_black(self) -> None:
        # The kept render must be white straps on BLACK (mirror the ref strip),
        # never the original white background rect.
        self.assertIn('fill="#000000"', self.out)
        self.assertNotIn('fill="#FFFFFF"', self.out)

    def test_recolours_straps_pure_white(self) -> None:
        # Near-white strap fills (#FCFDFD) -> pure #FFFFFF so they pop on black.
        self.assertIn("#FFFFFF", self.out)
        self.assertNotIn("#FCFDFD", self.out)

    def test_preserves_svg_viewbox(self) -> None:
        # The wrapper (viewBox/size) is kept verbatim so the rasterized PNG
        # aligns with the reference strip's coordinate frame.
        self.assertIn('viewBox="-289 -289 578 578"', self.out)

    def test_empty_weave_raises(self) -> None:
        # An SVG with no strapwork groups is a render that didn't weave — surface
        # it loudly, don't emit a blank PNG that reads as "matched nothing".
        no_weave = ('<svg viewBox="0 0 1 1"><rect fill="#FFF"/>'
                    '<g data-layer="1"><path d="M0,0 L1,1"/></g></svg>')
        with self.assertRaises(ValueError):
            woc.weave_only_svg(no_weave)


class RasterizerChoice(unittest.TestCase):
    """The weave-only SVG is pure strokes (no clipPaths), and magick renders it
    to an effectively 1x1 all-black frame (mean ~0.01) while rsvg-convert renders
    the strokes correctly (mean ~14). This is the OPPOSITE of the full-weave
    render's magick-first lesson (which is clipPath-specific). Pin rsvg-first so a
    future edit can't silently flip back to magick and produce a black diff.

    Witness frozen per Tenet 18 — the 2026-06-19 magick-renders-black debug.
    """

    def test_rasterize_prefers_rsvg_over_magick(self) -> None:
        src = (TOOLS_DIR / "weave-only-compare.py").read_text()
        rsvg_at = src.find('shutil.which("rsvg-convert")')
        magick_fallback = src.find("magick is the\n    # fallback")
        self.assertGreater(rsvg_at, -1, "rsvg-convert branch missing")
        # rsvg's which() check must come before the magick fallback runs.
        magick_run = src.find("[MAGICK,", rsvg_at)
        self.assertGreater(magick_run, rsvg_at,
                           "magick must be the FALLBACK, after the rsvg branch")


class PixelDiffJsonContract(unittest.TestCase):
    """Stage C reads qiyas pixel-diff's JSON to print the plain-language verdict.
    The keys it depends on are `similarity_pct` and the `coverage` block
    (`shared_pct` / `only_a_pct` / `only_b_pct`). When the code first read
    `score.get("score")` / `"similarity"` the verdict printed `None` silently —
    the diff ran, the numbers existed, but the wrong key was read. Pin the exact
    key names the script references so a qiyas schema rename surfaces here, not as
    a silent `None`. Witness frozen per Tenet 18 — the 2026-06-19 None-verdict bug.
    """

    def test_main_reads_the_real_pixel_diff_keys(self) -> None:
        src = (TOOLS_DIR / "weave-only-compare.py").read_text()
        # The keys qiyas pixel-diff actually emits (see pixel-diff.json).
        self.assertIn('"similarity_pct"', src)
        self.assertIn('"coverage"', src)
        for k in ("shared_pct", "only_a_pct", "only_b_pct"):
            self.assertIn(k, src, f"coverage key {k} not read")
        # And the OLD wrong keys must be gone (they read None).
        self.assertNotIn('.get("score")', src, "stale `score` key still read")
        self.assertNotIn('.get("similarity")', src, "stale `similarity` key still read")


class ReferenceThresholdKnobs(unittest.TestCase):
    """The Stage-A reference strip uses a SILHOUETTE mask, not a pure threshold:
    the white straps connect to the white background at the disc edge, so they
    can't be split by colour — they're split by REGION (close the coloured tiles
    into a solid blob, intersect with bright pixels). The two knobs are the
    lightness floor (white_min) and the morphology Close radius (close_radius).
    Pin that both reach the magick command — guards the split-brain default-drift
    failure mode (the field-defaults bug). 2026-06-19 silhouette-mask rework."""

    def test_both_knobs_reach_the_magick_command(self) -> None:
        cmd = woc.ref_strip_command(
            Path("/tmp/ref.jpg"), Path("/tmp/out.png"), white_min=55, close_radius=8
        )
        joined = " ".join(cmd)
        self.assertIn("55%", joined, "white_min not threaded into the command")
        self.assertIn("Disk:8", joined, "close_radius not threaded into the command")

    def test_knobs_are_independent(self) -> None:
        # Changing one knob changes only its own value in the command.
        cmd = woc.ref_strip_command(
            Path("/tmp/ref.jpg"), Path("/tmp/out.png"), white_min=60, close_radius=5
        )
        joined = " ".join(cmd)
        self.assertIn("60%", joined)
        self.assertIn("Disk:5", joined)
        self.assertNotIn("Disk:8", joined)

    def test_silhouette_mask_uses_two_lightness_planes_not_saturation(self) -> None:
        # The fix is region-based, not saturation-based: BOTH masks separate the
        # HSL B (Lightness) plane (one negated for the tile silhouette), and the
        # command must NOT reach for the G (Saturation) plane — saturation
        # fringing at strap edges is exactly what eroded the straps before.
        cmd = woc.ref_strip_command(
            Path("/tmp/ref.jpg"), Path("/tmp/out.png"), white_min=55, close_radius=8
        )
        # Two "-channel B -separate" (lightness) extractions, zero "-channel G".
        self.assertEqual(cmd.count("B"), 2, "expected two Lightness-plane masks")
        self.assertNotIn("G", cmd, "saturation plane must not be used")
        self.assertIn("Close", cmd, "morphology Close (silhouette fuse) missing")


if __name__ == "__main__":
    unittest.main()
