"""Regression: the studio's field-weave defaults stay BOUNDED and stay AGREED
across all three places that declare them, so a fresh studio load can't
re-explode and the three declarations can't drift apart.

Plain-English purpose (2026-06-19): field-Hankin over the full 10-wave outer
band (waves 13..22, ray 24) x 10 rotations emits ~147K SVG paths. rsvg-convert
then DROPS the outer arc-clipped faces and the owner sees "central-disc-only
color" — the two defects (#41 overpowering / #42 grey-cracks) traced to one
mechanism: path explosion + rasterizer degradation.

The bug this test pins is a SPLIT-BRAIN one: the bounded value has to be set in
THREE independent places —
  1. the JS client `state` object (what a fresh page initializes to),
  2. the HTML `<input value="...">` attributes (the slider's raw default),
  3. the Python server-side `build_weave_variant` fallbacks (`params.get(...)`).
If any one drifts, the studio behaves differently on the path that bypasses the
others (a fresh load reads the JS state; a sync-less render reads the HTML; a
direct /weave.png?style=field with no field_* params reads the Python fallback).

WHY THIS FILE WAS REWRITTEN (2026-08-18). The original froze the three legs
against a module-level literal, and that is a weaker check than it looks:

  * 29c5ff4 (2026-06-19) widened the band from 17..17 to 5..16 and says so in
    its own message — "Updated BOTH the JS state default and
    build_weave_variant's server-side fallback to 5/16 (split-brain guard)".
    BOTH is two of three. The HTML slider stayed at 17/17 for two months and
    `test_html_input_defaults_are_bounded` passed the whole time, because the
    literal it compared against was the stale one. The gate was green ON the
    exact defect it exists to catch. Fixed here: the sliders now read 5/16.
  * A literal also cannot tell a real regression from a deliberate change, so
    the two legs that DID move went red and stayed red — measured red on clean
    master, unrelated to the branch that surfaced them. A gate that cries wolf
    gets switched off, which is how it survived two months.

So the check is now two-layer, and the layer that does the work needs no
maintenance: **the three legs must agree with each other** (any single-leg
drift fails regardless of what number this file names), and **the agreed value
must be one somebody measured** (the ceiling below).

The bound is not a taste. 29c5ff4 measured the band it shipped at 23.9K paths
against the 147K explosion ceiling, and the band has to CROSS ring boundaries
(radial map: wave 1 = center, 3-7 inner, 8-12 middle, 13-22 outer) or the field
degenerates to one ring of detached rosettes — the single-wave 17..17 default
is what produced the owner's "weave nodules look wrong" verdict. Widening the
default again is allowed; doing it in fewer than three places is not, and doing
it without re-measuring the path count is not.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
SERVER = TOOLS_DIR / "wave-plan-server.py"

# The measured-safe default, from 29c5ff4 (2026-06-19): waves 5..16 spans
# inner->outer for a continuous field-wide lattice at 23.9K paths, well under
# the 147K explosion ceiling. ray 8 is unchanged from the original bound.
BOUNDED_RAY = 8
BOUNDED_WAVE_LO = 5
BOUNDED_WAVE_HI = 16

# Above this the rasterizer degrades (rsvg-convert drops the outer arc-clipped
# faces). The number is the ceiling 29c5ff4 measured against, kept here so the
# next widening has something to compare to instead of a vibe.
PATH_EXPLOSION_CEILING = 147_000


class StudioFieldDefaultsBounded(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.src = SERVER.read_text()

    # -- the three legs, read independently -------------------------------

    def _js_state(self) -> dict[str, int]:
        # `field_ray: N,` and `field_wave_lo: A, field_wave_hi: B,` in the JS
        # `state` literal (the value a fresh studio page initializes to).
        pats = {
            "ray": r"\bfield_ray:\s*(\d+)\b",
            "lo": r"\bfield_wave_lo:\s*(\d+)\b",
            "hi": r"\bfield_wave_hi:\s*(\d+)\b",
        }
        return self._read("JS state", pats)

    def _html_inputs(self) -> dict[str, int]:
        # The raw `<input ... value="N">` slider defaults.
        pats = {
            "ray": r'id="fieldRay"[^>]*value="(\d+)"',
            "lo": r'id="fieldWaveLo"[^>]*value="(\d+)"',
            "hi": r'id="fieldWaveHi"[^>]*value="(\d+)"',
        }
        return self._read("HTML input", pats)

    def _server_fallbacks(self) -> dict[str, int]:
        # The Python `params.get("field_ray", N)` fallbacks — what a
        # /weave.png?style=field with no field_* query params resolves to.
        pats = {
            "ray": r'params\.get\("field_ray",\s*(\d+)\)',
            "lo": r'params\.get\("field_wave_lo",\s*(\d+)\)',
            "hi": r'params\.get\("field_wave_hi",\s*(\d+)\)',
        }
        return self._read("server fallback", pats)

    def _read(self, leg: str, pats: dict[str, str]) -> dict[str, int]:
        out: dict[str, int] = {}
        for key, pat in pats.items():
            found = re.findall(pat, self.src)
            self.assertTrue(found, f"{leg}: no field_{key} declaration matched {pat!r}")
            # A leg may declare the same default more than once (the server
            # fallback appears in two branches). They must not disagree with
            # each other either — that is the same split-brain one level down,
            # and taking re.search's first match would have hidden it.
            self.assertEqual(
                len(set(found)), 1,
                f"{leg}: field_{key} declared with conflicting values {sorted(set(found))}",
            )
            out[key] = int(found[0])
        return out

    # -- layer 1: the legs agree with each other --------------------------

    def test_three_declarations_agree(self) -> None:
        """The check that needs no maintenance.

        This fails on ANY single-leg drift no matter what constants this file
        names — which is what the original could not do, and why the HTML
        slider sat two months behind the other two while its test was green.
        """
        legs = {
            "JS state": self._js_state(),
            "HTML input": self._html_inputs(),
            "server fallback": self._server_fallbacks(),
        }
        for key in ("ray", "lo", "hi"):
            values = {name: leg[key] for name, leg in legs.items()}
            self.assertEqual(
                len(set(values.values())), 1,
                f"field_{key} split-brain: {values}. All three declarations must "
                f"move together — see this module's docstring.",
            )

    # -- layer 2: the agreed value is the one that was measured ------------

    def test_agreed_default_is_the_measured_one(self) -> None:
        js = self._js_state()
        self.assertEqual(js["ray"], BOUNDED_RAY)
        self.assertEqual(js["lo"], BOUNDED_WAVE_LO)
        self.assertEqual(js["hi"], BOUNDED_WAVE_HI)

    def test_default_band_crosses_ring_boundaries(self) -> None:
        """A single-wave band is 10 rotated copies at ONE radius, so its contact
        rays only meet neighbours within that ring — one ring of detached
        rosettes, which is the defect 29c5ff4 was fixing. The band must span at
        least two of the radial zones (1 center / 3-7 inner / 8-12 middle /
        13-22 outer)."""
        js = self._js_state()
        zones = [(1, 2, "center"), (3, 7, "inner"), (8, 12, "middle"), (13, 22, "outer")]
        spanned = [n for lo, hi, n in zones if js["lo"] <= hi and js["hi"] >= lo]
        self.assertGreater(
            len(spanned), 1,
            f"default band {js['lo']}..{js['hi']} sits inside {spanned} only; a "
            f"band that does not cross a ring boundary degenerates to detached "
            f"rosettes (owner verdict 2026-06-19).",
        )

    # -- the rasterizer half of the same fix -------------------------------

    def test_no_unconditional_rsvg_branch_precedes_magick(self) -> None:
        """rsvg-convert drops the outer arc-clipped faces at high path counts,
        so the DEFAULT rasterizer path must reach magick first.

        Stated as "no unguarded rsvg branch before magick" rather than as a raw
        string-offset comparison. 953e3e0 (2026-06-21) added a legitimate
        `if prefer_rsvg and shutil.which("rsvg-convert")` branch above magick —
        an opt-in for the pure-stroke progress SVG, whose failure mode is the
        inverse (magick blanks it). The old assertion compared the first
        occurrence of each string and went red on that, even though the default
        preference never changed. The invariant is about the UNGUARDED branch.
        """
        magick = [m.start() for m in re.finditer(r'shutil\.which\("magick"\)', self.src)]
        rsvg = [m.start() for m in re.finditer(r'shutil\.which\("rsvg-convert"\)', self.src)]
        self.assertTrue(magick, "magick rasterizer branch missing")
        self.assertTrue(rsvg, "rsvg-convert fallback branch missing")

        def line_of(offset: int) -> str:
            start = self.src.rfind("\n", 0, offset) + 1
            end = self.src.find("\n", offset)
            return self.src[start: end if end != -1 else len(self.src)]

        unguarded = [o for o in rsvg if "prefer_rsvg" not in line_of(o)]
        self.assertTrue(
            unguarded,
            "every rsvg-convert branch is behind an opt-in flag — then nothing "
            "rasterizes by default; this assertion has lost its subject.",
        )
        self.assertLess(
            magick[0], unguarded[0],
            "an rsvg-convert branch with no opt-in guard precedes magick:\n"
            f"  guard-free rsvg at {unguarded[0]}: {line_of(unguarded[0]).strip()}\n"
            f"  first magick at {magick[0]}: {line_of(magick[0]).strip()}",
        )


if __name__ == "__main__":
    unittest.main()
