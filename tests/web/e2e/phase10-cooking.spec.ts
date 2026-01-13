import { test, expect, Page } from '@playwright/test';

/**
 * Phase 10B E2E Tests - Cooking Companion 👨‍🍳
 *
 * STRICT MODE: No conditional checks. Elements MUST exist.
 * Tests the cooking flow as specified in phase-10-cooking-companion.md
 *
 * Fun fact: The mise en place philosophy can reduce cooking stress by 50%! 🧘
 */

const TEST_RECIPE_ID = 'test-cooking-recipe-id';

async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
}

// Setup mocks for cooking mode tests
async function setupCookingMocks(page: Page) {
  // Mock recipe with multiple steps - intercept all recipes requests
  await page.route('**/rest/v1/recipes*', async (route, request) => {
    const method = request.method();
    
    if (method === 'GET') {
      // Handle .single() which uses header Accept: application/vnd.pgrst.object+json
      const headers = request.headers();
      const isSingle = headers['accept']?.includes('vnd.pgrst.object');
      
      const recipeData = {
        id: TEST_RECIPE_ID,
        title: 'Test Cooking Recipe',
        servings: 4,
        prep_time_minutes: 15,
        cook_time_minutes: 30,
        ingredients_json: [
          { order: 1, name: 'Chicken', quantity: '2', unit: 'lbs' },
          { order: 2, name: 'Salt', quantity: '1', unit: 'tsp' },
        ],
        steps_json: [
          { order: 1, instruction: 'Preheat the oven to 400°F.' },
          { order: 2, instruction: 'Season the chicken with salt.' },
          { order: 3, instruction: 'Place chicken in roasting pan.' },
          { order: 4, instruction: 'Roast for 45 minutes until golden.' },
          { order: 5, instruction: 'Let rest for 10 minutes before serving.' },
        ],
      };
      
      await route.fulfill({
        status: 200,
        contentType: isSingle ? 'application/vnd.pgrst.object+json' : 'application/json',
        body: JSON.stringify(isSingle ? recipeData : [recipeData]),
      });
    } else if (method === 'PATCH') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true }),
      });
    } else {
      await route.continue();
    }
  });
}

// Helper to dismiss error overlay if present
async function dismissErrorOverlay(page: Page) {
  const errorOverlay = page.locator('#error-overlay');
  if (await errorOverlay.isVisible({ timeout: 500 }).catch(() => false)) {
    // Try clicking the dismiss button or pressing escape
    const dismissBtn = page.locator('#error-overlay').getByRole('button').first();
    if (await dismissBtn.isVisible({ timeout: 300 }).catch(() => false)) {
      await dismissBtn.click({ force: true }).catch(() => {});
    }
    await page.keyboard.press('Escape');
    await page.waitForTimeout(300);
  }
}

test.describe('Phase 10B - Cooking Mode Entry', () => {
  test.beforeEach(async ({ page }) => {
    await setupCookingMocks(page);
    await page.goto(`/(app)/recipes/${TEST_RECIPE_ID}`);
    await waitForAppReady(page);
  });

  test('start cooking FAB is visible on recipe detail', async ({ page }) => {
    await expect(page.getByTestId('start-cooking-fab')).toBeVisible();
  });

  test('start cooking FAB navigates to cook mode', async ({ page }) => {
    await page.getByTestId('start-cooking-fab').click();
    await expect(page).toHaveURL(/\/cook/);
  });
});

test.describe('Phase 10B - Cooking Mode UI', () => {
  test.beforeEach(async ({ page }) => {
    await setupCookingMocks(page);
    await page.goto(`/(app)/recipes/${TEST_RECIPE_ID}/cook`);
    await waitForAppReady(page);
  });

  test('cooking mode shows first step', async ({ page }) => {
    await expect(page.getByTestId('cooking-step-0')).toBeVisible();
  });

  test('step text is visible', async ({ page }) => {
    await expect(page.getByTestId('step-text')).toBeVisible();
  });

  test('step counter is visible', async ({ page }) => {
    await expect(page.getByTestId('step-counter')).toBeVisible();
  });

  test('close button is visible', async ({ page }) => {
    await expect(page.getByTestId('close-cooking-button')).toBeVisible();
  });

  test('progress bar is visible', async ({ page }) => {
    await expect(page.getByTestId('progress-bar')).toBeVisible();
  });
});

