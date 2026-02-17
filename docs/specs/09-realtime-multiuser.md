# 09 — Realtime & Multi-User 🔄

> Live synchronization between household members. See changes as they happen — shopping checks, pantry updates, meal plan edits.

---

## Overview

The Kitchen app is designed for households, not individuals. When one person checks off milk at the store, the other person at home should see it immediately. When someone adds eggs to the pantry, the meal planner should know. Realtime sync is powered by Supabase Realtime (PostgreSQL LISTEN/NOTIFY over WebSockets).

This is not a "nice to have" — it's core to the multi-user kitchen experience.

**Fun fact:** 🐋 Pod communication in whales uses low-frequency sounds that travel thousands of miles underwater. Our WebSocket latency is admittedly better. 📡

---

## User Stories

### US-RT-01: See Shopping Checkmarks in Real-Time
**As a** household member shopping while my partner is at home,
**I want to** see their checkmarks appear on my list instantly,
**So that** we don't buy duplicates.

### US-RT-02: See Pantry Changes Live
**As a** user viewing my pantry,
**I want to** see items added or removed by other household members,
**So that** I always have an accurate picture.

### US-RT-03: See Meal Plan Updates
**As a** user viewing the weekly plan,
**I want to** see meals added, removed, or locked by others,
**So that** we're all on the same page.

### US-RT-04: Presence Indicators (Future)
**As a** user on any screen,
**I want to** see who else is currently using the app,
**So that** I know if someone else is shopping/planning simultaneously.

### US-RT-05: Conflict Resolution
**As a** user editing the same item as someone else,
**I want** the app to handle conflicts gracefully,
**So that** no one's changes are silently lost.

---

## User Flows

### Flow: Realtime Shopping Sync
1. User A opens shopping list → subscribes to `shopping_list` channel
2. User B checks off "Milk" on their device
3. Supabase broadcasts `UPDATE` event on `shopping_list` table
4. User A's channel receives event → invalidates TanStack Query cache
5. Shopping list refetches → "Milk" shows as checked on User A's screen
6. Latency: < 500ms typical

### Flow: Realtime Pantry Sync
1. User A viewing pantry → `useInventorySubscription` hook active
2. User B adds "Eggs" via add-item sheet
3. Supabase broadcasts `INSERT` event on `pantry_items` table
4. User A's subscription fires → invalidates `['pantry', householdId]` query
5. Pantry list refetches → "Eggs" appears

### Flow: Offline → Reconnect
1. User loses internet connection
2. Local changes queue (optimistic updates still show)
3. Connection restored → Supabase client reconnects
4. Queued changes sync → cache invalidated → fresh data loaded
5. If conflict → last-write-wins (simple strategy for now)

---

## Technical Architecture

### Supabase Realtime Channels
```typescript
// Shopping list subscription pattern
const channel = supabase
  .channel('shopping_list_changes')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'shopping_list',
    filter: `household_id=eq.${householdId}`
  }, () => {
    queryClient.invalidateQueries({ queryKey: ['shopping_list', householdId] });
  })
  .subscribe();
```

### Current Subscriptions
| Table | Hook/Location | Events |
|-------|--------------|--------|
| `pantry_items` | `useInventorySubscription()` | INSERT, UPDATE, DELETE |
| `shopping_list` | Shopping screen `useEffect` | INSERT, UPDATE, DELETE |
| `meal_plans` | Not yet wired | — |

### Cache Invalidation Strategy
- On realtime event → invalidate specific TanStack Query key
- Query refetches in background → UI updates
- Optimistic updates for user's own actions (instant feedback)
- Server reconciliation on refetch (source of truth)

### Connection Config
```typescript
// Supabase client setup
const supabase = createClient(url, key, {
  realtime: { params: { eventsPerSecond: 10 } }
});
```

---

## Data Model

No new tables — realtime operates on existing tables:
- `pantry_items` (household-filtered)
- `shopping_list` (household-filtered)
- `meal_plans` (household-filtered)
- `recipes` (household-filtered, future)

### Supabase Realtime Requirements
- PostgreSQL `REPLICA IDENTITY FULL` on tracked tables (for UPDATE events)
- Publication `supabase_realtime` includes target tables
- Realtime service running in Docker (port 4000 internally)
- WebSocket endpoint: `ws://{host}:{port}/realtime/v1/websocket`

---

## Business Rules

1. **Household scoping:** Realtime events filtered by `household_id` — users only see their own household's changes
2. **Last-write-wins:** For simultaneous edits, most recent write is accepted (no merge)
3. **Cache invalidation, not state patching:** On event, we refetch rather than apply diffs (simpler, more reliable)
4. **Optimistic UI for own actions:** User's own changes appear immediately, server confirms asynchronously
5. **Reconnection:** Supabase client auto-reconnects on network restoration
6. **Rate limiting:** Max 10 events/second to prevent flooding

---

## Current State

| Feature | Status | Notes |
|---------|--------|-------|
| Pantry realtime subscription | ✅ Wired | `useInventorySubscription` hook |
| Shopping realtime subscription | ✅ Wired | In shopping screen useEffect |
| Meal plan realtime | ❌ Not wired | No subscription yet |
| Optimistic updates (shopping) | ✅ Built | Check/uncheck instant |
| Supabase Realtime service | 🟡 Available | User confirmed accessible |
| **Platform URL detection** | ✅ Fixed (Round 7) | Web→localhost, emulator→10.0.2.2 |
| **Presence indicators** | ❌ Not built | Future feature |
| **Conflict resolution** | ⚠️ Basic | Last-write-wins only |
| **Offline queueing** | ❌ Not built | Supabase SDK handles basic reconnection |

---

## Open Questions

### OQ-RT-01: Meal Plan Realtime
Should meal plan changes broadcast in realtime? (e.g., one person adds a meal, the other sees it)

### OQ-RT-02: Presence UX
What should presence indicators look like? Avatar bubbles? "Alex is shopping" banner? Online dots?

### OQ-RT-03: Conflict UX
Should we show "Someone else changed this item" alerts? Or silently last-write-wins?

### OQ-RT-04: Notification Integration
Should realtime events trigger push notifications? (e.g., "Alex checked off 3 items at the store")
