/loop Continue the medallion-10 stage-gated reconstruction loop.

═══════════════════════════════════════════════════════════════
ON-DISK REFERENCES A COLD SESSION MUST READ FIRST
═══════════════════════════════════════════════════════════════
1. MEMORY.md — ~/.claude/projects/-Users-omareid-Workspace-git-bikar/memory/MEMORY.md
   (project facts, feedback memories, medallion-10 no-backdrop decision)
2. LOOP-PROMPT.md — /Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns/
   bikar-medallion-10/handoff/wave1-star-fit/LOOP-PROMPT.md
3. ISSUES-OBSERVED.md — in the medallion-10 session root (CloudStorage path above)
4. session.json — the gate-of-record:
   /Users/omareid/Library/CloudStorage/Dropbox/Data/sacred-patterns/bikar-medallion-10/session.json
5. OPEN-TASKS.md — the durable task ledger (same handoff dir as this prompt). The
   in-session task list does NOT survive /clear; this file is the source of truth for
   every open task's full intent. FIRST ACTION this session: read OPEN-TASKS.md and
   re-create the task list from it with TaskCreate (one task per open entry: #23 #27
   #31 #42 #45 #46 #48 #53 #54), setting the blockedBy edges per the dependency order
   below. Do this before any other work so no task is lost to the clear.

═══════════════════════════════════════════════════════════════
VERIFIED STATE (as of 2026-06-15)
═══════════════════════════════════════════════════════════════
STRUCTURE GATE: APPROVED. session.json stage_gates.structure.approved=true,
  approved_at_iter=71. Owner PICK A via the visual picker: "One shape — the lone
  central star," owner note verbatim "Its one shape, but its 10/3." This was a
  legitimate owner authorization (arrived through wave1-regate-picker). DO NOT
  reopen it. The "10/3" note is a NON-blocking construction-density refinement
  captured as task #54 (re-author wave-1 hankin star as a {10/3} star polygon,
  owner-gated build) — it does NOT block the color gate.

COLOR GATE: NOT yet agreed (stage_gates.color.palette_agreed=false). WEAVE: not
  started. waves_passed=null — per-wave owner_verdicts for waves 16–22 are still
  null; do NOT fabricate them.

