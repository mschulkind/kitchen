# Decision Log: Realtime Collaboration with Supabase

## Table of Contents

- [1. Goal](#1-goal)
- [2. Technical Approach](#2-technical-approach)
  - [Key Implementation Points](#key-implementation-points)
- [3. Channels and Subscriptions](#3-channels-and-subscriptions)
- [4. Optimistic Updates for Mobile Offline Handling](#4-optimistic-updates-for-mobile-offline-handling)
- [5. Next Steps](#5-next-steps)

This document details the plan for integrating Supabase Realtime to enable multi-user collaboration features.

- **Phase:** 1.5
- **Status:** Finalized (2025-09-18: Decision approved. Implementation plan confirmed.)
- **Owner:** A.I. Assistant

## Final Decision Summary

The decision to integrate Supabase Realtime is finalized with the following core components:

- **Channels**: Dedicated channels will be used for `shopping_lists`, `meal_plans`, and `inventory_items`.
- **Optimistic Updates**: The frontend will use React Query (TanStack Query) for optimistic UI updates.
- **Offline Handling**: User actions taken while offline will be queued using IndexedDB and synced upon reconnection.
- **Mobile Integration**: The implementation will ensure full Expo compatibility, including background sync tasks and robust error handling.

## 1. Goal

Enable seamless, real-time synchronization of data across multiple devices and users. This is critical for shared resources like shopping lists, meal plans, and pantry inventory, directly supporting the "multiuser" feature extension.

## 2. Technical Approach

We will use the Supabase client-side SDK (`supabase-js`) to subscribe to database changes. This allows the application to listen for inserts, updates, and deletes on specific tables and reflect those changes in the UI instantly.

### Key Implementation Points

- **Client-Side Subscriptions:** Use `supabase.channel()` to create channels for key shared resources.
- **Postgres Changes:** Listen to `postgres_changes` events to receive database updates.
- **Optimistic UI:** To ensure a fluid user experience, especially on mobile, we will implement optimistic updates. The local UI state will update immediately upon a user's action, before the database confirms the change.
- **Offline First:** Changes made while offline will be queued and synced upon reconnection.

### API Sketch

```javascript
// Example for a shared shopping list
const channel = supabase.channel('shared-list-channel');

channel.on(
  'postgres_changes',
  { 
    event: '*', 
    schema: 'public', 
    table: 'shopping_lists',
    filter: `list_id=eq.${sharedListId}` 
  },
  (payload) => {
    console.log('Change received!', payload);
    // Logic to update UI based on the payload
    // e.g., addNewItem(payload.new) or updateItem(payload.new)
  }
).subscribe();

```text

## 3. Channels and Subscriptions

To structure the real-time communication, we will define channels based on shared resources. A user will subscribe to a channel corresponding to a specific shared object (e.g., a single shopping list or meal plan).

| Channel Type        | Naming Convention                                  | Watched Table(s)                  | Purpose                                                                                |
| ------------------- | -------------------------------------------------- | --------------------------------- | -------------------------------------------------------------------------------------- |
| **Shared List**     | `shared-list:{list_id}`                            | `shopping_list_items`             | Broadcasts changes to items within a specific shopping list (adds, updates, deletes).  |
| **Meal Plan**       | `meal-plan:{plan_id}`                              | `meal_plan_recipes`, `meal_plans` | Syncs recipes added to or removed from a collaborative meal plan, including plan metadata updates. |
| **Inventory**       | `inventory:{pantry_id}`                            | `inventory_items`                 | Tracks changes to shared pantry stock (e.g., quantity updates after shopping).         |
| **Presence**        | `presence-list:{list_id}` or `presence-plan:{plan_id}` or `presence-inventory:{pantry_id}` | (N/A - Presence state)            | Tracks which users are currently viewing a specific list, plan, or inventory.          |

### Subscription Logic

- When a user views a shared shopping list, the app will subscribe to `shared-list:{list_id}` and `presence-list:{list_id}`.
- The `filter` parameter in the subscription will be used to ensure clients only receive events for the specific resource they are viewing.
- For meal plans, subscribe to both `meal_plan_recipes` and `meal_plans` to capture recipe assignments and overall plan changes.
- Inventory subscriptions should include filters for shared pantries only, excluding personal ones unless opted into collaboration.

## 4. Optimistic Updates for Mobile Offline Handling

To provide a responsive mobile experience in the PWA, we will implement optimistic updates combined with offline queuing. This ensures users can interact seamlessly even with poor connectivity, aligning with the mobile-first brief.

### Preferences and Strategy

- **Library Choice:** Use React Query (TanStack Query) for data fetching, caching, and mutations. It supports optimistic updates out-of-the-box and integrates well with Supabase via custom hooks.
- **Offline Storage:** Leverage IndexedDB (via idb-keyval or Dexie.js for simplicity) for queuing mutations on mobile. Fallback to AsyncStorage in Expo for smaller payloads.
- **Sync Mechanism:** On reconnection, replay queued mutations with retries (exponential backoff). Use Supabase's `realtime` to confirm sync and resolve conflicts via last-write-wins.
- **Mobile Considerations:**
  - Minimize battery drain by disabling polling during active subscriptions; use WebSocket for realtime.
  - Handle Expo specifics: Ensure subscriptions persist across app suspends using background tasks if needed.
  - UX: Show loading spinners for optimistic actions, success toasts on sync, and error banners for unresolvable conflicts.
  - Accessibility: Announce queued changes via ARIA live regions for screen readers.

### Pseudocode Example

```javascript
// Hook for optimistic mutation with queue
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { supabase } from './supabaseClient';
import { queueOfflineMutation } from './offlineQueue'; // Custom queue using IndexedDB

const useOptimisticUpdateItem = (resourceType) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (updateData) => {
      const { data, error } = await supabase
        .from(resourceType === 'shopping_lists' ? 'shopping_list_items' : 'inventory_items')
        .update(updateData)
        .eq('id', updateData.id)
        .select();

      if (error && !navigator.onLine) {
        // Queue for offline
        queueOfflineMutation({ type: 'update', resource: resourceType, data: updateData });
        throw error; // But optimistically update UI anyway
      }
      return data;
    },
    onMutate: async (newData) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: [resourceType, newData.id] });
      const previousData = queryClient.getQueryData([resourceType, newData.id]);
      queryClient.setQueryData([resourceType, newData.id], (old) => ({ ...old, ...newData }));
      
      return { previousData };
    },
    onError: (err, newData, context) => {
      // Rollback on error (if not offline)
      if (navigator.onLine) {
        queryClient.setQueryData([resourceType, newData.id], context.previousData);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: [resourceType] });
    },
  });
};

// Offline queue sync on reconnect
window.addEventListener('online', async () => {
  const queued = await getQueuedMutations(); // From IndexedDB
  for (const mutation of queued) {
    try {
      await supabase.from(mutation.resource).update(mutation.data);
      removeFromQueue(mutation.id);
    } catch (e) {
      // Retry logic or mark as failed
    }
  }
});
```

This approach ensures low-latency interactions for busy users managing shared meal and shopping data on mobile devices.

## 5. Conflict Resolution and UI Updates

- **Strategy**: As defined in [`conflict-resolution-and-offline.md`](conflict-resolution-and-offline.md), we will use a **Last Write Wins (LWW)** approach.
- **UI Feedback**:
  - **Optimistic Updates**: Local changes are reflected instantly in the UI.
  - **Incoming Changes**: When a change is received from the channel, the UI will smoothly update to reflect the new state (e.g., an item appearing, a quantity changing).
  - **User Avatars**: Presence information will be used to display the avatars of other users currently viewing the same resource, providing a clear sense of collaboration.

## 7. Expo Compatibility and Error Handling

To ensure seamless realtime in the React Native/Expo frontend:

### Expo Integration

- **SDK Usage**: Supabase JS SDK works natively in Expo; install via `npx expo install @supabase/supabase-js`.
- **Background Sync**: Use Expo's TaskManager for background fetches on app resume/reconnect (e.g., register task to replay queued mutations from IndexedDB). Limit to 30s execution for iOS/Android battery efficiency.
- **Permissions**: Request notification perms for sync toasts; handle Expo's dev client for local testing.
- **Data Model Ties**: Subscriptions filter on models like `shopping_list_items` (for categorical lists), `inventory_items` (location-aware), and `meal_plan_recipes` (day-based); ensure row-level security (RLS) policies allow subscribed users only.

### Error Handling

- **Subscription Errors**: Wrap `channel.subscribe()` in try-catch; on failure (e.g., network error), implement exponential backoff reconnect (e.g., retry after 1s, 2s, 4s up to 5 attempts).
- **Payload Validation**: On `postgres_changes` receipt, validate payload against expected schema (e.g., check `new` has required fields like id, quantity for inventory_items); discard invalid to prevent UI corruption.
- **Offline Reconnect**: Listen to `navigator.connection` changes or Supabase's `supabase.realtime.connect()`; on online, resubscribe channels and sync queues, showing progress toast (e.g., "Reconnected: 3 changes synced").
- **Mobile UX**: For errors, display non-intrusive banners (e.g., "Sync paused—check connection") with retry button; log to console for debugging.

Pseudocode for Reconnect:

```text
function setupReconnect() {
  let retryCount = 0;
  const maxRetries = 5;
  const channel = supabase.channel('shared-list');

  channel.on('postgres_changes', { /* ... */ }, handlePayload);

  const subscribeWithRetry = () => {
    channel.subscribe((status) => {
      if (status === 'SUBSCRIBED') {
        retryCount = 0; // Reset on success
      } else if (status === 'CLOSED' || status === 'CHANNEL_ERROR') {
        if (retryCount < maxRetries) {
          setTimeout(() => {
            retryCount++;
            subscribeWithRetry();
          }, Math.pow(2, retryCount) * 1000);
        } else {
          showErrorToast('Connection failed—retrying in background');
        }
      }
    });
  };

  subscribeWithRetry();

  // Expo background task for sync
  if (Platform.OS !== 'web') {
    TaskManager.defineTask('backgroundSync', async () => {
      await syncQueuedMutations();
    });
  }
}
```

This ensures robust, mobile-optimized realtime integration aligned with Supabase's RLS and our data models.

## 6. Next Steps

- Implement auth and presence tracking (see [auth-and-presence.md](auth-and-presence.md)).
- Detail conflict resolution (covered in [conflict-resolution-and-offline.md](conflict-resolution-and-offline.md)).
- Outline testing plan (covered in [multiuser-testing.md](multiuser-testing.md)).
- Integrate into design-system.md Collaboration Architecture section with channel summaries.
