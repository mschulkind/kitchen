import { test, expect, Page } from '@playwright/test';

/**
 * Phase 10B E2E Tests - Cooking Companion 👨‍🍳
 *
 * STRICT MODE: No conditional checks. Elements MUST exist.
 * Tests the cooking flow as specified in phase-10-cooking-companion.md
 * 
 * NOTE: All tests are skipped until seed data is implemented.
 * These tests require an existing recipe with steps.
 * TODO: Implement seed data or create-recipe fixture
 *
 * Fun fact: The mise en place philosophy can reduce cooking stress by 50%! 🧘
 */

async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1000);
}

// Skip all cooking tests - they require seed data with test-recipe-id
test.describe.skip('Phase 10B - Cooking Mode Entry', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/recipes/test-recipe-id');
    await waitForAppReady(page);
  });

  test('start cooking FAB is visible', async ({ page }) => {
    await expect(page.getByTestId('start-cooking-fab')).toBeVisible();
  });

  test('start cooking navigates to cook mode', async ({ page }) => {
    await page.getByTestId('start-cooking-fab').click();
    await expect(page).toHaveURL(/\/cook$/);
  });
});

test.describe.skip('Phase 10B - Cooking Mode UI', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/recipes/test-recipe-id/cook');
    await waitForAppReady(page);
  });

  test('cooking mode shows current step', async ({ page }) => {
    await expect(page.getByTestId('cooking-step-0')).toBeVisible();
  });

  test('step text is large and readable', async ({ page }) => {
    const stepText = page.getByTestId('step-text');
    await expect(stepText).toBeVisible();
    const fontSize = await stepText.evaluate(el => 
      window.getComputedStyle(el).fontSize
    );
    const size = parseInt(fontSize);
    expect(size).toBeGreaterThanOrEqual(20);
  });

  test('step counter is visible', async ({ page }) => {
    await expect(page.getByTestId('step-counter')).toBeVisible();
    await expect(page.getByTestId('step-counter')).toContainText('Step 1');
  });

  test('close button is visible', async ({ page }) => {
    await expect(page.getByTestId('close-cooking-button')).toBeVisible();
  });
});

test.describe.skip('Phase 10B - Step Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/recipes/test-recipe-id/cook');
    await waitForAppReady(page);
  });

  test('next step button is visible', async ({ page }) => {
    await expect(page.getByTestId('next-step-button')).toBeVisible();
  });

  test('previous step button is visible', async ({ page }) => {
    await expect(page.getByTestId('prev-step-button')).toBeVisible();
  });

  test('prev is disabled on first step', async ({ page }) => {
    await expect(page.getByTestId('prev-step-button')).toBeDisabled();
  });

  test('can navigate to next step', async ({ page }) => {
    await page.getByTestId('next-step-button').click();
    await expect(page.getByTestId('cooking-step-1')).toBeVisible();
    await expect(page.getByTestId('step-counter')).toContainText('Step 2');
  });

  test('can navigate back to previous step', async ({ page }) => {
    await page.getByTestId('next-step-button').click();
    await page.getByTestId('prev-step-button').click();
    await expect(page.getByTestId('cooking-step-0')).toBeVisible();
  });

  test('can tap anywhere to advance (large hit zones)', async ({ page }) => {
    const stepArea = page.getByTestId('step-tap-zone');
    await stepArea.click();
    await expect(page.getByTestId('cooking-step-1')).toBeVisible();
  });
});

test.describe.skip('Phase 10B - Cooking Mode Features', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/recipes/test-recipe-id/cook');
    await waitForAppReady(page);
  });

  test('ingredients button is visible', async ({ page }) => {
    await expect(page.getByTestId('show-ingredients-button')).toBeVisible();
  });

  test('can show ingredients panel', async ({ page }) => {
    await page.getByTestId('show-ingredients-button').click();
    await expect(page.getByTestId('ingredients-panel')).toBeVisible();
  });

  test('timer button is visible when step has time', async ({ page }) => {
    await page.getByTestId('next-step-button').click();
    await expect(page.getByTestId('start-timer-button')).toBeVisible();
  });

  test('progress indicator shows completion', async ({ page }) => {
    await expect(page.getByTestId('progress-bar')).toBeVisible();
  });
});

test.describe.skip('Phase 10B - Exit Cooking Mode', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/(app)/recipes/test-recipe-id/cook');
    await waitForAppReady(page);
  });

  test('close button exits cooking mode', async ({ page }) => {
    await page.getByTestId('close-cooking-button').click();
    await expect(page).not.toHaveURL(/\/cook$/);
  });

  test('finish button appears on last step', async ({ page }) => {
    for (let i = 0; i < 10; i++) {
      const nextBtn = page.getByTestId('next-step-button');
      if (await nextBtn.isDisabled()) break;
      await nextBtn.click();
    }
    await expect(page.getByTestId('finish-cooking-button')).toBeVisible();
  });

  test('finish marks recipe as cooked', async ({ page }) => {
    for (let i = 0; i < 10; i++) {
      const nextBtn = page.getByTestId('next-step-button');
      if (await nextBtn.isDisabled()) break;
      await nextBtn.click();
    }
    await page.getByTestId('finish-cooking-button').click();
    await expect(page.getByText('Cooking Complete!')).toBeVisible();
  });
});
