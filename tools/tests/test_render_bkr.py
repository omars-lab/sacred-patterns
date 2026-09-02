"""render_bkr must load bikar's ESM dist — the witness for the require() break.

bikar's built core (packages/core/dist/index.js) became ESM-only with the
vite8 upgrade (bikar 6f3de50); render_bkr's old `require()` snippet raised
ERR_REQUIRE_ESM and the loop's render step died. This test runs the real
node + real bikar dist + a real Tier-0 pattern file (fixtures by reference:
bikar `patterns/Petal Tutorial/Petal-Blueprint.bkr`) so a future dist-format
change fails here, not mid-loop. Skips when the bikar checkout or node is
absent (CI without the sibling repo).
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))

_spec = importlib.util.spec_from_file_location("auto_iterate", TOOLS_DIR / "auto-iterate.py")
assert _spec is not None and _spec.loader is not None
auto_iterate = importlib.util.module_from_spec(_spec)
# dataclasses resolves field types via sys.modules[cls.__module__] — register
# the module BEFORE exec or @dataclass blows up under file-location import.
sys.modules["auto_iterate"] = auto_iterate
_spec.loader.exec_module(auto_iterate)

PETAL_BKR = auto_iterate.REPO_BIKAR / "patterns" / "Petal Tutorial" / "Petal-Blueprint.bkr"

HAVE_BIKAR = auto_iterate.COMPILE_DSL_JS.is_file() and PETAL_BKR.is_file()
HAVE_NODE = shutil.which("node") is not None


@unittest.skipUnless(HAVE_BIKAR and HAVE_NODE, "needs node + the sibling bikar checkout")
class RenderBkrEsmWitness(unittest.TestCase):
    def test_renders_tier0_pattern_through_esm_dist(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            svg_out = Path(td) / "out.svg"
            ok, log = auto_iterate.render_bkr(PETAL_BKR, svg_out)
            self.assertTrue(ok, f"render_bkr failed:\n{log}")
            self.assertNotIn("ERR_REQUIRE_ESM", log)
            svg = svg_out.read_text()
            self.assertIn("<svg", svg)

    def test_bad_source_reports_failure_not_silence(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            bad = Path(td) / "bad.bkr"
            bad.write_text("this is not a bikar pattern {{{")
            svg_out = Path(td) / "out.svg"
            ok, log = auto_iterate.render_bkr(bad, svg_out)
            self.assertFalse(ok)
            self.assertTrue(log.strip(), "failure must carry a diagnostic log")


if __name__ == "__main__":
    unittest.main()
