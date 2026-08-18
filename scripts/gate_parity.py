#!/usr/bin/env python3
"""Prove `gate-parity.yaml` covers every git hook gate, and run the whole set.

This repo has **no CI**. There is no `.github/workflows` directory, and nothing
runs on a push or a pull request. Every enforced check lives in
`.husky/pre-commit` or `.husky/pre-push`, and each of those sees only what a
single commit stages. So the question the sibling repos answer with a CI-parity
manifest — *"can I run locally what CI runs?"* — inverts here into a question
that is, if anything, sharper: **what runs the gates over the whole tree, ever?**

Nothing did. A hook is not a substitute for CI in two specific ways, and both
are silent:

1. **Scope.** `eslint src/ts/` fires only when a staged file matches
   `^src/ts/.*\\.ts$`. A commit that touches only `tools/` never runs it, so
   debt accumulates in files no commit is currently touching.
2. **`--no-verify`.** One flag skips every gate in this repo, and there is no
   second line of defence behind it.

`gate-parity.yaml` names each gate block and its **wholesale form** — the same
check run over the tree rather than the staged subset. `--check` proves the
mapping complete in both directions: a gate block with no entry is a hole, and
an entry naming a block that no longer exists is a stale claim. `--run` executes
them, which is what `make local.ci` is.

The name `local.ci` is deliberate and slightly wrong on purpose: this repo has
no CI to be parity *with*, and calling the target `local.ci` is how the next
person finds it, having learned the name in bikar or qiyas. The output says
plainly that there is no remote counterpart, so the name cannot be mistaken for
a claim that something else also ran.

Gate ids are `<hook file>::<gate name>`, declared in the hook itself as a
`# gate: <name>` comment directly above the block. Renaming a gate renames its
id, which fails `--check` until this file is updated — that is the point.

Exit codes for ``--run``: 0 when every runnable gate passed (including the case
where some were NOT VERIFIED), 1 when a gate failed, 2 with ``--strict`` when
anything went unverified.

**Why an unmet precondition does not fail the run.** A gate that cries wolf gets
switched off, which is worse than having no gate. So the caveat is carried in
the *output*: the summary line can never read "all green" when something went
unverified.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import re
import shutil
import tempfile
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "gate-parity.yaml"
HOOKS = REPO / ".husky"

# Only the hooks git actually dispatches. `.husky/_` is husky's generated
# shim directory — untracked, and the thing that was dead in every worktree
# until sacred-patterns#39 pointed core.hooksPath at the tracked `.husky`.
HOOK_FILES = ("pre-commit", "pre-push")

GATE_RE = re.compile(r"^#\s*gate:\s*(?P<name>[\w.-]+)\s*$")


def discover_gates() -> list[str]:
    """Every `# gate: <name>` declaration in the dispatched hooks, in file order.

    Reads the hook files rather than a list, for the same reason the sibling
    repos read `.github/workflows` rather than a list: the source of truth has
    to be the thing that actually runs, or the manifest is checked against a
    second opinion that drifts exactly when it matters.
    """
    ids: list[str] = []
    seen: set[str] = set()
    for name in HOOK_FILES:
        path = HOOKS / name
        if not path.exists():
            raise SystemExit(
                f"gate-parity: {path} does not exist. Every gate in this repo lives in "
                f"a git hook; if that file is gone, so is the gate."
            )
        for line in path.read_text(encoding="utf-8").splitlines():
            m = GATE_RE.match(line.strip())
            if not m:
                continue
            gid = f"{name}::{m.group('name')}"
            if gid in seen:
                raise SystemExit(
                    f"gate-parity: two blocks share the id {gid!r}. Gate names must be "
                    f"unique within a hook — rename one."
                )
            seen.add(gid)
            ids.append(gid)
    return ids


def load_manifest() -> dict[str, Any]:
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8")) or {}


def check() -> int:
    manifest = load_manifest()
    entries = manifest.get("gates") or []
    categories = set(manifest.get("skip_categories") or {})
    preconditions = set(manifest.get("preconditions") or {})

    problems: list[str] = []
    by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        gid = entry.get("id")
        if not gid:
            problems.append(f"entry with no `id:`: {entry!r}")
            continue
        if gid in by_id:
            problems.append(f"duplicate entry for {gid!r}")
        by_id[gid] = entry

        has_wholesale = "wholesale" in entry
        has_skip = "skip" in entry
        if has_wholesale == has_skip:
            problems.append(f"{gid}: needs exactly one of `wholesale:` or `skip:`")
        if has_skip:
            if entry["skip"] not in categories:
                problems.append(
                    f"{gid}: skip category {entry['skip']!r} is not in `skip_categories:`"
                )
            if not entry.get("reason"):
                problems.append(f"{gid}: `skip:` needs a `reason:`")
        if "requires" in entry and entry["requires"] not in preconditions:
            problems.append(
                f"{gid}: requires {entry['requires']!r}, which is not in `preconditions:`"
            )

    actual = discover_gates()
    uncovered = [gid for gid in actual if gid not in by_id]
    stale = [gid for gid in by_id if gid not in actual]

    for gid in uncovered:
        problems.append(
            f"UNCOVERED hook gate, no entry in gate-parity.yaml: {gid}\n"
            f"    Add an entry with `wholesale:` (the same check over the whole tree) "
            f"or `skip:` + `reason:`."
        )
    for gid in stale:
        problems.append(
            f"STALE entry, no such hook gate any more: {gid}\n"
            f"    The `# gate:` block was renamed or removed — update or delete the entry."
        )

    if problems:
        print("gate-parity --check FAILED:\n", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print(
            f"\n  {len(actual)} hook gates, {len(by_id)} manifest entries.",
            file=sys.stderr,
        )
        return 1

    runnable = sum(1 for e in entries if "wholesale" in e)
    gated = sum(1 for e in entries if e.get("requires"))
    extras = len(manifest.get("local_only") or [])
    print(
        f"gate-parity: OK — {len(actual)} hook gates, all mapped "
        f"({runnable} runnable wholesale, {gated} of those need a precondition, "
        f"{len(entries) - runnable} skipped with a reason), "
        f"plus {extras} check(s) no hook runs at all."
    )
    return 0


def _probe(precondition: dict[str, Any]) -> bool:
    probe = precondition.get("probe")
    if not probe:
        return True
    return (
        subprocess.run(  # noqa: S602 - probes come from a checked-in manifest
            probe,
            shell=True,
            capture_output=True,
        ).returncode
        == 0
    )


def run(strict: bool, include_local_only: bool) -> int:
    manifest = load_manifest()
    entries = manifest.get("gates") or []
    preconditions = manifest.get("preconditions") or {}

    probe_cache: dict[str, bool] = {}
    passed: list[str] = []
    failed: list[tuple[str, int]] = []
    unverified: list[tuple[str, str]] = []

    def label(gid: str) -> str:
        return gid.split("::", 1)[-1]

    for entry in entries:
        if "wholesale" not in entry:
            continue
        gid = entry["id"]
        need = entry.get("requires")
        if need:
            if need not in probe_cache:
                probe_cache[need] = _probe(preconditions.get(need) or {})
            if not probe_cache[need]:
                hint = (preconditions.get(need) or {}).get("hint", "")
                unverified.append((gid, hint))
                print(f"[NOT VERIFIED] {label(gid)}  ({need} unavailable)")
                continue
        print(f"\n==> {label(gid)}\n    $ {entry['wholesale']}")
        started = time.monotonic()
        rc = subprocess.run(entry["wholesale"], shell=True, cwd=REPO).returncode  # noqa: S602
        took = time.monotonic() - started
        if rc == 0:
            passed.append(gid)
            print(f"    ok ({took:.1f}s)")
        else:
            failed.append((gid, rc))
            print(f"    FAILED rc={rc} ({took:.1f}s)")

    if include_local_only:
        for extra in manifest.get("local_only") or []:
            print(f"\n==> [no hook runs this] {extra['command']}")
            rc = subprocess.run(extra["command"], shell=True, cwd=REPO).returncode  # noqa: S602
            if rc == 0:
                passed.append(extra["command"])
                print("    ok")
            else:
                failed.append((extra["command"], rc))
                print(f"    FAILED rc={rc}")

    print("\n" + "=" * 72)
    if unverified:
        print("NOT VERIFIED — these gates did not run on this machine:")
        for gid, hint in unverified:
            print(f"  - {label(gid)}")
            if hint:
                print(f"      {hint.strip()}")
        print(
            "\n  A green summary below means green on what ran. This repo has no CI,\n"
            "  so there is nothing else that will catch what went unrun here."
        )
        print("=" * 72)

    for gid, rc in failed:
        print(f"FAILED: {label(gid)} (rc={rc})")

    # The summary line is the whole contract of this tool: it must never read
    # like a clean bill of health when something went unrun.
    if failed:
        verdict = f"{len(failed)} FAILED"
    elif unverified:
        verdict = f"{len(passed)} verified, {len(unverified)} NOT VERIFIED"
    else:
        verdict = f"all {len(passed)} verified"
    print(f"gate-parity: {verdict}  (no CI in this repo — this is the only run)")

    if failed:
        return 1
    if unverified and strict:
        print("gate-parity: --strict — an unverified gate is a failure here.")
        return 2
    return 0


# ---------------------------------------------------------------- self-test
#
# The by-design failure is the load-bearing case. A parity checker that only
# ever sees a correct manifest reports OK forever, including on the day it
# stops looking. `--check` on the real repo cannot stand in for this: it is the
# assertion that everything is fine, so it is green both when the repo is
# correct and when the checker has gone blind. Only a fixture can hold the
# counterexample — and the distinction bites hardest on the discoverer.
# Breaking GATE_RE is caught here only incidentally, because the 15 written
# entries all report STALE; against an empty manifest the same bug reads
# "0 hook gates, all mapped", which is the vacuous green.
#
# This repo has no CI, so there is no second opinion downstream. That makes the
# self-test the only thing standing between a silent regression here and a
# green summary line that a merge decision rests on.


def _fixture(tmp: Path, pre_commit: str, manifest: str, pre_push: str = "#!/bin/sh\n") -> None:
    (tmp / ".husky").mkdir(parents=True, exist_ok=True)
    (tmp / ".husky" / "pre-commit").write_text(pre_commit, encoding="utf-8")
    (tmp / ".husky" / "pre-push").write_text(pre_push, encoding="utf-8")
    (tmp / "gate-parity.yaml").write_text(manifest, encoding="utf-8")


@contextlib.contextmanager
def _rooted(tmp: Path):
    """Point the module's three path globals at a fixture repo."""
    global REPO, MANIFEST, HOOKS
    saved = (REPO, MANIFEST, HOOKS)
    REPO, MANIFEST, HOOKS = tmp, tmp / "gate-parity.yaml", tmp / ".husky"
    try:
        yield
    finally:
        REPO, MANIFEST, HOOKS = saved


