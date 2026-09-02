"""terminal_state truth table — the loop must never self-certify.

A metric-converged iteration is only "converged" when a sha-bound portal
verdict exists AND the reviewer passed it (decision
docs/decisions/2026-06-07-loop-terminal-condition.md, ACCEPTED Option C).
auto-iterate.py is a hyphenated CLI, so we load it via importlib and table
the extracted pure function directly.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

import portal_verdict  # noqa: E402

_spec = importlib.util.spec_from_file_location("auto_iterate", TOOLS_DIR / "auto-iterate.py")
assert _spec is not None and _spec.loader is not None
auto_iterate = importlib.util.module_from_spec(_spec)
# dataclasses resolves field types via sys.modules[cls.__module__] — register
# the module BEFORE exec or @dataclass blows up under file-location import.
sys.modules["auto_iterate"] = auto_iterate
_spec.loader.exec_module(auto_iterate)


def make_it(n: int = 3, go_no_go: str = "iterate") -> "auto_iterate.IterationResult":
    return auto_iterate.IterationResult(
        n=n,
        composite=0.81,
        structural="1.0",
        pixel=80.5,
        go_no_go=go_no_go,
        top_warning=None,
        blocking_issues=[],
        validation_path=Path("/dev/null"),
    )


class TerminalStateTruthTable(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.session = Path(self._tmp.name)
        self.iter_dir = self.session / "iterations" / "3"
        self.iter_dir.mkdir(parents=True)
        self.render = self.iter_dir / "render.svg"
        self.render.write_text("<svg>iter three</svg>", encoding="utf-8")

    def state(self, it, *, iter_count: int = 0, max_iterations: int = 30,
              window: list[float] | None = None,
              stagnation_window: int = 3, epsilon: float = 0.005) -> str:
        return auto_iterate.terminal_state(
            self.session, it,
            iter_count=iter_count, max_iterations=max_iterations,
            composite_window=window or [],
            stagnation_window=stagnation_window,
            stagnation_epsilon=epsilon,
        )

    def write_verdict(self, *, sha: str | None = None, recorded: bool = True,
                      passed: bool = True) -> None:
        payload = {
            "schema_version": 1,
            "artifact_kind": "qiyas-review-verdict",
            "image_sha256": sha if sha is not None else portal_verdict.sha256_of(self.render),
            "verdict_recorded": recorded,
            "review_passed": passed,
            "verdict_counts": {"right": 3, "wrong": 0 if passed else 2, "unsure": 0},
            "gaps": [],
        }
        (self.iter_dir / "review-verdict.json").write_text(
            json.dumps(payload), encoding="utf-8"
        )

    def test_metric_converged_without_verdict_awaits_portal_review(self) -> None:
        self.assertEqual(self.state(make_it(go_no_go="converged")), "awaiting-portal-review")

    def test_metric_converged_with_passing_verdict_is_converged(self) -> None:
        self.write_verdict(passed=True)
        self.assertEqual(self.state(make_it(go_no_go="converged")), "converged")

    def test_metric_converged_with_failing_verdict_keeps_iterating(self) -> None:
        # The reviewer's "wrong" marks ARE the next gap — not a terminal state.
        self.write_verdict(passed=False)
        self.assertEqual(self.state(make_it(go_no_go="converged")), "not-terminal")

    def test_stale_verdict_does_not_certify_convergence(self) -> None:
        self.write_verdict(sha="0" * 64, passed=True)
        self.assertEqual(self.state(make_it(go_no_go="converged")), "awaiting-portal-review")

    def test_budget_exhaustion(self) -> None:
        self.assertEqual(
            self.state(make_it(), iter_count=30, max_iterations=30), "handback-budget"
        )

    def test_stagnation_when_window_flat(self) -> None:
        self.assertEqual(
            self.state(make_it(), window=[0.80, 0.801, 0.8005]), "handback-stagnation"
        )

    def test_moving_composite_is_not_terminal(self) -> None:
        self.assertEqual(self.state(make_it(), window=[0.70, 0.75, 0.80]), "not-terminal")

    def test_portal_gap_pending_only_for_recorded_failing_verdict(self) -> None:
        self.assertFalse(auto_iterate.portal_gap_pending(self.session, 3))
        self.write_verdict(passed=False)
        self.assertTrue(auto_iterate.portal_gap_pending(self.session, 3))
        self.write_verdict(passed=True)
        self.assertFalse(auto_iterate.portal_gap_pending(self.session, 3))


if __name__ == "__main__":
    unittest.main()
