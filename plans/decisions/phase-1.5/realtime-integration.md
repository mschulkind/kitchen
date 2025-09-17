# Decision Log: Realtime Collaboration with Supabase

This document details the plan for integrating Supabase Realtime to enable multi-user collaboration features.

*   **Phase:** 1.5
*   **Status:** Scoping
*   **Owner:** A.I. Assistant

## 1. Goal

Enable seamless, real-time synchronization of data across multiple devices and users. This is critical for shared resources like shopping lists, meal plans, and pantry inventory, directly supporting the "multiuser" feature extension.

## 2. Technical Approach

We will use the Supabase client-side SDK (`supabase-js`) to subscribe to database changes. This allows the application to listen for inserts, updates, and deletes on specific tables and reflect those changes in the UI instantly.

### Key Implementation Points:

*   **Client-Side Subscriptions:** Use `supabase.channel()` to create channels for key shared resources.
*   **Postgres Changes:** Listen to `postgres_changes` events to receive database updates.
*   **Optimistic UI:** To ensure a fluid user experience, especially on mobile, we will implement optimistic updates. The local UI state will update immediately upon a user's action, before the database confirms the change.
*   **Offline First:** Changes made while offline will be queued and synced upon reconnection.

### API Sketch:

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

```

## 3. Next Steps
*   Define specific channels and tables for subscription.
*   Detail the conflict resolution strategy.
*   Outline the testing plan for real-time features.