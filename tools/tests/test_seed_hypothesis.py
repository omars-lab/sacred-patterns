"""seed-hypothesis.py contract: machine fields filled, judgment fields TODO.

The deterministic-seed-plus-agent-judgment split is only honest if the seed
never fabricates judgment: every field the iterate-construction-hypothesis
skill requires a routing decision for must carry a literal `TODO(judgment)`
marker, while the machine-knowable half (attempt number, top-ranked gap with
its annotation id, evidence trail) is pre-filled from review-verdict.json.
These tests run the real CLI via subprocess with `--date` pinned for
byte-determinism.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
SEED_CLI = TOOLS_DIR / "seed-hypothesis.py"


def make_verdict_with_gaps() -> dict:
    """A failing review with two ranked gaps — structural first (rank 0 < 1)."""
    gaps = [
        {
            "annotation_id": "q1-S001",
            "kind": "structural_mismatch",
            "rank": 0,
            "question": "Q1",
            "gap_sentence": "A structural element differs from the reference. "
            "Reviewer: outer strapwork band density is half the reference.",
            "target": {"shape_id": "S001"},
            "expected": {},
            "note": "outer strapwork band density is half the reference",
            "root_cause_step": None,
            "root_cause_field": None,
        },
        {
            "annotation_id": "q7-S009",
            "kind": "color_wrong",
            "rank": 2,
            "question": "Q7",
            "gap_sentence": "A region's colour does not match the reference.",
            "target": {"shape_id": "S009"},
            "expected": {"color": "#1B6CA8"},
            "note": "",
            "root_cause_step": None,
            "root_cause_field": None,
        },
    ]
    return {
        "schema_version": 1,
        "artifact_kind": "qiyas-review-verdict",
        "annotations_schema_version": 3,
        "image_path": "/tmp/render.svg",
        "image_sha256": "f" * 64,
        "captured_at": "2026-06-09T00:00:00+00:00",
        "qiyas_version": "0.0.0-test",
        "verdict_counts": {"right": 1, "wrong": 2, "unsure": 0},
        "verdict_recorded": True,
        "review_passed": False,
        "gaps": gaps,
        "pixel": {
            "similarity_pct": 70.8,
            "shared_pct": 46.8,
            "warning_messages": ["Channel drift is uneven: r=84.6 vs b=62.6 (spread 22.0)."],
        },
        "hypothesis_seed": {
            "gap_targeted": "A structural element differs from the reference. "
            "Reviewer: outer strapwork band density is half the reference.",
            "predicted_lift_seed": "clear annotation q1-S001",
            "evidence": ["annotation q1-S001", "pixel-diff.json: similarity 70.8%"],
        },
    }


def run_seed(session: Path, n: int = 3, date: str = "2026-06-10") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SEED_CLI), str(session), str(n), "--date", date],
        capture_output=True,
        text=True,
        check=False,
    )


class SeedHypothesisTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.session = Path(self._tmp.name)
        iter_dir = self.session / "iterations" / "3"
        iter_dir.mkdir(parents=True)
        (iter_dir / "review-verdict.json").write_text(
            json.dumps(make_verdict_with_gaps()), encoding="utf-8"
        )

    def seed_path(self) -> Path:
        return self.session / "iterations" / "4" / "hypothesis-seed.md"

    def test_seed_machine_fields_filled_judgment_fields_todo(self) -> None:
        proc = run_seed(self.session)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        body = self.seed_path().read_text(encoding="utf-8")

        # Machine half: attempt, date, drafted gap citing gaps[0].annotation_id,
        # detector_untouched, evidence trail with every gap's annotation id.
        self.assertIn("attempt: 4", body)
        self.assertIn("date: 2026-06-10", body)
        self.assertIn("[annotation q1-S001]", body.split("\n---", 1)[0])
        self.assertIn(
            'detector_untouched: "confirmed — no qiyas param/threshold/cost', body
        )
        self.assertIn("[annotation q7-S009]", body)
        self.assertIn("pixel similarity: 70.8%", body)
        self.assertIn("Channel drift is uneven", body)

        # Judgment half: every routing field is a literal TODO marker, and the
        # Tenet-24 expected-visual prompt is present but unauthored.
        for field in (
            "construction_hypothesis",
            "bkr_change",
            "predicted_lift",
            "predicted_cost",
            "prior_art_searched",
            "related_memory",
        ):
            self.assertRegex(body, rf"{field}: \"TODO\(judgment\)")
        self.assertIn("Expected visual (write BEFORE viewing any render — Tenet 24)", body)

    def test_predicted_lift_carries_machine_seed(self) -> None:
        run_seed(self.session)
        body = self.seed_path().read_text(encoding="utf-8")
        self.assertIn("seed: clear annotation q1-S001", body)

    def test_seed_is_byte_deterministic_for_pinned_date(self) -> None:
        run_seed(self.session)
        first = self.seed_path().read_bytes()
        self.seed_path().unlink()
        run_seed(self.session)
        self.assertEqual(first, self.seed_path().read_bytes())

    def test_refuses_silent_overwrite(self) -> None:
        self.assertEqual(run_seed(self.session).returncode, 0)
        proc = run_seed(self.session)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("already exists", proc.stderr)

    def test_missing_verdict_points_at_portal_handoff(self) -> None:
        proc = run_seed(self.session, n=9)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("portal-handoff.py", proc.stderr)


if __name__ == "__main__":
    unittest.main()
