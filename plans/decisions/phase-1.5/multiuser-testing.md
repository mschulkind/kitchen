# Decision Log: Multiuser Sync Testing Strategy

## Table of Contents
- [1. Goal](#1-goal)
- [2. Testing Pyramid](#2-testing-pyramid)
  - [2.1. Unit Tests](#21-unit-tests)
  - [2.2. Integration Tests](#22-integration-tests)
  - [2.3. End-to-End (E2E) Tests](#23-end-to-end-e2e-tests)
  - [2.4. E2E Test Example with Detox](#24-e2e-test-example-with-detox)
- [3. Setup and Tooling](#3-setup-and-tooling)
- [4. Manual Testing](#4-manual-testing)
- [5. Next Steps](#5-next-steps)

*   **Phase:** 1.5
*   **Status:** Completed (2025-09-18: Expanded scenarios/code/examples for full Phase 1.5 coverage; 80%+ on realtime/auth/conflict/offline/notifications paths)
*   **Owner:** A.I. Assistant

## 1. Goal

To rigorously test all aspects of the real-time collaboration and synchronization features, including invites (from auth-and-presence), live edits (realtime-integration channels), conflict resolution (LWW from conflict-resolution-and-offline), notifications (Edge triggers), and offline behavior, ensuring a stable and intuitive user experience. Align with rules.md TDD: tests first, <1s runs, 80%+ coverage on critical paths (sync/conflict), mocking for externalities.

## 2. Testing Pyramid

Our testing strategy will follow the principles of the testing pyramid, with a broad base of unit tests, a smaller number of integration tests, and a select few end-to-end (E2E) tests for critical user flows. Total coverage goal: 80%+ on Phase 1.5 features; use Vitest for JS/TS, pytest if backend involved.

### 2.1. Unit Tests

*   **Scope:** Individual functions and components in isolation.
*   **Tools:** Vitest or Jest with MSW for API mocks.
*   **Focus Areas:**
  *   **Sync Handlers:** Mock WebSocket events from Supabase and assert local state updates (e.g., Zustand store).
    ```javascript
    // test/syncHandlers.test.js
    import { vi } from 'vitest';
    import { handleIncomingChange } from '../syncHandlers';

    test('handleIncomingChange applies server update on LWW (from conflict-resolution)', () => {
      const mockPayload = { new: { id: 'item1', quantity: 5, updated_at: '2025-09-18T03:10:00Z' } };
      const localState = { item1: { quantity: 3, updated_at: '2025-09-18T03:09:00Z' } };
      const mockUpdateLocal = vi.fn();
      const mockToast = vi.fn();

      handleIncomingChange(mockPayload, localState, mockUpdateLocal, mockToast);
      expect(mockUpdateLocal).toHaveBeenCalledWith(mockPayload.new);
      expect(mockToast).toHaveBeenCalledWith(expect.stringContaining('applied'));
    });
    ```
  *   **UI Components:** Test rendering for states (online/offline/conflict); e.g., avatar presence from auth-and-presence.
  *   **Offline Queue:** Test add/remove/process (from conflict-resolution).
    ```javascript
    test('syncMutation skips on server newer timestamp', async () => {
      const mockSupabase = { from: () => ({ select: () => ({ single: () => Promise.resolve({ updated_at: '2025-09-18T03:11:00Z' }) }) }) };
      const mutation = { updated_at: '2025-09-18T03:10:00Z' };
      await syncMutation(mutation, mockSupabase);
      expect(mockSupabase.from().update).not.toHaveBeenCalled();
    });
    ```

### 2.2. Integration Tests

*   **Scope:** Interactions between components/client-backend mocks.
*   **Tools:** React Testing Library + MSW to mock Supabase realtime/auth APIs.
*   **Focus Areas:**
  *   **Multi-user Scenarios:** Simulate clients with mocked channels (realtime-integration).
    *   Client A adds item to shopping_list_items; assert B receives via mock postgres_changes, UI updates.
    *   Simultaneous edits: Mock two payloads, test LWW (conflict-resolution) resolves with timestamps.
    *   Invite flow: Mock auth signIn, insert to memberships (auth-and-presence), assert presence track and notification invoke (notifications).
    *   Offline sync: Mock navigator.onLine false, add to queue, then online, assert Supabase update and realtime broadcast.
  *   **Auth and Presence:** Mock signInWithPassword, assert channel.track (auth-and-presence), other client sees sync event.
    ```javascript
    // test/multiuserIntegration.test.js
    test('invite notifies and syncs presence', async () => {
      const mockSupabase = mswSetup(); // MSW mock for auth/realtime
      await userEvent.click(screen.getByText('Invite User B'));
      expect(mockSupabase.from('resource_memberships').insert).toHaveBeenCalled();
      expect(mockSupabase.functions.invoke).toHaveBeenCalledWith('send-invite-email'); // From notifications
      // Mock presence sync, assert UI avatars update
      fireEvent(new CustomEvent('presence-sync', { detail: { users: [{ id: 'B', online: true }] } }));
      expect(screen.getByText('User B Online')).toBeInTheDocument();
    });
    ```

### 2.3. End-to-End (E2E) Tests

*   **Scope:** Full user flows in real environment.
*   **Tool:** Detox for React Native/Expo, orchestrating multiple devices/simulators.
*   **Focus Areas (Critical Flows):**
  *   **Invitation Flow:** User A invites B (auth), B accepts, both edit list (realtime), B gets push (notifications).
  *   **Live Editing Flow:** A/B concurrent adds/checkoffs on shopping_list_items, verify sync via channels.
  *   **Offline-to-Online Sync:** A offline adds items (queue), online syncs, B sees updates; test conflict if B edits meanwhile (LWW).
  *   **Conflict Resolution:** A/B edit same item, assert toast on overwrite, UI reflects last write.
  *   **Notifications:** A adds item, B receives push in background, taps to open list.

### 2.4. E2E Test Example with Detox

Detox is uniquely suited for our needs because it can orchestrate multiple simulators. Here is a conceptual test case for a live editing flow:

```javascript
// e2e/shopping-list.test.js
describe('Shared Shopping List', () => {
  let listId;

  beforeAll(async () => {
    // Start two simulators: 'userA' and 'userB'
    await detox.init(); 
    await device.launchApp({ newInstance: true });
    // Assume login and list creation happens here, storing the listId
    listId = await createSharedShoppingList('userA');
    await launchAppForUser('userB', listId); 
  });

  it('should sync new items between users in real-time', async () => {
    // On User A's device, add a new item
    await device.select('userA');
    await element(by.id('add-item-input')).typeText('Apples');
    await element(by.id('add-item-button')).tap();
    
    // On User B's device, wait for the item to appear
    await device.select('userB');
    await waitFor(element(by.text('Apples'))).toBeVisible().withTimeout(5000);
    
    // On User B's device, check off the item
    await element(by.id('item-checkbox-Apples')).tap();

    // On User A's device, assert that the item is now checked
    await device.select('userA');
    await expect(element(by.id('item-checkbox-Apples'))).toHaveValue('checked');
  });

});
```
*(This is a conceptual example. The actual Detox API might differ slightly.)*

Additional Example - Invite & Conflict:
```javascript
it('invites user and handles conflict', async () => {
  await device.select('userA');
  await element(by.id('invite-button')).tap();
  await element(by.id('email-input')).typeText('userb@example.com');
  await element(by.id('send-invite')).tap();

  // Switch to B, accept invite
  await device.select('userB');
  await element(by.id('accept-invite')).tap(); // Deep link from notification mock
  await expect(element(by.text('Shared List'))).toBeVisible();

  // A adds item
  await device.select('userA');
  await addItem('Milk');

  // B edits same (conflict simulation)
  await device.select('userB');
  await element(by.id('milk-quantity')).typeText('2');
  await element(by.id('save')).tap();

  // A tries to edit to 3, but B's wins (mock timestamp)
  await device.select('userA');
  await element(by.id('milk-quantity')).typeText('3');
  await element(by.id('save')).tap();
  await expect(element(by.text('2'))).toBeVisible(); // LWW
  await expect(element(by.text('Update from User B'))).toBeVisible(); // Toast
});
```

## 3. Setup and Tooling

*   **Detox Configuration:** Two devices (iOS simulator 'userA', Android 'userB'); parallel execution for speed.
*   **Mock Server:** MSW for CI (mock Supabase realtime/auth/notifications); seed test DB with Supabase CLI for local.
*   **Test Data:** Pre-seed users/lists/memberships; reset between tests via supabase db reset.
*   **Coverage:** Use Vitest --coverage; target 80%+ on src/realtime, auth, offline modules; <1s total run with mocks.

## 4. Manual Testing

In addition to automated tests, structured manual testing will be essential.

*   **Test Plan:** Document in plans/testing-plan.md with scenarios: invites (email/social), live edits (2+ browsers/devices), conflicts (simultaneous), offline (network toggle), notifications (physical devices for push).
*   **Device Matrix:** iOS (iPhone 14 simulator/physical), Android (Pixel emulator), network: WiFi/5G/airplane/offline; browsers for PWA fallback.
*   **Exploratory Testing:** Bug bashes with team; log issues in GitHub issues linked to decisions.

## 5. Next Steps

*   Set up Detox/MSW in project; write first unit test for sync handler.
*   Develop E2E suite for top 3 flows (invite, live edit, conflict).
*   Create manual plan doc and run initial session.
*   Integrate testing strategy outline into design-system.md (Phase 4).