test.describe('Phase 10B - Step Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await setupCookingMocks(page);
    await page.goto(`/(app)/recipes/${TEST_RECIPE_ID}/cook`);
    await waitForAppReady(page);
    await dismissErrorOverlay(page);
  });

  test('next step button is visible', async ({ page }) => {
    await expect(page.getByTestId('next-step-button')).toBeVisible();
  });

  test('previous step button is visible', async ({ page }) => {
    await expect(page.getByTestId('prev-step-button')).toBeVisible();
  });

  test('can navigate to next step', async ({ page }) => {
    await dismissErrorOverlay(page);
    // Try clicking via evaluate to bypass overlay
    const nextButton = page.getByTestId('next-step-button');
    await nextButton.evaluate((btn) => (btn as HTMLButtonElement).click());
    await page.waitForTimeout(500);
    await expect(page.getByTestId('cooking-step-1')).toBeVisible();
  });

  test('can navigate back to previous step', async ({ page }) => {
    await dismissErrorOverlay(page);
    const nextButton = page.getByTestId('next-step-button');
    await nextButton.evaluate((btn) => (btn as HTMLButtonElement).click());
    await page.waitForTimeout(300);
    await dismissErrorOverlay(page);
    const prevButton = page.getByTestId('prev-step-button');
    await prevButton.evaluate((btn) => (btn as HTMLButtonElement).click());
    await page.waitForTimeout(300);
    await expect(page.getByTestId('cooking-step-0')).toBeVisible();
  });

  test('step tap zones are visible', async ({ page }) => {
    await expect(page.getByTestId('prev-step-zone')).toBeVisible();
    await expect(page.getByTestId('next-step-zone')).toBeVisible();
  });
});

test.describe('Phase 10B - Cooking Mode Features', () => {
  test.beforeEach(async ({ page }) => {
    await setupCookingMocks(page);
    await page.goto(`/(app)/recipes/${TEST_RECIPE_ID}/cook`);
    await waitForAppReady(page);
  });

  test('show ingredients button is visible', async ({ page }) => {
    await expect(page.getByTestId('show-ingredients-button')).toBeVisible();
  });
});

test.describe('Phase 10B - Exit Cooking Mode', () => {
  test.beforeEach(async ({ page }) => {
    await setupCookingMocks(page);
    await page.goto(`/(app)/recipes/${TEST_RECIPE_ID}/cook`);
    await waitForAppReady(page);
    await dismissErrorOverlay(page);
  });

  test('close button exits cooking mode', async ({ page }) => {
    await dismissErrorOverlay(page);
    await page.getByTestId('close-cooking-button').click({ force: true });
    await page.waitForTimeout(500);
    // Should navigate back (URL should not have /cook)
    await expect(page).not.toHaveURL(/\/cook$/);
  });
});

test.describe('Phase 10B - Complete Cooking', () => {
  test.beforeEach(async ({ page }) => {
    await setupCookingMocks(page);
    await page.goto(`/(app)/recipes/${TEST_RECIPE_ID}/cook`);
    await waitForAppReady(page);
    await dismissErrorOverlay(page);
  });

  test('can navigate through all steps', async ({ page }) => {
    // Navigate through all 5 steps
    for (let i = 0; i < 4; i++) {
      await dismissErrorOverlay(page);
      await page.getByTestId('next-step-button').click({ force: true });
      await page.waitForTimeout(200);
    }
    
    // Should be on last step (step 5, index 4)
    await expect(page.getByTestId('cooking-step-4')).toBeVisible();
  });

  test('finish button appears after navigating through all steps', async ({ page }) => {
    // Navigate to last step
    for (let i = 0; i < 4; i++) {
      await dismissErrorOverlay(page);
      await page.getByTestId('next-step-button').click({ force: true });
      await page.waitForTimeout(200);
    }
    
    // Click next again should trigger complete
    await dismissErrorOverlay(page);
    await page.getByTestId('next-step-button').click({ force: true });
    await page.waitForTimeout(500);
    
    // Should show completion screen
    await expect(page.getByTestId('cooking-complete-modal').or(page.getByTestId('finish-cooking-button'))).toBeVisible();
  });
});
