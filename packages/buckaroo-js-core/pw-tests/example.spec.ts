import { test, expect } from '@playwright/test';
import { Page } from '@playwright/test';
import {waitForCells, getRowContents, getRowCount } from './ag-pw-utils';
const waitForLog = async (page, expectedLog) => {
  return new Promise((resolve) => {
    const handler = (msg) => {
      if (msg.text().includes(expectedLog)) {
        page.off('console', handler);
        resolve();
      }
    };
    page.on('console', handler);
  });
};

const logCounts = {}
const setupCounter = (page, expectedLog) => {
    logCounts[expectedLog] = 0;
    const handler = (msg) => {
      if (msg.text().includes(expectedLog)) {
	  logCounts[expectedLog] +=1
      }
    };
    page.on('console', handler);
};

 async function waitForGridReady(page: Page) {
    await page.locator('ag-overlay-loading-center').first().waitFor({ state: 'hidden' });
    // Normal cells
    const cellLocator =page.locator('.ag-cell');
    // Grouped cells
    const cellWrapperLocator = page.locator('.ag-cell-wrapper');
    // Full width only cells
    const fullWidthRow = page.locator('.ag-full-width-row');
    // No rows to show
    const noRowsToShowLocator = page.locator('.ag-overlay-no-rows-center');
    await cellLocator.or(cellWrapperLocator).or(noRowsToShowLocator).or(fullWidthRow).first().waitFor({ state: 'visible' });
}
test('has title', async ({ page }) => {
    await page.goto('http://localhost:6006/iframe.html?viewMode=story&id=buckaroo-dfviewer-dfviewerinfiniteshadow--primary&globals=&args=')
    const RenderLogMsg= "[DFViewerInfinite] Total render time:"
    setupCounter(page, RenderLogMsg)

  //await page.locator('.ag-header-cell-label').first().click();
    await page.waitForTimeout(1000);
    await waitForGridReady(page);
    const rc = await getRowContents(page, 0);
    expect(rc).toStrictEqual(["20.00      ", "  20", "foo", "foo", ]);
    expect(logCounts[RenderLogMsg]).toBe(1);

    await page.getByRole('button', { name: 'Toggle Config' }).click();
    expect(logCounts[RenderLogMsg]).toBe(2);

});
