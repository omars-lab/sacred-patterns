#!/usr/bin/env python3
"""portal-handoff.py — pull the expert's portal review into the iteration dir.

After someone reviews `iterations/N/render.svg` in the qiyas review portal,
their marks live in a qiyas-owned session directory whose name embeds a path
hash we cannot (and should not) predict. This tool closes the gap: it asks
qiyas where the session lives (`qiyas review-path`), tells qiyas to emit the
machine verdict (`qiyas review-replay --emit hypothesis`), and lands
`review-verdict.json` in `iterations/N/` — exactly where the loop's
`portal_verdict_recorded` terminal check (and `tools/seed-hypothesis.py`)
look for it.

Usage:
    ./tools/portal-handoff.py SESSION_DIR N

    SESSION_DIR  the deconstruction session root (contains iterations/)
    N            the iteration number whose render was reviewed

If no review session exists yet, this fails with the exact `qiyas review`
command to run first. After emitting, it verifies the verdict's image_sha256
against the render's actual bytes — a mismatch means the render was
regenerated after the review (the verdict is stale) and is a hard error.

qiyas invocation: uses `qiyas` from PATH by default; set QIYAS_CMD to
override (e.g. QIYAS_CMD="uv run --project ~/Workspace/git/qiyas qiyas").

Dropbox caveat: ~/Dropbox is a symlink to ~/Library/CloudStorage/... — the
two spellings hash to different qiyas session slugs. We resolve the render
path once and try both the resolved and as-given spellings before erroring.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

import portal_verdict


def die(msg: str, exit_code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(exit_code)


def qiyas_cmd() -> list[str]:
    """The qiyas CLI invocation, overridable via QIYAS_CMD."""
    return shlex.split(os.environ.get("QIYAS_CMD", "qiyas"))


def run_qiyas(args: list[str]) -> subprocess.CompletedProcess[str]:
    cmd = qiyas_cmd() + args
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        die(
            f"qiyas CLI not found ({cmd[0]!r}). Install it on PATH or set "
            'QIYAS_CMD, e.g. QIYAS_CMD="uv run --project ~/Workspace/git/qiyas qiyas"'
        )
        raise AssertionError("unreachable")


def review_path_lookup(image: Path) -> dict | None:
    """Ask qiyas where IMAGE's review session lives; None when qiyas fails."""
    proc = run_qiyas(["review-path", str(image)])
    if proc.returncode != 0:
        print(proc.stderr.strip(), file=sys.stderr)
        return None
    try:
        payload = json.loads(proc.stdout)
    except ValueError:
        return None
    return payload if isinstance(payload, dict) else None


def find_annotations(render_given: Path, render_resolved: Path) -> Path | None:
    """Locate the session's annotations.json, trying both path spellings.

    The resolved spelling is canonical (the portal launcher resolves too);
    the as-given spelling covers sessions recorded before that rule, or a
    review launched through the ~/Dropbox symlink.
    """
    candidates = [render_resolved]
    if render_given != render_resolved:
        candidates.append(render_given)
    for candidate in candidates:
        payload = review_path_lookup(candidate)
        if payload is not None and payload.get("exists"):
            return Path(str(payload["annotations_path"]))
    return None


def main() -> int:
    p = argparse.ArgumentParser(
        description="Land iterations/N/review-verdict.json from the qiyas review session."
    )
    p.add_argument("session_dir", help="Deconstruction session root (contains iterations/)")
    p.add_argument("n", type=int, help="Iteration number whose render was reviewed")
    args = p.parse_args()

    session_dir = Path(args.session_dir)
    render_given = portal_verdict.render_path(session_dir, args.n)
    if not render_given.is_file():
        die(f"render not found: {render_given}")
    render = render_given.resolve()

    annotations = find_annotations(render_given, render)
    if annotations is None:
        die(
            "no review session found for this render. Run the portal review first:\n"
            f"  qiyas review {render} --against {session_dir.resolve()}/input/reference.jpg"
        )

    iteration_dir = render.parent
    proc = run_qiyas(
        [
            "review-replay",
            str(annotations),
            "--emit",
            "hypothesis",
            "--output-dir",
            str(iteration_dir),
        ]
    )
    if proc.returncode != 0:
        print(proc.stdout, end="")
        print(proc.stderr, end="", file=sys.stderr)
        die(f"qiyas review-replay failed (exit {proc.returncode})")

    verdict_file = portal_verdict.verdict_path(session_dir, args.n)
    verdict = portal_verdict.read_verdict(verdict_file)
    if verdict is None:
        die(f"review-replay reported success but {verdict_file} is missing/unreadable")

    render_sha = portal_verdict.sha256_of(render)
    verdict_sha = str(verdict.get("image_sha256", ""))
    if verdict_sha != render_sha:
        # One-glance stale diagnosis: both digests + when the render changed.
        die(
            "verdict is STALE — the render was regenerated after the review.\n"
            f"  render sha256:  {render_sha}\n"
            f"  verdict sha256: {verdict_sha}\n"
            f"  render mtime:   {render.stat().st_mtime}\n"
            "Re-run the portal review against the current render, then re-run this handoff."
        )

    counts = verdict.get("verdict_counts", {})
    print(f"wrote {verdict_file}")
    print(
        f"verdict: recorded={verdict.get('verdict_recorded')} "
        f"passed={verdict.get('review_passed')} "
        f"(right={counts.get('right')} wrong={counts.get('wrong')} "
        f"unsure={counts.get('unsure')}); {len(verdict.get('gaps', []))} gap(s)"
    )
    if verdict.get("review_passed") is not True:
        print(f"next: ./tools/seed-hypothesis.py {session_dir} {args.n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
