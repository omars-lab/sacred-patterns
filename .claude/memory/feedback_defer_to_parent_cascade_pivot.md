---
name: defer-to-parent-cascade-pivot
description: "When a defect surfaces on a path a parent cascade is already replacing, defer-and-re-measure usually beats refactoring the deprecated path"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---

When a bug surfaces on a code path that a *parent decision* is in the process of replacing, the right move is usually to **wait for the parent pivot to land and re-measure**, not to patch the deprecated path.

**Why:** confirmed 2026-05-20 on qiyas#371 (partial-polygon residue starvation). Issue doc's preliminary recommendation was Option A (2-3 day LineAggregate refactor); owner accepted Option E (defer to B1 Option B / qiyas#398 render.svg-direct path, re-measure on trigger). Rationale: refactoring the rasterize→trace foundation the parent B1 cascade is deprecating risks wasted work; Tenet 23 (DSL-as-source-of-truth) makes the alternative consumer-side heuristic a named violation; structural fallback (Option A) remains available if the trigger reveals the new path also starves.

**How to apply:** before recommending a refactor to fix a symptom, check whether an in-flight parent cascade will make the refactor obsolete. If yes:
1. Pick the deferral option in the decision doc.
2. File the trigger conditions explicitly per the present-options skill's conditional-task rule (don't rely on memory — the rationale rots).
3. Mark the symptom-issue as DEFERRED-PENDING-TRIGGER, not OPEN.
4. Annotate any downstream cascade that depended on the patched behavior as "leverage pending parent cascade landing."

The deferral option must have a *measurable trigger* and a *named fallback option* if the trigger reveals the parent pivot didn't dissolve the problem. Without those, "defer" rots into "do nothing."

Companion to [[no-narrow-corpus-tenet7-trap]] and the cross-repo Tenet 23 (DSL-as-source-of-truth).
