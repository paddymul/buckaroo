import { Page } from '@playwright/test';
import { test, expect } from '@playwright/test';

export async function waitForCells(page: Page) {
    await page.locator('.ag-overlay').first().waitFor({ state: 'hidden' });
    await page.locator('.ag-cell').first().waitFor({ state: 'visible' });
}

test('has title', async ({ page }) => {
    await page.goto('http://localhost:6006/iframe.html?viewMode=docs&id=buckaroo-dfviewer-dfviewerinfiniteshadow--docs&globals=')
    
    await waitForCells(page)
});

test('get started link', async ({ page }) => {
  await page.goto('https://playwright.dev/');

  // Click the get started link.
  await page.getByRole('link', { name: 'Get started' }).click();

  // Expects page to have a heading with the name of Installation.
  await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible();
});
