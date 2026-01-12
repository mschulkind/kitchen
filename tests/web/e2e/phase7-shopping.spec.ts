import { test, expect, Page } from '@playwright/test';

/**
 * Phase 7C E2E Tests - Shopping List 🛒
 *
 * Tests the shopping list functionality.
 *
 * STRICT MODE: No conditional checks. Elements MUST exist.
 */

async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
}

test.describe('Phase 7C - Shopping List Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/shopping');
    await waitForAppReady(page);
  });

  test('shopping page loads', async ({ page }) => {
    await expect(page.getByText('Shopping List')).toBeVisible();
  });

  test('can add a manual item', async ({ page }) => {
    const dataInput = page.getByPlaceholder('Add item...');
    await expect(dataInput).toBeVisible();
    
    await dataInput.fill('Milk');
    await page.getByTestId('add-item-button').click();
    
    // Should appear in list
    await expect(page.getByText('Milk')).toBeVisible();
  });

  test('can check off an item', async ({ page }) => {
    // Assuming 'Milk' is in the list from previous or seed
    // For strict test, we might need to add it first if db is clean
    const dataInput = page.getByPlaceholder('Add item...');
    await dataInput.fill('Eggs');
    await page.getByTestId('add-item-button').click();
    
    const checkbox = page.getByTestId('check-Eggs');
    await checkbox.click();
    
    // Should move to completed section or be crossed out
    await expect(page.getByTestId('completed-items')).toContainText('Eggs');
  });

  test('can clear completed items', async ({ page }) => {
    const clearBtn = page.getByText('Clear Completed');
    await expect(clearBtn).toBeVisible();
    await clearBtn.click();
    
    // Verify eggs are gone
    await expect(page.getByText('Eggs')).not.toBeVisible();
  });
});
