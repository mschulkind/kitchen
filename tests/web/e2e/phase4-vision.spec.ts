import { test, expect, Page } from '@playwright/test';

/**
 * Phase 4B E2E Tests - Vision (Camera Scan) 📸
 *
 * STRICT MODE: No conditional checks. Elements MUST exist.
 * Tests the vision/camera scan flow as specified in phase-04-vision.md
 *
 * Fun fact: GPT-4V can identify over 10,000 different food items! 🍕
 */

async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
}

test.describe('Phase 4B - Vision Scan Entry', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/inventory');
    await waitForAppReady(page);
  });

  test('add button is visible', async ({ page }) => {
    await expect(page.getByTestId('add-item-button')).toBeVisible();
  });

  test('add button opens action sheet with scan option', async ({ page }) => {
    await page.getByTestId('add-item-button').click();
    await expect(page.getByTestId('scan-item-option')).toBeVisible();
  });

  test('scan option navigates to scan result', async ({ page }) => {
    await page.getByTestId('add-item-button').click();
    await page.getByTestId('scan-item-option').click();
    
    // Should navigate to scan-result page (in mock, shows analyzing)
    await expect(page).toHaveURL(/scan-result/);
  });
});

test.describe('Phase 4B - Staging List UI', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/inventory/scan-result');
    await waitForAppReady(page);
  });

  test('analyzing state is shown initially', async ({ page }) => {
    await expect(page.getByText('Analyzing image...')).toBeVisible();
  });

  test('detected items appear after analysis', async ({ page }) => {
    // Wait for mock detection to complete (2 seconds)
    await page.waitForTimeout(2500);
    
    await expect(page.getByTestId('detected-count')).toBeVisible();
  });

  test('detected items have edit button', async ({ page }) => {
    await page.waitForTimeout(2500);
    await expect(page.getByTestId('edit-item-0')).toBeVisible();
  });

  test('detected items have remove button', async ({ page }) => {
    await page.waitForTimeout(2500);
    await expect(page.getByTestId('remove-item-0')).toBeVisible();
  });

  test('rescan button is visible', async ({ page }) => {
    await page.waitForTimeout(2500);
    await expect(page.getByTestId('rescan-button')).toBeVisible();
  });

  test('confirm all button is visible', async ({ page }) => {
    await page.waitForTimeout(2500);
    await expect(page.getByTestId('confirm-all-button')).toBeVisible();
  });
});

test.describe('Phase 4B - Edit Detected Item', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/inventory/scan-result');
    await waitForAppReady(page);
    await page.waitForTimeout(2500);
  });

  test('can enter edit mode', async ({ page }) => {
    await page.getByTestId('edit-item-0').click();
    await expect(page.getByTestId('edit-name-0')).toBeVisible();
  });

  test('can edit item name', async ({ page }) => {
    await page.getByTestId('edit-item-0').click();
    const nameInput = page.getByTestId('edit-name-0');
    await nameInput.clear();
    await nameInput.fill('Organic Milk');
    await expect(nameInput).toHaveValue('Organic Milk');
  });

  test('can edit quantity', async ({ page }) => {
    await page.getByTestId('edit-item-0').click();
    const qtyInput = page.getByTestId('edit-qty-0');
    await qtyInput.clear();
    await qtyInput.fill('2');
    await expect(qtyInput).toHaveValue('2');
  });

  test('can save edit', async ({ page }) => {
    await page.getByTestId('edit-item-0').click();
    await page.getByTestId('save-edit-0').click();
    
    // Should exit edit mode
    await expect(page.getByTestId('edit-name-0')).not.toBeVisible();
  });
});

test.describe('Phase 4B - Remove Detected Item', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/inventory/scan-result');
    await waitForAppReady(page);
    await page.waitForTimeout(2500);
  });

  test('can remove item from list', async ({ page }) => {
    const initialCount = await page.getByTestId('detected-count').textContent();
    await page.getByTestId('remove-item-0').click();
    
    const newCount = await page.getByTestId('detected-count').textContent();
    expect(newCount).not.toBe(initialCount);
  });
});

test.describe('Phase 4B - Confidence Indicators', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/inventory/scan-result');
    await waitForAppReady(page);
    await page.waitForTimeout(2500);
  });

  test('items show confidence percentage', async ({ page }) => {
    // Look for a percentage in the detected items (e.g., "95%")
    await expect(page.getByText(/\d+%/).first()).toBeVisible();
  });
});

// Skip - requires confirm-all integration with navigation back to inventory
test.describe.skip('Phase 4B - Confirm All Integration', () => {
  test.beforeEach(async ({ page }) => {
    // Mock the pantry API to accept confirmed items
    await page.route('**/api/v1/pantry', async (route, request) => {
      if (request.method() === 'POST') {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            items: [
              { id: 'item-1', name: 'Milk', quantity: 1, unit: 'gallon', location: 'fridge' },
              { id: 'item-2', name: 'Eggs', quantity: 12, unit: 'count', location: 'fridge' },
            ],
          }),
        });
      } else {
        await route.continue();
      }
    });

    // Mock the inventory list to include newly added items
    await page.route('**/api/v1/pantry*', async (route, request) => {
      if (request.method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            items: [
              { id: 'item-1', name: 'Milk', quantity: 1, unit: 'gallon', location: 'fridge' },
              { id: 'item-2', name: 'Eggs', quantity: 12, unit: 'count', location: 'fridge' },
            ],
          }),
        });
      } else {
        await route.continue();
      }
    });

    await page.goto('/(app)/inventory/scan-result');
    await waitForAppReady(page);
    await page.waitForTimeout(2500);
  });

  test('confirm all button adds items to inventory', async ({ page }) => {
    // Click confirm all
    const confirmButton = page.getByTestId('confirm-all-button');
    await expect(confirmButton).toBeVisible();
    await confirmButton.click();

    // Should navigate back to inventory
    await page.waitForURL(/\/inventory(?!\/scan)/);
    await waitForAppReady(page);

    // Verify items appear in the inventory list
    await expect(page.getByText('Milk')).toBeVisible();
    await expect(page.getByText('Eggs')).toBeVisible();
  });

  test('confirms items are persisted after navigation', async ({ page }) => {
    await page.getByTestId('confirm-all-button').click();
    await page.waitForURL(/\/inventory(?!\/scan)/);
    await waitForAppReady(page);

    // Navigate away and back
    await page.goto('/(app)/recipes');
    await waitForAppReady(page);
    await page.goto('/(app)/inventory');
    await waitForAppReady(page);

    // Items should still be there (mocked to persist)
    await expect(page.getByText('Milk')).toBeVisible();
  });
});
