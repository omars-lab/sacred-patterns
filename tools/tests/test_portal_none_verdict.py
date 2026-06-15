"""Regression: the build portal must not crash when a wave's owner_verdict is null.

Plain-English symptom (2026-06-14): opening the "watching it get built" page
(`/iterate`) returned an empty body / connection reset. The cause was a wave in
`session.json -> stage_gates.structure.waves_passed` whose `owner_verdict` was an
explicit `null` (which is exactly what the re-gate stamp writes before the owner
judges the wave). The page code read `gate.get("owner_verdict", {}).get("state")`
— the `{}` default only applies when the KEY IS ABSENT, so an explicit `None`
slipped through and `None.get("state")` raised AttributeError, taking the whole
request down.

This test stamps a session with a null-verdict passed wave, serves `/iterate`,
and asserts a 200 with a real body. The witness that found the bug (a wave stamped
with `owner_verdict: None`) lives here so a future refactor of the portal can't
silently reintroduce the crash (Tenet 18).
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
SERVER = TOOLS_DIR / "wave-plan-server.py"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _min_wave_plan() -> dict:
    # Two waves: wave 1 passed (with a null owner_verdict — the crash trigger),
    # wave 2 unbuilt (the "building now" card).
    return {
        "waves": [
            {"wave": 1, "color": "deep_navy", "where": "in the centre",
             "real_shape_count": 10, "shapes": []},
            {"wave": 2, "color": "navy", "where": "at the outer edge",
             "real_shape_count": 20, "shapes": []},
        ]
    }


def _session_with_null_verdict(root: Path) -> None:
    (root / "input").mkdir(parents=True, exist_ok=True)
    plan_dir = root / "input" / "reference-analysis" / "wave-plan"
    plan_dir.mkdir(parents=True, exist_ok=True)
    (plan_dir / "wave-plan.json").write_text(json.dumps(_min_wave_plan()))
    # The wave-N.png the "building now"/"coming up" cards reference.
    for n in (1, 2):
        (plan_dir / f"wave-{n}.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    # Pre-create wave-plan.html so the server SKIPS the startup regen() (which
    # shells out to plan-waves.py and needs a real reference.jpg we don't have).
    # The crash under test is in the /iterate page render, not the plan build.
    (plan_dir / "wave-plan.html").write_text("<html><body>stub plan</body></html>")
    # iterations/1/ must exist: the page scans it for this wave's gate picture
    # (latest_gate_sbs) before it reaches the owner_verdict read under test.
    (root / "iterations" / "1").mkdir(parents=True, exist_ok=True)
    session = {
        "stage_gates": {
            "structure": {
                "approved": None,
                "waves_passed": {
                    # The exact stamp shape that crashed the page: owner_verdict null.
                    "1": {"iter": 1, "coverage": 1.0, "iou": None,
                          "owner_verdict": None},
                },
            }
        }
    }
    (root / "session.json").write_text(json.dumps(session, indent=2))


class PortalNullVerdictDoesNotCrash(unittest.TestCase):
    def test_iterate_serves_200_with_null_owner_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _session_with_null_verdict(root)
            port = _free_port()
            proc = subprocess.Popen(
                [sys.executable, str(SERVER), str(root),
                 "--center", "386", "361", "--diameter", "738",
                 "--port", str(port)],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
            try:
                url = f"http://127.0.0.1:{port}/iterate"
                body, status = "", None
                deadline = time.time() + 10
                last_err: Exception | None = None
                while time.time() < deadline:
                    try:
                        with urllib.request.urlopen(url, timeout=2) as r:
                            status = r.status
                            body = r.read().decode("utf-8", "replace")
                        break
                    except Exception as e:  # server not up yet / mid-crash
                        last_err = e
                        time.sleep(0.25)
                self.assertEqual(status, 200,
                                 f"/iterate did not return 200 (last err: {last_err})")
                # A crash produced an empty body; a healthy page has the heading
                # and the built-wave badge for the null-verdict wave.
                self.assertIn("Watching it get built", body)
                self.assertIn("Wave 1", body)
                self.assertIn("built", body)
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()


if __name__ == "__main__":
    unittest.main()
