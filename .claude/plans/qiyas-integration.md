# Integrating qiyas into the sacred-patterns iteration loop

## TL;DR — decision

**Adopt qiyas now, but as a *third* signal alongside `arch-audit.py` and `svg-diff.sh` — not as a replacement for either.** It plugs into a real gap (we have no tool that pairs *our* shapes against *reference* shapes; arch-audit only checks our SVG against a hand-authored baseline, and svg-diff only scores pixels). It is good enough to add value today on the patterns we care about most (8/10/12-fold rosettes with stars, polygons, lenses, circles). The gaps that exist (interlace/strapwork, color-blind scoring, schema churn, install friction) are workable around — they don't block adoption, they shape *where* we use it.

The integration is small: one Makefile target (`make qiyas-diff`), one tools wrapper (`tools/qiyas-diff.sh`), and a new section in `iteration-guide.md` that runs qiyas after every iteration alongside svg-diff and arch-audit. No changes to the pattern-construction code itself.

If the gaps in §4 turn out worse than expected on real patterns (e.g. the strapwork-heavy ones), we drop back to arch-audit + svg-diff and revisit. Cost of trying: ~half a day. Cost of being wrong: zero — qiyas is purely additive.

---

## 1. What qiyas is, in our terms

qiyas is a CLI that turns a pattern image into a **structural fingerprint** (every detected shape — circle, regular polygon, star, rosette, lens, girih tiles — with position and parameters) and diffs two fingerprints into a composite score with per-shape pairings. Score breakdown: `0.4 · structural + 0.35 · geometric + 0.25 · symmetry`. It rotation-aligns the recon against the ref before scoring (so "correct, just rotated" doesn't read as "wholly different" — exactly the failure mode our svg-diff has). Stack is classical CV (OpenCV + scikit-image), no ML, no labelled data.

Three commands matter to us:

| Command | What we'd use it for |
|---|---|
| `qiyas encode <image>` | Fingerprint our iteration's SVG and the reference image. |
| `qiyas diff <ref.json> <recon.json>` | Compare the two fingerprints, get a score + pairings. |
| `qiyas validate <ref> <recon>` | One-shot encode-both-and-diff that emits an HTML report. |

Plus `qiyas review` (browser portal for verdicting individual shapes) and `qiyas trace --explain <id>` (per-detector telemetry for "why didn't shape X get detected"). We don't need these in the inner iteration loop, but they're how we'd debug qiyas itself when it disagrees with our eyes.

Install is solved locally — `ghcr.io/naqshcoffee/qiyas:dev` and `:v0.0.1` are already pulled. The contributor path (`uv run qiyas …` from `/Users/omareid/Workspace/git/qiyas`) also works.

## 2. Where qiyas fits in our current loop

Today, every iteration produces three signals:

1. **Visual** — screenshot vs reference, judged by Claude/user.
2. **Pixel** — `tools/svg-diff.sh` produces an overlay, heatmap, and similarity %. Useful for *regression detection*, not for guiding work (CLAUDE.md "Convergence Philosophy" already says so).
3. **Architectural (A1–A6)** — `tools/arch-audit.py [--baseline]` parses our SVG, runs symmetry / tile-distribution / coverage / band-network / baseline-shape checks. A6 is the only one that compares to a *user-verified ground truth* (`input/baseline.json` from the interpret-pattern skill).

The hole: nothing in this stack reads the **reference image** structurally. arch-audit reads only our SVG. The baseline.json is a *manual* description of what shapes the reference *should* contain — written by Claude+user during interpret-pattern. If interpret-pattern miscounts or mis-zones a shape, the A6 audit happily reports PASS against a wrong baseline.

qiyas plugs exactly into this hole. It reads the reference image *and* our SVG and pairs shapes between them. That gives us a fourth signal — call it **A7. Reference-grounded pairing** — that's independent of both pixel similarity and our hand-authored baseline.

Proposed loop (additions in **bold**):

```
iter N:
  compile pattern.json → output.html
  render in browser → screenshot.png + output.svg
  validate-svg.sh output.svg
  svg-diff.sh reference.svg output.svg          # pixel signal
  zone-audit.py …                                # zone signal
  arch-audit.py output.svg --baseline …          # A1–A6 signals
  **qiyas-diff.sh reference.{png,jpg} output.svg # A7 signal**
  evaluation.md / retrospective.md / guidance.md
```

## 3. What this concretely looks like

### 3.1 Wrapper script — `tools/qiyas-diff.sh`

Thin shim around `docker run … qiyas validate`. Inputs: `ref` (the pattern reference image) and `recon` (our iteration's SVG or PNG). Outputs:

- `iterations/{N}/qiyas/ref.encoding.json`
- `iterations/{N}/qiyas/recon.encoding.json`
- `iterations/{N}/qiyas/diff.json` (composite + per-shape pairings)
- `iterations/{N}/qiyas/report.html` (visual side-by-side from `qiyas validate`)

Skeleton:

```bash
#!/usr/bin/env bash
set -euo pipefail
ref="$1"; recon="$2"; outdir="$3"
mkdir -p "$outdir"
docker run --rm -v "$(pwd):/work" ghcr.io/naqshcoffee/qiyas:dev \
  qiyas validate "/work/$ref" "/work/$recon" \
    --output "/work/$outdir/diff.json" \
    --html-report "/work/$outdir/report.html" \
    --ref-encoding-output "/work/$outdir/ref.encoding.json" \
    --recon-encoding-output "/work/$outdir/recon.encoding.json"
```

(Verify the exact flag names against `qiyas validate --help`; the wrapper isolates that detail from the rest of our pipeline.)

### 3.2 Makefile target

```make
qiyas-diff:
	./tools/qiyas-diff.sh $(REF) $(RECON) $(OUT)
```

Used as `make qiyas-diff REF=session-X/input/reference.png RECON=session-X/iterations/42/output.svg OUT=session-X/iterations/42/qiyas/`.

### 3.3 Iteration-guide changes

Add a "Reference-grounded structural diff (qiyas)" subsection to `iteration-guide.md` between "svg-diff (pixel signal)" and "arch-audit (A1–A6)". It states:

- **Run every iteration** after SVG extraction.
- **What it tells us:** which reference shapes have/don't have a paired shape in our output, and how far off the paired ones are in position/parameters.
- **How to read it:** the *per-shape pairings* matter more than the composite score. A composite score moving up while a critical pairing (e.g. central rosette) is missing is a regression, not progress — same philosophy as Convergence-Hierarchy: *Topology before Geometry before Proportions before Coloring*. qiyas's structural sub-score maps to Topology+Geometry; it cannot judge color (by design) or fine line-weight, which is fine — we have other signals for those.
- **When to ignore the score:** if the score is high but a critical shape is unpaired, treat the unpaired shape as MALFORMED (G2 gate).
- **When to trust the score over arch-audit:** when arch-audit says PASS but the reference visibly contains shapes our output doesn't (or vice versa). qiyas grounds the audit in the reference image; arch-audit grounds it in our hand-authored baseline.

### 3.4 Cross-check against baseline.json (one-time)

The interpret-pattern skill currently builds `baseline.json` from Claude's visual inventory + user corrections. We can validate that baseline against `qiyas encode reference.png` for any new pattern — a sanity check that catches *interpretation* errors (Claude mis-saw a shape) before iteration starts. This is a small script (`tools/cross-check-baseline.py`): for each shape in baseline.json, look for a paired shape in the qiyas encoding; report unmatched ones as candidates for baseline correction. Not blocking, just an early-warning signal.

## 4. Gap analysis — and whether the gaps block adoption

The detailed shape-vocab gap analysis and qiyas detector limitations have moved to qiyas-side tracking — they're qiyas's roadmap, not sacred-patterns's. See:

- **`qiyas/docs/decisions-pending.md` §SP-1** — Shape-vocab reconciliation (kite, petal, rhombus, bowtie, band-segment → qiyas types). Decision: A6 baseline matching uses `vertex_count + zone` only, no type-aware matching needed for v1.
- **`qiyas/docs/sacred-patterns-integration.md`** — Architecture, divergence policy, A5 contingency.

Sacred-patterns-side gaps that affect *how we use qiyas* (not what qiyas should detect):

### 4.1 Color-blindness — **Minor (and intentional)**

qiyas explicitly does not score color. For us this is fine: color is the **last** rung of our convergence hierarchy. svg-diff covers color regression; qiyas covers topology+geometry. Complementary.

### 4.2 Schema churn — **Minor**

`SCHEMA_VERSION` is pre-v1 and bumps regularly. We use qiyas per-iteration; encodings don't outlive an iteration. Mitigation: include `qiyas --version` in `validation.json` metadata so cross-iteration comparison can detect a bumped schema.

### 4.3 Higher-fold symmetry detection is conservative — **Minor**

qiyas may report `dominant_fold=1` on clean 10-fold/12-fold references that don't clear its conservative threshold (qiyas issue #35). Mitigation: when qiyas symmetry contradicts the baseline.json `symmetry_order`, trust the baseline.

**Verify during integration:** run `qiyas encode` on a few of our 10-fold and 12-fold references and check the `dominant_fold` field. If it's clean, this gap closes for our corpus.

### 4.4 Install / runtime friction — **Minor**

Docker image is private (NaqshCoffee org). Already pulled locally, so day-1 cost is zero. CI cost is real if we ever want qiyas in CI — would need `read:packages` PAT.

### 4.5 Speed — **Unknown, probably Minor**

A full `qiyas validate` runs Stage 1–4 twice plus the diff. On 1024² images that's ~5–15 seconds per iteration — noise relative to render+evaluation time. Re-evaluate after Phase 0+1 has wall-clock data.

## 5. Adoption plan

Three small steps. Total: ~half a day.

### Step 1 — dry-run on three completed sessions (2 hours)

Pick three sessions with different characters (e.g. one rosette, one girih, one strapwork-heavy). For each:

1. Run `qiyas encode input/reference.{png,jpg}` and inspect the encoding.
2. Run `qiyas validate input/reference.{png,jpg} final/output.svg` and read the HTML report.
3. Note: did qiyas pair the central star? rosettes? satellites? did it call the symmetry order correctly? what did it call the strapwork tiles?

Outcome: empirical answers for §4.1, §4.2, §4.5. If it nails the rosette session and degrades gracefully on the strapwork one, ship Step 2. If it whiffs on the rosette, **stop and reassess** — that's the failure mode that means "not good enough yet."

### Step 2 — wire it in (2 hours)

1. Write `tools/qiyas-diff.sh`.
2. Add `qiyas-diff` Makefile target.
3. Add the "A7 signal" section to `iteration-guide.md` and update `CLAUDE.md`'s tool list.
4. Run on one in-flight session, end-to-end, to confirm the wiring.

### Step 3 — run it for real on the next pattern (next session)

Use the next learn-new-pattern session as the integration shakedown. Don't tune anything yet — just collect data. After 5–10 iterations, retrospect: was qiyas useful? did it surface anything arch-audit missed? did it mislead?

Decision point: keep, drop, or extend (write a `band_segment` detector upstream).

## 6. What this is *not*

- Not a replacement for `arch-audit.py`. arch-audit reads our SVG element-by-element; qiyas reads images. Different lenses on the same problem.
- Not a replacement for `svg-diff.sh`. Pixel diff is still our color/coverage regression detector.
- Not a stop-condition. Same as everything else in the convergence hierarchy: shape before pixels, structural completeness before score.
- Not part of the interpret-pattern skill. baseline.json stays user-authored. qiyas optionally cross-checks it (§3.4) but doesn't replace it.

## 7. Open questions to resolve in Step 1

1. Does `qiyas encode` correctly report `dominant_fold=10` on our 10-fold rosette references? (Tests gap §4.5.)
2. How does qiyas type our kite tiles — `regular_polygon` n=4, `unknown`, or `square`? (Tests gap §4.1.)
3. Does the rotation-alignment work cleanly when the reference is a JPG photograph and the recon is a clean SVG? (Reference photos have perspective + lighting; recons are perfectly axial.)
4. What's the actual per-iteration runtime of `qiyas validate` on our 1024² renders? (Tests §4.8.)
5. Does the `qiyas validate` HTML report add value over our existing `output.html` — or is it redundant?

The Step 1 dry-run answers all five. If 1–3 come back clean, adoption is clearly worth it. If 1–3 are messy, rerun this decision with the empirical data.
