"""The guard that earns the `# nosemgrep` in tools/weave-only-compare.py.

semgrep's `dynamic-urllib-use-detected` fires on that file's
`urllib.request.urlopen(req)` because the URL originates in
`BIKAR_STUDIO_URL`. The concern is not stylistic: urllib dispatches on the
scheme, so `BIKAR_STUDIO_URL=file:///etc/passwd` would turn
`fetch_our_weave_svg` from an HTTP POST into a local-file read whose bytes the
tool then treats as "our weave SVG" and diffs against the owner's reference.

`_studio_url()` removes that by pinning the scheme at import time, and the
finding is suppressed on that basis. semgrep is syntactic and cannot see a
guard in another function, so it cannot re-check the claim — which makes the
suppression exactly the shape this repo names as a trap: *a fallback weaker
than the thing it falls back from*, used at the moment nothing else is
watching.

This file is what keeps the trade honest. Delete or weaken `_studio_url()` and
these go red inside the same `make local.ci` run that stopped flagging the
urlopen. The suppression cannot outlive its guard.
"""

from __future__ import annotations

import importlib.util
import os
import unittest
from pathlib import Path
from unittest import mock

TOOL = Path(__file__).resolve().parents[1] / "weave-only-compare.py"


def load_with_env(value: str | None):
    """Import weave-only-compare.py fresh under a given BIKAR_STUDIO_URL.

    The guard runs at module scope, so the only way to exercise it is to
    re-import — which is also the honest test, since that is when it fires in
    production.
    """
    env = dict(os.environ)
    env.pop("BIKAR_STUDIO_URL", None)
    if value is not None:
        env["BIKAR_STUDIO_URL"] = value
    with mock.patch.dict(os.environ, env, clear=True):
        spec = importlib.util.spec_from_file_location("_woc_under_test", TOOL)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


class StudioUrlSchemeGuard(unittest.TestCase):
    def test_file_scheme_is_rejected(self) -> None:
        """The exact attack the semgrep rule names."""
        with self.assertRaises(SystemExit) as cm:
            load_with_env("file:///etc/passwd")
        self.assertIn("http:// or https://", str(cm.exception))

    def test_other_urllib_schemes_are_rejected(self) -> None:
        """file:// is the one the rule names, not the only one urllib opens."""
        for bad in ("ftp://example.com", "data:text/plain,hello", "gopher://x"):
            with self.subTest(url=bad), self.assertRaises(SystemExit):
                load_with_env(bad)

    def test_schemeless_value_is_rejected_with_a_readable_message(self) -> None:
        """`localhost:8765` parses with scheme="localhost" and no netloc. Without
        the guard it fails later, deep in urlopen, reading like the studio is
        down rather than like a typo in the variable."""
        with self.assertRaises(SystemExit) as cm:
            load_with_env("localhost:8765")
        self.assertIn("BIKAR_STUDIO_URL", str(cm.exception))

    def test_http_and_https_are_accepted(self) -> None:
        self.assertEqual(load_with_env("http://localhost:8765").STUDIO_URL,
                         "http://localhost:8765")
        self.assertEqual(load_with_env("https://studio.example.com").STUDIO_URL,
                         "https://studio.example.com")

    def test_trailing_slash_is_normalised(self) -> None:
        """The call sites build `f"{STUDIO_URL}/api/preview-svg"`, so an origin
        with a trailing slash would request `//api/preview-svg`."""
        self.assertEqual(load_with_env("http://localhost:8765/").STUDIO_URL,
                         "http://localhost:8765")

    def test_default_is_local_http(self) -> None:
        self.assertEqual(load_with_env(None).STUDIO_URL, "http://localhost:8765")

    def test_the_suppression_names_this_file(self) -> None:
        """The `# nosemgrep` comment claims this test backs it. If the comment
        is rewritten to point somewhere else, or this file is renamed without
        updating it, the claim is stale and this fails — the same class of
        check as the pointer gates in the sibling repos."""
        src = TOOL.read_text()
        self.assertIn("nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected", src)
        self.assertIn(Path(__file__).name, src,
                      "the nosemgrep rationale must name this test file")


SERVER = Path(__file__).resolve().parents[1] / "wave-plan-server.py"


class ReferenceSquareFetchIsLoopback(unittest.TestCase):
    """The second `# nosemgrep` in this repo, on the same semgrep rule.

    wave-plan-server.py fetches its own `/reference-square.png` so the raster
    compare sees the proven endpoint's output rather than a second rendering
    path. semgrep flags it for the same reason it flagged weave-only-compare —
    a variable appears in the URL — but here the variable is a port number the
    process read off its own listening socket, and the scheme and host are
    literal. No int can make `file://`.

    That reasoning is only worth anything while it stays true of the code, and
    semgrep stops looking the moment the directive is there. These are what
    re-check it.
    """

    def setUp(self) -> None:
        self.src = SERVER.read_text()

    def test_scheme_and_host_are_literal(self) -> None:
        """The whole argument is that only the port is dynamic. If the literal
        prefix is ever replaced by a variable — a configurable host, a scheme
        read from a header — the suppression is asserting something false."""
        self.assertIn('f"http://127.0.0.1:{port}/reference-square.png"', self.src,
                      "the reference-square URL must keep its literal http://127.0.0.1 "
                      "prefix; if it became configurable, the nosemgrep above it is "
                      "suppressing a real finding")

    def test_the_port_comes_from_our_own_socket(self) -> None:
        """`server_address` is the bound socket, not user input. A port taken
        from a query parameter or an env var would be a different claim."""
        self.assertIn("port = self.server.server_address[1]", self.src,
                      "the port must come from this process's own listening socket")

    def test_no_other_urlopen_hides_behind_this_suppression(self) -> None:
        """A `# nosemgrep` covers the line below it, so a second urlopen added
        underneath would inherit a rationale written for a different call.
        One urlopen in this file, and it is the one the comment describes."""
        self.assertEqual(self.src.count("_urlreq.urlopen("), 1,
                         "a second urlopen appeared in wave-plan-server.py — the "
                         "nosemgrep rationale covers exactly one loopback fetch")

    def test_the_suppression_names_this_file(self) -> None:
        self.assertIn(
            "nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected",
            self.src)
        self.assertIn(Path(__file__).name, self.src,
                      "the nosemgrep rationale must name this test file")


if __name__ == "__main__":
    unittest.main()
