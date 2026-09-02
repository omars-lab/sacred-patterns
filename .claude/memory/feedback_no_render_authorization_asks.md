---
name: no-render-authorization-asks
description: "Never gate work on \"authorize the render\" / \"authorize the re-render\" / similar reversible session-directory mutations — just do it"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

Never present blockers of the shape "authorize the bikar-medallion-10 iter-N render", "authorize the re-render", "authorize the orchestrator run", or any equivalent permission-ask for reversible session-directory mutations. Bias to act: run the render, observe the output, move on. The render itself is reversible (output lands in a new iter-N+1 subdir; nothing prior is overwritten) and falls inside the existing autonomy contract.

**Why:** 2026-05-25 — after presenting "unblock options" that included "Option A: Authorize the bikar-medallion-10 iter-18 render (one-shot)" and "Option B: Standing authorization for re-render an existing iteration everywhere", owner direction was "I never want to see blockers like 'Authorize the bikar-medallion-10 iter-18 render (one-shot)' again, you should be biasing to act, do the change and move on." The session-directory render fear was an artifact of an earlier permission-denial precedent that was over-generalized. The actual rule is: reversible operations whose worst-case outcome is "a new file appears in a session subdir" are pre-authorized; they don't need a question.

**How to apply:** When the next move is a render, re-render, orchestrator re-run, or any non-destructive session/output mutation that produces *new* files (not overwriting existing ones), just run it. Don't author an "Option A — authorize this" bullet. Don't ask. The artifacts the loop produces are themselves the audit trail. If the render fails or surfaces a regression, *that* is the moment to report — not "may I render?". Companion to [[feedback_decision_pick_authorization]] (decision-pick authority) and [[feedback_push_authorization_general]] (push authority) — together these form the autonomy contract: ship documented defaults, push tested-green chunks, run reversible orchestrator steps without asking.

**Anti-pattern this names:** presenting a menu where one option is "let me do the obvious safe next thing" — the menu itself is the failure. The right shape: do the thing, report the outcome. If there's a genuine fork (e.g., two equally-weighted decisions where evidence can only come from owner intent), present *that* — not the routine work.
