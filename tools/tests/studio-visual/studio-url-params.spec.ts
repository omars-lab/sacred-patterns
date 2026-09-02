/**
 * Contract round-trip for the weave-studio URL params, driven through a REAL
 * browser (owner 2026-06-17: "are we visually verifying the different knobs /
 * expectations via playwright / image extraction?").
 *
 * The Python-side test (tools/tests/test_portal_studio_url_params.py) proves the
 * HTTP plumbing: /weave-studio?<knobs> serves 200 and the page ships the JS.
 * What it CANNOT prove is the in-browser behaviour the owner actually asked
 * about — that a shared link DRIVES the dials and the render, and that touching
 * a dial writes the bar back. This spec does, end-to-end:
 *
 *   1. A shared link lands the controls on its values (loadFromURL +
 *      syncControlsFromState): ?field_ray=8&style=field&… → the ray slider reads
 *      8, the Field button is selected, the field dials are visible.
 *   2. The render is non-empty (the params produced a real SVG, not a blank).
 *   3. Moving a dial writes the new value back to the address bar (syncURL), so
 *      the link stays shareable after edits.
 *   4. Zero console / page errors across the whole flow.
 *
 * Deterministic — asserts DOM/URL state, NOT pixels (snapshot bytes diverge
 * across CPU/font; the existing review-site-visually skill flags this). Run via
 * the sibling studio.config.ts, which boots wave-plan-server.py as its
 * webServer against the live medallion-10 session.
 */
import { test, expect } from "@playwright/test";

// A link that exercises one knob from every family, so a single load proves the
// whole round-trip. field_ray=8 is the "tamer" setting surfaced in the studio.
const SHARED_LINK =
  "/weave-studio?style=field&width=12&color=%23F2EEE6&shadow=40&network=1" +
  "&field_angle=50&field_ray=8&field_wave_lo=16&field_wave_hi=20&rings=center,outer";

test.describe("weave-studio URL params", () => {
  test("a shared link lands every dial on its value, with no console errors", async ({
    page,
  }) => {
    const errors: string[] = [];
    page.on("console", (m) => {
      if (m.type() === "error") errors.push(m.text());
    });
    page.on("pageerror", (e) => errors.push(e.message));

    await page.goto(SHARED_LINK);

    // The Field style is selected and its dials are the visible ones (syncStyle
    // ran off the loaded state, not the HTML default 'flat').
    await expect(page.locator("#styleField")).toHaveClass(/sel/);
    await expect(page.locator("#styleFlat")).not.toHaveClass(/sel/);
    await expect(page.locator("#fieldRayDial")).toBeVisible();
    await expect(page.locator("#ringsDial")).toBeHidden(); // crossing-only dial

    // Every knob slider/checkbox reads the URL value (syncControlsFromState).
    await expect(page.locator("#width")).toHaveValue("12");
    await expect(page.locator("#shadow")).toHaveValue("40");
    await expect(page.locator("#fieldAngle")).toHaveValue("50");
    await expect(page.locator("#fieldRay")).toHaveValue("8");
    await expect(page.locator("#fieldWaveLo")).toHaveValue("16");
    await expect(page.locator("#fieldWaveHi")).toHaveValue("20");
    await expect(page.locator("#network")).toBeChecked();
    // The color swatch matching the URL hex carries the selected ring.
    await expect(
      page.locator('.swatch[data-color="#F2EEE6"]'),
    ).toHaveClass(/sel/);

    // The render actually produced geometry for these params (not a blank box).
    const drawn = page.locator("#ours svg path");
    await expect(drawn.first()).toBeVisible({ timeout: 20_000 });
    expect(await drawn.count(), "field weave should draw paths").toBeGreaterThan(0);

    expect(errors, `console/page errors: ${errors.join(" | ")}`).toHaveLength(0);
  });

  test("moving a dial writes the new value back to the address bar (syncURL)", async ({
    page,
  }) => {
    await page.goto(SHARED_LINK);
    await expect(page.locator("#fieldRay")).toHaveValue("8");

    // Drive the ray slider to a new value; syncURL must reflect it.
    await page.locator("#fieldRay").fill("14");
    await page.locator("#fieldRay").dispatchEvent("input");

    await expect
      .poll(() => new URL(page.url()).searchParams.get("field_ray"))
      .toBe("14");
    // The rest of the link is preserved (style + the other knobs stay in the bar).
    const q = new URL(page.url()).searchParams;
    expect(q.get("style")).toBe("field");
    expect(q.get("field_wave_lo")).toBe("16");
  });

  test("switching style flips which dials show and updates the URL", async ({
    page,
  }) => {
    await page.goto("/weave-studio?style=field&field_ray=8");
    await expect(page.locator("#fieldRayDial")).toBeVisible();

    await page.locator("#styleCross").click();
    await expect(page.locator("#styleCross")).toHaveClass(/sel/);
    // Crossing dials appear; field dials hide.
    await expect(page.locator("#ringsDial")).toBeVisible();
    await expect(page.locator("#stepDial")).toBeVisible();
    await expect(page.locator("#fieldRayDial")).toBeHidden();
    await expect
      .poll(() => new URL(page.url()).searchParams.get("style"))
      .toBe("crossing");
  });
});
