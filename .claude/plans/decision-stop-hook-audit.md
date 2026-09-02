# Stop-hook audit — does any hook nudge "write a decision doc when stopping"?

**Status:** INSTALLED 2026-05-06 — hook live in sacred-patterns
(`.claude/hooks/decision-doc-watch.py` + `.claude/settings.local.json` `Stop`
entry). Tested both positive (reminder fires when options presented + no
decision doc touched) and negative (silent when doc exists) paths.
**Discovered:** 2026-05-06, after the second consecutive session where I
went straight from "owner picked option X" to scoping work without writing
a decision doc

## Why this audit

In the previous session (Option I I-D), the owner asked: *"why didn't we
write a decision doc? do we have proper stop hooks to remind us to write
a doc when we are stopping work to present options?"* I wrote the doc
manually that time. This session, immediately after picking Option A on a
new decision, I again went into scoping work without writing the doc —
caught only when the owner asked the same question a second time.

That's the failure mode worth mechanizing.

## Findings — current hook landscape

Audited `.claude/settings.json` and `.claude/settings.local.json` in
sacred-patterns, qiyas, and bikar, plus user-level
`/Users/omareid/.claude/settings*.json`.

| Repo            | UserPromptSubmit | PostToolUse | Stop |
|-----------------|------------------|-------------|------|
| sacred-patterns | —                | —           | —    |
| qiyas           | —                | skill-drift, arch-currency, web-curation | — |
| bikar           | repo-identity check | —        | living-artifacts, plan-completion grep, cf-setup-validate |
| user-level      | —                | —           | —    |

Findings:

1. **Sacred-patterns has zero hooks.** That's the gap. Every other repo
   in the cascade has at least one nudge mechanism; sacred-patterns has
   none. Settings file has no `hooks` key.
2. **No "options-presented / decision-needed" hook exists in any of the
   three repos.** Bikar's `Stop` hook greps the last assistant message
   for "plan complete" / "phase N complete" patterns, which is the
   closest precedent. It does *not* match phrases like "stop, awaiting
   decision" or "owner pick A/B/C" or "spec divergence — options below."
3. **Stop hooks are the right vehicle.** They fire at end-of-turn, get
   the last assistant message via stdin, and emit text that lands as
   context in the next turn. Bikar's `check-living-artifacts.py` and the
   inline `plan-completion grep` are working examples.
4. **Stop hooks are non-blocking by convention.** The bikar hooks all
   exit 0 on errors and write reminders to stdout. Adding a new Stop
   hook can't break the conversation flow if it's defensive.

## What a decision-stop-hook should detect

The detector should fire when the assistant *just stopped* with text that
looks like "here are some options, awaiting your pick" but no decision
doc was written this session. Heuristic phrases I'd grep for in the
last assistant message:

- `awaiting (owner|user) (pick|decision|sign-off|review)`
- `options? (below|above|considered)` followed by enumerations like
  `A\. .* B\. .*` or `Option A` / `Option B`
- `recommendation:?\s` near multiple option names
- `STOP[:\s\-—]` (the literal hard-stop marker the loop uses)
- `surfac(ing|ed)\s+(divergence|spec gap|decision)` near a plan/issue
  doc path

And the negative check: in the same session, did anything written under
`docs/decisions/YYYY-MM-DD-*.md` get touched? (Check git status / git
diff.) If nothing, the hook reminds.

False positives are tolerable as long as they're rare and the reminder
is short — the cost of a missed reminder (this session) is higher than
the cost of an extra one.

## Proposed hook — sacred-patterns/.claude/hooks/decision-doc-watch.py

The hook wouldn't install itself — it'd live in the repo and the owner
would need to add it to `.claude/settings.json`. I have NOT created the
hook file or modified settings. Here's the design:

