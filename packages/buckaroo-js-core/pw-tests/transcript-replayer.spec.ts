import { test, expect } from "@playwright/test";
import { waitForCells, getRowCount } from "./ag-pw-utils";

test.describe("PinnedRowsTranscriptReplayer", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to Storybook with the PinnedRowsTranscriptReplayer story
    await page.goto(
      "http://localhost:6006/iframe.html?args=&id=buckaroo-dfviewer-pinnedrowstranscriptreplayer--primary&viewMode=story"
    );
  });

  test("should render the transcript replayer UI", async ({ page }) => {
    // Check that the description text is visible
    const description = page.locator("text=Replays a captured transcript");
    await expect(description).toBeVisible();

    // Check that the Start Replay button exists
    const startButton = page.getByRole("button", { name: "Start Replay" });
    await expect(startButton).toBeVisible();

    // Check that the events count is displayed
    const eventsCount = page.locator("text=/events: \\d+/");
    await expect(eventsCount).toBeVisible();
  });

  test("should render the DFViewerInfinite grid", async ({ page }) => {
    // Wait for the ag-grid to appear
    await waitForCells(page);

    // Check that the grid is rendered
    const grid = page.locator(".ag-root-wrapper");
    await expect(grid).toBeVisible();

    // Check for expected column headers (index, a, b from baseConfig)
    const indexHeader = page.locator('.ag-header-cell-text:has-text("index")');
    const aHeader = page.locator('.ag-header-cell-text:has-text("a")');
    const bHeader = page.locator('.ag-header-cell-text:has-text("b")');

    await expect(indexHeader).toBeVisible();
    await expect(aHeader).toBeVisible();
    await expect(bHeader).toBeVisible();
  });

  test("should have Start Replay button that can be clicked", async ({ page }) => {
    const startButton = page.getByRole("button", { name: "Start Replay" });
    await expect(startButton).toBeEnabled();

    // Click the button (it won't do much with 0 events, but shouldn't error)
    await startButton.click();

    // After clicking, button should be disabled
    await expect(startButton).toBeDisabled();
  });

  test("should show initial grid with None values when no transcript", async ({ page }) => {
    await waitForCells(page);

    // With no transcript data, the grid should show "None" values
    const noneCells = page.locator('.ag-cell:has-text("None")');
    const count = await noneCells.count();
    expect(count).toBeGreaterThan(0);
  });
});

