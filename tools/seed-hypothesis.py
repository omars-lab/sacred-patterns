#!/usr/bin/env python3
"""seed-hypothesis.py — draft the next iteration's hypothesis scaffold from the portal verdict.

Once `tools/portal-handoff.py` lands `iterations/N/review-verdict.json`, this
tool drafts `iterations/N+1/hypothesis-seed.md` — the Step-1 template of the
iterate-construction-hypothesis skill with the machine-knowable half
pre-filled (attempt number, the top-ranked gap with its annotation id, the
evidence trail) and every judgment field a literal `TODO(judgment)` marker.

The split is deliberate (deterministic-seed-plus-agent-judgment): verdict
counts, gap ranking, and evidence are pure functions of the review session,
but `construction_hypothesis` / `bkr_change` / the Tenet-24 expected visual
require the skill's routing decision and must be authored by the agent or
human — a templated expectation is a fudged one. A seed still containing
TODO(judgment) is never a valid hypothesis.md; the skill's checklist blocks
shipping it.

Usage:
    ./tools/seed-hypothesis.py SESSION_DIR N [--date YYYY-MM-DD]

Reads  iterations/N/review-verdict.json   (run portal-handoff.py first)
Writes iterations/N+1/hypothesis-seed.md  (never overwrites silently)
"""

from __future__ import annotations

import argparse
import datetime as _dt
import sys
from pathlib import Path

import portal_verdict

TODO = "TODO(judgment)"


def die(msg: str, exit_code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(exit_code)


def _draft_gap_targeted(verdict: dict) -> str:
    """Machine draft of gap_targeted, citing the top gap's annotation id.

    The citation is load-bearing: the skill allows rewording the draft but
    requires either keeping the annotation-id citation or justifying why
    the ranking is overridden.
    """
    seed = verdict.get("hypothesis_seed")
    gaps = verdict.get("gaps", [])
    if isinstance(seed, dict) and gaps:
        top = gaps[0]
        return f"{seed.get('gap_targeted', '')} [annotation {top.get('annotation_id')}]"
    return f"{TODO}: review passed or no ranked gaps — name the gap yourself"


def _evidence_lines(verdict: dict) -> list[str]:
    counts = verdict.get("verdict_counts", {})
    lines = [
        f"- verdict: right={counts.get('right')} wrong={counts.get('wrong')} "
        f"unsure={counts.get('unsure')}; review_passed={verdict.get('review_passed')}",
    ]
    pixel = verdict.get("pixel")
    if isinstance(pixel, dict) and pixel.get("similarity_pct") is not None:
        lines.append(f"- pixel similarity: {pixel['similarity_pct']}%")
        for warning in pixel.get("warning_messages", []):
            lines.append(f"- pixel warning: {warning}")
    gaps = verdict.get("gaps", [])
    if gaps:
        lines.append("- gaps (ranked, structure before pixels):")
        for i, gap in enumerate(gaps, start=1):
            lines.append(
                f"  {i}. [annotation {gap.get('annotation_id')}] "
                f"({gap.get('question')} {gap.get('kind')}, rank {gap.get('rank')}): "
                f"{gap.get('gap_sentence')}"
            )
    return lines


def render_seed(verdict: dict, attempt: int, date: str) -> str:
    """The hypothesis-seed.md body — skill Step-1 template, machine half filled."""
    seed = verdict.get("hypothesis_seed")
    lift_seed = (
        seed.get("predicted_lift_seed", "") if isinstance(seed, dict) else ""
    )
    lift = (
        f"{TODO}: +0.NN composite — seed: {lift_seed}"
        if lift_seed
        else f"{TODO}: +0.NN composite, and which warning it should clear"
    )
    lines = [
        "---",
        f"attempt: {attempt}",
        f"date: {date}",
        f'gap_targeted: "{_draft_gap_targeted(verdict)}"',
        f'construction_hypothesis: "{TODO}: what about the CONSTRUCTION is wrong, and why"',
        f'bkr_change: "{TODO}: the smallest single .bkr edit — or named bikar primitive to add"',
        f'predicted_lift: "{lift}"',
        f'predicted_cost: "{TODO}: what the edit might BREAK — new false faces, fold change"',
        f'prior_art_searched: "{TODO}: web search query for the construction technique, or \'none\'"',
        f'related_memory: "{TODO}: memory files read that bear on this construction"',
        'detector_untouched: "confirmed — no qiyas param/threshold/cost in this iteration"',
        "---",
        "",
        "## Portal evidence (machine-drafted from review-verdict.json)",
        "",
        *_evidence_lines(verdict),
        "",
        "## Plan",
        f"{TODO}: why this gap, why this construction hypothesis, why this is the smallest edit.",
        f"{TODO}: Expected visual (write BEFORE viewing any render — Tenet 24).",
        "",
        "## Guardrails check",
        f"- This is a CONSTRUCTION edit (.bkr / bikar primitive), not a detector edit: {TODO}",
        f"- Construction-philosophy memory checked — approach not already falsified: {TODO}",
        f"- predicted_cost names a concrete failure mode I will look for in the render: {TODO}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Draft iterations/N+1/hypothesis-seed.md from iterations/N/review-verdict.json."
    )
    p.add_argument("session_dir", help="Deconstruction session root (contains iterations/)")
    p.add_argument("n", type=int, help="Reviewed iteration number (seed targets N+1)")
    p.add_argument(
        "--date",
        default=_dt.date.today().isoformat(),
        help="Date stamped into the seed frontmatter (default: today)",
    )
    args = p.parse_args()

    session_dir = Path(args.session_dir)
    verdict_file = portal_verdict.verdict_path(session_dir, args.n)
    verdict = portal_verdict.read_verdict(verdict_file)
    if verdict is None:
        die(
            f"no readable verdict at {verdict_file}. "
            f"Run ./tools/portal-handoff.py {session_dir} {args.n} first."
        )

    attempt = args.n + 1
    out_path = session_dir / "iterations" / str(attempt) / "hypothesis-seed.md"
    if out_path.exists():
        die(f"{out_path} already exists — remove it first if you want a fresh draft")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_seed(verdict, attempt, args.date), encoding="utf-8")
    print(f"wrote {out_path}")
    print(
        "next: author iterations/"
        f"{attempt}/hypothesis.md from the seed — fill every {TODO} yourself "
        "(iterate-construction-hypothesis Step 1) BEFORE editing pattern.bkr"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
