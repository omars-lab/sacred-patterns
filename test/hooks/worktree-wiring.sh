#!/usr/bin/env sh
# The hooks must actually run in a linked worktree — not merely exist.
#
# THE DEFECT THIS IS THE REGRESSION TEST FOR. `core.hooksPath` was `.husky/_`,
# husky's generated shim directory. It is untracked, so it exists only in the
# checkout where `npm install` last ran. `.git/config` is shared across
# worktrees, so a linked worktree inherited the *setting* and not the
# *directory*, and git's behaviour when hooksPath names a directory that is not
# there is to run nothing and say nothing. Measured 2026-08-17, before the fix:
# a commit whose staged file fails eslint went in at exit 0 with no hook output,
# while the same hook run by hand on the same staged file exited 1.
#
# WHY IT GOES THROUGH `git commit`. Running `.husky/pre-commit` directly proves
# the gate works and proves nothing about the wiring — and the wiring was the
# broken half. Only git can answer "would git have run this?", so the test asks
# git.
#
# WHY THE PROBE IS A SECRET AND NOT A LINT ERROR. The gitleaks block at the end
# of pre-commit is the only one with no staged-path filter, so it runs on any
# commit, and it fails closed both ways: it blocks when the scan finds
# something, and it blocks when gitleaks is not installed. Either way a wired
# hook rejects this commit and an unwired one accepts it, with no dependency on
# node_modules being present in the worktree.
#
# The probe is generated at run time, never checked in. Two reasons: a
# secret-shaped literal in this file would be found by the repo's own pre-push
# scan, and — the lesson 3d-models wrote down after building a dead gate and
# not noticing — a probe gitleaks ignores scans clean and looks exactly like a
# passing test.
#
# That is not a hypothetical caution. The first version of this file used
# `AKIA` + 16 random uppercase characters, and the positive control below
# rejected it on the first run: gitleaks 8.30.x does NOT flag a lone AWS key id,
# only the id paired with a secret. Had the control not been written first,
# this test would have "passed" against a completely unwired repo. Measured the
# same day, these all do flag: a `ghp_` + 36 random token, the AWS id/secret
# pair, a `xoxb-` slack token, and a random OPENSSH private-key block.
set -e

root=$(git rev-parse --show-toplevel)
cd "$root"

wt=$(mktemp -d)/wiring
fail=0

cleanup() {
  git worktree remove --force "$wt" >/dev/null 2>&1 || true
  rm -rf "$(dirname "$wt")" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# A random 36-char suffix, so the result cannot be an allowlisted example token
# and cannot be the sequential placeholder the rule set also filters out.
suffix=$(LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 36)
probe="ghp_$suffix"

if command -v gitleaks >/dev/null 2>&1; then
  # Positive control FIRST. A probe gitleaks ignores would make the real
  # assertion below vacuous — it would pass on an unwired repo too.
  if printf 'token = %s\n' "$probe" | gitleaks stdin --no-banner --redact --exit-code 1 >/dev/null 2>&1; then
    echo "FAIL  positive control: gitleaks did not flag the probe, so the assertion below would be vacuous"
    echo "      (the probe is generated randomly; if this recurs, the rule set has changed)"
    exit 1
  fi
  echo "ok    positive control — gitleaks flags the probe, so a wired hook must reject it"
else
  echo "ok    positive control — gitleaks absent, so pre-commit's own 'not installed' branch must reject it"
fi

git worktree add --detach "$wt" HEAD >/dev/null 2>&1
printf 'token = %s\n' "$probe" > "$wt/o5-wiring-probe.txt"
git -C "$wt" add o5-wiring-probe.txt

# The assertion. `commit` must FAIL. If it succeeds, hooks did not run — which
# is the whole defect, and it is invisible from inside the commit output.
if git -C "$wt" -c user.email=hooks@test -c user.name=hooks \
     commit -m "wiring probe — must be rejected" >/dev/null 2>&1; then
  echo "FAIL  git commit SUCCEEDED in a linked worktree — pre-commit did not run"
  echo ""
  echo "      core.hooksPath = $(git config core.hooksPath || echo '(unset)')"
  echo "      Does that resolve inside a worktree? $([ -e "$wt/$(git config core.hooksPath || echo .husky)" ] && echo yes || echo NO)"
  echo ""
  echo "      Fix: npm run setup-hooks   (points core.hooksPath at the tracked .husky/)"
  fail=1
else
  echo "ok    git commit was rejected in a linked worktree — pre-commit ran"
fi

# The other half of the claim: hooks must be reachable in the MAIN checkout too.
# A hooksPath that resolves only in worktrees would pass the test above and
# still be wrong.
hooks_path=$(git config core.hooksPath || echo "")
if [ -z "$hooks_path" ]; then
  echo "FAIL  core.hooksPath is unset — git is looking in .git/hooks/, which this repo does not populate"
  echo "      Fix: npm run setup-hooks"
  fail=1
elif [ ! -x "$root/$hooks_path/pre-commit" ]; then
  echo "FAIL  core.hooksPath=$hooks_path, but $hooks_path/pre-commit is missing or not executable in the main checkout"
  fail=1
else
  echo "ok    core.hooksPath=$hooks_path resolves to an executable pre-commit in the main checkout"
fi

# And it must be a TRACKED directory, or the fix is only true until the next
# fresh clone. This is the assertion that would have failed on .husky/_.
if [ -n "$hooks_path" ] && ! git ls-files --error-unmatch "$hooks_path/pre-commit" >/dev/null 2>&1; then
  echo "FAIL  $hooks_path/pre-commit is not tracked — it will be absent in a fresh clone and in every worktree"
  fail=1
elif [ -n "$hooks_path" ]; then
  echo "ok    $hooks_path/pre-commit is tracked, so a fresh clone and every worktree have it"
fi

if [ "$fail" -ne 0 ]; then
  echo ""
  echo "hooks: WIRING BROKEN — the gates exist and git is not running them."
  exit 1
fi

echo "hooks: wired — git runs the tracked hooks in the main checkout and in a linked worktree"
