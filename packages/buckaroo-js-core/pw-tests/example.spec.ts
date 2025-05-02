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
    ///await page.goto('http://localhost:6006/iframe.html?viewMode=docs&id=buckaroo-dfviewer-dfviewerinfiniteshadow--docs&globals=')
    
    await page.goto('http://localhost:6006/iframe.html?viewMode=story&id=buckaroo-dfviewer-dfviewerinfiniteshadow--primary&globals=&args=')
  //await page.locator('.ag-header-cell-label').first().click();
    await page.waitForTimeout(1000);
    await waitForGridReady(page);
    const rc = await getRowContents(page, 0);
    expect(rc).toBe([  "20.00",
  "20",
  "foo",
  "foo",
		    ]);
//     expect(rc).toBe(["20.00      ",
// "  20",
// "foo",
// "foo",
// undefined,
// undefined,
// undefined,
// undefined,
// 		    ])

    // await page.waitForLoadState(); // The promise resolves after 'load' event.

    // await page.waitForLoadState('domcontentloaded');
    // await page.waitForTimeout(1000);
    // await page.p
    // await waitForLog(page, "[DFViewerInfinite] Total render time: ")
    // await waitForLog(page, "[DFViewerInfinite] Total render time: ")
    // await waitForLog(page, "[DFViewerInfinite] Total render time: ")
    // await waitForLog(page, "[DFViewerInfinite] Total render time: ")
    // await waitForLog(page, "[DFViewerInfinite] Total render time: ")
    //await waitForLog(page, "[DFViewerInfinite] Total render time: ")
    //await waitForLog(page, "[DFViewerInfinite] Total render time: ")
    
    // await waitForCells(page)
    // // const rowIndex=2;
    // // const locatorString = `[row-index="${rowIndex}"]`;
    // // const rowSomething =  page.locator(locatorString);
    // // console.log(rowSomething)
    // expect(await getRowCount(page)).toBe(4);


    // //const cells = await getRowLocator(page, rowIndex).getByRole('gridcell').all();
    // // const cells = await rowSomething.getByRole('gridcell').all();
    // // expect(cells).toBe("")
    // // expect(rowSomething).toBe("")
    // await expect( getRowCount(page)).toBe(3)
});

// test('get started link', async ({ page }) => {
//   await page.goto('https://playwright.dev/');

//   // Click the get started link.
//   await page.getByRole('link', { name: 'Get started' }).click();

//   // Expects page to have a heading with the name of Installation.
//   await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible();
// });
