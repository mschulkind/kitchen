# 07 — Shopping Lists 🛒

> Shared shopping lists with smart categorization, autocomplete, item profiles, and store-aware aisle sorting.

---

## Overview

The Shopping List is where meal planning meets the real world. Users add items manually, or the planner auto-generates them from recipes. Items are automatically categorized (Produce, Dairy, Meat, etc.) and can be checked off as you shop. The list is realtime — multiple household members can check off items simultaneously.

The big vision: each item builds a **profile** over time — brand preferences, notes, aisle numbers, pictures. Autocomplete draws from a USDA-based taxonomy and past purchase history. Categories are smart enough to predict which aisle an item is in.

**Fun fact:** 🐋 A whale shark filters 6,000 liters of water per hour looking for food. Our shopping list autocomplete is basically the same concept but for groceries. 🦈

---

## User Stories

### US-SHOP-01: Add Item Manually
**As a** user who remembers something to buy,
**I want to** type it and add to the list,
**So that** I don't forget it at the store.

### US-SHOP-02: Check Off Items While Shopping
**As a** user at the store,
**I want to** tap items to mark them bought,
**So that** I track my progress through the list.

### US-SHOP-03: See Items by Category
**As a** user navigating a store,
**I want to** items grouped by department (Produce, Dairy, Meat...),
**So that** I can shop efficiently without backtracking.

### US-SHOP-04: Auto-Generate from Meal Plan
**As a** user with a complete meal plan,
**I want to** generate a shopping list from all recipes,
**So that** I buy exactly what I need without manual entry.

### US-SHOP-05: Delete Items
**As a** user who changed my mind,
**I want to** remove items from the list,
**So that** I don't buy things I don't need.

### US-SHOP-06: Clear Completed Items
**As a** user who finished shopping,
**I want to** clear all checked items,
**So that** the list is clean for next time.

### US-SHOP-07: Autocomplete When Adding
**As a** user adding items,
**I want to** see suggestions as I type (from common items and past purchases),
**So that** I can add items faster and with consistent naming.

### US-SHOP-08: Realtime Multi-User Sync
**As a** household member shopping with my partner,
**I want to** see checkmarks appear in real-time,
**So that** we don't buy duplicates.

### US-SHOP-09: Item Profiles
**As a** a regular shopper,
**I want to** build up notes, brand preferences, and aisle info for items I buy often,
**So that** shopping gets faster and more informed over time.

### US-SHOP-10: Aisle-Sorted View
**As a** user at a specific store,
**I want to** items sorted by aisle number,
**So that** I can walk through the store in order.

---

## User Flows

### Flow: Add Item Manually
1. User types item name in add bar (top of screen)
2. **Autocomplete dropdown** appears showing:
   - Recent items (from purchase history)
   - Common items (from USDA taxonomy, matching query)
   - Each suggestion shows: name, category badge, aisle hint (if known)
3. User taps a suggestion OR finishes typing and taps "Add"
4. Item added with auto-assigned category
5. Item appears in correct category group in the list
6. Input clears, ready for next item

### Flow: Check Off Items
1. User taps checkbox next to item
2. **Optimistic update:** Item immediately shows strikethrough + gray
3. Database updates in background
4. Other household members see the change in real-time
5. Checked items move to "Completed" section (if shown)

### Flow: Auto-Generate from Planner
1. User taps "Generate Shopping List" on Planner screen
2. System collects all recipe ingredients for the week
3. Compares against existing shopping list (dedup)
4. Compares against pantry (skip items user already has)
5. Adds missing items with category + recipe source annotation
6. Navigates to Shopping List screen
7. Toast: "Added X items from Y recipes"

### Flow: Browse Item Profile
1. User long-presses (or taps info icon) on an item
2. Profile sheet opens showing:
   - Item name + category
   - Aisle hint (if known)
   - Notes (e.g., "Get the organic brand")
   - Preferred brand
   - Photo (if captured)
   - Purchase history (last 5 times bought)
3. User can edit notes, brand, aisle
4. Changes saved to household item profile

---

## UI Behavior

### Shopping List Screen
- **Add bar:** Text input + "Add" button (orange)
  - Autocomplete dropdown below input ← NEW
  - Shows up to 8 suggestions
  - Categories as colored badges
- **Item list:** Grouped by category with headers
  - Category order: Produce → Dairy → Meat → Bakery → Frozen → Beverages → Pantry → Other
  - Each item: checkbox + name + qty/unit + delete icon
  - Checked items: strikethrough + gray
- **Summary footer:** "X items to buy" + "✓ Y completed"
- **Clear Completed:** Header button (red), only if completed items exist
- **Max-width:** 800px (desktop)

