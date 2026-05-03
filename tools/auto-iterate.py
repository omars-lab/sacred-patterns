#!/usr/bin/env python3
"""auto-iterate.py — Phase 1 of the auto-iterate plan.

Drives the iteration loop end-to-end EXCEPT the edit step itself.
Each cycle:

  1. Reads validation.json from the current best iteration.
  2. Checks terminal conditions (converged / stagnation / budget).
  3. Stops and prompts the human to apply the warning to a NEW
     iteration directory (Phase 1 manual edit; Phase 2 will swap
     this for an Agent call).
  4. After the human signals ready, renders the new pattern.bkr via
     bikar's compileDSL.
  5. Validates via tools/iteration-validate.sh.
  6. Records the predicted-vs-actual delta in auto-iterate-run.md.
  7. Loops.

Phase 1.5 (the post-iteration capture checklist) is a separate file
and is not yet wired in.

Usage:
    tools/auto-iterate.py SESSION_DIR [--max-iterations N]
                                      [--stagnation-window N]
                                      [--stagnation-epsilon F]

Exits:
    0  converged
    1  stagnation
    2  budget exhaustion
    3  uncaught error (broken render that didn't recover, etc.)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

REPO_SACRED = Path(__file__).resolve().parent.parent
REPO_BIKAR = Path("/Users/omareid/Workspace/git/bikar")
COMPILE_DSL_JS = REPO_BIKAR / "packages/core/dist/index.js"
ORCHESTRATOR = REPO_SACRED / "tools/iteration-validate.sh"


# ============================================================
# Data structures
# ============================================================

@dataclass
class IterationResult:
    n: int
    composite: Optional[float]
    structural: str
    pixel: Optional[float]
    go_no_go: str
    top_warning: Optional[dict]
    blocking_issues: list[str]
    validation_path: Path


# ============================================================
# Filesystem helpers
# ============================================================

def find_iterations(session_dir: Path) -> list[int]:
    iters_dir = session_dir / "iterations"
    if not iters_dir.is_dir():
        return []
    out: list[int] = []
    for p in iters_dir.iterdir():
        if p.is_dir() and p.name.isdigit():
            out.append(int(p.name))
    out.sort()
    return out


def latest_validated(session_dir: Path) -> Optional[int]:
    for n in reversed(find_iterations(session_dir)):
        if (session_dir / "iterations" / str(n) / "validation" / "validation.json").is_file():
            return n
    return None


def load_iteration(session_dir: Path, n: int) -> IterationResult:
    vp = session_dir / "iterations" / str(n) / "validation" / "validation.json"
    with vp.open() as f:
        v = json.load(f)
    o = v.get("overall", {})
    warnings = o.get("warnings") or []
    return IterationResult(
        n=n,
        composite=o.get("composite_score"),
        structural=o.get("structural_score") or "n/a",
        pixel=o.get("pixel_similarity"),
        go_no_go=o.get("go_no_go") or "unknown",
        top_warning=warnings[0] if warnings else None,
        blocking_issues=o.get("blocking_issues") or [],
        validation_path=vp,
    )


# ============================================================
# Render + validate
# ============================================================

def render_bkr(bkr_path: Path, svg_out: Path) -> tuple[bool, str]:
    """Compile a .bkr to SVG via bikar's compileDSL. Returns (ok, log)."""
    if not COMPILE_DSL_JS.is_file():
        return False, f"bikar dist not found at {COMPILE_DSL_JS}"
    js = (
        f"const {{compileDSL}} = require({json.dumps(str(COMPILE_DSL_JS))});\n"
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({json.dumps(str(bkr_path))}, 'utf-8');\n"
        f"fs.writeFileSync({json.dumps(str(svg_out))}, compileDSL(src));\n"
    )
    proc = subprocess.run(
        ["node", "-e", js],
        capture_output=True, text=True,
    )
    log = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0 and svg_out.is_file(), log


