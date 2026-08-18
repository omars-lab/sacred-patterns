---
name: When implementing a paper algorithm, web-search a reference implementation early
description: Don't iterate on a hand-coded algorithm-from-paper through three same-symptom failures. Find the canonical C/Python implementation and cross-check, especially the indices and sign conventions.
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
When implementing an algorithm specified in a research paper (Arkin-Chew-Kedem
turning function, Hungarian matcher, RANSAC variants, etc.) and you hit two or
three iterations where a fix attempt produces the SAME residual constant /
SAME unexpected behavior, stop iterating. Web-search for a canonical
reference implementation (GitHub, original-author site, common libraries).
Read the indices, sign conventions, and event-enumeration carefully — those
are exactly the parts that are easy to flip silently when reading the paper
prose.

**Why:** The I1 iter-2 turning-function bug surfaced as
"d ≈ 0.97 between identical polygons under start-shift" three different times
in succession. I rewrote `_l2_distance_at_shift`, then `_reverse_turning_function`,
then introduced a periodic-extension fix in `_l2_distance_at_shift` again,
each time getting closer but always leaving 0.97 (or 0.11 with the partial
fix) on the table. The actual root cause was a one-character index flip in
the critical-event enumeration: I had `(s1 - s2) % 1.0` but the canonical
Arkin algorithm shifts the SECOND polygon, so the candidates are
`(s2 - s1) % 1.0`. The C source from Stony Brook (mirrored at
DBraun/turning-function on GitHub) made this obvious in 30 seconds; no amount
of staring at my own code would have surfaced it because both formulas
"looked right" in isolation.

**How to apply:**
- Same symptom across two or three independent fix attempts = stop hand-debugging.
- Search "<paper title> github implementation" or "<algorithm name> C source"
  before the third rewrite.
- Match against the canonical impl line-by-line for: index conventions,
  sign of differences, where modular arithmetic is applied, event/critical-point
  enumeration, optimal-parameter formulas (the "obvious" closed forms are
  often the hidden bug surface).
- Cite the source in the relevant code docstring so the next reader doesn't
  redo the search.
- The web-search itself is also the right move when the user asks "are we
  going in circles?" — that question is the loop-detection signal.

Applies to any paper-derived algorithm in qiyas: turning function, Procrustes
matching, RANSAC, Hungarian matcher, hash families, geometric primitives.
