"""Truth table for the portal_verdict binding predicate.

The loop's terminal check (docs/decisions/2026-06-07-loop-terminal-condition.md,
ACCEPTED Option C) hinges on `portal_verdict_recorded(session_dir, n)`: a verdict
only counts when it exists, parses, sha-binds to the current render bytes, and
says the reviewer actually recorded something. Each test is one row of that
truth table with a canned verdict in a tmp dir — no qiyas needed.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

import portal_verdict  # noqa: E402


def make_verdict(image_sha256: str, *, recorded: bool = True, passed: bool = False) -> dict:
    """A minimal schema-v1 review-verdict payload (mirrors qiyas verdict.py)."""
    return {
        "schema_version": 1,
        "artifact_kind": "qiyas-review-verdict",
        "annotations_schema_version": 3,
        "image_path": "/tmp/render.svg",
        "image_sha256": image_sha256,
        "captured_at": "2026-06-09T00:00:00+00:00",
        "qiyas_version": "0.0.0-test",
        "verdict_counts": {"right": 1, "wrong": 0 if passed else 2, "unsure": 0},
        "verdict_recorded": recorded,
        "review_passed": passed,
        "gaps": [],
        "pixel": None,
        "hypothesis_seed": None,
    }


class PortalVerdictTruthTable(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.session = Path(self._tmp.name)
        self.iter_dir = self.session / "iterations" / "3"
        self.iter_dir.mkdir(parents=True)
        self.render = self.iter_dir / "render.svg"
        self.render.write_text("<svg>iteration three</svg>", encoding="utf-8")
        self.render_sha = portal_verdict.sha256_of(self.render)

    def write_verdict(self, payload: object) -> None:
        (self.iter_dir / "review-verdict.json").write_text(
            payload if isinstance(payload, str) else json.dumps(payload),
            encoding="utf-8",
        )

    def test_missing_verdict_file_is_not_recorded(self) -> None:
        self.assertFalse(portal_verdict.portal_verdict_recorded(self.session, 3))

    def test_corrupt_json_is_not_recorded_and_does_not_raise(self) -> None:
        self.write_verdict("{not json")
        self.assertIsNone(portal_verdict.read_verdict(self.iter_dir / "review-verdict.json"))
        self.assertFalse(portal_verdict.portal_verdict_recorded(self.session, 3))

    def test_non_dict_json_is_not_recorded(self) -> None:
        self.write_verdict('["a", "list"]')
        self.assertFalse(portal_verdict.portal_verdict_recorded(self.session, 3))

    def test_sha_mismatch_is_stale_not_recorded(self) -> None:
        self.write_verdict(make_verdict("0" * 64))
        self.assertFalse(portal_verdict.portal_verdict_recorded(self.session, 3))

    def test_rerendered_iteration_self_invalidates(self) -> None:
        # The binding's whole point: a verdict recorded against yesterday's
        # bytes stops counting the moment the render changes.
        self.write_verdict(make_verdict(self.render_sha))
        self.assertTrue(portal_verdict.portal_verdict_recorded(self.session, 3))
        self.render.write_text("<svg>regenerated</svg>", encoding="utf-8")
        self.assertFalse(portal_verdict.portal_verdict_recorded(self.session, 3))

    def test_verdict_recorded_false_is_not_recorded(self) -> None:
        self.write_verdict(make_verdict(self.render_sha, recorded=False))
        self.assertFalse(portal_verdict.portal_verdict_recorded(self.session, 3))

    def test_missing_render_is_not_recorded(self) -> None:
        self.write_verdict(make_verdict(self.render_sha))
        self.render.unlink()
        self.assertFalse(portal_verdict.portal_verdict_recorded(self.session, 3))

    def test_happy_path_is_recorded(self) -> None:
        self.write_verdict(make_verdict(self.render_sha))
        self.assertTrue(portal_verdict.portal_verdict_recorded(self.session, 3))

    def test_review_passed_requires_valid_verdict_and_pass(self) -> None:
        self.write_verdict(make_verdict(self.render_sha, passed=False))
        self.assertFalse(portal_verdict.review_passed(self.session, 3))
        self.write_verdict(make_verdict(self.render_sha, passed=True))
        self.assertTrue(portal_verdict.review_passed(self.session, 3))

    def test_review_passed_false_when_verdict_stale(self) -> None:
        self.write_verdict(make_verdict("0" * 64, passed=True))
        self.assertFalse(portal_verdict.review_passed(self.session, 3))


if __name__ == "__main__":
    unittest.main()