def run_orchestrator(svg: Path, reference: Path, baseline: Path,
                     out_dir: Path) -> tuple[bool, str]:
    cmd = [
        str(ORCHESTRATOR),
        "--svg", str(svg),
        "--reference", str(reference),
        "--baseline", str(baseline),
        "--out", str(out_dir),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    log = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, log


# ============================================================
# Run-log
# ============================================================

def append_run_log(session_dir: Path, line: str) -> None:
    log = session_dir / "auto-iterate-run.md"
    new_file = not log.exists()
    with log.open("a") as f:
        if new_file:
            f.write("# Auto-iterate run\n\n")
            f.write("| iter | composite | structural | pixel | go_no_go | "
                    "top_warning | predicted Δ | actual Δ | predicted-vs-actual error |\n")
            f.write("|---|---|---|---|---|---|---|---|---|\n")
        f.write(line + "\n")


def fmt_run_row(it: IterationResult, predicted_delta: Optional[float],
                prev_composite: Optional[float]) -> str:
    actual = None
    if it.composite is not None and prev_composite is not None:
        actual = round(it.composite - prev_composite, 4)
    err = None
    if predicted_delta is not None and actual is not None:
        err = round(predicted_delta - actual, 4)
    top = it.top_warning.get("id") if it.top_warning else "-"
    return (
        f"| {it.n} | {it.composite if it.composite is not None else '-'} "
        f"| {it.structural} | {it.pixel if it.pixel is not None else '-'} "
        f"| {it.go_no_go} | {top} "
        f"| {predicted_delta if predicted_delta is not None else '-'} "
        f"| {actual if actual is not None else '-'} "
        f"| {err if err is not None else '-'} |"
    )


# ============================================================
# Manual edit prompt (Phase 1 — Phase 2 swaps for an Agent call)
# ============================================================

def prompt_manual_edit(session_dir: Path, n: int, k: int,
                       it: IterationResult) -> bool:
    """Print the warning context and wait for the human. Returns True
    when iter K's pattern.bkr exists and the human signals ready."""
    next_dir = session_dir / "iterations" / str(k)
    next_dir.mkdir(parents=True, exist_ok=True)
    next_bkr = next_dir / "pattern.bkr"

    base_bkr = session_dir / "iterations" / str(n) / "pattern.bkr"
    if not base_bkr.is_file():
        print(f"[error] no pattern.bkr at iter {n}; can't seed iter {k}", file=sys.stderr)
        return False
    if not next_bkr.exists():
        shutil.copy(base_bkr, next_bkr)

    w = it.top_warning or {}
    rationale = (w.get("context") or {}).get("counterfactual_rationale") or "-"
    print()
    print(f"=== iter {k} edit prompt (Phase 1: manual) ===")
    print(f"  base:        iterations/{n}/pattern.bkr (copied to {k}/)")
    print(f"  warning id:  {w.get('id')}")
    print(f"  source:      {w.get('source')}")
    print(f"  delta:       {w.get('counterfactual_score_delta')}")
    print(f"  message:     {w.get('message')}")
    print(f"  rationale:   {rationale}")
    print()
    print(f"  Edit:        {next_bkr}")
    print(f"  Then:        press <enter> here to render + validate iter {k}")
    print(f"  Or 'q':      quit the loop, leaving iter {k} in place")
    print()
    try:
        ans = input("> ").strip().lower()
    except EOFError:
        return False
    if ans in ("q", "quit", "exit"):
        return False
    return True


# ============================================================
# Main loop
# ============================================================

def composite_changed(window: list[float], epsilon: float) -> bool:
    if len(window) < 2:
        return True
    deltas = [abs(window[i] - window[i - 1]) for i in range(1, len(window))]
    return any(d >= epsilon for d in deltas)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("session_dir")
    p.add_argument("--max-iterations", type=int, default=30)
    p.add_argument("--stagnation-window", type=int, default=3)
    p.add_argument("--stagnation-epsilon", type=float, default=0.005)
    args = p.parse_args()

    session_dir = Path(args.session_dir).resolve()
    if not session_dir.is_dir():
        print(f"[error] session_dir not a directory: {session_dir}", file=sys.stderr)
        return 3

    reference = session_dir / "input" / "reference.jpg"
    baseline = session_dir / "input" / "baseline.json"
    for required in (reference, baseline):
        if not required.is_file():
            print(f"[error] required input missing: {required}", file=sys.stderr)
            return 3

    n = latest_validated(session_dir)
    if n is None:
        print("[error] no validated iteration in session", file=sys.stderr)
        return 3

    base_bkr = session_dir / "iterations" / str(n) / "pattern.bkr"
    if not base_bkr.is_file():
        print(f"[error] iter {n} has no pattern.bkr at {base_bkr}", file=sys.stderr)
        print("[error] auto-iterate currently supports BIKAR DSL sessions only;",
              file=sys.stderr)
        print("        D3-authored sessions need a different edit skill (not yet built).",
              file=sys.stderr)
        return 3

    it = load_iteration(session_dir, n)
    print(f"[start] session={session_dir.name} latest_iter={n} "
          f"composite={it.composite} go_no_go={it.go_no_go}")

    composite_window: list[float] = []
    if it.composite is not None:
        composite_window.append(it.composite)
    start_n = n
    iter_count = 0

    while True:
        # Terminal: convergence
        if it.go_no_go == "converged":
            print(f"[done] converged at iter {it.n}")
            return 0

        # Terminal: budget
        if iter_count >= args.max_iterations:
            print(f"[stop] budget exhausted ({args.max_iterations} iters from {start_n})")
            return 2

        # Terminal: no actionable warning
        if it.top_warning is None and it.go_no_go != "broken":
            print(f"[stop] iter {it.n} has no warnings[0]; check qiyas score availability")
            print(f"       blocking_issues: {it.blocking_issues}")
            return 3

        predicted_delta = None
        if it.top_warning is not None:
            predicted_delta = it.top_warning.get("counterfactual_score_delta")

        k = it.n + 1
        prev_composite = it.composite

        # === Edit step (Phase 1: manual prompt; Phase 2: Agent call) ===
        if not prompt_manual_edit(session_dir, it.n, k, it):
            print("[stop] user quit during edit step")
            return 3

        # === Render ===
        next_bkr = session_dir / "iterations" / str(k) / "pattern.bkr"
        next_svg = session_dir / "iterations" / str(k) / "render.svg"
        ok, render_log = render_bkr(next_bkr, next_svg)
        if not ok:
            print(f"[error] iter {k} render failed:")
            print(render_log)
            print("[stop] forced into G1 broken-render mode; Phase 1 ends here")
            return 3

        # === Validate ===
        next_val_dir = session_dir / "iterations" / str(k) / "validation"
        ok, val_log = run_orchestrator(next_svg, reference, baseline, next_val_dir)
        if not ok:
            print(f"[error] iter {k} orchestrator failed:")
            print(val_log[-2000:])
            return 3

        new_it = load_iteration(session_dir, k)

        # === Run-log ===
        row = fmt_run_row(new_it, predicted_delta, prev_composite)
        append_run_log(session_dir, row)
        print(f"[iter {k}] composite={new_it.composite} "
              f"structural={new_it.structural} go_no_go={new_it.go_no_go}")

        # === Stagnation check ===
        if new_it.composite is not None:
            composite_window.append(new_it.composite)
            composite_window = composite_window[-args.stagnation_window:]
        if (len(composite_window) >= args.stagnation_window
                and not composite_changed(composite_window, args.stagnation_epsilon)):
            print(f"[stop] stagnation: last {args.stagnation_window} composites "
                  f"within {args.stagnation_epsilon} (window={composite_window})")
            return 1

        it = new_it
        iter_count += 1


if __name__ == "__main__":
    sys.exit(main())
