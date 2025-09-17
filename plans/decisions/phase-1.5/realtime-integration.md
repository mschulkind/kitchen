# Decision Log: Realtime Collaboration with Supabase

## Table of Contents
- [1. Goal](#1-goal)
- [2. Technical Approach](#2-technical-approach)
  - [Key Implementation Points](#key-implementation-points)
- [3. Channels and Subscriptions](#3-channels-and-subscriptions)
- [4. Conflict Resolution and UI Updates](#4-conflict-resolution-and-ui-updates)
- [5. Next Steps](#5-next-steps)

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

## 3. Channels and Subscriptions

To structure the real-time communication, we will define channels based on shared resources. A user will subscribe to a channel corresponding to a specific shared object (e.g., a single shopping list or meal plan).

| Channel Type        | Naming Convention                                  | Watched Table(s)        | Purpose                                                                                |
| ------------------- | -------------------------------------------------- | ----------------------- | -------------------------------------------------------------------------------------- |
| **Shared List**     | `shared-list:{list_id}`                            | `shopping_list_items`   | Broadcasts changes to items within a specific shopping list (adds, updates, deletes).  |
| **Meal Plan**       | `meal-plan:{plan_id}`                              | `meal_plan_recipes`     | Syncs recipes added to or removed from a collaborative meal plan.                      |
| **Presence**        | `presence-list:{list_id}` or `presence-plan:{plan_id}` | (N/A - Presence state)  | Tracks which users are currently viewing a specific list or plan.                      |

### Subscription Logic:
- When a user views a shared shopping list, the app will subscribe to `shared-list:{list_id}` and `presence-list:{list_id}`.
- The `filter` parameter in the subscription will be used to ensure clients only receive events for the specific resource they are viewing.

## 4. Conflict Resolution and UI Updates

- **Strategy**: As defined in [`conflict-resolution-and-offline.md`](conflict-resolution-and-offline.md), we will use a **Last Write Wins (LWW)** approach.
- **UI Feedback**:
    - **Optimistic Updates**: Local changes are reflected instantly in the UI.
    - **Incoming Changes**: When a change is received from the channel, the UI will smoothly update to reflect the new state (e.g., an item appearing, a quantity changing).
    - **User Avatars**: Presence information will be used to display the avatars of other users currently viewing the same resource, providing a clear sense of collaboration.

## 5. Next Steps
*   Detail the conflict resolution strategy (covered in the dedicated document).
*   Outline the testing plan for real-time features (covered in the dedicated document).
*   Implement a proof-of-concept with two simulated clients.