import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  await page.goto('http://localhost:6006/iframe.html?viewMode=docs&id=buckaroo-dfviewer-dfviewerinfiniteshadow--docs&globals=');
  await page.locator('.ag-header-cell-label').first().click();


  await page.locator('#cell-a-1218').click({
    button: 'right'
  });
  await page.locator('.ag-center-cols-container > div:nth-child(5) > div:nth-child(2)').first().click();
  await page.locator('#story--buckaroo-dfviewer-dfviewerinfiniteshadow--primary--primary-inner').getByRole('button', { name: 'Toggle Config' }).click();
  await page.getByText('Current Config: Secondary').click();
});