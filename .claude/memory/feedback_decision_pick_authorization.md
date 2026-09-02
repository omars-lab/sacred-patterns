---
name: decision-pick-authorization
description: Standing authorization to ship documented defaults on owner-PENDING decision docs when mechanism is reversible and rationale exists; granted 2026-05-24
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

Under the standing `/loop` directive, when a critical-path task is blocked solely on an owner pick AND a decision doc names a default option AND the mechanism is reversible (no force-push, no destructive deletion of others' work), the loop is **pre-authorized** to ship the default and report the outcome via commit message + chat update.

**Why:** owner granted 2026-05-24 after the 2026-05-23 7-task gridlock (decision doc `sacred-patterns/docs/decisions/2026-05-23-unblock-critical-path-workstream.md` Option B). Per-pick gating burned 4 heartbeat cycles and produced zero throughput; one standing authorization clears the queue. Companion to [[feedback_push_authorization_general.md]] and [[feedback_cross_repo_authority.md]] — the third leg of the autonomy contract (push autonomy + repo-switch autonomy + decision-pick autonomy).

**How to apply:**
- When a TaskGet reveals a task is blocked on "owner pick" and a decision doc exists: read the doc's recommendation, ship it, log in commit message.
- Reversibility precondition: shipment can be reverted with one revert PR. Schema-breaking-across-many-published-consumers does NOT disqualify (see [[feedback_no_backwards_compatibility.md]]) — owner explicitly waived backwards-compat as a gate.
- **Still requires owner OK:**
  - Force-push / history rewrite
  - Pushing to others' branches
  - Decisions where the doc explicitly says "PENDING — owner intent required" with no recommendation
  - Picks that close a product cascade as "accepted ceiling" (e.g., medallion-10 iter-14 acceptance — owner explicitly said "no, we must strive to get better" on 2026-05-24)
- Outcome: ship, commit with rationale ("per Option X of decision doc YYYY-MM-DD-slug.md, owner pre-authorized 2026-05-24"), push, move on.

**Companion to:** Tenet 12 (commit autonomously on tested chunks), Tenet 19 (bias for action), Tenet 24 (don't fear breaking things — granted 2026-05-24), [[feedback_push_authorization_general.md]] (push), [[feedback_cross_repo_authority.md]] (repo switch), [[feedback_no_backwards_compatibility.md]] (no backcompat gate).