### Autocomplete Dropdown (NEW)
```
┌─────────────────────────────────┐
│ 🕐 Milk (Dairy)         Aisle 4│
│ 🕐 Milky Way bars (Pantry)     │
│ ── Common Items ──              │
│ 🥛 Milk, whole (Dairy)  Aisle 4│
│ 🥛 Milk, 2% (Dairy)    Aisle 4│
│ 🥛 Milk, almond (Dairy) Aisle 7│
└─────────────────────────────────┘
```
- Recent items marked with 🕐 clock icon
- Common items from taxonomy below
- Each shows category + aisle (if known)
- Tap to select and auto-fill

### Item Profile Sheet (NEW)
```
┌─────────────────────────────────┐
│ Milk, Whole                     │
│ Category: Dairy · Aisle 4       │
│                                 │
│ 📝 Notes: Get Horizon Organic   │
│ 🏷️ Brand: Horizon Organic       │
│ 📸 [Photo placeholder]          │
│                                 │
│ Purchase History:               │
│ · Feb 15 — 1 gallon             │
│ · Feb 8 — 1 gallon              │
│ · Feb 1 — 2 gallons             │
│                                 │
│ [Save] [Close]                  │
└─────────────────────────────────┘
```

---

## Data Model

### `shopping_list` Table (existing — used by frontend directly)
```
shopping_list
├── id: uuid (PK)
├── household_id: uuid (FK)
├── name: text
├── quantity: numeric (optional)
├── unit: text (optional)
├── category: text (auto-assigned)
├── checked: boolean (default: false)
├── aisle_hint: text (optional)
├── notes: text (optional)
├── recipe_source: text (optional, which recipe added this)
├── created_at: timestamp
└── updated_at: timestamp
```

### `item_profiles` Table (NEW)
```
item_profiles
├── id: uuid (PK)
├── canonical_name: text (normalized, lowercase)
├── display_name: text (user-friendly)
├── category: text (Produce, Dairy, Meat, etc.)
├── subcategory: text (optional, e.g., "Citrus Fruits")
├── usda_category: text (from USDA taxonomy)
├── default_unit: text (e.g., "lb", "oz", "count")
├── default_aisle: integer (optional, generic aisle estimate)
├── is_global: boolean (true = seed data, false = household)
├── household_id: uuid (FK, null for global)
├── created_at: timestamp
└── updated_at: timestamp
```

### `household_item_overrides` Table (NEW)
```
household_item_overrides
├── id: uuid (PK)
├── household_id: uuid (FK)
├── item_profile_id: uuid (FK → item_profiles)
├── preferred_brand: text (optional)
├── notes: text (optional)
├── photo_url: text (optional)
├── custom_aisle: integer (optional, store-specific)
├── store_id: uuid (optional, FK → stores, future)
├── created_at: timestamp
└── updated_at: timestamp
```

### `purchase_history` Table (NEW)
```
purchase_history
├── id: uuid (PK)
├── household_id: uuid (FK)
├── item_profile_id: uuid (FK → item_profiles)
├── quantity: numeric
├── unit: text
├── purchased_at: timestamp
├── shopping_list_id: uuid (FK, optional)
└── created_at: timestamp
```

### USDA Taxonomy Seed Data
- Source: USDA FoodData Central (SR Legacy or Foundation)
- Filter: Common consumer-friendly names only
- Fields: name, category, subcategory
- Enrichment: Add default aisle estimates per category
- Size: ~2,000-5,000 items (curated, not full database)
- Naming: User-friendly ("Bananas" not "Musa acuminata")

### Category → Aisle Mapping (KNN-style)
```
Category classification hierarchy:
├── Produce (Aisle 1-2)
│   ├── Fruits (1)
│   ├── Vegetables (2)
│   └── Herbs (2)
├── Dairy (Aisle 3-4)
│   ├── Milk & Cream (3)
│   ├── Cheese (3)
│   ├── Yogurt (4)
│   └── Eggs (4)
├── Meat & Seafood (Aisle 5)
├── Bakery (Aisle 6)
├── Frozen (Aisle 7-8)
├── Beverages (Aisle 9)
├── Pantry/Dry Goods (Aisle 10-12)
│   ├── Grains & Pasta (10)
│   ├── Canned Goods (11)
│   └── Baking & Spices (12)
└── Other (varies)
```

---

## Business Rules

