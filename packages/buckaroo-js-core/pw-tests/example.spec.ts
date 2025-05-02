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
test('has title', async ({ page }) => {
    await page.goto('http://localhost:6006/iframe.html?viewMode=docs&id=buckaroo-dfviewer-dfviewerinfiniteshadow--docs&globals=')
    
  await page.goto('http://localhost:6006/iframe.html?viewMode=docs&id=buckaroo-dfviewer-dfviewerinfiniteshadow--docs&globals=');
  await page.locator('.ag-header-cell-label').first().click();

    // await page.waitForLoadState(); // The promise resolves after 'load' event.

    // await page.waitForLoadState('domcontentloaded');
    // await page.waitForTimeout(1000);
    // await page.
    // await waitForLog(page, "[DFViewerInfinite] Total render time: ")
    // await waitForLog(page, "[DFViewerInfinite] Total render time: ")
    // await waitForLog(page, "[DFViewerInfinite] Total render time: ")
    // await waitForLog(page, "[DFViewerInfinite] Total render time: ")
    // await waitForLog(page, "[DFViewerInfinite] Total render time: ")
    //await waitForLog(page, "[DFViewerInfinite] Total render time: ")
    //await waitForLog(page, "[DFViewerInfinite] Total render time: ")
    
    await waitForCells(page)
    // const rowIndex=2;
    // const locatorString = `[row-index="${rowIndex}"]`;
    // const rowSomething =  page.locator(locatorString);
    // console.log(rowSomething)
    expect(await getRowCount(page)).toBe(4);
    const rc = await getRowContents(page, 0);
    expect(rc).toBe(["20.00      ",
"  20",
"foo",
"foo",
undefined,
undefined,
undefined,
undefined,
		    ])

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
