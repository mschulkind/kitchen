# Decision Log: Conflict Resolution & Offline Handling

## Table of Contents
- [1. Goal](#1-goal)
- [2. Conflict Resolution Strategy](#2-conflict-resolution-strategy)
  - [How It Works](#how-it-works)
  - [Future Enhancements (Post-MVP)](#future-enhancements-post-mvp)
- [3. Offline Handling Strategy](#3-offline-handling-strategy)
  - [Implementation Details](#implementation-details)
  - [Example Flow](#example-flow)
- [4. Offline Queue Implementation](#4-offline-queue-implementation)
- [5. User Feedback & UI](#5-user-feedback--ui)
- [6. Next Steps](#6-next-steps)

*   **Phase:** 1.5
*   **Status:** Scoping
*   **Owner:** A.I. Assistant

## 1. Goal

To ensure data integrity and provide a predictable, user-friendly experience when multiple users edit the same data simultaneously or when a user makes changes while offline.

## 2. Conflict Resolution Strategy

For initial implementation, we will adopt a **"Last Write Wins" (LWW)** strategy. This is the simplest approach to implement and is often sufficient for collaborative list management where the risk of destructive simultaneous edits is low.

### How It Works:

*   When two users edit the same item, the change that is saved to the database last will overwrite any previous changes.
*   Timestamps will be crucial. Every record will have an `updated_at` field that is set by the database on every write.

### Future Enhancements (Post-MVP):

*   **CRDTs (Conflict-free Replicated Data Types):** For more complex scenarios, we may explore CRDTs, which are data structures designed to resolve conflicts automatically.
*   **Three-Way Merge:** For critical data, we could implement a three-way merge UI, showing the user the conflicting versions and allowing them to resolve the conflict manually.

## 3. Offline Handling Strategy

The application will be built with an **offline-first** mindset, leveraging an optimistic UI and a local data cache.

### Implementation Details:

*   **Optimistic UI:** When a user makes a change, the UI will update immediately, without waiting for a server response. The change is assumed to be successful.
*   **Local Queue/Cache:** All user actions (creates, updates, deletes) will be stored in a local queue (e.g., using IndexedDB or AsyncStorage).
*   **Sync on Reconnect:** When the application regains connectivity, the queue of changes will be processed and sent to the server.
*   **User Feedback:** The UI will provide clear feedback on the sync status. For example, a small toast notification like "Changes synced" or an icon indicating "Offline mode".

### Example Flow:

1.  User is offline and checks an item off a shopping list.
2.  The UI immediately shows the item as checked.
3.  The "check item" action is added to a local queue: `{ action: 'update', table: 'shopping_list_items', id: 123, payload: { checked: true } }`.
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
      payload: { listId: 'abc-123', itemId: 'xyz-789', newQuantity: 3 }
    },
    {
      type: 'ADD_ITEM',
      payload: { listId: 'abc-123', name: 'Milk', quantity: 1 }
    }
  ]
}
```

- **Sync Manager**: A dedicated "sync manager" will be responsible for:
    1.  Listening for changes in network status (online/offline).
    2.  When the app comes online, it iterates through the `offlineQueue`.
    3.  For each action, it calls the corresponding Supabase API function.
    4.  Upon successful API confirmation, the action is removed from the queue.
    5.  If an API call fails, the action remains in the queue for a later retry, and the UI is notified of the conflict/error.

## 5. User Feedback & UI

Clear communication about sync status is essential for user trust.

- **Global Indicator**: A subtle, persistent indicator (e.g., a small cloud icon in the header) will show the current status:
    - **Green Cloud**: Online and all changes are synced.
    - **Yellow Cloud with Spinner**: Online and currently syncing.
    - **Grey Cloud with Slash**: Offline.
- **Toast Notifications**: Non-intrusive toast messages will provide contextual updates:
    - "You are currently offline. Changes will be synced later." (When going offline)
    - "Syncing 3 changes..." (When coming online with a pending queue)
    - "All changes synced!" (When the queue is successfully cleared)
    - "Could not sync 'Add Milk'. Please check your connection." (On a persistent error)
- **UI State**: While offline, UI elements should remain fully interactive. Optimistic updates ensure the app feels fast and responsive, regardless of network connectivity.

## 6. Next Steps

*   Implement the Zustand `persist` middleware with `AsyncStorage`.
*   Develop the sync manager logic to process the offline queue.
*   Create the global UI components for displaying sync status and toasts.
*   Write unit tests for the sync manager, covering various success and failure scenarios.