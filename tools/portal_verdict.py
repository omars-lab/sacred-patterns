#!/usr/bin/env python3
"""portal_verdict.py — read qiyas review-verdict.json and decide "was this iteration reviewed?".

When the art expert reviews a render in the qiyas portal, `tools/portal-handoff.py`
lands a machine-readable `review-verdict.json` in that iteration's directory. This
module is the single place that answers "does iteration N carry a valid portal
verdict?" — the `portal_verdict_recorded` conjunct of the loop's terminal
condition (docs/decisions/2026-06-07-loop-terminal-condition.md, ACCEPTED
Option C). Both the handoff CLI and `tools/auto-iterate.py` import it; tests
live in `tools/tests/`.

The binding predicate (no qiyas session slugs cross this seam):

    portal_verdict_recorded(session_dir, N) :=
        iterations/N/review-verdict.json exists (and parses)
        AND verdict.image_sha256 == sha256(iterations/N/render.svg)
        AND verdict.verdict_recorded

The sha binding makes stale verdicts self-invalidating: re-render the
iteration and yesterday's verdict no longer counts.

Underscore filename on purpose: sibling tools are hyphenated CLIs, but this
one is a library — `python tools/portal-handoff.py` imports it as
`import portal_verdict` (script dir is on sys.path), and tests do the same.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


def render_path(session_dir: Path, n: int) -> Path:
    """`iterations/<n>/render.svg` under the session dir."""
    return session_dir / "iterations" / str(n) / "render.svg"


def verdict_path(session_dir: Path, n: int) -> Path:
    """`iterations/<n>/review-verdict.json` under the session dir."""
    return session_dir / "iterations" / str(n) / "review-verdict.json"


def sha256_of(path: Path) -> str:
    """Hex sha256 of a file's bytes — the verdict's binding key."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_verdict(path: Path) -> dict | None:
    """Tolerant read: missing / unparsable / non-dict → None.

    Fail-closed for the predicate (no verdict means not reviewed), but
    never an exception — a corrupt file must not crash the loop.
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return raw if isinstance(raw, dict) else None


def portal_verdict_recorded(session_dir: Path, n: int) -> bool:
    """True iff iteration N's render carries a sha-bound portal verdict."""
    verdict = read_verdict(verdict_path(session_dir, n))
    if verdict is None:
        return False
    render = render_path(session_dir, n)
    if not render.is_file():
        return False
    if verdict.get("image_sha256") != sha256_of(render):
        return False
    return verdict.get("verdict_recorded") is True


def review_passed(session_dir: Path, n: int) -> bool:
    """True iff a valid verdict exists AND the reviewer found nothing wrong."""
    if not portal_verdict_recorded(session_dir, n):
        return False
    verdict = read_verdict(verdict_path(session_dir, n))
    return verdict is not None and verdict.get("review_passed") is True
