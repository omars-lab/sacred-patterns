"""Truth table for wave-feedback's denied-wave reader.

The loop consumes the owner's per-wave verdicts (session.json
waves_passed[<n>].owner_verdict) BEFORE advancing construction — a "Needs
work" verdict is the decisive steering signal (Tenets 24/25/27). This test
pins the contract wave-feedback.py exposes to the loop: which waves count as
denied, the newest-first ordering, the exit-code branch signal (2 = work to
do, 0 = clean), and that approved/un-judged waves are never reported.

Witness this codifies (Tenet 18): the 2026-06-12 portal feedback-panel
shipment, where Deny+comment was defined as a fix request the loop must pick
up. No qiyas needed — canned session.json in a tmp dir.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location("wave_feedback", TOOLS_DIR / "wave-feedback.py")
wave_feedback = importlib.util.module_from_spec(_spec)
sys.modules["wave_feedback"] = wave_feedback
_spec.loader.exec_module(wave_feedback)


def session_with(verdicts: dict[str, dict]) -> dict:
    """A session.json skeleton whose waves_passed carries the given verdicts.

    `verdicts` maps wave-string -> owner_verdict dict (or omit the key for an
    un-judged wave). Every wave gets a plausible iter so iter passthrough is
    exercised.
    """
    waves: dict[str, dict] = {}
    for w in ("1", "3", "7"):
        entry = {"iter": 70, "coverage": 0.9, "iou": 0.8}
        if w in verdicts:
            entry["owner_verdict"] = verdicts[w]
        waves[w] = entry
    return {"stage_gates": {"structure": {"waves_passed": waves}}}


class DeniedWaves(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def write(self, session: dict) -> Path:
        p = self.dir / "session.json"
        p.write_text(json.dumps(session))
        return p

    def test_no_verdicts_is_clean(self) -> None:
        p = self.write(session_with({}))
        self.assertEqual(wave_feedback.denied_waves(p), [])

    def test_approved_waves_are_not_denied(self) -> None:
        p = self.write(session_with({
            "1": {"state": "approved", "note": "", "date": "2026-06-12"},
            "7": {"state": "approved", "note": "looks great", "date": "2026-06-12"},
        }))
        self.assertEqual(wave_feedback.denied_waves(p), [])

    def test_denied_wave_is_reported_with_its_note(self) -> None:
        p = self.write(session_with({
            "7": {"state": "denied",
                  "note": "the center star is rotated 18deg too far",
                  "date": "2026-06-12"},
        }))
        denied = wave_feedback.denied_waves(p)
        self.assertEqual(len(denied), 1)
        self.assertEqual(denied[0]["wave"], 7)
        self.assertEqual(denied[0]["note"], "the center star is rotated 18deg too far")
        self.assertEqual(denied[0]["iter"], 70)

    def test_newest_verdict_first(self) -> None:
        p = self.write(session_with({
            "7": {"state": "denied", "note": "older", "date": "2026-06-12"},
            "3": {"state": "denied", "note": "newer", "date": "2026-06-13"},
        }))
        denied = wave_feedback.denied_waves(p)
        self.assertEqual([d["wave"] for d in denied], [3, 7])

    def test_mixed_state_only_denied_surface(self) -> None:
        p = self.write(session_with({
            "1": {"state": "approved", "note": "", "date": "2026-06-12"},
            "3": {"state": "denied", "note": "fix this", "date": "2026-06-13"},
            # wave 7 left un-judged
        }))
        denied = wave_feedback.denied_waves(p)
        self.assertEqual([d["wave"] for d in denied], [3])

    def test_note_is_stripped(self) -> None:
        p = self.write(session_with({
            "3": {"state": "denied", "note": "  spaces around  ", "date": "2026-06-13"},
        }))
        self.assertEqual(wave_feedback.denied_waves(p)[0]["note"], "spaces around")


class ExitCodes(unittest.TestCase):
    """The exit code IS the loop's branch signal: 2 = owner-requested work."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_main(self, argv: list[str]) -> int:
        old = sys.argv
        sys.argv = ["wave-feedback.py"] + argv
        try:
            return wave_feedback.main()
        finally:
            sys.argv = old

    def test_exit_2_when_denied(self) -> None:
        (self.dir / "session.json").write_text(json.dumps(session_with({
            "7": {"state": "denied", "note": "x", "date": "2026-06-12"},
        })))
        self.assertEqual(self.run_main([str(self.dir), "--quiet"]), 2)

    def test_exit_0_when_clean(self) -> None:
        (self.dir / "session.json").write_text(json.dumps(session_with({
            "7": {"state": "approved", "note": "", "date": "2026-06-12"},
        })))
        self.assertEqual(self.run_main([str(self.dir), "--quiet"]), 0)

    def test_exit_1_when_no_session(self) -> None:
        self.assertEqual(self.run_main([str(self.dir / "missing"), "--quiet"]), 1)


if __name__ == "__main__":
    unittest.main()
