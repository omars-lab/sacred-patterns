"""The rollup's validate-svg.log reader must actually read validate-svg.log.

Discovered 2026-07-31 by an audit for the "parse structurally, fail closed"
rule. `parse_validate_log` matched its lines with

    re.match(r"^[✓✗xX*✓✗].*?([A-Za-z][A-Za-z0-9 _-]+)$", stripped)

under a bare `if m:` with no else. `tools/validate-svg.sh` emits no `✓` or `✗`
anywhere — its three per-check emitters are

    pass() { echo -e "  ${GREEN}PASS${NC} $1"; }
    fail() { echo -e "  ${RED}FAIL${NC} $1"; ERRORS=$((ERRORS + 1)); }
    warn() { echo -e "  ${YELLOW}WARN${NC} $1"; }

so every real line starts with an ANSI escape that `str.strip()` does not
remove. The reader matched **nothing its producer has ever written**, returned
`{}` on every run since it was written, and nothing raised, warned, or logged.
That is the whole argument for failing closed: a silent skip is
indistinguishable from a pass, so a completely dead reader survived inside a
validation tool without anyone noticing.

The blast radius was small — `compute_overall` takes its verdict from
`validate_exit`, the exit code, not from `checks`, and nothing outside this file
reads `.checks`. That is worth stating plainly and it does not weaken the
witness. The defect was invisible *because* it was silent, not because it was
harmless.

The first test below is the witness: it feeds the exact bytes `validate-svg.sh`
writes and fails against the old reader. Run: make tool-tests
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

_MODULE_PATH = Path(__file__).resolve().parents[1] / "iteration-validate-rollup.py"
_spec = importlib.util.spec_from_file_location("iteration_validate_rollup", _MODULE_PATH)
assert _spec and _spec.loader
rollup = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rollup)


GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[0;33m"
NC = "\033[0m"

# Byte-for-byte what `validate-svg.sh` writes for one file: the block header,
# the separator, three coloured check lines, the "Fix:" hint that follows a
# failure, and the per-file verdict. Reproduced here rather than shelling out so
# the test runs without bash and still goes red if the reader drifts.
REAL_LOG = "\n".join(
    [
        "",
        "Validating: recon.svg",
        "---",
        f"  {GREEN}PASS{NC} Contains xmlns attribute (browser-renderable)",
        f"  {RED}FAIL{NC} Missing viewBox (required)",
        '       Fix: sed -i \'\' \'s/<svg /<svg xmlns="http:\\/\\/www.w3.org\\/2000\\/svg" /\' recon.svg',
        f"  {YELLOW}WARN{NC} No title element",
        "",
        f"  {RED}INVALID{NC} — 1 issue(s) found",
        "",
        "================================",
        f"{RED}1 of 1 SVG file(s) invalid.{NC}",
        "",
    ]
)


class ParseValidateLog(unittest.TestCase):
    def _parse(self, text: str) -> dict:
        with TemporaryDirectory() as tmp:
            log = Path(tmp) / "validate-svg.log"
            log.write_text(text, encoding="utf-8")
            return rollup.parse_validate_log(log)

    def test_reads_the_lines_validate_svg_actually_emits(self):
        """The witness. Against the pre-fix reader every assertion here fails."""
        result = self._parse(REAL_LOG)

        self.assertEqual(
            result["checks"],
            {
                "Contains xmlns attribute (browser-renderable)": "PASS",
                "Missing viewBox (required)": "FAIL",
                "No title element": "WARN",
            },
        )
        self.assertNotIn("parse_error", result)

    def test_does_not_mistake_prose_for_a_check(self):
        """The block header, the separator, the Fix hint and the two summary
        lines are all prose. Only the closed status vocabulary counts."""
        checks = self._parse(REAL_LOG)["checks"]

        for label in checks:
            self.assertNotIn("Validating", label)
            self.assertNotIn("Fix:", label)
        # `VALID`/`INVALID` are file verdicts, not checks, and they are coloured
        # exactly like one — which is why membership in the vocabulary, rather
        # than "looks like a status word", is the test.
        self.assertEqual(len(checks), 3)

    def test_a_log_it_cannot_read_is_an_error_not_an_empty_dict(self):
        """Fail closed. This is the assertion the original defect could never
        have satisfied: it returned `{}` and said nothing."""
        drifted = "\n".join(
            [
                "Validating: recon.svg",
                "---",
                "  [ok] Contains xmlns attribute",
                "  [!!] Missing viewBox",
            ]
        )
        result = self._parse(drifted)

        self.assertEqual(result["checks"], {})
        self.assertIn("parse_error", result)
        self.assertIn("drifted", result["parse_error"])

    def test_an_empty_or_absent_log_is_not_an_error(self):
        """No validation block means the tool did not run — which the exit code
        already reports. Blocking twice on one fact is noise, not rigour."""
        self.assertNotIn("parse_error", self._parse(""))

        with TemporaryDirectory() as tmp:
            missing = Path(tmp) / "nope.log"
            self.assertEqual(
                rollup.parse_validate_log(missing), {"checks": {}, "stdout": ""}
            )

    def test_a_multi_file_log_is_an_error_rather_than_last_write_wins(self):
        """`validate-svg.sh` accepts a directory and repeats check names per
        file; the schema is a flat label→status map. Silently keeping the last
        one would be this function's original defect in miniature."""
        two_files = "\n".join(
            [
                "Validating: a.svg",
                f"  {GREEN}PASS{NC} Contains xmlns attribute",
                "Validating: b.svg",
                f"  {RED}FAIL{NC} Contains xmlns attribute",
            ]
        )
        result = self._parse(two_files)

        self.assertIn("parse_error", result)
        self.assertIn("Contains xmlns attribute", result["parse_error"])


class ComputeOverallBlocksOnParseError(unittest.TestCase):
    """A parse_error nobody acts on is the same silence in a new field."""

    def _overall(self, validate_svg: dict) -> dict:
        return rollup.compute_overall(
            validate_exit=0,
            validate_svg=validate_svg,
            svg_audit={"available": False},
            diff_traced={"available": False},
            diff_jpg={"available": False},
            qiyas={"available": False},
            qiyas_score={"available": False},
            has_baseline=False,
        )

    def test_a_drifted_reader_is_a_blocking_issue(self):
        blocking = self._overall({"checks": {}, "parse_error": "reader drifted"})[
            "blocking_issues"
        ]
        self.assertIn("reader drifted", blocking)

    def test_a_clean_parse_adds_no_blocker_of_its_own(self):
        blocking = self._overall({"checks": {"Has xmlns": "PASS"}})["blocking_issues"]
        # The `qiyas score unavailable` blocker still fires — that one is real
        # and pre-existing. What must not appear is a second, invented one.
        self.assertEqual([b for b in blocking if "reader" in b or "drift" in b], [])


if __name__ == "__main__":
    unittest.main()
