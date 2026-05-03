"""Phase 1.5 — post-iteration capture checklist.

After each successful iteration, the harness asks five questions and
routes any "yes" to a concrete artifact in the right repo. The point
is meta-loop discipline: cross-iteration gaps (qiyas misclassifications,
BIKAR DSL gaps, translation-table holes, novel construction techniques)
get captured the moment they're noticed, not lost in conversation.

See `.claude/plans/autonomous-iteration-loop.md` Phase 1.5 for the
routing table and rationale.

Hard rule (tenet 3): if a question answers "yes" but the routing
artifact can't be written (sibling repo not on disk), raise CaptureError
and let the harness fail the loop loudly. Silently skipping defeats the
purpose.
"""
from __future__ import annotations

import datetime
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

REPO_QIYAS = Path("/Users/omareid/Workspace/git/qiyas")
REPO_BIKAR = Path("/Users/omareid/Workspace/git/bikar")
REPO_SACRED = Path(__file__).resolve().parent.parent

QIYAS_ISSUES_DIR = REPO_QIYAS / "docs/issues"
BIKAR_DSL_GAPS = REPO_BIKAR / "docs/dsl-gaps.md"
BIKAR_TRANSLATION_SKILL = (
    REPO_BIKAR / ".claude/skills/iterate-pattern-from-qiyas-warnings/SKILL.md"
)
SACRED_TECHNIQUES = (
    REPO_SACRED / ".claude/skills/generate-drawing/learnings/construction-techniques.md"
)


class CaptureError(RuntimeError):
    """Routing destination unavailable; harness must fail the loop."""


@dataclass
class IterContext:
    session_name: str  # e.g. "bikar-medallion-10"
    iter_n: int
    bkr_path: Path
    validation_path: Path
    top_warning_id: Optional[str]


# ============================================================
# Prompt helpers
# ============================================================

def _ask_yes_no(question: str) -> bool:
    print(f"\n  {question}")
    try:
        ans = input("  [y/N] > ").strip().lower()
    except EOFError:
        return False
    return ans in ("y", "yes")


def _ask_line(prompt: str) -> str:
    print(f"  {prompt}")
    try:
        return input("  > ").strip()
    except EOFError:
        return ""


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60] or "untitled"


# ============================================================
# Routing destinations — verify on import; the harness catches the
# CaptureError and fails the loop before the first iteration runs.
# ============================================================

def assert_destinations_writable() -> None:
    """Tenet 3 upfront check: fail fast if any sibling repo is missing.
    Run once before the loop starts so we don't discover a missing repo
    AFTER an iteration has surfaced a gap."""
    for path, label in (
        (REPO_QIYAS, "qiyas repo"),
        (REPO_BIKAR, "bikar repo"),
        (BIKAR_TRANSLATION_SKILL.parent, "bikar translation skill dir"),
        (SACRED_TECHNIQUES.parent, "sacred-patterns learnings dir"),
    ):
        if not path.exists():
            raise CaptureError(
                f"capture destination missing: {label} at {path}"
            )


# ============================================================
# Question 1 — qiyas misclassification / detector / weight issue
# ============================================================

def capture_qiyas_issue(ctx: IterContext) -> Optional[Path]:
    if not _ask_yes_no(
        "Q1: Did qiyas misclassify a shape, run a wrong detector, "
        "or score a warning incorrectly this iteration?"
    ):
        return None
    if not QIYAS_ISSUES_DIR.is_dir():
        raise CaptureError(f"qiyas issues dir missing: {QIYAS_ISSUES_DIR}")

    title = _ask_line("Short title (e.g. 'A4 coverage misses inner ring'):")
    if not title:
        raise CaptureError("Q1 answered yes but no title given — cannot route")
    symptom = _ask_line("Symptom (concrete observation, with iter ref):")
    root_guess = _ask_line("Root cause guess (or 'unknown'):")

    today = datetime.date.today().isoformat()
    slug = _slugify(title)
    out = QIYAS_ISSUES_DIR / f"{today}-{slug}.md"
    if out.exists():
        out = QIYAS_ISSUES_DIR / f"{today}-{slug}-{ctx.iter_n}.md"

    body = f"""# {title}

## Status
OPEN

## Discovered
{today} during {ctx.session_name} iter {ctx.iter_n} (auto-iterate Phase 1.5 capture).
Top warning at time of capture: `{ctx.top_warning_id or '-'}`.
Validation: `{ctx.validation_path}`.

## Symptom
{symptom}

## Root cause
{root_guess}

## Options considered
_(fill in when triaging)_

## Decision
_(pending)_

## Follow-ups
_(none yet)_
"""
    out.write_text(body)
    print(f"  → wrote {out}")
    return out


# ============================================================
# Question 2 — BIKAR DSL gap
# ============================================================

