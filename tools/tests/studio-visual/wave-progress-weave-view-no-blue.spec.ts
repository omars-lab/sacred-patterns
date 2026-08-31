/**
 * The weave view must show ours WEAVE-ONLY — no blue (owner 2026-06-22: "why are
 * we still seeing blue? weaves are still not the same"). The page compares the two
 * panels weave-to-weave: the reference panel is white-straps-on-black (its coloured
 * tiles stripped out), so the OURS panel must also be straps-only in the weave view,
 * or the blue girih field drowns the straps and the panels aren't comparable.
 *
 * ROOT CAUSE the fix addresses: render() used `flipped ? true : cellsBox.checked`,
 * so a `cells=1` URL (or a ticked checkbox) painted the blue cells in the weave
 * view. The fix pins cells to the view: `showCells = flipped` — cells ON only in
 * the SHAPES view, OFF in the weave view, regardless of the checkbox.
 *
 * What this freezes: loading the weave view with cells=1 in the URL, the preview
 * POST that drives the ours panel carries cells:false (straps only, no blue).
 *
 * Run via the sibling studio.config.ts (boots wave-plan-server.py as webServer).
 */
import { test, expect } from "@playwright/test";

test.describe("weave view is weave-only — no blue cells", () => {
  test("cells=1 in the URL still renders ours straps-only in the weave view", async ({
    page,
  }) => {
    const posts: Array<{ params: { cells: boolean } }> = [];
    page.on("request", (r) => {
      if (r.url().includes("/api/preview-progress-svg") && r.method() === "POST") {
        try {
          posts.push(JSON.parse(r.postData() || "{}"));
        } catch {
          /* ignore non-JSON bodies */
        }
      }
    });

    // Owner's surfaced link carried cells=1; the weave view must override it off.
    await page.goto("/weave-progress?wave=1&waves=22&star=4&width=3&cells=1&clip=1");

    // The ours panel renders via POST /api/preview-progress-svg; wait for paths.
    await expect
      .poll(() => page.locator("#ours svg path").count(), { timeout: 20_000 })
      .toBeGreaterThan(8);

    expect(posts.length, "at least one preview POST fired").toBeGreaterThan(0);
    const last = posts[posts.length - 1];
    expect(
      last.params.cells,
      `weave-view preview POST cells=${last.params.cells} must be false (no blue)`,
    ).toBe(false);
  });
});
