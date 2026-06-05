/**
 * Automated visual regression for the gh-pages gallery (Path B of the
 * review-site-visually skill). Asserts the structural invariants the eye
 * checks in Path A: all 8 patterns render a non-empty svg, the controls
 * work, the debug menu opens, and the page loads with zero console errors.
 *
 * Kept OUT of the gating `npm test` (the fast JSDOM geometry check) — run
 * via `npm run test:visual` after `npm run build`. Screenshot snapshots are
 * advisory (bytes diverge across CPU arch / fonts); the structural asserts
 * are the load-bearing gate.
 *
 * Prereq: `npm run build` populated site/index.html + site/bundle.js. The
 * config (playwright.config.ts) starts `npx serve site` as its webServer.
 */
import { test, expect } from "@playwright/test";

// The 8 generators, by their per-card mount id (matches templates/index.tpl).
const PATTERN_IDS = ["d6", "d0", "d2", "d3", "d7", "d5", "d1", "d4"];

test.describe("sacred-patterns gallery", () => {
  test("loads with zero console errors", async ({ page }) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });
    page.on("pageerror", (err) => errors.push(err.message));

    await page.goto("/");
    await page.waitForSelector("#mount-d6 svg");
    expect(errors, `console/page errors: ${errors.join(" | ")}`).toHaveLength(0);
  });

  test("renders all 8 patterns into non-empty svgs", async ({ page }) => {
    await page.goto("/");
    for (const id of PATTERN_IDS) {
      const svg = page.locator(`#mount-${id} svg`).first();
      await expect(svg, `pattern ${id} should render an svg`).toBeVisible();
      // Non-empty: the svg must contain at least one drawn primitive.
      const drawn = await page
        .locator(`#mount-${id} svg polyline, #mount-${id} svg circle`)
        .count();
      expect(drawn, `pattern ${id} svg should contain drawn geometry`).toBeGreaterThan(0);
    }
  });

  test("changing a palette select keeps the render non-empty", async ({ page }) => {
    await page.goto("/");
    await page.selectOption("#line-d6", "2"); // gold line theme
    await page.waitForSelector("#mount-d6 svg polyline");
    const polylines = await page.locator("#mount-d6 svg polyline").count();
    expect(polylines).toBeGreaterThan(0);
  });

  test("regenerate redraws the card", async ({ page }) => {
    await page.goto("/");
    const card = page.locator(".card", { hasText: "Hexagon Nonagon Star" });
    await card.getByRole("button", { name: "Regenerate" }).click();
    await expect(page.locator("#mount-d6 svg").first()).toBeVisible();
    expect(await page.locator("#mount-d6 svg polyline").count()).toBeGreaterThan(0);
  });

  test("debug menu opens with provenance, config, and export links", async ({ page }) => {
    await page.goto("/");
    await page.locator("#debugToggle").click();
    const panel = page.locator("#debugPanel");
    await expect(panel).toBeVisible();
    await expect(panel.locator("#config")).toHaveValue(/background_theme/);
    await expect(panel.locator("#download")).toBeVisible();
    await expect(panel.locator("#download-inverted")).toBeVisible();
  });

  test("full-page snapshot (advisory across arch)", async ({ page }) => {
    await page.goto("/");
    await page.waitForSelector("#mount-d4 svg");
    // Advisory: pin baselines to the CI arch; structural tests above are the gate.
    await expect(page).toHaveScreenshot("gallery.png", { fullPage: true, maxDiffPixelRatio: 0.02 });
  });
});