def capture_dsl_gap(ctx: IterContext) -> Optional[Path]:
    if not _ask_yes_no(
        "Q2: Did you want to express a construction in BIKAR DSL but "
        "couldn't, or had to use a workaround?"
    ):
        return None
    if not REPO_BIKAR.exists():
        raise CaptureError(f"bikar repo missing: {REPO_BIKAR}")

    wanted = _ask_line("Wanted (ideal syntax / capability):")
    workaround = _ask_line("Workaround (what shipped instead):")
    why = _ask_line("Why the workaround was needed:")
    if not wanted or not workaround:
        raise CaptureError("Q2 answered yes but wanted/workaround empty")

    new_file = not BIKAR_DSL_GAPS.exists()
    BIKAR_DSL_GAPS.parent.mkdir(parents=True, exist_ok=True)
    with BIKAR_DSL_GAPS.open("a") as f:
        if new_file:
            f.write("# BIKAR DSL gaps\n\n")
            f.write("Running list of constructions the DSL can't yet express. "
                    "Captured by sacred-patterns auto-iterate Phase 1.5.\n\n")
            f.write("Format: one line per gap.\n\n")
        f.write(
            f"- iter {ctx.session_name}/{ctx.iter_n} — "
            f"wanted: {wanted} · workaround: {workaround} · why: {why}\n"
        )
    print(f"  → appended to {BIKAR_DSL_GAPS}")
    return BIKAR_DSL_GAPS


# ============================================================
# Question 3 — translation-table hole
# ============================================================

def capture_translation_hole(ctx: IterContext) -> Optional[Path]:
    if not _ask_yes_no(
        "Q3: Did the BIKAR translation skill (warning id → DSL edit) "
        "lack a row for this warning, or did you have to interpret freely?"
    ):
        return None
    if not BIKAR_TRANSLATION_SKILL.is_file():
        raise CaptureError(
            f"bikar translation skill missing: {BIKAR_TRANSLATION_SKILL}"
        )

    warn_id = _ask_line(
        f"Warning id needing a row (default: {ctx.top_warning_id or 'unknown'}):"
    ) or (ctx.top_warning_id or "unknown")
    resolution = _ask_line("Resolution pattern (what edit fixes this warning):")
    example = _ask_line("Worked-example one-liner (iter ref + concrete edit):")
    if not resolution:
        raise CaptureError("Q3 answered yes but no resolution given")

    today = datetime.date.today().isoformat()
    block = (
        f"\n<!-- auto-iterate capture {today} {ctx.session_name}/iter{ctx.iter_n} -->\n"
        f"### Pending row: `{warn_id}`\n\n"
        f"- Resolution: {resolution}\n"
        f"- Worked example: {example}\n"
    )
    with BIKAR_TRANSLATION_SKILL.open("a") as f:
        f.write(block)
    print(f"  → appended pending row to {BIKAR_TRANSLATION_SKILL}")
    return BIKAR_TRANSLATION_SKILL


# ============================================================
# Question 4 — predicted vs actual delta (always recorded by harness)
# ============================================================
# This is not a yes/no question — the harness already records every
# row in auto-iterate-run.md via fmt_run_row(). No prompt here; the
# checklist surfaces it as a reminder that calibration is automatic.

def confirm_calibration_logged(ctx: IterContext) -> None:
    print(
        "  Q4: predicted vs actual Δ — auto-recorded in "
        "auto-iterate-run.md (no action needed)"
    )


# ============================================================
# Question 5 — reusable construction technique
# ============================================================

def capture_technique(ctx: IterContext) -> Optional[Path]:
    if not _ask_yes_no(
        "Q5: Did this iteration use a reusable construction technique "
        "that's NOT already in construction-techniques.md?"
    ):
        return None
    if not SACRED_TECHNIQUES.parent.is_dir():
        raise CaptureError(
            f"sacred learnings dir missing: {SACRED_TECHNIQUES.parent}"
        )

    title = _ask_line("Technique name (e.g. 'wedge-and-rotate'):")
    one_liner = _ask_line("One-line description of when to use it:")
    if not title or not one_liner:
        raise CaptureError("Q5 answered yes but title/description empty")

    today = datetime.date.today().isoformat()
    block = (
        f"\n## {title}\n\n"
        f"_Captured {today} during {ctx.session_name} iter {ctx.iter_n}._\n\n"
        f"{one_liner}\n\n"
        f"_TODO: expand with example bkr/d3 snippet when revisited._\n"
    )
    new_file = not SACRED_TECHNIQUES.exists()
    SACRED_TECHNIQUES.parent.mkdir(parents=True, exist_ok=True)
    with SACRED_TECHNIQUES.open("a") as f:
        if new_file:
            f.write("# Construction techniques\n\n"
                    "Reusable algorithms discovered across iteration sessions.\n")
        f.write(block)
    print(f"  → appended technique to {SACRED_TECHNIQUES}")
    return SACRED_TECHNIQUES


# ============================================================
# Top-level checklist
# ============================================================

def run_checklist(ctx: IterContext) -> list[Path]:
    """Run all five questions in order. Returns list of artifacts written.
    Raises CaptureError on any routing failure (caller fails the loop)."""
    print(f"\n=== iter {ctx.iter_n} post-capture checklist ===")
    written: list[Path] = []
    for fn in (capture_qiyas_issue, capture_dsl_gap,
               capture_translation_hole):
        out = fn(ctx)
        if out is not None:
            written.append(out)
    confirm_calibration_logged(ctx)
    out = capture_technique(ctx)
    if out is not None:
        written.append(out)
    print(f"  checklist done — {len(written)} artifact(s) written\n")
    return written


if __name__ == "__main__":
    # Standalone smoke: validate destinations and exit.
    try:
        assert_destinations_writable()
        print("all capture destinations writable")
    except CaptureError as e:
        print(f"[error] {e}", file=sys.stderr)
        sys.exit(1)
