"""Regression: the studio's field-weave defaults stay BOUNDED across all three
places that declare them, so a fresh studio load can't re-explode.

Plain-English purpose (2026-06-19): field-Hankin over the full 10-wave outer
band (waves 13..22, ray 24) × 10 rotations emits ~147K SVG paths. rsvg-convert
then DROPS the outer arc-clipped faces and the owner sees "central-disc-only
color" — the two defects (#41 overpowering / #42 grey-cracks) traced to one
mechanism: path explosion + rasterizer degradation. The fix bounds the defaults
to a single wave band (17..17) and a short ray (8), which stays ~3.7K paths with
full-field color.

The bug this test pins is a SPLIT-BRAIN one: the bounded value has to be set in
THREE independent places —
  1. the JS client `state` object (what a fresh page initializes to),
  2. the HTML `<input value="...">` attributes (the slider's raw default),
  3. the Python server-side `build_weave_variant` fallbacks (`params.get(...)`).
If any one drifts back to the exploding band, the studio re-explodes on the path
that bypasses the others (a fresh load reads the JS state; a sync-less render
reads the HTML; a direct /weave.png?style=field with no field_* params reads the
Python fallback). This froze the witness so the next studio edit can't silently
reintroduce ray=24 / waves=13..22 in any one of the three.

Witness frozen per Tenet 18 — the shell `grep` sweep that found the client/server
divergence (server fixed to 8/17/17 but JS state still 24/13..22) lives here.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
SERVER = TOOLS_DIR / "wave-plan-server.py"

# The bounded values the fix standardized on. ray 8 / single wave 17 keeps the
# field render ~3.7K paths (full-field color) instead of ~147K (rsvg drops the
# outer faces). If the owner later wants a wider band the default still must be
# bounded — they widen it via the dial, not via an exploding default.
BOUNDED_RAY = 8
BOUNDED_WAVE_LO = 17
BOUNDED_WAVE_HI = 17


class StudioFieldDefaultsBounded(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.src = SERVER.read_text()

    def test_js_state_defaults_are_bounded(self) -> None:
        # `field_ray: N,`  and  `field_wave_lo: A, field_wave_hi: B,` in the JS
        # `state` literal (the value a fresh studio page initializes to).
        ray = re.search(r"\bfield_ray:\s*(\d+)\b", self.src)
        lo = re.search(r"\bfield_wave_lo:\s*(\d+)\b", self.src)
        hi = re.search(r"\bfield_wave_hi:\s*(\d+)\b", self.src)
        self.assertIsNotNone(ray, "field_ray default not found in JS state")
        self.assertIsNotNone(lo, "field_wave_lo default not found in JS state")
        self.assertIsNotNone(hi, "field_wave_hi default not found in JS state")
        self.assertEqual(int(ray.group(1)), BOUNDED_RAY)
        self.assertEqual(int(lo.group(1)), BOUNDED_WAVE_LO)
        self.assertEqual(int(hi.group(1)), BOUNDED_WAVE_HI)

    def test_html_input_defaults_are_bounded(self) -> None:
        # The raw `<input ... value="N">` slider defaults.
        ray = re.search(r'id="fieldRay"[^>]*value="(\d+)"', self.src)
        lo = re.search(r'id="fieldWaveLo"[^>]*value="(\d+)"', self.src)
        hi = re.search(r'id="fieldWaveHi"[^>]*value="(\d+)"', self.src)
        self.assertIsNotNone(ray, "fieldRay input value not found")
        self.assertIsNotNone(lo, "fieldWaveLo input value not found")
        self.assertIsNotNone(hi, "fieldWaveHi input value not found")
        self.assertEqual(int(ray.group(1)), BOUNDED_RAY)
        self.assertEqual(int(lo.group(1)), BOUNDED_WAVE_LO)
        self.assertEqual(int(hi.group(1)), BOUNDED_WAVE_HI)

    def test_server_fallbacks_are_bounded(self) -> None:
        # The Python `params.get("field_ray", N)` fallbacks — what a
        # /weave.png?style=field with no field_* query params resolves to.
        ray = re.search(r'params\.get\("field_ray",\s*(\d+)\)', self.src)
        lo = re.search(r'params\.get\("field_wave_lo",\s*(\d+)\)', self.src)
        hi = re.search(r'params\.get\("field_wave_hi",\s*(\d+)\)', self.src)
        self.assertIsNotNone(ray, "field_ray server fallback not found")
        self.assertIsNotNone(lo, "field_wave_lo server fallback not found")
        self.assertIsNotNone(hi, "field_wave_hi server fallback not found")
        self.assertEqual(int(ray.group(1)), BOUNDED_RAY)
        self.assertEqual(int(lo.group(1)), BOUNDED_WAVE_LO)
        self.assertEqual(int(hi.group(1)), BOUNDED_WAVE_HI)

    def test_rasterizer_prefers_magick_over_rsvg(self) -> None:
        # The other half of the fix: magick must be tried BEFORE rsvg-convert,
        # because rsvg-convert is the one that drops the outer faces at high path
        # counts. Assert magick's which() check appears before rsvg-convert's.
        magick_at = self.src.find('shutil.which("magick")')
        rsvg_at = self.src.find('shutil.which("rsvg-convert")')
        self.assertGreater(magick_at, -1, "magick rasterizer branch missing")
        self.assertGreater(rsvg_at, -1, "rsvg-convert fallback branch missing")
        self.assertLess(magick_at, rsvg_at,
                        "magick must be preferred BEFORE rsvg-convert")


if __name__ == "__main__":
    unittest.main()
