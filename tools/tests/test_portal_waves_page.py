"""Regression: the /waves page shows every wave with all views + a code diff.

Plain-English purpose (2026-06-15): the owner replaced the per-wave view PICKER
with a plain "waves page" — "I dont want a view picker per wave ... rather a
waves page with all these views per wave ... and even a code diff view". Each
wave card shows, with no picking: a tight CROP of the reference photo zoomed to
that wave's shapes (the default/primary tile), our build, just-this-wave's
shapes, and a foldaway recipe (.bkr) diff. This test pins that contract:

  1. /waves renders one card per wave, each with the primary crop tile, the two
     ghost tiles, and a code-diff section.
  2. The old /wave-options URL 301-redirects to /waves (bookmarks still land).
  3. /inspect renders the shape→wave hotspots (one clickable spot per shape) and
     the plain "tap a shape" readout.
  4. The removed picker is gone: no /api/wave-view-pick acceptance on this page,
     no "view you picked per wave" roll-up on /iterate.

Witness frozen per Tenet 18 — the curl probes that confirmed the redesign
(22 cards, 22 crop tiles, 22 code diffs, the 301, the inspector hotspots) live
here as the test.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
SERVER = TOOLS_DIR / "wave-plan-server.py"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _min_wave_plan() -> dict:
    # Two waves, each with a shape carrying pixel x/y + area (the crop generator
    # and the inspector hotspots both read these).
    return {
        "waves": [
            {"wave": 1, "color": "deep_navy", "where": "in the centre",
             "real_shape_count": 1,
             "shapes": [{"id": 1, "x": 386.0, "y": 361.0, "area_px": 1600,
                         "r_frac": 0.0, "theta_deg": 0.0, "color": "navy"}]},
            {"wave": 6, "color": "navy", "where": "around the rosettes",
             "real_shape_count": 2,
             "shapes": [
                 {"id": 2, "x": 250.0, "y": 250.0, "area_px": 900,
                  "r_frac": 0.3, "theta_deg": 45.0, "color": "navy"},
                 {"id": 3, "x": 520.0, "y": 470.0, "area_px": 900,
                  "r_frac": 0.3, "theta_deg": 225.0, "color": "navy"}]},
        ]
    }


def _make_session(root: Path) -> None:
    plan_dir = root / "input" / "reference-analysis" / "wave-plan"
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / "wave-plan.json").write_text(json.dumps(_min_wave_plan()))
    (plan_dir / "wave-plan.html").write_text("<html><body>stub</body></html>")
    png = b"\x89PNG\r\n\x1a\n"
    # A real reference image so /inspect can read its size (PIL).
    try:
        from PIL import Image
        Image.new("RGB", (753, 722), "white").save(root / "input" / "reference.jpg")
    except Exception:
        (root / "input" / "reference.jpg").write_bytes(png)
    # The per-wave pictures the /waves card links to (crop + ghost + iso),
    # baked under the best iteration's wave-ghosts dir.
    gdir = root / "iterations" / "1" / "wave-ghosts"
    gdir.mkdir(parents=True, exist_ok=True)
    for n in (1, 6):
        (gdir / f"wave-{n}-crop.png").write_bytes(png)
        (gdir / f"wave-{n}.png").write_bytes(png)
        (gdir / f"wave-{n}-iso.png").write_bytes(png)
    # A pattern.bkr per built iteration so the code-diff has something to diff.
    (root / "iterations" / "1" / "pattern.bkr").write_text(
        "blueprint\n  circle C0 center(0,0) radius 100\npattern\n  connect 0 1\n")
    session = {
        "name": "test-medallion",
        "stage_gates": {
            "structure": {
                "approved": None,
                "wave_plan": {"agreed": True},
                "waves_passed": {
                    "1": {"iter": 1, "coverage": 1.0, "owner_verdict": None},
                    "6": {"iter": 1, "coverage": 1.0, "owner_verdict": None},
                },
            }
        },
    }
    (root / "session.json").write_text(json.dumps(session, indent=2))


def _get(url: str, follow: bool = True) -> tuple[int, str, str]:
    # Returns (status, body, redirect_location). When follow is False we catch
    # the 3xx ourselves to assert the redirect target.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    opener = (urllib.request.build_opener()
              if follow else urllib.request.build_opener(NoRedirect))
    try:
        with opener.open(url, timeout=3) as r:
            return r.status, r.read().decode("utf-8", "replace"), ""
    except urllib.error.HTTPError as e:
        return e.code, "", e.headers.get("Location", "")


class WavesPage(unittest.TestCase):
    def test_waves_inspect_and_redirect(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_session(root)
            port = _free_port()
            proc = subprocess.Popen(
                [sys.executable, str(SERVER), str(root),
                 "--center", "386", "361", "--diameter", "738",
                 "--port", str(port)],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
            base = f"http://127.0.0.1:{port}"
            try:
                deadline = time.time() + 10
                while time.time() < deadline:
                    try:
                        _get(f"{base}/waves")
                        break
                    except Exception:
                        time.sleep(0.25)

                # 1. /waves: one card per wave, every view tile, a code diff.
                st, body, _ = _get(f"{base}/waves")
                self.assertEqual(st, 200)
                self.assertEqual(body.count("data-wave-card='"), 2,
                                 "expected one card per wave")
                self.assertEqual(body.count("view primary"), 2,
                                 "expected one primary crop tile per wave")
                # All three views are equal-size grid cells (owner: "all three
                # wave cards should be same size") — 3 tiles/card, and each tile
                # carries an expand-to-fullscreen button into a single lightbox.
                self.assertIn("repeat(3, minmax(0, 1fr))", body,
                              "tiles must be an equal 3-column grid")
                self.assertEqual(body.count("class='view"), 6,
                                 "3 equal tiles per wave (crop+ours+iso)")
                self.assertEqual(body.count("class='expand'"), 6,
                                 "every tile needs a fullscreen-expand button")
                self.assertIn("id='lightbox'", body, "fullscreen lightbox missing")
                self.assertNotIn("side-views", body,
                                 "old primary-bigger-than-sides layout removed")
                for ref in ("wave-1-crop.png", "wave-6-crop.png",
                            "/wave-ghosts/wave-1.png", "wave-1-iso.png"):
                    self.assertIn(ref, body, f"missing view image {ref}")
                self.assertEqual(body.count("class='codediff'"), 2,
                                 "expected a code-diff section per built wave")
                # The diff actually diffed something (added lines present).
                self.assertIn("class='ins'", body)

                # 2. /wave-options 301-redirects to /waves.
                code, _, loc = _get(f"{base}/wave-options", follow=False)
                self.assertEqual(code, 301)
                self.assertTrue(loc.endswith("/waves"), f"redirect was {loc!r}")

                # 3. /inspect: a clickable hotspot per shape + the plain readout.
                sti, it, _ = _get(f"{base}/inspect")
                self.assertEqual(sti, 200)
                self.assertEqual(it.count("class='spot'"), 3,
                                 "one hotspot per wave-plan shape (1 + 2)")
                self.assertIn("Tap a shape on your photo", it)
                self.assertIn("data-wave='6'", it)

                # 4. The removed picker leaves no trace on /iterate.
                sti2, itr, _ = _get(f"{base}/iterate")
                self.assertEqual(sti2, 200)
                self.assertNotIn("view you picked per wave", itr)
                self.assertIn("/waves", itr)
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()


if __name__ == "__main__":
    unittest.main()