1. **Auto-categorization:** When adding an item, category is guessed from name keywords
2. **Deduplication:** Shopping list generation skips items already on the list
3. **Pantry-aware:** Generation skips items user already has in pantry
4. **Optimistic updates:** Checking/unchecking items updates UI immediately, syncs in background
5. **Realtime sync:** All changes broadcast via Supabase realtime channels
6. **Item aggregation:** If multiple recipes need "onion", combine into one item with total quantity
7. **Global profiles are read-only:** Users can't modify seed data, only add household overrides
8. **Purchase history auto-tracks:** When items are checked off, record in history
9. **Autocomplete prioritizes recency:** Recent purchases appear first, then taxonomy matches

---

## Current State

| Feature | Status | Notes |
|---------|--------|-------|
| Add item manually | ✅ Built | Text input + add button |
| Check off items | ✅ Built | Optimistic updates |
| Category grouping | ✅ Built | 8 categories with order |
| Auto-categorization | ✅ Built | Keyword-based guessing |
| Delete items | ✅ Built | Trash icon per item |
| Clear completed | ✅ Built | Header button |
| Generate from planner | ✅ Built | Aggregates recipe ingredients |
| Realtime sync | ✅ Wired | Channel setup, needs live test |
| Desktop layout | ✅ Built (Round 7) | maxWidth 800px |
| **Autocomplete** | 🔴 Not started | Need USDA data + API |
| **Item profiles** | 🔴 Not started | New tables needed |
| **Household overrides** | 🔴 Not started | New tables needed |
| **Purchase history** | 🔴 Not started | New tables needed |
| **Aisle sorting** | ⚠️ Backend only | API exists, not in frontend |
| **USDA taxonomy seed** | 🔴 Not started | Data curation needed |

---

## Open Questions

### OQ-SHOP-01: USDA Data Curation
How do we filter the USDA database to ~2-5K consumer-friendly items? Manual curation? LLM-assisted?

### OQ-SHOP-02: Aisle Accuracy
Aisle numbers vary wildly by store. Should we start with generic category-based ordering and let users customize per store later?

### OQ-SHOP-03: Item Matching
How do we match "milk" (shopping list) to "Milk, whole" (USDA)? Fuzzy matching? Alias table?

### OQ-SHOP-04: Photo Capture
Should item profiles support photos? (e.g., "This is the exact brand I want") If so, where stored?

### OQ-SHOP-05: Multi-Store Support
The user mentioned starting with one store. When do we add multi-store? What changes in the data model?

### OQ-SHOP-06: Recipe Source Annotation
When items come from meal plan generation, should the list show which recipe they're for? (e.g., "Chicken thighs — for Honey Garlic Chicken")

---

## 🏪 Store Intelligence (Future Enhancement)

> From the original phase-08 spec — make shopping lists aware of actual store layouts.

### Phase 1: Basic Category Sorting (Built)
- Items sorted by grocery category: Produce → Dairy → Meat → Bakery → Frozen → Beverages → Pantry → Other
- Works for any store since most follow similar general layouts

### Phase 2: Per-Store Aisle Mapping (Planned)
- User can configure aisle numbers per category for their preferred store
- Shopping list sorted by actual aisle order for that specific store
- "Learning mode": app remembers when users manually reorder items

### Phase 3: Advanced Store Intelligence (Future)
- **Store floor plan visualization** — map view of the store with your items plotted
- **Optimal path calculation** — shortest walking route through the store
- **Multi-store support** — different aisle configs per store, pick which store you're at
- **Community data** — share aisle mappings with other users of the same store
- **Price tracking** — estimated cost per item, budget totals

### Per-Store Data Model (Future)
```sql
CREATE TABLE store_configs (
  id UUID PRIMARY KEY,
  household_id UUID REFERENCES households(id),
  store_name TEXT NOT NULL,
  is_default BOOLEAN DEFAULT FALSE
);

CREATE TABLE store_aisle_mappings (
  id UUID PRIMARY KEY,
  store_config_id UUID REFERENCES store_configs(id),
  category TEXT NOT NULL,       -- e.g., "Produce"
  aisle_number TEXT,            -- e.g., "1" or "Perimeter"
  sort_order INTEGER,           -- order when walking the store
  notes TEXT                    -- e.g., "Back wall"
);
```

---

## 🛒 Grocery Delivery Integration (Future Idea)

> Inspired by Mealime, Whisk, and other apps that connect to delivery services.

### Concept
- Export shopping list to delivery services (Instacart, Amazon Fresh, Walmart)
- One-tap "Order Online" button that pre-fills your cart
- Price comparison across services
- Delivery scheduling from within the app

### Implementation
- Most services have affiliate APIs or URL-based cart building
- Start with simple "export as text" for manual pasting
- Graduate to API integration for popular services

**Fun fact:** 🐋 Whales migrate thousands of miles for food but never use Instacart. We can do better. 📦
