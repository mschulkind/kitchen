# Decision Log: Conflict Resolution & Offline Handling

## Table of Contents
- [1. Goal](#1-goal)
- [2. Conflict Resolution Strategy](#2-conflict-resolution-strategy)
  - [How It Works](#how-it-works)
  - [LWW Pseudocode](#lww-pseudocode)
  - [Future Enhancements (Post-MVP)](#future-enhancements-post-mvp)
- [3. Offline Handling Strategy](#3-offline-handling-strategy)
  - [Implementation Details](#implementation-details)
  - [Example Flow](#example-flow)
- [4. Offline Queue Implementation](#4-offline-queue-implementation)
- [5. User Feedback & UI](#5-user-feedback--ui)
- [6. TDD: Testing Offline & Conflicts](#6-tdd-testing-offline--conflicts)
- [7. Next Steps](#7-next-steps)

*   **Phase:** 1.5
*   **Status:** Completed (2025-09-18: Added LWW details, rollback, Expo queuing, TDD sketches; tied to realtime and RLS)
*   **Owner:** A.I. Assistant

## 1. Goal

To ensure data integrity and provide a predictable, user-friendly experience when multiple users edit the same data simultaneously or when a user makes changes while offline.

## 2. Conflict Resolution Strategy

For initial implementation, we will adopt a **"Last Write Wins" (LWW)** strategy. This is the simplest approach to implement and is often sufficient for collaborative list management where the risk of destructive simultaneous edits is low. Integrates with realtime-integration.md channels for instant propagation and auth-and-presence.md RLS to ensure only authorized users trigger conflicts.

### How It Works:
*   When two users edit the same item, the change that is saved to the database last will overwrite any previous changes.
*   Timestamps will be crucial. Every record will have an `updated_at` field that is set by the database on every write (use Supabase's `now()` trigger).
*   On sync/realtime update, compare local `updated_at` with server; if server is newer, rollback local optimistic change and alert user.

### LWW Pseudocode:
```javascript
// On realtime change receipt (from postgres_changes)
function handleIncomingChange(payload, localState) {
  const serverUpdatedAt = payload.new.updated_at;
  const localUpdatedAt = localState[payload.new.id]?.updated_at;

  if (serverUpdatedAt > localUpdatedAt) {
    // Server wins: Rollback local to server state
    updateLocalState(payload.new);
    showConflictToast(`Update from ${payload.user} applied (your change overwritten)`);
  } else if (localUpdatedAt > serverUpdatedAt) {
    // Local wins: Resend queued mutation
    queueMutation({ type: 'UPDATE', data: localState[payload.new.id], force: true });
  }
}

// During sync from queue
async function syncMutation(mutation) {
  const { data: serverData, error } = await supabase.from(table).select('updated_at').eq('id', mutation.id).single();
  
  if (error || !serverData) {
    // Insert new
    await supabase.from(table).insert({ ...mutation.payload, updated_at: new Date().toISOString() });
  } else if (mutation.updated_at > serverData.updated_at) {
    // Local newer: Update
    await supabase.from(table).update({ ...mutation.payload, updated_at: new Date().toISOString() }).eq('id', mutation.id);
  } else {
    // Server newer: Skip/rollback
    removeFromQueue(mutation.id);
    updateLocalState(serverData); // Fetch latest
    showConflictToast('Your change was overwritten by another user');
  }
}
```

### Future Enhancements (Post-MVP):
*   **CRDTs (Conflict-free Replicated Data Types):** For more complex scenarios, we may explore CRDTs, which are data structures designed to resolve conflicts automatically.
*   **Three-Way Merge:** For critical data, we could implement a three-way merge UI, showing the user the conflicting versions and allowing them to resolve the conflict manually.

## 3. Offline Handling Strategy

The application will be built with an **offline-first** mindset, leveraging an optimistic UI and a local data cache. Ties to realtime for post-sync propagation via channels.

### Implementation Details:
*   **Optimistic UI:** When a user makes a change, the UI will update immediately, without waiting for a server response. The change is assumed to be successful.
*   **Local Queue/Cache:** All user actions (creates, updates, deletes) will be stored in a local queue (e.g., using IndexedDB or AsyncStorage).
*   **Sync on Reconnect:** When the application regains connectivity, the queue of changes will be processed and sent to the server.
*   **User Feedback:** The UI will provide clear feedback on the sync status. For example, a small toast notification like "Changes synced" or an icon indicating "Offline mode".
*   **Mobile Focus (Expo):** Use AsyncStorage for lightweight queuing (key: 'offlineQueue', value: JSON array); persist across app closes. On app start/resume, trigger sync if queue.length > 0.

### Example Flow:
1.  User is offline and checks an item off a shopping list.
2.  The UI immediately shows the item as checked.
3.  The "check item" action is added to a local queue: `{ action: 'update', table: 'shopping_list_items', id: 123, payload: { checked: true, updated_at: new Date().toISOString() } }` (stored in AsyncStorage).
4.  User comes back online.
5.  The app detects connectivity and processes the queue.
6.  The "update" action is sent to the Supabase API.
7.  Once the API confirms the write, the item is removed from the queue.
8.  A toast notification "Changes synced" is briefly displayed.

## 4. Offline Queue Implementation

- **Library Choice**: We will use **Zustand** with the `persist` middleware for state management and offline caching. Zustand is lightweight, simple, and already planned for our stack. The `persist` middleware can be configured with `AsyncStorage` (for React Native) to automatically save and rehydrate state, including our offline queue.

- **Queue Schema**: The offline queue will be a simple array within our Zustand store. Each item in the array will represent a pending mutation.

```typescript
// Example state slice in Zustand store
{
  offlineQueue: [
    {
      type: 'UPDATE_ITEM_QUANTITY',
      payload: { listId: 'abc-123', itemId: 'xyz-789', newQuantity: 3, updated_at: '2025-09-18T03:00:00Z' }
    },
    {
      type: 'ADD_ITEM',
      payload: { listId: 'abc-123', name: 'Milk', quantity: 1, updated_at: '2025-09-18T03:01:00Z' }
    }
  ]
}
```

- **Sync Manager**: A dedicated "sync manager" will be responsible for:
  1.  Listening for changes in network status (online/offline) via `NetInfo` in Expo.
  2.  When the app comes online, it iterates through the `offlineQueue`.
  3.  For each action, it calls the corresponding Supabase API function with LWW check.
  4.  Upon successful API confirmation, the action is removed from the queue.
  5.  If an API call fails (e.g., conflict), rollback local state, retain in queue for retry, and notify UI.

## 5. User Feedback & UI

Clear communication about sync status is essential for user trust.

- **Global Indicator**: A subtle, persistent indicator (e.g., a small cloud icon in the header) will show the current status:
  - **Green Cloud**: Online and all changes are synced.
  - **Yellow Cloud with Spinner**: Online and currently syncing.
  - **Grey Cloud with Slash**: Offline.
- **Toast Notifications**: Non-intrusive toast messages will provide contextual updates (using Expo Toast for mobile):
  - "You are currently offline. Changes will be synced later." (When going offline)
  - "Syncing 3 changes..." (When coming online with a pending queue)
  - "All changes synced!" (When the queue is successfully cleared)
  - "Could not sync 'Add Milk'. Another user updated it—view changes?" (On conflict, with tap to resolve)
- **UI State**: While offline, UI elements should remain fully interactive. Optimistic updates ensure the app feels fast and responsive, regardless of network connectivity. For conflicts, modal with big buttons: "Keep My Version" (resend) / "Accept Theirs" (rollback).

## 6. TDD: Testing Offline & Conflicts
Align with rules.md TDD practices; fast tests (<1s) using mocks.

- **Unit Tests (e.g., Vitest for frontend)**: Test sync manager isolation.
  ```javascript
  test('syncMutation resolves LWW with local newer', async () => {
    const mockSupabase = { from: () => ({ select: () => ({ single: () => Promise.resolve({ updated_at: '2025-09-18T02:00:00Z' }) }) }) };
    const mutation = { updated_at: '2025-09-18T03:00:00Z', payload: { quantity: 2 } };
    await syncMutation(mutation, mockSupabase);
    expect(mockSupabase.from().update).toHaveBeenCalledWith(expect.objectContaining({ quantity: 2 }));
  });

  test('queue adds mutation on offline', () => {
    const store = createStore();
    addToQueue({ type: 'ADD_ITEM', payload: { name: 'Milk' } });
    expect(store.getState().offlineQueue.length).toBe(1);
  });
  ```

- **Integration Tests**: Mock WebSocket events for multiuser; use Supabase test DB.
  ```javascript
  test('multiuser conflict: remote update overwrites local', async () => {
    // Setup: Local optimistic add, then simulate remote update via mock channel
    const mockPayload = { new: { id: 123, checked: true, updated_at: '2025-09-18T03:05:00Z' } };
    handleIncomingChange(mockPayload, { 123: { updated_at: '2025-09-18T03:04:00Z' } });
    expect(localState[123].checked).toBe(true); // Rolled back
    expect(toastCalled).toBe(true);
  });

  // E2E-like: Use Detox for mobile offline simulation (toggle network, assert queue/toasts)
  ```

Aim 80% coverage on sync/conflict paths; mock Supabase for speed.

## 7. Next Steps
*   Implement Zustand persist with AsyncStorage for Expo.
*   Develop sync manager with NetInfo listener.
*   Create UI components for indicators/toasts (mobile-optimized).
*   Write and run TDD tests for queue/sync/conflicts.
*   Integrate with design-system.md offline section.