TWO UNPUSHED BRANCHES, both held pending ONE batched GHA cycle (owner-gated, GHA
budget tenet #22):
  • bikar  feat/divide-offset  — 4 commits ahead of main, NO upstream:
      50897af #53 authored-region id (data-authored-region + evidence.authored_region)
      35c96d6 data-wave provenance + strapwork suppress_radial
      deef89f blueprint display:none for non-JS rasterizers
      3ff260a divide <circle> into N offset <deg>
    Tree clean. Core builds clean. Full suite 980 pass + 3 expected-fail.
    Tier-0 witness: packages/core/tests/render/authored-region-id.test.ts (6 green).
  • sacred-patterns  loop/regate-automation  — 11 commits ahead of origin/master
    (NOTE: sacred-patterns default branch is MASTER, not main):
      f1ae423 /simplify portal experience (#44–#52)
      ec3da96 /waves redesign + null-verdict crash fix + data-wave contract mirror
      ecd49ef docs: isolation check retargets #23
    Untracked (do NOT commit without asking): .claude/plans/playful-giggling-patterson.md

NOTE: the portal /simplify work is already COMMITTED as f1ae423 (the LOOP-PROMPT's
  "held uncommitted in tools/wave-plan-server.py" line is stale — it is committed,
  just unpushed). Portal :8765 should be healthy (200).

═══════════════════════════════════════════════════════════════
THE LOOP IS IDLE-BLOCKED ON OWNER, NOT STUCK
═══════════════════════════════════════════════════════════════
Three unfired triggers, each owner-gated. The single highest-leverage one:
  (a) PUSH 50897af (bikar feat/divide-offset → main). This is the keystone:
      it UNBLOCKS #53 step 4 (/simplify consumer fuses faces by
      data-authored-region before clustering — currently BLOCKED because the
      portal can't render the attr until the engine that emits it is deployed).
      Pushing costs one GHA cycle (bikar deploy.yml → Cloudflare Pages).
  (b) Color-gate work — only after the owner signals the color phase is next.
  (c) Commit/push the sacred-patterns branch (11 commits) → second GHA cycle.

DEPENDENCY ORDER (read before picking work — the keystone is #53):
  #53 (push 50897af → deploy → step 4 portal fuse)
    ├─ unblocks → #45 (inventory count is only real once petals fuse, not shards)
    ├─ unblocks → #46 (flower/rosette grouping reads fused shapes; blocked-by #53)
    └─ #48 (rim-band exclusion) is INDEPENDENT — local clusterer fix, no push
  #42 (simplification UX umbrella) is blocked-by #45 + #46 + #48 — closes LAST.
  #31, #27, #23, #54 are INDEPENDENT of the push (see per-task closure below).
  So the order is NOT "do #45/#46 locally before the push" — they chain BEHIND it.

WHAT TO DO THIS SESSION — every open task has a closure path; drive them in this order:

  0. STARTUP: read OPEN-TASKS.md, re-create the task list (TaskCreate per open #),
     set blockedBy edges (#46←#53; #42←#45,#46,#48). Then re-read session.json
     (mtime, stage_gates, waves_passed, wave_view_choices) + portal :8765 health.
     If unchanged + still owner-gated on the push, surface the PUSH option in ONE
     line and hold — do not spam.

  1. INDEPENDENT-NOW (no push, no GHA, closeable this session — do these first):
     • #31 — trace /waves + /inspect data source; confirm both read the agreed
       wave-plan (session.json authority) for color+count+band, not just position.
       Close when verified.
     • #48 — clusterer rim-band fix: the 142× "round" class is the outer-rim frame,
       not a placeable shape; filter or split it. Local clusterer change. Close +
       regression-test (Tenet 18). Feeds #42.
     • #27 — shape inspector: portal page that reads data-wave (ships in bikar
       35c96d6) on click → highlights the face + names the wave that introduced it.
       The enabling attribute already renders, so this is portal-read only. Close
       when click→wave lookup works; record a visual verdict (Tenet 25).

  2. KEYSTONE (owner-gated push): if the owner says PUSH, mirror CI locally FIRST
     (npm run build -w packages/core && npm run build -w packages/web && make test
     — or npx vitest run if Docker is down), confirm green, push bikar
     feat/divide-offset → main, wait for Cloudflare deploy. Then close #53:
     author the /simplify fuse-by-authored-region pre-pass (group faces by
     data-authored-region before clustering), AND file the canonical
     sacred-patterns contract amendment (currently mirrored only in bikar). Verify
     the /simplify vocabulary count drops from fragment-count toward designed-shape
     count, "tap to find it" lands on a real shape — record the visual verdict.
     Decision discipline: layer onto the existing face-extractor / region-identity
     doc (Tenet C5), do NOT open a new tag.

  3. AFTER #53 LANDS (now meaningful): #45 (unique-shape inventory on the fused
     input) → #46 (group fused shapes into flowers/rosettes/bands) → #42 (umbrella
     closes once #45+#46+#48 are all done).

  4. OWNER-GATED / PARKED (do NOT force):
     • #54 — re-author wave-1 star as {10/3} (owner note "Its one shape, but its
       10/3"). Construction-density refinement of an APPROVED gate — does NOT reopen
       it, does NOT block the color gate. Build only when the owner asks or picks the
       color phase. When built: render, surface for owner A/B vs the hankin version.
     • #23 — re-enable strapwork (weave phase). Block is COMMENTED (not deleted) in
       iterations/71/pattern.bkr with suppress_radial 55 preserved. Re-enable only
       when the owner asks for weave. Deliberate park, not a gap.

  As each task closes, move its entry to the "Closed" section of OPEN-TASKS.md with
  the commit/decision that closed it, and TaskUpdate status=completed.

OPEN TASKS (all 9, none dropped): #23 #27 #31 #42 #45 #46 #48 #53(step4) #54.

═══════════════════════════════════════════════════════════════
STANDING CONSTRAINTS (non-negotiable)
═══════════════════════════════════════════════════════════════
• NEVER self-approve a structure/color/weave gate. Owner authority only.
• NO push/commit without explicit owner go-ahead (GHA budget tenet #22 — every
  push burns billable NaqshCoffee Actions minutes; batch, mirror CI locally first).
• Do NOT re-run the full test suite on an unchanged tree.
• qiyas detector is FROZEN — do not touch it.
• Node 22 required: export PATH=/Users/omareid/.nvm/versions/node/v22.22.3/bin:$PATH
• WORKTREE GOTCHA: bash cwd resets to the empty vite8-upgrade-verify worktree each
  call. The real trees are /Users/omareid/Workspace/git/bikar and
  /Users/omareid/Workspace/git/sacred-patterns — cd into them explicitly.
• On a bare "continue" with identical unchanged state: surface the push option in
  one line, do NOT re-park silently, do NOT spam AskUserQuestion (ask at most once
  per several identical ticks).
• Decision-record discipline (tenet C5): #53 layers onto the existing
  face-extractor / region-identity decision doc — do NOT open a new tag.
