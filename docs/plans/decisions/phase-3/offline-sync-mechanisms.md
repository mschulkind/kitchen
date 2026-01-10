# Decision: Outline Offline Sync Mechanisms

## Overview

This decision details strategies for handling offline mode in the PWA, ensuring data persistence and seamless reconnection for features like inventory updates, shopping lists, and meal plans. Leverage Supabase SDK for offline queuing and IndexedDB for local storage, focusing on mobile reliability per brief.md.

## Options

- **Option 1: Periodic Polling with Local Storage**
  - Store changes in IndexedDB; poll Supabase on reconnect (e.g., every 30s or on app focus).
  - Simple sync: Upload queued mutations, download updates.

- **Option 2: Background Sync via Service Worker**
  - Use Workbox or native Service Worker for background fetches; queue events with timestamps.
  - Integrate with Expo for push notifications on sync completion.

- **Option 3: Optimistic Updates with Realtime Fallback**
  - Apply changes locally immediately; use Supabase realtime subscriptions on reconnect to resolve conflicts (e.g., last-write-wins).
  - For multiuser: Broadcast pending changes via channels.

## Pros/Cons

- **Periodic Polling**:
  - Pros: Straightforward implementation; works without advanced APIs.
  - Cons: Battery drain from polling; delayed sync (not instant).

- **Background Sync**:
  - Pros: Efficient, user-transparent; handles intermittent connectivity well.
  - Cons: Browser limitations (e.g., no guaranteed execution); complex debugging.

- **Optimistic Updates**:
  - Pros: Responsive UI; aligns with realtime collaboration.
  - Cons: Conflict risks in multiuser; needs rollback logic for failures.

## Questions for User

- Preferred sync trigger: On reconnect, periodic, or user-initiated (e.g., pull-to-sync gesture)?
- Conflict resolution priority: Last-write-wins, manual merge, or notify for review?
- Scope: Full app offline (all features) or limited (e.g., view-only for meal plans)?
- Integration with notifications: Alert on sync failures or conflicts?

## Next Steps

Select mechanism and add Mermaid flow diagram; update hosting.md and design-system.md with implementation notes. Reference: [plans/hosting.md](../hosting.md), [plans/design-system.md](../design-system.md), [plans/brief.md](../brief.md).

*Decision Pending - Awaiting User Input*
