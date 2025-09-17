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
*   **Status:** Scoping
*   **Owner:** A.I. Assistant

## 1. Goal

To rigorously test all aspects of the real-time collaboration and synchronization features, including invites, live edits, conflict resolution, and offline behavior, ensuring a stable and intuitive user experience.

## 2. Testing Pyramid

Our testing strategy will follow the principles of the testing pyramid, with a broad base of unit tests, a smaller number of integration tests, and a select few end-to-end (E2E) tests for critical user flows.

### 2.1. Unit Tests

*   **Scope:** Individual functions and components in isolation.
*   **Tools:** Vitest or Jest.
*   **Focus Areas:**
    *   **Sync Handlers:** Mock WebSocket events from Supabase and assert that the local state (e.g., Redux store, component state) updates correctly.
    *   **UI Components:** Test that components render correctly based on different states (e.g., online, offline, syncing, conflict).
    *   **Offline Queue:** Test the logic for adding, removing, and processing items from the offline action queue.

### 2.2. Integration Tests

*   **Scope:** Interactions between multiple components or between the client and a mocked backend.
*   **Tools:** React Testing Library, potentially with MSW (Mock Service Worker) to mock Supabase API calls.
*   **Focus Areas:**
    *   **Multi-user Scenarios:** Simulate two or more clients interacting with the same data. For example:
        *   Client A and Client B both load the same shopping list.
        *   Client A adds an item. Assert that Client B's UI updates in real-time.
        *   Client B checks off an item. Assert that Client A's UI updates.
        *   Client A and Client B edit the same item's quantity simultaneously to test the "Last Write Wins" conflict resolution.
    *   **Auth and Presence:** Test that logging in correctly establishes a presence session and that other clients see the user as online.

### 2.3. End-to-End (E2E) Tests

*   **Scope:** Full user flows in a real application environment.
*   **Tool:** **Detox** for React Native/Expo. Detox allows for controlling multiple simulators/devices in a single test script, which is ideal for E2E testing of real-time features.
*   **Focus Areas (Critical Flows):**
    *   **Invitation Flow:** User A invites User B to a shopping list, User B accepts, and both can edit the list.
    *   **Live Editing Flow:** User A and User B concurrently add and check off items from a list, verifying that both UIs stay in sync.
    *   **Offline-to-Online Sync:** One user goes offline, makes several changes, comes back online, and their changes are correctly synced and reflected for the other user.

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

## 3. Setup and Tooling

*   **Detox Configuration**: The `.detoxrc.js` file will be configured with two device profiles (`userA` and `userB`) to allow parallel execution.
*   **Mock Server**: For CI/CD environments, we will use a mocked Supabase backend to ensure tests are deterministic and don't rely on a live network connection. MSW (Mock Service Worker) can be used to intercept and mock `fetch` requests made by the Supabase client.
*   **Test Data**: Before each test run, the database (or mock server) will be seeded with a consistent set of test data to ensure reproducibility.

## 4. Manual Testing

In addition to automated tests, structured manual testing will be essential.

*   **Test Plan:** A manual test plan will be created in a shared document (e.g., Google Sheets) with specific scenarios covering invites, live edits, offline mode, and conflict resolution.
*   **Device Matrix:** Testing will be performed on a matrix of different physical devices (e.g., iPhone 13, Google Pixel 6) and network conditions (WiFi, 5G, throttled 3G, and airplane mode).
*   **Exploratory Testing:** Testers will be encouraged to perform exploratory "bug bashes" to find edge cases not covered by the scripted tests.

## 5. Next Steps

*   Set up Detox in the Expo project with a two-device configuration.
*   Write the first E2E test for the user invitation flow.
*   Develop a suite of unit tests for the core sync logic using Vitest and React Testing Library.
*   Create the initial manual test plan document.