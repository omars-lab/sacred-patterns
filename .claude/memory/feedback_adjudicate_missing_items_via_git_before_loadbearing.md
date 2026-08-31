---
name: adjudicate-missing-items-via-git-before-loadbearing
description: "a decision doc's \"N items are missing/dropped/excluded\" premise must be git-provenance-adjudicated before it drives an option's cost or scope"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When a decision doc's premise is "N artifacts are missing from / dropped by / excluded from X" (a corpus index, a baseline set, a manifest), **adjudicate each of the N via `git log --oneline -1 <path>` before that count becomes load-bearing** for an option's cost, scope, or recommendation. The dirname/label is not provenance; the commit subject is.

**Why:** qiyas#656 (2026-05-28) — the `2026-05-28-i1-ratchet-tree-walk-vs-index.md` doc claimed "7 real witnesses dropped from the corpus index," and Option A was costed at 2-3 days partly to "add the 7 back." Git adjudication (`git log -1` per dir) proved all 7 were FALSIFIED #132 Tick experiments — their commit subjects all contained `FALSIFIED`; they simply lacked the `FALSIFIED-` *dirname* prefix that the other 8 phantoms had. None belonged in the index. The corrected premise dissolved the "add 7 witnesses" prerequisite entirely, collapsing Option A to a half-day pure-CLI change that removes 18 never-meant-to-be-scored dirs. The premise had been built from dirname pattern-matching, not provenance.

**How to apply:** the moment a doc (or a plan, or a task) leans on a "these items are missing/extra/wrong" count, run the provenance check on each item *before* writing the recommendation or the cost. For corpus/baseline/fixture sets: `git log --oneline -1 <dir-or-file>` and read the subject — FALSIFIED/experiment/probe commits are not corpus members regardless of where they sit on disk. If even one item flips, re-derive the count; the option weighing built on the wrong count is itself falsified (handle-falsification L3: enumeration-premise wrong, not mechanism). This is the same shape as [[feedback_pattern_extrapolation_at_n5_breaks_at_n6]] — a pattern read off surface features (dirname prefix / N witnesses) isn't load-bearing until the discriminating property (commit provenance / out-of-class witness) is checked directly.

**Companion to:** handle-falsification skill (L3 enumeration introspection), present-options §4 (every premise-question needs a named answer-source — here the source is `git log`, not the dirname), Tenet 4 (verify before claiming done).
