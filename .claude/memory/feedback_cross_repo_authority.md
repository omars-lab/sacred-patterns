---
name: Cross-repo authority — all three repos share one goal
description: User authorizes work in qiyas + bikar + sacred-patterns interchangeably; do not gate cross-repo progress on "wrong repo" reasoning
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
When working under `/loop until we address all our issues` (or any open-ended directive), you are authorized to act in qiyas, bikar, and sacred-patterns interchangeably — the three repos share one main goal (closing the medallion-10 / pattern-fidelity cascade end-to-end).

**Why:** User said explicitly 2026-05-17 in the middle of a sacred-patterns drain loop: "do whatever you need to in other repos / all repos share main goal / remember this." This was triggered by a scheduled-wait state where every remaining sacred-patterns task was blocked on qiyas or bikar work — sitting idle when cross-repo work was available is the failure mode being corrected.

**How to apply:**
- When a loop iteration finds no unblocked work in the current repo, scan TaskList for unblocked tasks in the sibling repos and pick one up rather than scheduling another wait.
- Cross-repo work still respects the "Executing actions with care" rules: don't push/merge/create PRs in any repo without explicit approval. Local commits per tenet 12 are fine in any repo.
- Don't ask "should I switch to qiyas?" mid-loop — just switch when the work is there.
- Continue to use issue/cross-repo-dependency conventions (file under each repo's `docs/issues/`, link via `qiyas#NN` / `bikar#NN` / `sacred-patterns#NN`).
- This does NOT override decision-doc / typed-data / no-silencer tenets — cross-repo authority is about *where* to work, not about lowering quality bars.
