"""portal-handoff.py failure paths + the cross-repo contract witness.

The handoff is the seam between repos: sacred-patterns trusts the
review-verdict.json that `qiyas review-replay --emit hypothesis` writes. The
cheap tests here exercise the handoff CLI's guard rails with no qiyas at all
(missing render; missing qiyas binary with the QIYAS_CMD hint). The end-to-end
test runs the REAL qiyas emitter against its own checked-in fixture and asserts
the verdict carries every field the sacred-patterns side reads — skipped when
the qiyas repo or uv is unavailable, so `make tool-tests` stays runnable
anywhere.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
HANDOFF_CLI = TOOLS_DIR / "portal-handoff.py"

QIYAS_REPO = Path(os.environ.get("QIYAS_REPO", str(Path.home() / "Workspace/git/qiyas")))
QIYAS_FIXTURE = QIYAS_REPO / "tests/fixtures/review-annotations/replay-mixed.json"


def run_handoff(session: Path, n: int, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    merged = dict(os.environ)
    if env:
        merged.update(env)
    return subprocess.run(
        [sys.executable, str(HANDOFF_CLI), str(session), str(n)],
        capture_output=True,
        text=True,
        check=False,
        env=merged,
    )


class HandoffGuardRails(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.session = Path(self._tmp.name)

    def test_missing_render_dies_with_path(self) -> None:
        proc = run_handoff(self.session, 3)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("render not found", proc.stderr)

    def test_missing_qiyas_binary_hints_qiyas_cmd(self) -> None:
        iter_dir = self.session / "iterations" / "3"
        iter_dir.mkdir(parents=True)
        (iter_dir / "render.svg").write_text("<svg/>", encoding="utf-8")
        proc = run_handoff(self.session, 3, env={"QIYAS_CMD": "definitely-not-a-real-binary"})
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("QIYAS_CMD", proc.stderr)


@unittest.skipUnless(
    shutil.which("uv") is not None and QIYAS_FIXTURE.is_file(),
    "qiyas repo + uv required (set QIYAS_REPO to override the default location)",
)
class CrossRepoContractWitness(unittest.TestCase):
    """The real qiyas emitter must produce what portal_verdict + seed-hypothesis read."""

    def test_review_replay_emits_the_contract_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            proc = subprocess.run(
                [
                    "uv", "run", "--project", str(QIYAS_REPO), "qiyas",
                    "review-replay", str(QIYAS_FIXTURE),
                    "--emit", "hypothesis", "--output-dir", str(out_dir),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            verdict_file = out_dir / "review-verdict.json"
            self.assertTrue(verdict_file.is_file(), "review-replay did not write the verdict")
            verdict = json.loads(verdict_file.read_text(encoding="utf-8"))

        # Every key the sacred-patterns side reads (portal_verdict predicate +
        # seed-hypothesis renderer). A rename in qiyas breaks here first.
        self.assertEqual(verdict["schema_version"], 1)
        self.assertEqual(verdict["artifact_kind"], "qiyas-review-verdict")
        self.assertTrue(verdict["verdict_recorded"])
        self.assertFalse(verdict["review_passed"])  # fixture has wrong marks
        for key in ("image_path", "image_sha256", "verdict_counts", "gaps", "hypothesis_seed"):
            self.assertIn(key, verdict)
        self.assertEqual(len(verdict["image_sha256"]), 64)
        counts = verdict["verdict_counts"]
        for key in ("right", "wrong", "unsure"):
            self.assertIsInstance(counts[key], int)
        gaps = verdict["gaps"]
        self.assertGreater(len(gaps), 0)
        for gap in gaps:
            for key in ("annotation_id", "kind", "rank", "question", "gap_sentence"):
                self.assertIn(key, gap)
        self.assertEqual(
            [g["rank"] for g in gaps], sorted(g["rank"] for g in gaps),
            "gaps must arrive structure-first (sorted by rank)",
        )
        seed = verdict["hypothesis_seed"]
        self.assertEqual(seed["gap_targeted"], gaps[0]["gap_sentence"])


if __name__ == "__main__":
    unittest.main()
