# 03 — Pantry & Inventory 📦

> Track what's in your kitchen — by location, by type, with expiry alerts and staple management.

---

## Overview

The Pantry is the foundation of the Kitchen app. It answers the most basic cooking question: "What do I have?" Items are organized by physical location (fridge, freezer, pantry shelf, counter, garden) and can be flagged as **staples** — things you always keep around. The pantry feeds into recipe matching, meal planning, and shopping list generation.

**Fun fact:** 🐋 A blue whale's "pantry" is the entire ocean. They eat up to 4 tons of krill per day. Our pantry management is slightly more nuanced. 🦐

---

## User Stories

### US-INV-01: Add Item Manually
**As a** user putting away groceries,
**I want to** quickly add items to my pantry with name, quantity, and location,
**So that** my inventory stays current.

### US-INV-02: Browse by Location
**As a** user looking for ingredients,
**I want to** filter items by location (fridge, freezer, pantry, counter, garden),
**So that** I can find things where they physically are.

### US-INV-03: See Expiring Items
**As a** user who hates food waste,
**I want to** see items expiring within 3 days highlighted in yellow/red,
**So that** I can use them before they go bad.

### US-INV-04: Delete Items
**As a** user who used up an ingredient,
**I want to** remove it from inventory,
**So that** my pantry reflects reality.

### US-INV-05: Search Pantry
**As a** user checking if I have something,
**I want to** search by name,
**So that** I don't have to scroll through everything.

### US-INV-06: Mark Staples
**As a** user who always keeps certain items in stock (salt, oil, flour),
**I want to** flag them as "staples,"
**So that** they're tracked differently — I don't need exact counts, just whether I have them.

### US-INV-07: Sort by Different Criteria
**As a** user organizing my pantry view,
**I want to** sort by name, expiry date, quantity, or location,
**So that** I can find what I need based on my current context.

### US-INV-08: Filter Staples vs. Non-Staples
**As a** user reviewing my pantry,
**I want to** toggle between "all items," "staples only," and "non-staples only,"
**So that** I can focus on what I'm looking for.

### US-INV-09: Realtime Multi-User Sync
**As a** household member,
**I want to** see pantry changes from other members in real-time,
**So that** we don't double-buy or lose track of what's been used.

---

## User Flows

### Flow: Add Item Manually
1. User taps "+" button on Pantry screen
2. Action sheet appears: "Scan Items" or "Add Manually"
3. User selects "Add Manually" → bottom sheet opens
4. User fills: name, quantity, unit
5. User selects location (5 buttons: ❄️ Fridge, 🧊 Freezer, 🥫 Pantry, 🍌 Counter, 🌱 Garden)
6. User taps "Add Item" → item created in DB → sheet closes → list refreshes
7. New item appears in correct location group

### Flow: Delete Item
1. User taps trash icon on item card
2. ConfirmDialog appears: "Delete {item}?" / "This will remove it from your inventory"
3. User taps "Delete" → item removed → list refreshes
4. Or user taps "Cancel" → dialog closes, no action

### Flow: Toggle Staple Flag
1. User taps item card → edit screen (or toggle directly on card)
2. User toggles "Staple" checkbox
3. Item updates: if staple, quantity/expiry tracking becomes optional
4. Item appears in "Staples" filter view

### Flow: Filter by Location
1. User taps filter dropdown (default: "All Locations")
2. Selects location (e.g., "❄️ Fridge")
3. List filters to show only fridge items
4. Select "All Locations" to reset

### Flow: Sort Items
1. User taps sort dropdown (default: "Name")
2. Selects criteria (Name, Expiry Date, Quantity, Location)
3. List re-sorts accordingly

### Flow: Realtime Update
1. Another household member adds/removes/modifies an item
2. Supabase realtime channel fires `postgres_changes` event
3. TanStack Query cache invalidated → list refetches
4. Updated item appears/disappears without manual refresh

---

## UI Behavior

### Pantry Screen
- **Search bar:** Filter items by name (client-side filtering)
- **Sort dropdown:** Name | Expiry Date | Quantity | Location
- **Filter dropdown:** All Locations | ❄️ Fridge | 🧊 Freezer | 🥫 Pantry | 🍌 Counter | 🌱 Garden
- **Staple filter:** All Items | Staples Only | Non-Staples Only ← NEW
- **Expiring banner:** Yellow warning bar showing count of items expiring in 3 days
- **Item list:** Grouped by location with emoji headers
- **FAB:** "+" button → opens add action sheet
- **Max-width:** 800px (desktop centered)

