#!/usr/bin/env python3
"""regate-all.py — re-cut EVERY passed wave's gate against one iteration's render.

Plain English: when a fix changes geometry that more than one wave's crop
sees — the medallion's center star sits inside the middle-flower crops of
waves 1, 2 and 3, the blueprint scaffolding leaks into all of them, a
renderer change re-rasters everything — re-running ONE wave's gate leaves
every other wave's portal picture stale, showing the OLD geometry. The
owner then sees "the center changed between wave 1 and wave 2" when nothing
changed except which iteration each crop was cut from.

This tool closes that gap in one idempotent command. It re-runs wave-diff.py
for every wave already recorded as passed (session.json
stage_gates.structure.waves_passed) against a single iteration's render.svg,
then re-stamps each wave's coverage/iou to the freshly measured numbers
(preserving the prior {iter,coverage,iou} under `prev`). After it runs, the
portal's latest_gate_sbs() resolves every passed wave to the SAME iteration,
so every crop shows the same current geometry.

This is the codification of Cookbook 2b-ALL (a shared-geometry change stales
EVERY built wave's crop, not just the changed wave's) — run once by hand
twice on 2026-06-12 (wave-1 rotation fix, blueprint display:none fix), now a
single command so the next shared-geometry change doesn't require remembering
to re-cut all 15 by hand.

Usage (qiyas venv python — it has cairosvg/PIL/numpy/scipy):
    /Users/omareid/Workspace/git/qiyas/.venv/bin/python tools/regate-all.py \
        <session-dir> <iter>

    # dry-run: print what would re-cut, touch nothing
    regate-all.py <session-dir> <iter> --dry-run

    # re-cut only, don't re-stamp session.json (preview the numbers)
    regate-all.py <session-dir> <iter> --no-stamp

The iteration must have iterations/<iter>/render.svg. Every passed wave is
re-cut from THAT svg; waves not yet passed are skipped (they have no gate to
stale). Idempotent: running it twice with the same iter produces the same
crops and the same stamped numbers (the second run's `prev` is preserved
from the first, not overwritten with the just-written value — see stamp()).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# The canonical wave-diff entrypoint and the python that has its deps.
# regate-all shells wave-diff.py (rather than importing it) so the ONE
# rasterization path stays owned by wave-diff.py — no second cairosvg call
# site to drift (Tenet 11, the one-raster rule wave-diff.py documents).
TOOLS_DIR = Path(__file__).resolve().parent
WAVE_DIFF = TOOLS_DIR / "wave-diff.py"


def passed_waves(session_json: Path) -> dict:
    """The waves_passed dict: {wave_str: {iter,coverage,iou,date,note,prev}}.

    Example: a session three waves in returns
    {"1": {"iter": 70, "coverage": 0.932, ...}, "2": {...}, "3": {...}}.
    Returns {} if the structure gate has recorded no passes yet.
    """
    s = json.loads(session_json.read_text())
    return s.get("stage_gates", {}).get("structure", {}).get("waves_passed", {})


def run_wave_diff(session_dir: Path, wave: int, render_svg: Path) -> dict:
    """Re-cut one wave's gate; return its fresh wave-diff.json as a dict.

    Shells wave-diff.py with the canonical args, then reads back the
    coverage/iou it wrote under iterations/<iter>/wave-diff/wave-NN/. Raises
    if wave-diff.py fails (a non-zero exit means the wave's shape ids no
    longer match the photo — a real problem the caller must see, not swallow).
    """
    rel = render_svg.relative_to(session_dir) if render_svg.is_absolute() else render_svg
    cmd = [
        sys.executable, str(WAVE_DIFF),
        str(session_dir), str(wave),
        "--render", str(rel),
    ]
    subprocess.run(cmd, check=True)
    out = (render_svg.parent / "wave-diff" / f"wave-{wave:02d}" / "wave-diff.json")
    return json.loads(out.read_text())


def stamp(entry: dict, iter_n: int, fresh: dict, date: str, note: str) -> dict:
    """Re-stamp one waves_passed entry to fresh numbers, preserving `prev`.

    The invariant that makes this idempotent: `prev` records the FIRST
    pre-regate number, never the value written by a previous regate run. So
    re-running regate-all against the same iter keeps `prev` pointing at the
    genuine prior baseline (e.g. the {10/4} record before the rotation fix),
    not at the regate result. We only refresh `prev` when this regate moves
    the entry to a DIFFERENT iteration than it currently records — that's a
    real re-baseline; a same-iter re-cut leaves `prev` untouched.

    Example: entry at iter 41 cov 0.897, regate to iter 70 -> writes
    iter 70 cov <fresh>, prev {iter:41, cov:0.897}. Regate to iter 70 AGAIN
    -> iter unchanged, prev stays {iter:41,...}.
    """
    new = dict(entry)
    if entry.get("iter") != iter_n:
        new["prev"] = {
            "iter": entry.get("iter"),
            "coverage": entry.get("coverage"),
            "iou": entry.get("iou"),
        }
    new["iter"] = iter_n
    new["coverage"] = fresh["coverage"]
    new["iou"] = fresh["iou"]
    new["date"] = date
    new["note"] = note
    return new


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session_dir", type=Path)
    ap.add_argument("iter", type=int, help="iteration whose render.svg every wave re-cuts against")
    ap.add_argument("--date", default=None,
                    help="date string stamped into re-baselined entries (default: today, "
                         "passed in by the hook; falls back to the entry's existing date)")
    ap.add_argument("--note", default=None,
                    help="override the re-baseline note (default: a generic re-cut note)")
    ap.add_argument("--dry-run", action="store_true", help="list what would re-cut, change nothing")
    ap.add_argument("--no-stamp", action="store_true",
                    help="re-cut the crops but do NOT modify session.json")
    args = ap.parse_args()

    session_dir = args.session_dir.resolve()
    session_json = session_dir / "session.json"
    render_svg = session_dir / "iterations" / str(args.iter) / "render.svg"

    if not render_svg.exists():
        raise SystemExit(f"no render.svg at {render_svg} — build iter {args.iter} first")

    waves = passed_waves(session_json)
    if not waves:
        print("no passed waves recorded — nothing to re-cut")
        return

    wave_nums = sorted(int(w) for w in waves)
    print(f"re-cutting {len(wave_nums)} passed wave(s) {wave_nums} against "
          f"iter-{args.iter}/render.svg")
    if args.dry_run:
        for n in wave_nums:
            cur = waves[str(n)]
            print(f"  wave {n:>2}: currently iter-{cur.get('iter')} "
                  f"cov {cur.get('coverage')} iou {cur.get('iou')} -> would re-cut")
        return

    default_note = (
        f"RE-GATE (iter-{args.iter}, regate-all): wave-diff re-cut from iter-{args.iter} "
        "render so every gate picture shows the same current geometry. Coverage "
        "re-measured uniformly through the canonical cairosvg path (Cookbook #13 "
        "one-raster rule); this wave's geometry was NOT re-authored. Cookbook 2b-ALL."
    )
    note = args.note or default_note

    s = json.loads(session_json.read_text())
    wp = s["stage_gates"]["structure"]["waves_passed"]
    changed = 0
    for n in wave_nums:
        fresh = run_wave_diff(session_dir, n, render_svg)
        cov, iou = fresh["coverage"], fresh["iou"]
        prev_cov = waves[str(n)].get("coverage")
        delta = f"{cov - prev_cov:+.3f}" if isinstance(prev_cov, (int, float)) else "n/a"
        print(f"  wave {n:>2}: cov {cov:.3f} (Δ{delta})  iou {iou:.3f}")
        if not args.no_stamp:
            date = args.date or waves[str(n)].get("date", "")
            wp[str(n)] = stamp(waves[str(n)], args.iter, fresh, date, note)
            changed += 1

    if args.no_stamp:
        print("--no-stamp: crops re-cut, session.json untouched")
        return

    session_json.write_text(json.dumps(s, indent=2) + "\n")
    print(f"re-stamped {changed} wave(s) in session.json to iter-{args.iter}")
    print("portal latest_gate_sbs() now resolves every passed wave to this iteration")


if __name__ == "__main__":
    main()