def _capture(fn) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        rc = fn()
    return rc, out.getvalue()


# The declaration is a comment, which is the one line a shell will never
# complain about being wrong. Nothing but GATE_RE reads it, so if GATE_RE
# stops matching the spelling the hooks use, every gate silently vanishes
# from the manifest's field of view. That is the first case below.
_HOOK_OK = """\
#!/bin/sh
# gate: alpha
echo a

# gate: beta
echo b
"""

_MF_OK = """\
skip_categories:
  interactive: needs a human at a keyboard
gates:
  - id: 'pre-commit::alpha'
    wholesale: 'true'
  - id: 'pre-commit::beta'
    skip: interactive
    reason: nothing to run unattended.
"""


def self_test() -> int:
    failures: list[str] = []
    ran: list[str] = []

    # The count in the closing line is derived, not typed. A hand-written
    # "all 14 checks pass" beside 15 expect() calls is the same defect class
    # this file exists to catch, one level up.
    def expect(name: str, ok: bool, detail: str = "") -> None:
        ran.append(name)
        if ok:
            print(f"  ok   {name}")
        else:
            failures.append(f"{name}{': ' + detail if detail else ''}")
            print(f"  FAIL {name}{': ' + detail if detail else ''}")

    print("gate-parity --self-test:")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        with _rooted(tmp):
            # 1. The `# gate:` declarations must actually be seen.
            _fixture(tmp, _HOOK_OK, _MF_OK)
            rc, out = _capture(check)
            expect("`# gate:` declarations are discovered", "2 hook gates" in out, out.strip())
            expect("a complete manifest passes", rc == 0, out.strip())

            # 2. Drift in either direction is a failure, not a shrug.
            _fixture(tmp, _HOOK_OK.replace("# gate: beta\necho b\n", ""), _MF_OK)
            rc, out = _capture(check)
            expect("a manifest entry for a vanished gate is STALE",
                   rc == 1 and "STALE" in out, out.strip())

            _fixture(tmp, _HOOK_OK + "\n# gate: gamma\necho g\n", _MF_OK)
            rc, out = _capture(check)
            expect("a hook gate with no entry is UNCOVERED",
                   rc == 1 and "UNCOVERED" in out, out.strip())

            # 3. A hook file that is gone is a gate that is gone — the check
            #    must say so rather than discovering zero gates and passing.
            _fixture(tmp, _HOOK_OK, _MF_OK)
            (tmp / ".husky" / "pre-push").unlink()
            rc, out = _capture(lambda: _swallow_exit(check))
            expect("a missing hook file is fatal, not zero gates",
                   rc != 0 and "does not exist" in out, out.strip())

            # 4. Two blocks cannot share a name, or one of them is invisible.
            _fixture(tmp, _HOOK_OK + "\n# gate: alpha\necho again\n", _MF_OK)
            rc, out = _capture(lambda: _swallow_exit(check))
            expect("a duplicate gate name is rejected",
                   rc != 0 and "share the id" in out, out.strip())

            # 5. Entry shape. Exactly one of wholesale:/skip:, skip: needs why.
            _fixture(tmp, _HOOK_OK, _MF_OK.replace(
                "    wholesale: 'true'",
                "    wholesale: 'true'\n    skip: interactive\n    reason: both"))
            rc, out = _capture(check)
            expect("both `wholesale:` and `skip:` is rejected",
                   rc == 1 and "exactly one" in out, out.strip())

            _fixture(tmp, _HOOK_OK, _MF_OK.replace("    reason: nothing to run unattended.\n", ""))
            rc, out = _capture(check)
            expect("`skip:` without a `reason:` is rejected",
                   rc == 1 and "needs a `reason:`" in out, out.strip())

            _fixture(tmp, _HOOK_OK, _MF_OK.replace("skip: interactive", "skip: invented"))
            rc, out = _capture(check)
            expect("an unlisted skip category is rejected",
                   rc == 1 and "not in `skip_categories:`" in out, out.strip())

            _fixture(tmp, _HOOK_OK, _MF_OK.replace(
                "    wholesale: 'true'", "    wholesale: 'true'\n    requires: nosuch"))
            rc, out = _capture(check)
            expect("a `requires:` naming no declared precondition is rejected",
                   rc == 1 and "not in `preconditions:`" in out, out.strip())

            # 6. The summary line. This is the sentence a merge rests on, and
            #    in a repo with no CI it is the only sentence there is.
            _fixture(tmp, _HOOK_OK, """\
preconditions:
  nope:
    probe: 'exit 1'
    hint: deliberately unsatisfiable.
skip_categories:
  interactive: needs a human at a keyboard
gates:
  - id: 'pre-commit::alpha'
    wholesale: 'true'
  - id: 'pre-commit::beta'
    wholesale: 'true'
    requires: nope
""")
            rc, out = _capture(lambda: run(strict=False, include_local_only=False))
            expect("an unmet precondition reports NOT VERIFIED",
                   "NOT VERIFIED" in out, out.strip())
            expect("the summary never claims all-verified when one went unrun",
                   "gate-parity: 1 verified, 1 NOT VERIFIED" in out
                   and "all 2 verified" not in out, out.strip())
            expect("--run exits 0 on an unmet precondition (a gate that cries "
                   "wolf gets switched off)", rc == 0, out.strip())
            rc, out = _capture(lambda: run(strict=True, include_local_only=False))
            expect("--strict turns the same run into exit 2", rc == 2, out.strip())

            # 7. A failing wholesale command is a failure, full stop.
            _fixture(tmp, _HOOK_OK, _MF_OK.replace("    wholesale: 'true'", "    wholesale: 'exit 3'"))
            rc, out = _capture(lambda: run(strict=False, include_local_only=False))
            expect("a failing gate exits 1 and is named",
                   rc == 1 and "1 FAILED" in out, out.strip())

    if failures:
        print(f"\ngate-parity --self-test FAILED ({len(failures)}):", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"gate-parity --self-test: all {len(ran)} checks pass.")
    return 0


def _swallow_exit(fn) -> int:
    """discover_gates() raises SystemExit for the two structural faults.

    Catching it here keeps those two cases inside the same expect() shape as
    the rest — the point being that they are loud, not how they are loud.
    """
    try:
        return fn()
    except SystemExit as e:
        print(str(e))
        return 1

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="prove the manifest covers the hooks")
    group.add_argument("--run", action="store_true", help="run every gate's wholesale form")
    group.add_argument(
        "--self-test",
        action="store_true",
        help="prove --check and --run fail on manifests that should fail",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="with --run: exit 2 if any gate could not be verified",
    )
    parser.add_argument(
        "--with-local-only",
        action="store_true",
        help="with --run: also run the checks no hook runs at all",
    )
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.check:
        return check()
    if not shutil.which("make"):
        print("gate-parity: `make` not found on PATH.", file=sys.stderr)
        return 1
    return run(strict=args.strict, include_local_only=args.with_local_only)


if __name__ == "__main__":
    sys.exit(main())
