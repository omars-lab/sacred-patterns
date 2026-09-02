#!/usr/bin/env python3
"""Stop-hook: nudge to re-cut ALL wave gates when an iteration's render
changed but the portal's per-wave crops weren't regenerated.

Plain English: the portal shows one "ours beside yours" picture per passed
wave, each cut from some iteration's render. When a fix changes geometry
that more than one wave's crop sees (the center star inside the middle-
flower crops; the blueprint scaffolding; any whole-image re-raster), only
the wave you happened to re-cut updates — every other wave's crop silently
shows the OLD geometry until someone remembers to re-run wave-diff for all
of them. That "remember to re-cut all" step is exactly what got missed
twice on 2026-06-12 (the wave-1 rotation fix and the blueprint display:none
fix both left waves 2+ stale). tools/regate-all.py automates the re-cut;
this hook is the tripwire that fires when it's NEEDED but hasn't been run.

How it decides "needed": for each known medallion session, it finds the
highest passed iteration's render.svg and compares its mtime against the
session.json mtime. If render.svg is NEWER than session.json, the render was
rebuilt after the last gate stamp — the crops are (potentially) stale and
regate-all should run. It emits a one-line reminder naming the exact
command; it does NOT run the 15-wave cairosvg loop itself (too heavy for a
5s Stop-hook timeout, and a hook that mutates session.json + 45 PNGs without
the agent's intent is surprising). Nudge, like decision-doc-watch.py.

Defensive: any error -> exit 0 silently. Hooks must never block.
"""

import json
import sys
from pathlib import Path

# Sessions this hook watches. A session qualifies if it has session.json with
# stage_gates.structure.waves_passed and an iterations/ dir. Add new session
# roots here (or the hook auto-discovers any dir under the data roots below
# that has the expected shape).
DATA_ROOTS = [
    Path.home() / "Dropbox" / "Data" / "sacred-patterns",
    Path.home() / "Library" / "CloudStorage" / "Dropbox" / "Data" / "sacred-patterns",
]


def passed_iters(session_json: Path) -> list[int]:
    """The distinct iteration numbers recorded as passed in this session."""
    try:
        s = json.loads(session_json.read_text())
        wp = s.get("stage_gates", {}).get("structure", {}).get("waves_passed", {})
        return sorted({g["iter"] for g in wp.values() if isinstance(g.get("iter"), int)})
    except Exception:
        return []


def stale_sessions() -> list[tuple[Path, int]]:
    """Sessions whose top passed iteration's render.svg is newer than
    session.json — i.e. the render was rebuilt after the gates were stamped.

    Returns (session_dir, top_iter) pairs. Empty when everything is fresh.
    """
    out: list[tuple[Path, int]] = []
    seen: set[Path] = set()
    for root in DATA_ROOTS:
        if not root.exists():
            continue
        for session_json in root.glob("*/session.json"):
            session_dir = session_json.parent.resolve()
            if session_dir in seen:
                continue
            seen.add(session_dir)
            iters = passed_iters(session_json)
            if not iters:
                continue
            top = iters[-1]
            render = session_dir / "iterations" / str(top) / "render.svg"
            try:
                if render.exists() and render.stat().st_mtime > session_json.stat().st_mtime:
                    out.append((session_dir, top))
            except Exception:
                continue
    return out


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    # Don't re-fire on our own stop chain.
    if str(payload.get("stop_hook_active", "")).lower() == "true":
        return 0

    stale = stale_sessions()
    if not stale:
        return 0

    lines = [
        "⚠️  An iteration's render.svg is newer than its gate stamps — the "
        "portal's per-wave crops may be stale (a shared-geometry change "
        "re-cuts only the wave you touched; every other passed wave keeps the "
        "OLD crop). Re-cut all passed waves so every gate picture shows the "
        "same current geometry (Cookbook 2b-ALL):"
    ]
    for session_dir, top in stale:
        lines.append(
            f"  /Users/omareid/Workspace/git/qiyas/.venv/bin/python "
            f"tools/regate-all.py {session_dir} {top}"
        )
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
