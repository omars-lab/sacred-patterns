#!/usr/bin/env python3
"""Stop-hook: nudge to write a decision doc when the last assistant
message presented options without recording the choice.

Reads the Stop-hook stdin payload, extracts last_assistant_message,
matches against decision-presenting phrases (see PHRASES below), and if
matched AND no docs/decisions/YYYY-MM-DD-*.md was modified this session,
emits a markdown reminder block.

Defensive: any error -> exit 0 silently. Hooks must never block.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

PHRASES = [
    r'awaiting\s+(owner|user|your|the)?\s*(pick|decision|sign-off|review|response)',
    r'\bOption\s+[A-D]\b.*\bOption\s+[A-D]\b',
    r'\b[A-D]\.\d+\b.*\b[A-D]\.\d+\b',
    r'^STOP[:\s\-—]',
    r'surfac(ing|ed)\s+(divergence|spec\s+gap|decision|sub-decision)',
    r'\bsub-decision\b',
    r'pick\s*[:\-]\s*[A-D](\.\d+)?\b',
]
PATTERN = re.compile('|'.join(PHRASES), re.IGNORECASE | re.MULTILINE)


def session_touched_decision_doc(repo_root: Path) -> bool:
    """Return True if any docs/decisions/*.md is staged or modified
    in repo_root or its sibling repos (qiyas, bikar)."""
    roots = [repo_root]
    for sibling in ('../qiyas', '../bikar'):
        sib = (repo_root / sibling).resolve()
        if sib.exists() and sib != repo_root:
            roots.append(sib)
    for root in roots:
        try:
            result = subprocess.run(
                ['git', '-C', str(root), 'status', '--porcelain'],
                capture_output=True, text=True, timeout=3,
            )
        except Exception:
            continue
        for line in result.stdout.splitlines():
            if '/decisions/' in line and line.rstrip().endswith('.md'):
                return True
    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    if str(payload.get('stop_hook_active', '')).lower() == 'true':
        return 0

    msg = payload.get('last_assistant_message', '') or ''
    if not PATTERN.search(msg):
        return 0

    repo_root = Path(__file__).resolve().parent.parent.parent
    if session_touched_decision_doc(repo_root):
        return 0

    print(
        "⚠️  The last response presented options or surfaced a decision, "
        "but no `docs/decisions/YYYY-MM-DD-*.md` was written this session.\n"
        "Consider invoking the `present-options` skill before continuing - "
        "or, if a doc already exists for this decision, edit it to record "
        "the picked option and rationale."
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
