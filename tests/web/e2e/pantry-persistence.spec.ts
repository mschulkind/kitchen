import { test, expect, Page } from '@playwright/test';

/**
 * Pantry Persistence Regression Test 🍏
 *
 * Validates that items added to the pantry are persisted to the database
 * and visible after reload.
 *
 * Bugs Covered:
 * - [2026-01-19] Pantry Item Persistence (BLOCKER)
 */

async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  // Wait for the root to be stable (simple heuristic)
  await page.waitForTimeout(2000); 
}

test.describe('Pantry Persistence', () => {

  test('User can add item and it persists', async ({ page }) => {
    page.on('console', msg => console.log('PAGE LOG:', msg.text()));
    
    // --- 1. LOGIN ---
    console.log('Step 1: Dev Login');
    await page.goto('/devlogin');
    
    await expect(page.getByLabel('Service Account Email')).toBeVisible();
    await page.getByLabel('Service Account Email').fill('admin@kitchen.local');
    await page.getByLabel('Password').fill('admin123'); // Password from seed_dev_data.py
    
    console.log('Current URL:', page.url());
    // console.log('Page Content:', await page.content());
    
    await page.getByTestId('dev-login-button').click();
    
    // Should pass through to landing or hub? 
    // Usually devlogin redirects to router.replace('/(app)')
    await expect(page).not.toHaveURL(/devlogin/);
    await waitForAppReady(page);

    // --- 2. NAVIGATE TO PANTRY ---
    console.log('Step 2: Navigate to Pantry');
    // We might be on Hub. Check if we can find navigating to Pantry.
    const onHub = await page.getByTestId('hub-screen').isVisible();
    if (onHub) {
        await page.getByTestId('pantry-card').click();
    } else {
        // Force navigation just in case
        await page.goto('/(app)/inventory');
    }
    
    await expect(page.getByRole('heading', { name: 'Pantry' })).toBeVisible();

    // --- 3. ADD ITEM ---
    console.log('Step 3: Add Item "Test Apple"');
    
    // Depending on empty state or not, we might have specific button
    // The header button is always there
    const addButton = page.getByTestId('add-item-button');
    if (await addButton.isVisible()) {
        await addButton.click();
    } else {
        // Try the empty state button
        await page.getByTestId('add-first-item').click();
    }
    
    // Wait for sheet
    await expect(page.getByText('Add Item ➕')).toBeVisible();
    
    const itemName = `Test Apple ${Date.now()}`;
    await page.getByTestId('item-name-input').fill(itemName);
    // Use last() to avoid strict mode violation if ID is duplicated
    await page.getByTestId('location-fridge').last().click({ force: true });
    await page.getByTestId('save-item-button').click({ force: true });
    
    // Wait for sheet to close or explicit success
    try {
        await expect(page.getByText('Add Item ➕')).not.toBeVisible();
    } catch (e) {
        // If sheet is still open, dump content
        // locator('..') from header gets the parent YStack
        const sheetContent = await page.getByText('Add Item ➕').locator('..').textContent();
        console.log('❌ Sheet Content:', sheetContent);
        throw e;
    }

    // --- 4. VERIFY PERSISTENCE ---
    console.log(`Step 4: Verify ${itemName} exists`);
    await expect(page.getByText(itemName)).toBeVisible(); // Might be in list

    // --- 5. RELOAD ---
    console.log('Step 5: Reload and Verify');
    await page.reload();
    await waitForAppReady(page);
    await expect(page.getByText(itemName)).toBeVisible();
    
    console.log('Success! Pantry item persisted.');
  });
});
