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

  test("should replay injected transcript and update grid with data", async ({ page }) => {
    // Inject mock transcript BEFORE navigating (addInitScript runs before page scripts)
    await page.addInitScript(() => {
      const ts = Date.now();
      (window as any)._buckarooTranscript = [
        {
          ts: ts,
          event: "dfi_cols_fields",
          fields: ["index", "name", "value"],
        },
        {
          ts: ts + 10,
          event: "all_stats_update",
          len: 2,
          sample: { index: "null_count", name: 0, value: 0 },
          all_stats: [
            { index: "null_count", name: 0, value: 0 },
            { index: "empty_count", name: 0, value: 0 },
          ],
        },
        {
          ts: ts + 20,
          event: "pinned_rows_config",
          pinned_keys: ["null_count", "empty_count"],
          cfg: {
            pinned_rows: [
              { primary_key_val: "null_count", displayer_args: { displayer: "obj" } },
              { primary_key_val: "empty_count", displayer_args: { displayer: "obj" } },
            ],
          },
        },
        {
          ts: ts + 30,
          event: "infinite_resp_parsed",
          key: null,
          rows_len: 3,
          total_len: 3,
          rows: [
            { index: 0, name: "Alice", value: 100 },
            { index: 1, name: "Bob", value: 200 },
            { index: 2, name: "Charlie", value: 300 },
          ],
        },
      ];
    });

    // Navigate to the story (transcript will be available on mount)
    await page.goto(
      "http://localhost:6006/iframe.html?args=&id=buckaroo-dfviewer-pinnedrowstranscriptreplayer--primary&viewMode=story"
    );
    await waitForCells(page);

    // Note: events count shows 0 due to useRef not triggering re-render (story bug)
    // Click Start Replay - the events were loaded into eventsRef on mount
    const startButton = page.getByRole("button", { name: "Start Replay" });
    await startButton.click();

    // Wait for replay to process events (they have small delays of 120ms each)
    await page.waitForTimeout(800);

    // After replay, the grid should show the replayed data
    // Check for column headers that match our injected fields
    const nameHeader = page.locator('.ag-header-cell-text:has-text("name")');
    const valueHeader = page.locator('.ag-header-cell-text:has-text("value")');
    
    await expect(nameHeader).toBeVisible({ timeout: 5000 });
    await expect(valueHeader).toBeVisible({ timeout: 5000 });

    // Check that our replayed data appears in cells
    const aliceCell = page.locator('.ag-cell:has-text("Alice")');
    const bobCell = page.locator('.ag-cell:has-text("Bob")');
    
    await expect(aliceCell).toBeVisible({ timeout: 5000 });
    await expect(bobCell).toBeVisible({ timeout: 5000 });
  });

  test("should update column config during replay", async ({ page }) => {
    // Inject transcript with column config before navigation
    await page.addInitScript(() => {
      const ts = Date.now();
      (window as any)._buckarooTranscript = [
        {
          ts: ts,
          event: "dfi_cols_fields",
          fields: ["index", "custom_col_1", "custom_col_2", "custom_col_3"],
        },
      ];
    });

    await page.goto(
      "http://localhost:6006/iframe.html?args=&id=buckaroo-dfviewer-pinnedrowstranscriptreplayer--primary&viewMode=story"
    );
    await waitForCells(page);

    // Click replay
    const startButton = page.getByRole("button", { name: "Start Replay" });
    await startButton.click();

    // Wait for replay to process (120ms per event)
    await page.waitForTimeout(300);

    // Check that the new column headers appear
    const col1Header = page.locator('.ag-header-cell-text:has-text("custom_col_1")');
    const col2Header = page.locator('.ag-header-cell-text:has-text("custom_col_2")');
    
    await expect(col1Header).toBeVisible({ timeout: 5000 });
    await expect(col2Header).toBeVisible({ timeout: 5000 });
  });
});

