---
name: audit-pending-tasks-against-slice-plans
description: "pending tasks pointing at a slice plan must be re-checked against that plan's status (shipped slices, deferred slices, trigger conditions) before being treated as unblocked-actionable"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When the open-task list shows a `[pending]` task whose subject references a multi-slice plan ("A5 detector", "F2 cascade", "Universal DSL Tagging Slice N"), read the plan file before classifying the task as Class-5 unblocked-actionable work. The task description was authored at task-creation time; slices may have shipped, been re-scoped, or been deferred behind triggers since then, with the per-task status never updated.

**Why:** 2026-05-30 idle tick — tasks #25/#59/#60 looked like "unblocked but unstarted A5 work" in every audit. Reading `qiyas/.claude/plans/a5-slices.md` revealed Slices 1+4 already SHIPPED 2026-05-01 and Slices 2-3 are DEFERRED behind a strapwork witness trigger. Three idle ticks scheduled before noticing.

**How to apply:** Before declaring "no Class-5 work" in an autonomous-loop idle tick, for every `[pending]` task pointing at a `.claude/plans/<slice>.md` file: read the plan's status block, check shipped/deferred/trigger sections, then either (a) update the task description to reflect the actual gating, (b) re-classify it as trigger-gated and stop re-evaluating it, or (c) confirm it's genuinely unblocked. The Class-5 "look harder" pass IS this audit — looking at task subjects alone misses stale gating.

**Companion to:** [[reference_post_i1_routing_plan]], [[feedback_cross_repo_authority]], [[project_2026_05_24_decisions]] — those memories cover *what* to pick up; this one covers *how to know* a candidate is genuinely actionable vs stale.
