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

### Alternative Strategies Considered

To ensure a well-rounded decision, here are other common conflict resolution strategies and their trade-offs compared to LWW.

| Strategy | Complexity | Pros | Cons | Best For |
| :--- | :--- | :--- | :--- | :--- |
| **Last-Write-Wins (LWW)** | **Low** | Simple to implement, often the default behavior of databases. No complex client-side logic needed. | Can lead to unintentional data loss if users are not aware of each other's changes. | Simple applications where the risk of critical data loss from overwrites is low, like our checklist/inventory app. |
| **Operational Transformation (OT)** | **High** | Preserves user intent by transforming operations so they can be applied in any order. Provides a very granular and intuitive collaboration experience. | Extremely complex to implement correctly. Requires a central server to manage and transform operations, which can be a single point of failure. | Real-time collaborative text editors like Google Docs, where preserving every keystroke is critical. |
| **Conflict-Free Replicated Data Types (CRDTs)** | **Medium-High** | Mathematically proven to converge to the same state without a central server. Excellent for peer-to-peer and offline-first applications. | Can have higher storage/memory overhead. The data types and merge logic can be complex to reason about and debug. Some operations are difficult to model. | Multi-user applications that require strong eventual consistency and offline capabilities, like collaborative drawing tools or certain types of databases. |
| **Three-Way Merge** | **Medium** | A common strategy used in version control (like Git). Compares changes against a common ancestor to merge conflicts. | Requires storing the "ancestor" version of the data. Can require user intervention to resolve complex conflicts, which may not be ideal for our seamless mobile UX. | Systems where users can manually resolve merge conflicts, like code repositories or document versioning systems. |

Given our focus on rapid development for a mobile-first PWA where the most common action is toggling a checkbox or updating a quantity, the simplicity and low implementation overhead of **Last-Write-Wins** remains the most pragmatic choice for our MVP.

### Future Evolution: Phased Migration to CRDTs
While LWW is ideal for the MVP, a more sophisticated approach may be needed as the application's collaborative features mature. A transition to CRDTs is the recommended path for a future version (V2).

**Phase 1: MVP (Current Plan)**
- **Strategy**: Implement **Last-Write-Wins** as described above.
- **Data Model**: Simple state-based model. An update overwrites the entire record (e.g., `UPDATE shopping_list_items SET checked = true WHERE id = ?`).
- **Goal**: Rapid development and delivery of core features.

**Phase 2: V2 Migration to CRDTs**
- **Strategy**: Transition the data synchronization layer to use **Conflict-Free Replicated Data Types**.
- **Data Model**: Shift from a state-based to an operation-based model. Instead of sending the new state, the client sends the action (e.g., `{'op': 'checkItem', 'itemId': 'uuid-123'}`).
- **Client-Side Changes**:
    - Implement a CRDT library (e.g., Y.js, Automerge) to manage the local state and merge operations from the server and other clients.
    - The sync queue would be adapted to store these operations instead of full state updates.
- **Backend Changes**:
    - The backend would need to be adapted to store and relay these operations to all connected clients. Supabase Realtime can still be used as the transport layer.
- **Benefit**: This would provide a truly seamless and robust multi-user experience, eliminating data loss from concurrent edits and providing a solid foundation for more advanced collaborative features.

By adopting this phased approach, we can move quickly now while ensuring the architecture is prepared for future enhancements.

## Decision
*This section will be filled in once the proposal is approved.*

## Rationale
*This section will detail why the chosen approach is the best fit for the project.*

## Implementation Details
*This section will provide technical details for implementation.*

## Testing Strategy
*This section will outline how the conflict resolution and offline handling will be tested.*