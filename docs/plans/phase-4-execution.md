# Phase 4: Execution & Realtime

**Goal**: Support the user *in the store* and *in the kitchen*. This phase focuses on the "Realtime" and "Offline" capabilities of the App.

## 4.1 The Shopping Experience

### Data Model
- **`shopping_list_items`**
    - `id`: UUID
    - `plan_id`: UUID (Optional, link to origin plan)
    - `name`: String
    - `category`: String
    - `is_checked`: Boolean
    - `checked_by`: UUID (User who checked it)

### Realtime Sync
- **Supabase Realtime**: Listen to `postgres_changes` on `shopping_list_items`.
- **UI**:
    - When User A checks "Milk", User B's screen updates instantly.
    - Show "toast" or visual indicator: "Alex bought Milk".

### Offline Support
- **TanStack Query (React Query)**: Configure `persister` to save state to `AsyncStorage`.
- **Optimistic Updates**: UI updates immediately. If offline, the mutation is queued.
- **Reconciliation**: When online, replay mutations. Last-write-wins is acceptable for shopping lists.

## 4.2 The Cooking Experience (5-Way View)

Implement the varied view modes for recipes.

1.  **Mise-en-place**:
    - Extract ingredients and prep instructions.
    - Checklist style: "Chop onions", "Measure spices".
2.  **Timeline**:
    - Gantt chart style visualization if multiple dishes are being cooked (advanced).
    - Or simple step-by-step focusing on parallelism ("While water boils, cut veg").
3.  **Chef's Shorthand**:
    - Dense text, no fluff. "Sauté onions 5m. Add spices. Deglaze."
4.  **Flavor Layers**:
    - Educational view. "Base: Onions/Garlic", "Acid: Lemon", "Finish: Herbs".
5.  **Sensory**:
    - "Smell for nuttiness", "Look for golden brown".

## 4.3 Consumption Logic

- **"I Cooked This" Button**:
    - Trigger: User marks a meal as done.
    - Action: Backend decrements the estimated amounts from `pantry_items`.
    - *Note*: This is inexact. We might just mark the plan as "Archived" and rely on the next Phase 2 Scan to true-up inventory. Auto-decrementing can lead to "Data Drift" frustration.

## Definition of Done (Phase 4)
- [ ] Shared Shopping List works with < 500ms latency between devices.
- [ ] Offline shopping works (add/check items in Airplane mode, sync on reconnect).
- [ ] Recipe details screen supports at least 2 views (Standard + Mise-en-place).
- [ ] "Cooked" action logs history.
