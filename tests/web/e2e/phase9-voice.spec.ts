import { test, expect } from '@playwright/test';

/**
 * Phase 9A E2E Tests - Voice Webhook Integration 🎙️
 *
 * STRICT MODE: Tests API webhook endpoints directly.
 * Tests the voice webhook endpoint as specified in phase-09-voice.md
 *
 * Fun fact: Natural Language Processing has improved 10x since 2017! 🤖
 */

const API_BASE_URL = process.env.API_URL || 'http://localhost:5300';
const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET || 'test-secret';

test.describe('Phase 9A - Voice Webhook Endpoint', () => {
  test('health endpoint is reachable', async ({ request }) => {
    const response = await request.get(`${API_BASE_URL}/api/v1/health`);
    expect(response.status()).toBe(200);
  });

  test('add-item webhook exists', async ({ request }) => {
    const response = await request.post(
      `${API_BASE_URL}/api/v1/hooks/add-item?key=${WEBHOOK_SECRET}`,
      {
        data: { text: 'milk' },
        failOnStatusCode: false,
      }
    );
    
    // Should not be 404 - endpoint exists
    expect(response.status()).not.toBe(404);
  });

  test('webhook requires authentication', async ({ request }) => {
    const response = await request.post(
      `${API_BASE_URL}/api/v1/hooks/add-item`,
      {
        data: { text: 'milk' },
        failOnStatusCode: false,
      }
    );
    
    // Should be 401 or 403 without key
    expect([401, 403]).toContain(response.status());
  });

  test('webhook parses single item', async ({ request }) => {
    const response = await request.post(
      `${API_BASE_URL}/api/v1/hooks/add-item?key=${WEBHOOK_SECRET}`,
      { data: { text: 'bread' } }
    );
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.items).toHaveLength(1);
    expect(data.items[0].name).toBe('bread');
  });

  test('webhook parses quantity', async ({ request }) => {
    const response = await request.post(
      `${API_BASE_URL}/api/v1/hooks/add-item?key=${WEBHOOK_SECRET}`,
      { data: { text: '2 gallons of milk' } }
    );
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.items[0].quantity).toBe(2);
    expect(data.items[0].unit).toBe('gallon');
    expect(data.items[0].name).toBe('milk');
  });

  test('webhook parses multiple items', async ({ request }) => {
    const response = await request.post(
      `${API_BASE_URL}/api/v1/hooks/add-item?key=${WEBHOOK_SECRET}`,
      { data: { text: 'bread and butter and 3 eggs' } }
    );
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.items.length).toBeGreaterThanOrEqual(3);
  });
});

test.describe('Phase 9A - Voice Quick Add UI', () => {
  test('microphone button is visible on shopping list', async ({ page }) => {
    await page.goto('/(app)/shopping');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);
    
    await expect(page.getByTestId('voice-add-button')).toBeVisible();
  });

  test('microphone button opens voice modal', async ({ page }) => {
    await page.goto('/(app)/shopping');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);
    
    await page.getByTestId('voice-add-button').click();
    await expect(page.getByTestId('voice-modal')).toBeVisible();
  });

  test('voice modal shows listening state', async ({ page }) => {
    await page.goto('/(app)/shopping');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(1000);
    
    await page.getByTestId('voice-add-button').click();
    await expect(page.getByText('Listening...')).toBeVisible();
  });
});
