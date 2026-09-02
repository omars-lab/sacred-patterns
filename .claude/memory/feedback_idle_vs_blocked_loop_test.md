---
name: idle-vs-blocked-loop-test
description: "In an autonomous loop, before idling, name the specific unfired trigger OR the named blocker (task#/artifact); 'nothing to do' without one of those is the tell you haven't looked. A GHA-budget freeze blocks pushes, never local work."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 346af4f5-c695-4afc-832d-ec66056fd627
---

The operational test for "am I idling or genuinely blocked," to run at every idle tick of an autonomous loop, BEFORE declaring "converged" / "owner-gated" / "nothing to do": name (a) the specific unfired trigger you are waiting on, OR (b) the named external blocker — a task#, a decision-doc owner-gate, a concrete missing artifact. If you can name neither, you are NOT blocked — bias to action on the lowest-tier broken thing (Tenet 20). "Nothing to do" with no cited trigger or blocker is a tell that you stopped looking, not that the work is done.

**Why:** Retrospective mistake M4 (`docs/retrospectives/2026-06-06-image-to-dsl-retrospective.md` §4) recurred across many ticks with no operational test: 15-tick idle holding 58 commits; 11+ ticks re-asserting "converged-idle"; a one-shot "authorization blocker" that wasn't real; stalling on status summaries. The bias-for-action tenet (19) existed the whole time — but a tenet alone doesn't fire at the moment of temptation; an operational check does. A GHA-budget freeze was repeatedly mis-read as a hard work-blocker when it only ever blocks *pushes* — local builds, mirror-CI, and accumulating held commits all proceed (see [[gha-spend-limit-never-blocks-push]] and [[never-block-on-gha-find-workarounds]]).

**How to apply:** each idle tick must cite, in its Done/Left/Next/Held entry, the exact trigger it is waiting on or the task# blocking it — a bare "idle" is non-conforming. Distinguish *idle* (no unfired trigger — legitimately nothing) from *blocked* (a named dependency). A real GHA freeze is a reason to hold a *push*, not to stop *working*: mirror CI locally, batch docs commits, keep shipping to the local tree. This is tenet C3 made operational, and is enforced by the loop-idle guard wired to this memory.

**Companion to:** tenets 19 (bias for action), 20 (fix the simplest broken thing first), C3 (idle is not blocked, with the GHA carve-out); the [[present-options]] §0 premise discipline (here the "premise" to validate is "I am blocked"); and [[gha-spend-limit-never-blocks-push]] / [[never-block-on-gha-find-workarounds]]. Cross-link to [[validate-premise-before-options]] — "I'm blocked" is a claim, not a fact, until you name the blocker.