### Pantry Item Card
- **Left border color:** Green (fresh) → Orange (expiring soon) → Red (expired/today)
- **Content:** Item name, quantity + unit, expiry date
- **Staple badge:** ⭐ icon or "Staple" tag when flagged ← NEW
- **Actions:** Edit (pencil icon), Delete (trash icon)
- **Cursor:** pointer on interactive elements
- **Notes:** Displayed below main info if present

### Add Item Sheet
- **Name input:** Required, auto-focus
- **Quantity input:** Numeric, optional for staples
- **Unit input:** Text (e.g., "lbs", "oz", "count")
- **Location buttons:** 5 buttons in a row, tap to select
- **Staple checkbox:** "This is a staple item" ← NEW
- **Save button:** Disabled until name filled

---

## Data Model

### `pantry_items` Table
```
pantry_items
├── id: uuid (PK)
├── household_id: uuid (FK → households)
├── name: text (required)
├── quantity: numeric (optional for staples)
├── unit: text (optional)
├── location: enum (pantry | fridge | freezer | counter | garden)
├── expiry_date: date (optional)
├── notes: text (optional)
├── is_staple: boolean (default: false)  ← NEW
├── created_at: timestamp
└── updated_at: timestamp
```

### Staple Behavior
- When `is_staple = true`:
  - Quantity tracking is **optional** (can be null)
  - Expiry date tracking is **optional** (can be null)
  - Item shows in "Staples" filter
  - Recipe matching treats it as "available" (binary: have it or don't)
  - During meal plan verification, user confirms "still have it?" (yes/no)
- When `is_staple = false`:
  - Quantity is expected (though not enforced)
  - Expiry tracking is recommended for perishables
  - Normal inventory behavior

---

## Business Rules

1. **Name normalization:** Title case, trimmed whitespace
2. **Unit normalization:** Lowercase
3. **Household scoping:** All queries filtered by `household_id`
4. **Expiry warnings:** Items expiring within 3 days shown in yellow; today/past shown in red
5. **Location grouping:** Items displayed in location groups with emoji headers
6. **Staples don't expire:** If marked staple, expiry warnings suppressed
7. **Lazy Discovery (D13):** Items can be added to pantry during recipe stock-check ("I have this" button)
8. **Search is case-insensitive:** Uses `ilike` pattern matching
9. **Realtime sync:** Pantry changes broadcast to all household members via Supabase channels

---

## Current State

| Feature | Status | Notes |
|---------|--------|-------|
| Add item manually | ✅ Built | Name, qty, unit, location |
| Delete item | ✅ Built | With ConfirmDialog (Round 7) |
| Search by name | ✅ Built | Client-side filtering |
| Sort (4 criteria) | ✅ Built | Name, Expiry, Quantity, Location |
| Filter by location | ✅ Built | 6 options including "All" |
| Expiry warnings | ✅ Built | 3-day window, color coding |
| Location grouping | ✅ Built | Emoji headers per location |
| Lazy Discovery | ✅ Built | "I have this" in stock check |
| Realtime subscription | ✅ Wired | Needs testing with live Supabase |
| Desktop layout | ✅ Built (Round 7) | maxWidth 800px |
| **Staple flag** | ❌ Not built | `is_staple` column exists but no UI |
| **Staple filter** | ❌ Not built | Need filter option in dropdown |
| **Edit item screen** | ⚠️ Partial | Route exists but basic |
| Scan items (vision) | ⏸️ Parked | Backburnered per user decision |

---

## Open Questions

### OQ-INV-01: Staple Onboarding
Should there be a "seed your staples" flow? (e.g., pre-populated checklist of common staples: salt, pepper, oil, flour, sugar, etc.)

### OQ-INV-02: Quantity Tracking for Staples
Should staples show "In Stock" / "Out of Stock" instead of quantity? Or keep quantity optional but show it if provided?

### OQ-INV-03: Expiry Date Input
Should there be a date picker for expiry? Currently it's just a text field. Mobile-friendly date picker would be better.

### OQ-INV-04: Item Profiles Link
Should pantry items link to shopping item profiles (spec #07)? So "Butter" in pantry and "Butter" on shopping list share metadata (brand, notes, aisle)?
