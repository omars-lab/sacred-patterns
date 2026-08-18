# Running every gate over the whole tree

## The one command

```sh
make local.ci
```

It runs every git-hook gate in its **wholesale form** — the same check over the
whole tree instead of the staged subset — plus the checks no hook runs at all,
and it names anything it could not verify. The last line is the whole contract:

```
gate-parity: all 5 verified                      (no CI in this repo — this is the only run)
gate-parity: 3 verified, 2 NOT VERIFIED          (no CI in this repo — this is the only run)
gate-parity: 4 FAILED                            (no CI in this repo — this is the only run)
```

Two variants:

- `make local.gate-parity` — the hook gates only, without the unwired checks.
- `make local.ci-strict` — as `local.ci`, but an unverifiable gate is a
  **failure** (exit 2). `local.ci` exits 0 on an unmet precondition on purpose:
  a gate that cries wolf on a laptop missing `yq` gets switched off, which is
  worse than a gate that reports honestly.

The target is called `local.ci` even though this repo has no CI, because that is
the name the next person will have learned in bikar or qiyas. The parenthetical
on the summary line exists so the name can never be mistaken for a claim that
something else also ran.

## Why this repo's version is the inverted one

bikar and qiyas answer *"can I run what CI runs?"*. There is no
`.github/workflows` directory here and nothing runs on a push or a pull request,
so that question has no content — and a sharper one takes its place: **what runs
these gates over the whole tree, ever?**

Nothing did. A hook is not a CI job in two ways, and both are silent:

1. **Scope.** The lint/typecheck block fires only when a staged path matches
   `^src/ts/.*\.ts$`. A branch that touches only `tools/` never runs it, and the
   debt sits in files no commit happens to be touching.
2. **`--no-verify`.** One flag skips every gate in this repo, and there is no
   second line of defence behind it. sacred-patterns#39 is the reminder that
   this is not theoretical: `core.hooksPath` pointed at husky's generated
   `.husky/_`, which `npm install` creates and git never tracks, so in a fresh
   worktree a file failing eslint committed at exit 0 with no hook output at all.

## Why a manifest and not a make target

A hand-maintained "run all the gates" chain drifts the first time somebody adds
a hook block, and reports success the whole time it is wrong. So the mapping is
**data** — [`gate-parity.yaml`](../gate-parity.yaml) — and
[`scripts/gate_parity.py`](../scripts/gate_parity.py) proves it complete in both
directions:

- a `# gate:` block with no entry is a hard failure (`UNCOVERED`);
- an entry naming a gate that no longer exists is a hard failure (`STALE`).

Both directions are exercised: renaming one entry produces `UNCOVERED` *and*
`STALE` in the same run, which is what makes the check a mapping rather than a
count.

Gate ids are `<hook file>::<gate name>`, and the name is declared in the hook
itself as a `# gate: <name>` line above the block — so the source of truth is the
file git actually dispatches, not a second list that drifts exactly when it
matters.

The check runs in two places, and the first is self-referential on purpose:

1. `.husky/pre-commit`, as its own `# gate: gate-parity` block carrying its own
   manifest entry. It earned that entry immediately — the moment the block was
   added, `--check` reported it `UNCOVERED`. An unmapped parity gate is the one
   hole the mapping could never see.
2. As a prerequisite of every `local.ci*` target, so the runner never runs
   against a mapping it has not just proved complete.

## What the first honest run found

Every one of the five hook gates passes wholesale. **Four of the five checks
that no hook runs at all are red**, and all four failures are in `tools/` — the
directory no hook trigger reaches:

| check | result |
|---|---|
| `npm run build && npm test` | needed the build first; `test/regression/check.js` reads `site/bundle.js` and exits 1 without it |
| `make tool-tests` | 3 of 63 failing — `tools/tests/test_studio_field_defaults_bounded.py` |
| `make spelling` | 11 hits — ten in `tools/wave-plan-server.py`, one in `tools/tests/` |
| `make semgrep` | 1 finding — dynamic `urllib.request.urlopen` in `tools/weave-only-compare.py` |

