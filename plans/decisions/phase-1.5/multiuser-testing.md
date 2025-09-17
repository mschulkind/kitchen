# Decision Log: Multiuser Sync Testing Strategy

This document outlines the testing strategy to ensure the reliability and correctness of real-time multiuser features.

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

## 3. Manual Testing

In addition to automated tests, structured manual testing will be essential.

*   **Test Plan:** A manual test plan will be created with specific scenarios.
*   **Device Matrix:** Testing will be performed on a matrix of different devices (iOS/Android) and network conditions (WiFi, 4G, throttled/offline connections).
*   **Exploratory Testing:** Testers will be encouraged to perform exploratory testing to find edge cases not covered by the scripted tests.

## 4. Next Steps

*   Set up Detox in the Expo project.
*   Write the first E2E test for the invitation flow.
*   Develop a suite of unit tests for the core sync logic.