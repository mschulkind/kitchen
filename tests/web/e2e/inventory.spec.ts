import { test, expect } from '@playwright/test';

test('add inventory item', async ({ page }) => {
  // 1. Go to Inventory Page
  await page.goto('http://localhost:8081/inventory');

  // 2. Click Add
  await page.getByRole('button', { name: 'Add (+)' }).click();

  // 3. Fill Form
  await page.getByLabel('Name').fill('Milk');
  await page.getByLabel('Quantity').fill('1');
  await page.getByLabel('Unit').fill('Gallon');

  // 4. Save
  await page.getByRole('button', { name: 'Save' }).click();

  // 5. Verify
  await expect(page.getByText('Milk')).toBeVisible();
  await expect(page.getByText('1 Gallon')).toBeVisible();
});