Two of those targets carried a comment asserting they were clean: semgrep's said
*"0 findings at baseline"* and spelling's said *"triaged to 0 at baseline"*.
Nothing had re-run either since the day it was written, so nothing rechecked the
claim — the same defect this manifest exists to stop, arriving from the other
side. Both comments are corrected to say what was measured. **The findings are
left red rather than baselined away**; fixing them is separate work.

## What it verifies, and what it does not

Ask the tool, do not retype from memory — `python3 scripts/gate_parity.py
--check` prints the current split.

One skip category is defined in the manifest:

- **`no-wholesale-form`** — the staged-subset form *is* the whole check; there
  is no larger tree-wide version to run. `pre-commit::gitleaks-staged` is the
  only member: its tree-wide form is exactly the `pre-push` history scan, which
  is mapped, and running both would report one finding as two.

**A wholesale green covers the tree at this commit, not the history.** Only the
gitleaks pre-push gate looks backwards.

## Troubleshooting

### `yq` or `jq` missing

`brew install yq jq`. The decision gates read structured frontmatter through
them. They report NOT VERIFIED rather than passing over, and with no CI here,
nothing else will run them later.

### `gitleaks` missing

`brew install gitleaks`. History goes unscanned with no backstop; a pushed
credential is compromised whether or not the commit is later removed.

Note that `make gitleaks` still says `gitleaks detect`, the pre-8.19 spelling of
a different subcommand than the one the hooks use. The target and the hook had
already drifted apart before this file existed — which is the drift the manifest
now pins.

### `node_modules` missing — two gates report NOT VERIFIED

`npm ci`. Every `npm run` gate needs it, and without it they exit 127 "command
not found". Until 2026-08-18 the runner reported that as **FAILED**, which is
the wrong sentence: FAILED is a claim about the branch, and *eslint is not
installed in this checkout* is a claim about the machine. Two gates
(`pre-commit::typecheck-lint` and the `npm run build && npm test` local-only
entry) now carry `requires: node-modules` and say NOT VERIFIED instead.

The gap was structural rather than an oversight in one entry: `local_only:`
entries had no `requires:` support at all, so exactly half the manifest could
not express "did not run" — and the half that could not is the half no hook
covers, which is the half most likely to be missing a tool. It surfaced the
first time this ran in a fresh git worktree, because that is the only place the
precondition is genuinely absent; a repo you have been working in all day never
shows it to you. `--self-test` now carries five cases for the `local_only:`
half specifically.

### `codespell` / `semgrep` missing

`pip install codespell semgrep`. Each failure names the command; none is
silently skipped.

### `ERROR: site/bundle.js not found`

Run `npm run build` first. The manifest's `local_only` command is
`npm run build && npm test` for exactly this reason — an ordering nothing stated,
because nothing ran the pair.

### The parity gate itself fails

```
UNCOVERED hook gate, no entry in gate-parity.yaml: <id>
```

You added a `# gate:` block. Add an entry saying how to run it over the whole
tree (`wholesale:`) or why there is no such form (`skip:` + `reason:`). This is
the gate working — the moment to write that down is while you still remember why
the block exists.

```
STALE entry, no such hook gate any more: <id>
```

A gate was renamed or removed. Update or delete the entry.

## The other repos

bikar and qiyas each carry a `ci-parity.yaml` + `scripts/ci_parity.py` against
their `.github/workflows`, with the same entry kinds and the same `local.ci` /
`local.ci-strict` targets; their runbooks are `bikar:docs/local-ci-runbook.md`
and `qiyas:docs/local-ci-runbook.md`. 3d-models has no workflows either, and its
`.githooks/pre-commit.d/` hooks are its CI — `make validate` runs every one over
the whole tree, and `3d-models:.claude/gates/hook_parity.py` fails a hook that
does not declare its own wholesale form.

**The pattern across all four.** Every repo in this family had a gate that read
like a working one and could not run: this repo's `core.hooksPath` pointing at an
untracked directory, 3d-models' `.git/hooks` guard that `core.hooksPath` made
unreachable, qiyas's `local.ci` covering 3 of 8 CI steps under a name that
claimed all of them, and bikar's covering 5 sub-targets against 6 workflows.
None was caught by a test, because each was tested by running the thing it wired
*directly*, which answers a different question. **Assert the wiring through the
mechanism that uses it:** ask git to commit, not the hook to run — and ask the
manifest what the gates are, not the Makefile what you remember it running.
