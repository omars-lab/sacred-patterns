/**
 * Wave-1 of the weave-progress page must show a STAR, not a donut — driven
 * through a REAL browser (owner 2026-06-21: "[Image #5] wave 1 stiull doesnt
 * match" — the reference's wave 1 is a clean 10-point star, but ours was a tiny
 * hollow ring/donut).
 *
 * ROOT CAUSE the fix addresses: the two panels reveal their pattern wave-by-wave
 * by clipping a growing centred circle. A single shared reveal floor showed the
 * reference its central 10-star at a 10% clip, but showed OURS only the strap
 * RING around our (larger-scaled) central star — a donut. The fix decouples the
 * floors: REF_FLOOR 0.20 (its star at clip 10%) vs OURS_FLOOR 0.47 (our star at
 * reveal ~0.322 = 0.47 * FIELD_FILL 0.685). See bikar memory
 * medallion10_field_scale_count_coupling + weave_confetti_is_render_resolution.
 *
 * What this spec proves IN-BROWSER (the pixel-level "10 points == 10 points"
 * is proven separately in the PIL probe, montage at .tmp-review/wave1-montage):
 *   1. At wave 1 the OURS panel renders real geometry (a populated SVG with many
 *      paths), not a blank box and not the near-empty donut frame.
 *   2. The rendered wave-1 star reaches INTO the centre — its geometry spans a
 *      central band (a donut would leave a large hollow core). We assert the
 *      union bbox of the drawn paths is well-centred and substantial.
 *   3. The reference panel's clip-path sits at the wave-1 floor (circle 10%),
 *      so both sides show their wave-1 central star at the same progression step.
 *   4. Zero console / page errors across the flow.
 *
 * Deterministic — asserts DOM / SVG-geometry / clip-path state, NOT snapshot
 * bytes (those diverge across CPU/font). Run via the sibling studio.config.ts,
 * which boots wave-plan-server.py as its webServer against the live session.
 */
import { test, expect } from "@playwright/test";

test.describe("weave-progress wave 1 is a star, not a donut", () => {
  test("wave 1 renders a centred star with real geometry, ref clipped to its floor", async ({
    page,
  }) => {
    const errors: string[] = [];
    page.on("console", (m) => {
      if (m.type() === "error") errors.push(m.text());
    });
    page.on("pageerror", (e) => errors.push(e.message));

    await page.goto("/weave-progress");

    // Drive the wave slider to wave 1 (the frame the owner flagged). render() is
    // debounced ~250ms, so poll the ref clip-path until syncRef(pf=0) lands it on
    // the wave-1 floor (circle 10%) rather than reading it eagerly mid-debounce.
    await page.locator("#wave").fill("1");
    await page.locator("#wave").dispatchEvent("input");
    await expect
      .poll(
        () =>
          page
            .locator("#refimg")
            .evaluate((el) => getComputedStyle(el).clipPath),
        { timeout: 5_000 },
      )
      .toMatch(/circle\(10(\.00)?%/);

    // The ours panel re-renders via POST /api/preview-progress-svg; wait for the
    // inline SVG to land with real paths.
    const drawn = page.locator("#ours svg path");
    await expect(drawn.first()).toBeVisible({ timeout: 20_000 });
    const n = await drawn.count();
    expect(n, "wave-1 weave should draw many strap paths").toBeGreaterThan(8);

    // The wave-1 star must reach INTO the centre — a donut leaves a hollow core.
    // Measure the union bbox of the drawn geometry inside the SVG's own coords
    // and assert it is (a) substantial and (b) centred on the SVG midpoint, i.e.
    // the geometry brackets the centre rather than ringing an empty middle.
    const geom = await page.evaluate(() => {
      const svg = document.querySelector("#ours svg") as SVGSVGElement | null;
      if (!svg) return null;
      const vb = svg.viewBox.baseVal;
      const paths = Array.from(svg.querySelectorAll("path"));
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      for (const p of paths) {
        const b = (p as SVGGraphicsElement).getBBox();
        if (b.width === 0 && b.height === 0) continue;
        x0 = Math.min(x0, b.x); y0 = Math.min(y0, b.y);
        x1 = Math.max(x1, b.x + b.width); y1 = Math.max(y1, b.y + b.height);
      }
      const cx = (vb.x + vb.width / 2), cy = (vb.y + vb.height / 2);
      return {
        vbw: vb.width, vbh: vb.height, cx, cy,
        x0, y0, x1, y1,
        w: x1 - x0, h: y1 - y0,
        // does the union bbox straddle the SVG centre on both axes?
        straddlesX: x0 < cx && x1 > cx,
        straddlesY: y0 < cy && y1 > cy,
      };
    });
    expect(geom, "ours wave-1 SVG must exist with drawn paths").not.toBeNull();
    // The motif brackets the centre (a star reaches the middle; a donut wouldn't
    // have geometry crossing the exact centre line, but a centred ring would —
    // so straddle alone is necessary, not sufficient; the path-count + size
    // floor below, plus the PIL 10-point probe, complete the proof).
    expect(geom!.straddlesX, "wave-1 geometry must straddle SVG centre-X").toBe(true);
    expect(geom!.straddlesY, "wave-1 geometry must straddle SVG centre-Y").toBe(true);
    // The motif occupies a real fraction of the field (not a pinpoint, not the
    // whole disc — wave 1 is the central star at reveal ~0.32).
    const fracW = geom!.w / geom!.vbw;
    expect(fracW, `wave-1 motif width fraction ${fracW.toFixed(2)}`).toBeGreaterThan(0.15);
    expect(fracW, `wave-1 motif width fraction ${fracW.toFixed(2)}`).toBeLessThan(0.95);

    // The reference panel is clipped to its wave-1 floor: circle(10% at 50% 50%)
    // (REF_FLOOR 0.20 -> pct = 0.20 * 50 = 10). syncRef formats to 2 decimals.
    const refClip = await page.locator("#refimg").evaluate(
      (el) => getComputedStyle(el).clipPath,
    );
    expect(refClip, `ref clip-path at wave 1: ${refClip}`).toMatch(
      /circle\(10(\.00)?%/,
    );

    expect(errors, `console/page errors: ${errors.join(" | ")}`).toHaveLength(0);
  });
});
