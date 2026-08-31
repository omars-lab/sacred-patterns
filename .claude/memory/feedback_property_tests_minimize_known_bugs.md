---
name: Property tests minimize known-but-elusive bug reproducers
description: When a known bug has only one hand-picked reproducer, hypothesis shrinking will often find a smaller / more general one within the same property — file as second witness even if the fix is deferred
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
When adding property tests to a module that has a known-OPEN bug with a single hand-picked reproducer (e.g. qiyas#268's `scalene_triangle` combined-transforms failure), hypothesis will frequently surface the same failure class with a much smaller / structurally different reproducer in the very first run. Capture both reproducers in the issue doc as independent witnesses — they constrain the eventual fix harder than one fixture would.

**Why:** the original bug in qiyas#268 was found via one example. The property test for `test_starting_vertex_invariant` falsified at `[19.5, 1.0, 1.0]` (extreme-aspect triangle) on the *first* hypothesis run, and `test_combined_transforms` falsified at `[1.0, 1.0, 2.0, 1.0]` (asymmetric quad, no rotation/scale/translate, just start-shift). Both minimal via shrinking. Both are now in the issue doc as witness #2 and witness #3, constraining the fix far more than the single original reproducer could.

**How to apply:** when adding property tests to a module with an OPEN issue tracking a known bug, (a) don't be surprised when the property surfaces the same bug, (b) mark the test `xfail(strict=False, reason="...")` linked to the issue doc, (c) append the shrunk reproducer to the issue doc as an independent witness, (d) ship the property test alongside the issue note. This is tenet 3 (surface, don't hide) — the failing test stays visible until the fix lands, and the failure now has two independent reproducers instead of one.

**Anti-pattern to avoid:** seeing the property fail on the known bug and either (i) silently skipping the test, or (ii) deciding "the property test doesn't add value because we already know about the bug." Both are wrong — the SECOND witness is the value-add, regardless of whether the bug is already filed.
