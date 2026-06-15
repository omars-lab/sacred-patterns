---
# human-readable (kept; never machine-parsed)
status: ACCEPTED 2026-06-15 — Option A (mirror-layout — code → git sessions/<name>/, images → Dropbox, handoff+plans → .claude/)
discovered: 2026-06-15
decided: 2026-06-15
owner: omareid
# structured (machine-read — the contract)
status_token: ACCEPTED
picked_option: A
tag: session-artifact-storage
supersedes: []
superseded_by: []
related:
  - seam: tools/start-session.py
  - claude-md: CLAUDE.md
  - memory: feedback_plain_language_in_plans.md
---

## 0. Premise check (MANDATORY)

**Premise:** "Reconstruction-session artifacts all live in Dropbox
(`~/Library/CloudStorage/Dropbox/Data/sacred-patterns/<name>/`), so the *code*
that drives a session — the generators, clusterers, regression tests, the `.bkr`
constructions, the analysis notes — has no version history, no diff review, no
CI reach, and cannot be code-reviewed. Only the images need a blob store; the
code needs git."

**Verified against the actual session tree** (`bikar-medallion-10`, read
2026-06-15). The premise holds and the split is clean. A file-type census across
`iterations/`:

| ext | count | nature | belongs in |
|-----|-------|--------|------------|
| `.png` | 1870 | rendered raster output | Dropbox (blob) |
| `.svg` | 152 | rendered vector output | Dropbox (blob) |
| `.json` | 697 | mostly generated (`pattern.gt.json` 7 MB, per-wave `clusters.json`) | Dropbox (generated blob) |
| `.py` | 60 | **generators, clusterer, regression tests** | **git** |
| `.bkr` | 103 | **the pattern constructions (source-of-record)** | **git** |
| `.md` | 107 | **analysis, hypothesis, discoveries notes** | **git** |
| `.html`| 19 | generated cluster atlases / proofs | Dropbox (generated) |
| `.log`/`.txt`/`.err` | 133 | run logs | Dropbox (ephemeral) |

The dividing line is **authored vs rendered**: a human (or the loop) *wrote* the
`.py` / `.bkr` / `.md`; a tool *emitted* the `.png` / `.svg` / big `.json`. The
authored side is what a future session re-runs, re-reads, and re-reviews — it is
code and must be versioned. The rendered side is large, regenerable from the
authored side, and only ever *looked at* — it stays a Dropbox blob.

**LEDGER lookup (tag `session-artifact-storage`):** no prior doc on this tag
(`grep docs/decisions/*.md` 2026-06-15 — tag newly added to `tags.yaml` in this
same commit per Tenet C5). This is the first authoritative decision on where
session artifacts live.

## 1. Context — what the owner asked

Verbatim, across five messages (2026-06-15):
> "what should we naturally move from dropbox to source control … i think
> iterations code should be in source control but images in dropbox … how do we
> update things / set our skills up / etc in this regard?"
> "also handoff prompts, etc should be moved to .claude/"
> "along with plans / etc"
> "this mental model should be in the claude..md too"
> "we should have a dedicated directory to hold our iterations code wise in the
> sacred-patterns repo itself"

The ask is a **storage-routing rule**, not a one-off move: every future session
must know, without re-deciding, which artifact goes where.

## 2. Options

- **Option A — Mirror layout (PICKED).** Code lives in the repo at
  `sacred-patterns/sessions/<name>/` at the *same relative path* it has in
  Dropbox; images stay in Dropbox at the same relative path. Handoff prompts and
  plans move to `.claude/`. The two trees mirror each other path-for-path, so a
  tool or human can map a code file to its render by swapping the root.
- **Option B — Everything in git (images via Git LFS).** Rejected: 1870 PNGs +
  152 SVGs is a multi-GB blob history; LFS adds a billing + bandwidth surface and
  defeats the "images are cheap to regenerate" property. The owner explicitly
  said images stay in Dropbox.
- **Option C — Everything in Dropbox, symlink code into git.** Rejected:
  symlinks across CloudStorage are fragile, don't diff, and don't reach CI. The
  code would still have no real version history.

## 3. Decision — the mirror-layout contract

**Code → git.** A new dedicated directory `sacred-patterns/sessions/<name>/`
holds every *authored* artifact of a reconstruction session:
- `.bkr` constructions (the source-of-record patterns)
- `.py` generators, clusterers, slicers, regression tests
- `.md` analysis / hypothesis / discoveries / handoff-adjacent notes
- `session.json` (the gate-of-record) — small, hand/loop-edited, must be diffable
- Any hand-authored config the session depends on

**Images → Dropbox.** Every *rendered* artifact stays at
`~/Library/CloudStorage/Dropbox/Data/sacred-patterns/<name>/` at the same
relative path:
- `.png` / `.svg` renders, crops, overlays, proofs, cluster atlases
- large generated `.json` (`pattern.gt.json`, per-wave `clusters.json`)
- `.log` / `.txt` / `.err` run logs

**Handoff prompts + plans → `.claude/`.** `CLOSEOUT-PROMPT.md`, `LOOP-PROMPT.md`,
`OPEN-TASKS.md` and the like move under `.claude/` (handoff prompts referenced by
`/loop`); plans live in `.claude/plans/` (already the convention).

**Mirror invariant:** the relative path is identical in both roots. A render at
Dropbox `<name>/iterations/71/render.png` corresponds to code at git
`sessions/<name>/iterations/71/pattern.bkr` — swap the root, keep the path. This
is what makes "given a render, find the code that made it" a path-swap, not a
search.

## 4. How it propagates (the seam changes)

1. **`tools/start-session.py`** — currently `--base` defaults to
   `Path.home()/"Dropbox/Data/sacred-patterns"` (L67). Split into two roots:
   `--code-base` (default `<repo>/sessions`) and `--image-base` (default the
   Dropbox path). Authored files write under `--code-base`; rendered files under
   `--image-base`. The mirror invariant means both use the same `<name>/...`
   suffix.
2. **`.gitignore`** — `sessions/**/*.png`, `*.svg`, `*.log`, `*.err`,
   `pattern.gt.json`, `clusters.json`, `cluster-atlas.png` etc. are ignored so a
   stray render committed into `sessions/` doesn't bloat history. (Belt-and-braces:
   renders are supposed to write to Dropbox, but the ignore catches mistakes.)
3. **Skills** — `/pattern-decomposition` and any skill that writes session files
   reference the two roots, not one Dropbox path.
4. **CLAUDE.md** — the mental-model section (this commit) so every cold session
   reads the rule before touching a session file.

## 5. Migration

`bikar-medallion-10` is the live session. Its code (`.py`/`.bkr`/`.md`/
`session.json`) copies into `sacred-patterns/sessions/bikar-medallion-10/` at the
mirrored path; images stay put. This is a **copy-then-verify**, not a move — the
Dropbox tree stays intact until the git mirror is confirmed renderable, so no
in-flight loop work is lost. Migration is a follow-on task, not part of this
decision commit (which is doc + tag + CLAUDE.md only, no file moves).

## 6. Consequences

- **Won:** session code gets version history, diff review, CI reach, and
  code-review; the `.bkr` source-of-record is finally tracked; a cold session
  reads the routing rule from CLAUDE.md instead of guessing.
- **Cost:** start-session.py and the decomposition skills carry a two-root seam;
  the mirror invariant must be maintained by tooling (a render and its code no
  longer sit in the same directory).
- **Reversible?** Yes — the mirror invariant means re-collapsing to one root is a
  path-preserving copy.