```python
#!/usr/bin/env python3
"""Stop-hook: nudge to write a decision doc when the last assistant
message presented options without recording the choice.

Reads the Stop-hook stdin payload, extracts last_assistant_message,
matches against decision-presenting phrases (see PHRASES below), and if
matched AND no docs/decisions/YYYY-MM-DD-*.md was modified this session,
emits a markdown reminder block.

Defensive: any error → exit 0 silently. Hooks must never block.
"""

import json, re, subprocess, sys
from pathlib import Path

PHRASES = [
    r'awaiting (owner|user) (pick|decision|sign-off|review)',
    r'\bOption\s+[A-D]\b.*\bOption\s+[A-D]\b',  # ≥2 options enumerated
    r'^STOP[:\s\-—]',
    r'surfac(ing|ed)\s+(divergence|spec\s+gap|decision)',
]
PATTERN = re.compile('|'.join(PHRASES), re.IGNORECASE | re.MULTILINE)

def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # malformed payload — never block

    if str(payload.get('stop_hook_active', '')).lower() == 'true':
        return 0  # avoid recursion

    msg = payload.get('last_assistant_message', '') or ''
    if not PATTERN.search(msg):
        return 0  # no decision phrasing, nothing to nudge about

    # Did this session write any decision doc?
    repo_root = Path(__file__).resolve().parent.parent.parent
    try:
        result = subprocess.run(
            ['git', '-C', str(repo_root), 'status', '--porcelain'],
            capture_output=True, text=True, timeout=3,
        )
    except Exception:
        return 0
    decision_doc_touched = any(
        '/decisions/' in line and '.md' in line
        for line in result.stdout.splitlines()
    )
    # Also check sibling repos (qiyas, bikar) since cross-repo decisions
    # often land in those.
    for sibling in ['../qiyas', '../bikar']:
        sib_root = (repo_root / sibling).resolve()
        if not sib_root.exists():
            continue
        try:
            sib = subprocess.run(
                ['git', '-C', str(sib_root), 'status', '--porcelain'],
                capture_output=True, text=True, timeout=3,
            )
            if any('/decisions/' in line and '.md' in line
                   for line in sib.stdout.splitlines()):
                decision_doc_touched = True
                break
        except Exception:
            pass

    if decision_doc_touched:
        return 0  # doc was written this session — no nudge needed

    print(
        "⚠️  The last response presented options or surfaced a decision, "
        "but no `docs/decisions/YYYY-MM-DD-*.md` was written this session.\n"
        "Consider invoking the `decision-doc` skill before continuing — "
        "or, if a doc already exists for this decision, edit it to record "
        "the picked option and rationale."
    )
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

Wired into `.claude/settings.json` like so (similarly defensive shape to
bikar's):

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/decision-doc-watch.py",
        "timeout": 5
      }]
    }]
  }
}
```

## What this hook would NOT catch

- Decisions made **without** explicit option-presenting phrasing (e.g.,
  the owner says "go with X" before I've written down what X is). This
  hook only fires on the option-presenting half of the failure mode.
- Decisions where I write a partial doc (just options, no chosen)
  versus a full doc. The hook only checks "any decision doc touched"
  — quality is up to me / owner review.
- Cross-cascade decisions where the relevant doc lives outside
  `docs/decisions/` (e.g., issue files under `docs/issues/`). Could be
  extended to grep both directories if it turns out to matter.

These are tenet-3-acceptable misses: the hook surfaces the most common
failure mode loudly; the rest stays the responsibility of the
decision-doc skill's "When to STOP and write the doc instead of
continuing" rule. False negatives are tolerable; false positives
(reminding when not needed) are tuned to be rare via the dual condition
(option-phrasing AND no decision-doc edit this session).

## Action requested

I have NOT created the hook file or edited
`.claude/settings.local.json`. Both are explicit-permission actions
under the executing-actions-with-care rules in CLAUDE.md (settings
modifications affect shared state).

If the owner approves, the install would be:
1. Create `.claude/hooks/decision-doc-watch.py` with the body above
   (chmod +x).
2. Edit `.claude/settings.local.json` to add the `hooks.Stop` array.
3. Test by running it manually with a fake stdin payload.
4. Document in CLAUDE.md under a new "Hooks" section.

Awaiting yes/no on installation.

## Cross-repo follow-up (decoupled from sacred-patterns install)

If this pattern works in sacred-patterns, the same hook (or the same
stdin-grep + git-status logic) belongs in qiyas and bikar — both already
have active hook infrastructure and both are decision-rich repos. Filed
mentally as a follow-up; not blocking this audit.
