"""Regression: the weave studio is shareable — every knob round-trips via the URL.

Plain-English purpose (2026-06-17): the owner asked "add url param supprot for
all knobs" so a render can be shared/bookmarked by link. Two things must hold,
and both had a real failure mode this test pins:

  1. `/weave-studio?style=field&...` must serve 200. The GET router originally
     did an EXACT `self.path == "/weave-studio"` match, so ANY query string
     404'd — which is the entire point of the feature (a shared link always
     carries `?...`). The fix matches path-only (`split("?", 1)[0]`).
  2. The page ships the client-side URL plumbing — `loadFromURL` (read params
     into state on init), `syncURL` (write state back to the address bar on
     every change), `syncControlsFromState` (mirror loaded params onto the
     dials), and the `URL_KEYS` map that enumerates every knob. Without these
     the link is inert.

Witness frozen per Tenet 18 — the throwaway-port curl probes that confirmed the
feature (bare studio 200, studio?params 200, the four JS symbols present) live
here so a future router refactor can't silently reintroduce the 404 or drop the
plumbing.
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


def _make_session(root: Path) -> None:
    # Minimal session: the /weave-studio route reads session().stage_gates.weave
    # for the approved flag; nothing else is needed to render the page shell.
    (root / "input").mkdir(parents=True, exist_ok=True)
    plan_dir = root / "input" / "reference-analysis" / "wave-plan"
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / "wave-plan.json").write_text(json.dumps({"waves": []}))
    (plan_dir / "wave-plan.html").write_text("<html><body>stub</body></html>")
    session = {
        "stage_gates": {
            "weave": {"approved": False, "verdicts": [], "note": ""},
        }
    }
    (root / "session.json").write_text(json.dumps(session, indent=2))


def _get(url: str) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""


class StudioUrlParams(unittest.TestCase):
    def test_studio_serves_with_query_and_ships_url_plumbing(self) -> None:
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
                        _get(f"{base}/weave-studio")
                        break
                    except Exception:
                        time.sleep(0.25)

                # 1. Bare studio: 200, with the URL plumbing.
                st, body = _get(f"{base}/weave-studio")
                self.assertEqual(st, 200, "bare /weave-studio must serve 200")
                for sym in ("loadFromURL", "syncURL", "syncControlsFromState",
                            "URL_KEYS"):
                    self.assertIn(sym, body, f"missing URL-param JS: {sym}")

                # 2. The shared-link case: a query string carrying every knob
                #    must STILL serve 200 (the exact-match 404 regression).
                qs = ("style=field&width=12&color=%23F2EEE6&step=3&shadow=40"
                      "&network=1&field_angle=50&field_ray=18"
                      "&field_wave_lo=14&field_wave_hi=20&rings=center,outer")
                st2, _ = _get(f"{base}/weave-studio?{qs}")
                self.assertEqual(st2, 200,
                                 "/weave-studio?<knobs> must serve 200 (not 404)")

                # 3. Every knob this feature claims to support is named in the
                #    URL_KEYS map (guards a knob silently dropping out of the map).
                for key in ("style", "width", "color", "step", "shadow",
                            "network", "field_angle", "field_ray",
                            "field_wave_lo", "field_wave_hi", "rings"):
                    self.assertIn(f"{key}:", body,
                                  f"knob {key} not wired into URL_KEYS")
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()


if __name__ == "__main__":
    unittest.main()
