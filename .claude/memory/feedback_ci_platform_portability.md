---
name: CI platform-portability — pinned baselines diverge across CPU architecture
description: qiyas encoder produces different shape counts / composite scores on ARM64 vs x86_64; baselines captured on Apple Silicon don't reproduce on x86_64 CI even at identical pip versions
type: feedback
originSessionId: ad36e137-d613-4fc8-83b4-32c5cec74bee
---
When pinning baselines that come out of the qiyas pipeline (encoded fixtures, robustness composite floors, shape counts), measuring once on the dev machine (Apple Silicon macOS) and using `observed - cushion` does NOT cover the gap to GitHub Actions ubuntu-latest CI. Same `pip install qiyas[dev]` lockfile, same cv2/skimage/numpy/PIL versions — but **the result differs by CPU architecture, not by operating system**.

**Why:** The 2026-05-19 CI restoration (qiyas#461) surfaced 3 sister failures (#468/#469/#470) of this shape. #469 was a 555→554 shape count for `bikar-medallion-10-strapwork` (fixture captured on macOS); #470 was robustness floors set as `macOS_observed - 0.05` cushion that x86_64 CI missed by 0.024-0.048. Confirmed via Docker reproduction:

- `ubuntu:24.04` arm64 (Apple Silicon mac, identical arch to local) → 555 shapes PASSES
- `ubuntu:24.04` x86_64 (QEMU emulation, identical arch to CI) → 554 shapes FAILS

So it's **CPU arch divergence**, not native-lib divergence. Likely culprits: OpenCV NEON-vs-SSE/AVX optimized contour-detection paths, numpy/scipy BLAS routines (Accelerate on ARM Mac, OpenBLAS on x86 Linux) giving different rounding on threshold-boundary pixels, or libjpeg arch-specific decode paths producing 1-pixel different decoded JPEG byte buffers.

**How to apply:** When authoring tests or scripts that pin baselines from the qiyas image pipeline (encoder, fold detection, composite diff):

1. Measure on the *actual CI architecture* (x86_64 ubuntu via QEMU if you're on Apple Silicon) — `docker run --platform=linux/amd64 ubuntu:24.04 ...` works and is the fastest way to reproduce x86_64 results from a Mac.
2. If pinning a numeric floor, take `min(arm64_observed, x86_64_observed) - 0.05` cushion.
3. If pinning an exact baseline (fixture shape count, byte-equality), commit the x86_64 baseline as canonical and document that dev boxes may locally diverge.
4. Better: use `workflow_dispatch` to run measurement scripts in the actual CI runner and commit the artifact back — that's the meta-task #471 captures.

**Anti-pattern to avoid:** "Same Python lib versions, so it'll reproduce" — the 2026-05-19 session burned an hour proving same `cv2.__version__` doesn't mean same `cv2.findContours` output. CPU arch matters more than pip lockfile.

**Anti-pattern to avoid:** "I ran it locally and it's within 0.05, that's enough" — same trap #470 set up. The 0.05 cushion was sized for same-arch jitter, not cross-arch.
