# Decision Log: Conflict Resolution & Offline Handling

This document specifies the strategy for managing data conflicts in a multi-user environment and ensuring a seamless experience for users who may have intermittent connectivity.

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

## 4. Next Steps

*   Choose a library for managing the offline queue (e.g., `redux-persist` with a custom storage engine, or a dedicated library like WatermelonDB if complexity warrants it).
*   Define the exact schema for the offline action queue.
*   Write unit and integration tests for the sync manager.