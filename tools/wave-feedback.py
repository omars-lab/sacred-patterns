#!/usr/bin/env python3
"""wave-feedback.py — surface the owner's per-wave verdicts so the loop acts on them.

Plain English: the owner reviews each built wave in the portal and presses
"This wave looks right" or "Needs work" (with a comment saying what's wrong).
That verdict lands in session.json under waves_passed[<n>].owner_verdict. A
"Needs work" verdict is the highest-priority steering signal in the whole
loop — it means the owner's EYE caught a defect the census/coverage metrics
missed, which is the entire reason the portal exists (Tenets 24/25/27). The
loop must consume it BEFORE advancing construction, not after.

This tool is what the loop runs at pickup to find out whether the owner has
asked for any fixes. It reads every wave's owner_verdict and reports the
denied ones — the wave number, the owner's note (the fix request), and when
it was set — newest-comment first. The note IS the fix instruction (owner's
design: "Deny + comment = a fix request").

Exit code is the loop's branch signal:
    2  — one or more waves are denied (there is owner-requested work to do)
    0  — no denials (every built wave is either approved or un-judged)
    1  — usage / read error

Usage:
    tools/wave-feedback.py <session-dir>            # human-readable report
    tools/wave-feedback.py <session-dir> --json     # machine-readable, for tools
    tools/wave-feedback.py <session-dir> --quiet     # exit code only, no output

Example (medallion-10, wave 7 denied):
    $ tools/wave-feedback.py ~/Dropbox/Data/sacred-patterns/bikar-medallion-10
    1 wave needs work (owner pressed "Needs work" in the portal):

      wave  7 — "the center star is rotated 18deg too far"   (2026-06-12)

    Fix the denied wave(s) BEFORE advancing construction (Tenet 24/25/27:
    the owner's eye is the decisive gate). The note is the fix instruction.
    $ echo $?
    2
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def denied_waves(session_json: Path) -> list[dict]:
    """Every wave the owner marked "Needs work", newest-verdict-date first.

    Each entry: {wave:int, note:str, date:str, iter:int|None}. A wave counts
    as denied only when its owner_verdict.state == "denied"; approved and
    un-judged waves are omitted. Reads waves_passed —
    stage_gates.structure.waves_passed[<n>].owner_verdict.

    Example: a session with wave 7 denied returns
    [{"wave": 7, "note": "the center star is rotated 18deg too far",
      "date": "2026-06-12", "iter": 70}].
    """
    s = json.loads(session_json.read_text())
    wp = s.get("stage_gates", {}).get("structure", {}).get("waves_passed", {})
    out: list[dict] = []
    for wave_str, entry in wp.items():
        verdict = entry.get("owner_verdict") or {}
        if verdict.get("state") != "denied":
            continue
        out.append({
            "wave": int(wave_str),
            "note": (verdict.get("note") or "").strip(),
            "date": verdict.get("date", ""),
            "iter": entry.get("iter"),
        })
    # Newest verdict first, then by wave so output is stable for a given date.
    out.sort(key=lambda d: (d["date"], -d["wave"]), reverse=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session_dir", type=Path)
    ap.add_argument("--json", action="store_true",
                    help="emit the denied-wave list as JSON")
    ap.add_argument("--quiet", action="store_true",
                    help="no output; communicate only through the exit code")
    args = ap.parse_args()

    session_json = args.session_dir.resolve() / "session.json"
    if not session_json.exists():
        if not args.quiet:
            print(f"no session.json at {session_json}", file=sys.stderr)
        return 1

    try:
        denied = denied_waves(session_json)
    except Exception as e:  # noqa: BLE001 — a malformed session.json is a usage error
        if not args.quiet:
            print(f"could not read verdicts: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(denied, indent=2))
        return 2 if denied else 0

    if args.quiet:
        return 2 if denied else 0

    if not denied:
        print("No waves need work — every built wave is approved or un-judged.")
        return 0

    n = len(denied)
    print(f"{n} wave{'s' if n != 1 else ''} need{'s' if n == 1 else ''} work "
          "(owner pressed \"Needs work\" in the portal):\n")
    for d in denied:
        note = d["note"] or "(no comment — ask the owner what to change)"
        when = f"   ({d['date']})" if d["date"] else ""
        print(f"  wave {d['wave']:>2} — \"{note}\"{when}")
    print("\nFix the denied wave(s) BEFORE advancing construction (Tenet "
          "24/25/27: the owner's eye is the decisive gate). The note is the "
          "fix instruction.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
