/**
 * The shareable PNG twin of the wave-progress page (GET /weave-progress.png) must
 * render the SAME wave as the live page — owner 2026-06-22: "wave 1 still off …
 * size is bigger". Two of those complaints were NOT geometry at all; they were the
 * twin and the page DISAGREEING, so the render I surfaced for review was not the
 * render the owner judged on screen (Tenet 25b: the surfaced PNG has to be the page).
 *
 * Two divergences this spec freezes as regressions:
 *   1. wave→reveal: the twin used a bare N/M (wave 1 of 22 = reveal 0.045 = a near-
 *      empty clip) while the page uses the floor-decoupled OURS_FLOOR 0.47 /
 *      FIELD_FILL 0.685 (wave 1 = reveal 0.322 = the central 10-star). A bare N/M
 *      twin came back 451 bytes / 1-bit blank.
 *   2. shells default: the twin defaulted shells=0 (a SINGLE lone central rosette)
 *      while the page fixes SHELLS=1 (the ~10-rosette converged field).
 *
 * What this proves (pixel-level, deterministic ranges not byte snapshots), decoding
 * the twin PNG via a browser <canvas> so the spec needs no extra npm dep:
 *   A. wave-1 twin is NEITHER blank NOR the full disc — non-card content fraction
 *      sits in a mid band (the reveal-0.322 central motif): regression 1.
 *   B. the wave-1 twin's content is CENTRED (centroid near image centre).
 *   C. with cells on, the DEAD-CENTRE pixel is dark navy, not cyan — the value-mood
 *      fix the owner asked for ("central isn't the same shape / it's cyan").
 *   D. wave 22 twin fills materially MORE than wave 1 (the reveal actually grows).
 *
 * Run via the sibling studio.config.ts (boots wave-plan-server.py as webServer).
 */
import { test, expect, type Page } from "@playwright/test";

interface Stats {
  byteLen: number;
  frac: number; // non-card content fraction 0..1
  cx: number; // content centroid x, 0..1
  cy: number; // content centroid y, 0..1
  centre: [number, number, number]; // dead-centre pixel RGB
}

// Decode a same-origin PNG URL inside the page via <canvas> and return content
// stats. The card background is ~#14171a (each channel < 40); content (white
// straps, coloured cells) is brighter or saturated.
async function statsFor(page: Page, url: string): Promise<Stats> {
  return await page.evaluate(async (u): Promise<Stats> => {
    const resp = await fetch(u);
    const blob = await resp.blob();
    const byteLen = blob.size;
    const bmp = await createImageBitmap(blob);
    const cv = document.createElement("canvas");
    cv.width = bmp.width;
    cv.height = bmp.height;
    const ctx = cv.getContext("2d")!;
    ctx.drawImage(bmp, 0, 0);
    const { data } = ctx.getImageData(0, 0, bmp.width, bmp.height);
    let count = 0, sx = 0, sy = 0;
    for (let y = 0; y < bmp.height; y++) {
      for (let x = 0; x < bmp.width; x++) {
        const i = (y * bmp.width + x) << 2;
        const r = data[i], g = data[i + 1], b = data[i + 2];
        if (!(r < 40 && g < 40 && b < 40)) { count++; sx += x; sy += y; }
      }
    }
    const ci = ((bmp.height >> 1) * bmp.width + (bmp.width >> 1)) << 2;
    const total = bmp.width * bmp.height;
    return {
      byteLen,
      frac: count / total,
      cx: count ? sx / count / bmp.width : 0.5,
      cy: count ? sy / count / bmp.height : 0.5,
      centre: [data[ci], data[ci + 1], data[ci + 2]],
    };
  }, url);
}

test.describe("weave-progress PNG twin matches the page", () => {
  test("wave-1 twin is the reveal-0.322 central motif, navy-centred, not blank/lone-rosette", async ({
    page,
  }) => {
    // Need a same-origin document so fetch()/createImageBitmap resolve the studio.
    await page.goto("/weave-progress");

    // (A,B) wave-1 weave-only: real, mid-band, centred.
    const s1 = await statsFor(page, "/weave-progress.png?wave=1&waves=22&star=4&width=1.8");
    // A blank 1-bit twin (the old bug) is ~451 bytes; a real RGB frame is ~100KB.
    expect(s1.byteLen, `wave-1 twin byte size ${s1.byteLen}`).toBeGreaterThan(10_000);
    // Not blank (the 0.045-reveal bug rendered near-nothing) and not the full disc.
    expect(s1.frac, `wave-1 content fraction ${s1.frac.toFixed(3)}`).toBeGreaterThan(0.02);
    expect(s1.frac, `wave-1 content fraction ${s1.frac.toFixed(3)}`).toBeLessThan(0.30);
    // Centred motif (centroid within 12% of image centre on each axis).
    expect(Math.abs(s1.cx - 0.5), `wave-1 centroid x ${s1.cx.toFixed(3)}`).toBeLessThan(0.12);
    expect(Math.abs(s1.cy - 0.5), `wave-1 centroid y ${s1.cy.toFixed(3)}`).toBeLessThan(0.12);

    // (C) wave-1 WITH cells: the dead-centre pixel must be dark navy, not cyan.
    const s1c = await statsFor(
      page,
      "/weave-progress.png?wave=1&waves=22&star=4&width=1.8&cells=1&clip=1",
    );
    const [cr, cg, cb] = s1c.centre;
    // navy #0F2765 ≈ (15,39,101): blue-dominant, red low, NOT cyan (cyan has high
    // green AND blue, e.g. #3EAACC ≈ (62,170,204)). Assert green well below blue and
    // a dark pixel — excludes the old cyan octagon centre.
    expect(cb, `centre B ${cb} must dominate R ${cr}`).toBeGreaterThan(cr);
    expect(cg, `centre G ${cg} must be << B ${cb} (not cyan)`).toBeLessThan(cb * 0.75);
    expect(cr + cg + cb, `centre brightness ${cr + cg + cb}`).toBeLessThan(360);

    // (D) wave-22 fills materially more than wave-1 (the reveal grows).
    const s22 = await statsFor(page, "/weave-progress.png?wave=22&waves=22&star=4&width=1.8");
    expect(
      s22.frac,
      `wave-22 ${s22.frac.toFixed(3)} > 1.3 × wave-1 ${s1.frac.toFixed(3)}`,
    ).toBeGreaterThan(s1.frac * 1.3);
  });
});
