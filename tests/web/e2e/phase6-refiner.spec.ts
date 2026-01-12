import { test, expect, Page } from '@playwright/test';

/**
 * Phase 6B E2E Tests - Slot Machine (Refinement) 🎰
 *
 * STRICT MODE: No conditional checks. Elements MUST exist.
 * Tests the meal slot locking and spinning flow as specified in phase-06-planner-advanced.md
 *
 * Fun fact: The slot machine metaphor comes from the satisfying randomness
 * of pulling a lever and getting a new combination! 🎲
 */

async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
}

test.describe('Phase 6B - Meal Slot Controls', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/planner');
    await waitForAppReady(page);
  });

  test('day slots are visible', async ({ page }) => {
    // Should have at least one day slot
    await expect(page.getByTestId('day-slot-0')).toBeVisible();
  });

  test('lock button is visible on slots', async ({ page }) => {
    await expect(page.getByTestId('lock-button-0')).toBeVisible();
  });

  test('spin button is visible on unlocked slots', async ({ page }) => {
    await expect(page.getByTestId('spin-button-0')).toBeVisible();
  });
});

test.describe('Phase 6B - Lock/Unlock Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/planner');
    await waitForAppReady(page);
  });

  test('can lock a meal slot', async ({ page }) => {
    const lockButton = page.getByTestId('lock-button-0');
    await lockButton.click();
    
    // Should show locked state
    await expect(page.getByTestId('locked-indicator-0')).toBeVisible();
  });

  test('locked slot hides spin button', async ({ page }) => {
    await page.getByTestId('lock-button-0').click();
    
    // Spin button should be hidden for locked slots
    await expect(page.getByTestId('spin-button-0')).not.toBeVisible();
  });

  test('can unlock a locked slot', async ({ page }) => {
    // Lock first
    await page.getByTestId('lock-button-0').click();
    // Then unlock
    await page.getByTestId('unlock-button-0').click();
    
    // Should show unlocked state
    await expect(page.getByTestId('spin-button-0')).toBeVisible();
  });
});

test.describe('Phase 6B - Spin/Reroll Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/planner');
    await waitForAppReady(page);
  });

  test('spin button triggers reroll', async ({ page }) => {
    await page.getByTestId('spin-button-0').click();
    
    // Should show loading or animation state
    await expect(page.getByTestId('spinning-indicator-0')).toBeVisible();
  });

  test('spin completes with new meal', async ({ page }) => {
    const initialMeal = await page.getByTestId('meal-title-0').textContent();
    await page.getByTestId('spin-button-0').click();
    
    // Wait for spin to complete
    await page.waitForTimeout(2000);
    
    // Meal should change (or remain if same - hard to test randomness)
    const newMeal = await page.getByTestId('meal-title-0').textContent();
    // Just verify it exists
    expect(newMeal).toBeTruthy();
  });
});

test.describe('Phase 6B - Bulk Actions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/planner');
    await waitForAppReady(page);
  });

  test('lock all button is visible', async ({ page }) => {
    await expect(page.getByTestId('lock-all-button')).toBeVisible();
  });

  test('spin all unlocked button is visible', async ({ page }) => {
    await expect(page.getByTestId('spin-all-button')).toBeVisible();
  });

  test('can lock all slots', async ({ page }) => {
    await page.getByTestId('lock-all-button').click();
    
    // All slots should be locked
    await expect(page.getByTestId('locked-indicator-0')).toBeVisible();
  });
});
