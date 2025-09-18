# Decision: Conflict Resolution & Offline Handling

## Table of Contents
- [Proposal](#proposal)
- [Decision](#decision)
- [Rationale](#rationale)
- [Implementation Details](#implementation-details)
- [Testing Strategy](#testing-strategy)

## Proposal
Based on the requirements outlined in [`plans/development-todo.md`](../../development-todo.md), the following strategy is proposed for handling data conflicts and offline functionality. This approach prioritizes a seamless user experience, especially on mobile devices where connectivity can be intermittent.

### 1. Conflict Resolution Strategy: Last-Write-Wins (LWW)
For the sake of simplicity and rapid development, a **Last-Write-Wins (LWW)** strategy will be implemented for all user-modifiable data (e.g., shopping list items, pantry inventory).

- **Mechanism**: The last update received by the Supabase server for a specific record will overwrite any preceding updates. This is the default behavior and requires no complex server-side logic.
- **Rationale**: Given the nature of the app (managing personal or shared household lists), the risk of destructive concurrent edits is low. The most recent change is likely the most relevant.
- **User Experience**: To minimize confusion, the UI will update in realtime. If a user's action is overwritten by another collaborator, their screen will simply reflect the new state. For critical actions, we will explore adding subtle, non-blocking notifications in a future iteration.

### 2. Offline Handling: Optimistic UI with a Sync Queue
To ensure the app remains responsive and functional offline, we will adopt an optimistic UI pattern backed by a local sync queue.

- **Optimistic UI**: When a user performs an action (e.g., checking off an item), the UI will update instantly, without waiting for server confirmation. This provides immediate feedback and makes the app feel fast and responsive.
- **Sync Queue Mechanism**:
    - All data-mutating actions (creates, updates, deletes) will be added to a persistent queue stored locally in the browser/device using **IndexedDB**. This ensures that pending changes are not lost if the app is closed.
    - A background process will be responsible for processing this queue, sending the requests to the Supabase backend once a network connection is available.
    - Upon successful synchronization, the item is removed from the queue.
- **Mobile Focus**: This approach is ideal for mobile PWA usage. Users can continue to manage their lists, and all changes will sync automatically in the background when they come back online. User-friendly toasts will provide feedback on sync status (e.g., "Your changes have been saved and will sync when you're back online.").

### 3. Testing Strategy: Test-Driven Development (TDD)
A rigorous TDD approach will be taken to ensure the reliability of this critical functionality.

- **Unit Tests**: We will write unit tests for the sync handlers. This will involve mocking WebSocket events and IndexedDB operations to verify that the application state is updated correctly under various conditions (e.g., successful sync, failed sync, offline queuing).
- **Integration Tests**: Multi-user scenarios will be tested to validate the LWW strategy. This will involve simulating two clients editing the same data concurrently and asserting that the final state is correct.
- **End-to-End (E2E) Tests**: For mobile flows, tools like Detox or Playwright may be used to simulate offline/online transitions and verify the full sync process from the user's perspective.

This proposal provides a robust yet straightforward foundation for building a reliable, multi-user, offline-first application.

## Decision
*This section will be filled in once the proposal is approved.*

## Rationale
*This section will detail why the chosen approach is the best fit for the project.*

## Implementation Details
*This section will provide technical details for implementation.*

## Testing Strategy
*This section will outline how the conflict resolution and offline handling will be tested.*