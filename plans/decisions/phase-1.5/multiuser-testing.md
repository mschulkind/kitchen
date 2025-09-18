# Decision: Testing Strategy for Multiuser Sync

## Table of Contents
- [Status](#status)
- [Context](#context)
- [Decision](#decision)
- [Next Steps](#next-steps)

## Status
**Finalized**

## Context
As per the requirements in [`plans/development-todo.md`](../../development-todo.md:59), we need a comprehensive testing strategy for the realtime multiuser synchronization features. The development strategy, outlined in [`plans/brief.md`](../../brief.md), prioritizes a multi-platform approach using `react-native-web`. A **desktop web application** (PWA) will be used for initial development and testing, with a native **Android application** as the final mobile target.

This testing plan must therefore account for both environments. Manual testing will be performed primarily on the web application for rapid feedback, while automated E2E tests with Detox will target the Android platform specifically to validate mobile-native functionality.

## Phased Testing Strategy
To align with the project's development roadmap, our testing efforts will be phased as follows. This ensures we apply the right type of testing at the right time.

### Phase 1: PWA / Web App Development
During the initial development phase focused on the web application, testing will prioritize speed and core logic validation.

-   **Focus**: Manual testing and component/integration tests (Vitest/RTL).
-   **Environment**: Desktop web browsers (e.g., Chrome, Firefox).
-   **Manual Testing**: All manual test scenarios (invites, live edits, offline sync) will be executed on the web app. This allows for rapid iteration and debugging using browser developer tools.
-   **Automated Testing**: We will write unit and integration tests for the shared React components and business logic. E2E tests with Detox are **deferred** at this stage, as they are specific to the native Android environment.

### Phase 2: Native Android App Development
Once the core features are stable on the web, development will shift to the native Android wrapper. At this point, testing expands to include mobile-specific validation.

-   **Focus**: End-to-end (E2E) testing and manual regression testing on a native device/emulator.
-   **Environment**: Android Emulator and physical Android devices.
-   **Manual Testing**: A full regression run of the manual test scenarios will be performed on the Android app to catch any platform-specific bugs.
-   **Automated E2E Testing**: The **Detox test suite will be implemented** during this phase. The test cases outlined below will be automated to run against the Android app, ensuring that critical multiuser and offline flows work reliably in a native context.

This phased approach allows us to validate core functionality quickly on the web and then build a robust, mobile-specific E2E test suite for long-term stability on Android.

## Decision
We will adopt a two-pronged, phased testing strategy:

### 1. Manual Testing Scenarios
A dedicated QA or development team member will execute the following manual tests using at least two separate browser windows or devices to simulate a collaborative environment. These tests will be performed on the **web application** running locally.

- **Invitation Flow:**
  - User A invites User B to a shared shopping list.
  - Verify User B receives the invitation (e.g., in-app notification).
  - Verify User B can accept and access the shared list.
  - User A removes User B's access.
  - Verify User B can no longer access the list.

- **Live Edits &amp; Synchronization:**
  - User A and User B are viewing the same shopping list in different browser tabs.
  - User A adds an item. Verify it appears instantly for User B.
  - User B checks off an item. Verify it updates instantly for User A.
  - User A edits the quantity of an item. Verify the change for User B.
  - Both users add items simultaneously. Verify both items appear for both users.

- **Conflict Handling (based on Last-Write-Wins):**
  - User A and User B edit the name of the *same* item at nearly the same time in their respective browser tabs.
  - Verify that the last change saved is the one that persists for both users.
  - Verify there is a clear but unobtrusive UI indicator of the change (e.g., a subtle highlight or toast message).

- **Presence Indicators:**
  - User A and User B are on the same list.
  - Verify that both users can see that the other is "online" or "active" on that list.
  - User B navigates away or closes the app.
  - Verify User A sees User B's presence indicator disappear.

- **Offline Syncing:**
  - User A opens the web app and loads a shared list.
  - User A disconnects from the network (e.g., using browser developer tools).
  - User A checks off three items. Verify the UI updates optimistically.
  - User A reconnects to the network.
  - Verify the changes are synced and are visible to User B on their device.
  - Verify a toast message confirms the successful sync.

### 2. Automated E2E Testing with Detox
For long-term stability on the **native mobile platform**, we will implement an e2e test suite using Detox. These tests will be run against the compiled **Android application**.

- **Setup:**
  - Configure Detox in the project for the **Android emulator**. (iOS is out of scope for now).
  - Create helper functions to manage test users and shared list states (e.g., `createSharedList(userA, userB)`).
  - Tests will run against the local Supabase stack managed by the `Procfile.dev` setup.

- **Initial Test Cases:**
  - **Test Case 1: Live Item Addition**
    - `userA` launches the app and creates a shared list.
    - `userB` launches the app and accepts an invite to the list.
    - `userA` adds "Milk" to the list.
    - Assert that `userB`'s app shows "Milk" within a reasonable time (~2 seconds).
  - **Test Case 2: Live Item Check-off**
    - Building on the previous state...
    - `userB` taps to check off "Milk".
    - Assert that `userA`'s app shows "Milk" as checked off.
  - **Test Case 3: Offline Sync**
    - `userA` launches the app and loads a list.
    - `userA`'s device simulates going offline.
    - `userA` adds "Bread" to the list.
    - `userA`'s device simulates coming back online.
    - Assert that `userB`'s app shows "Bread" on their list after the sync.

## Next Steps
- Await approval of this proposed strategy.
- Upon approval, change the status to **Finalized**.
- Begin implementation of the Detox test suite setup.
- Execute a full manual test run.
