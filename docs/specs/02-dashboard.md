# 02 — Dashboard / Hub 🏠

> The main screen after login. At-a-glance kitchen status and navigation to all features.

---

## Overview

The Dashboard (internally "Hub") is the command center of the Kitchen app. It shows what's for dinner tonight, alerts about expiring items, and provides one-tap access to every major feature. It should feel like walking into your kitchen and seeing everything at a glance.

**Fun fact:** 🐋 Whales don't have kitchens, but if they did, the dashboard would probably just show "krill" every night.

---

## User Stories

### US-HUB-01: See Tonight's Dinner
**As a** user arriving home,
**I want to** see what's planned for dinner tonight,
**So that** I know what to cook without digging through the planner.

### US-HUB-02: Quick Shopping Count
**As a** user heading to the store,
**I want to** see how many items are on my shopping list,
**So that** I know if I need to stop by the store.

### US-HUB-03: Expiry Alerts
**As a** user who hates food waste,
**I want to** see items expiring soon,
**So that** I can use them before they go bad.

### US-HUB-04: Navigate to Features
**As a** user,
**I want to** tap any feature card to jump to that section,
**So that** navigation is fast and intuitive.

---

## User Flows

### Flow: Dashboard Load
1. User authenticates → lands on Dashboard
2. Dashboard fetches in parallel:
   - Tonight's meal plan (today's date, meal_type = 'main')
   - Shopping list unchecked count
   - Pantry items expiring within 3 days
3. Data renders into widgets
4. Pull-to-refresh invalidates all queries

### Flow: Navigate to Feature
1. User taps a module card (Recipes, Pantry, Planner, Shopping)
2. Navigate to that feature's index screen
3. Back button returns to Dashboard

---

## UI Behavior

### Layout
- **Greeting header:** Time-based ("Good Morning/Afternoon/Evening") + user's first name
- **Avatar:** Top-right, links to Settings
- **Max-width:** 800px centered (desktop responsive)

### Tonight's Dinner Widget
- Shows recipe title if meal planned for today
- Tappable → navigates to recipe detail
- Empty state: "No dinner planned" with link to Planner
- Shows prep + cook time (if > 0)

### Quick Stats Row (2 cards)
- **Shopping:** Orange cart icon + unchecked item count + "items to buy"
- **Expiring:** Blue/yellow alert icon + expiring count + "expiring soon"
- Both tappable → navigate to respective screens

### Module Grid (2×2)
- **Recipes:** Orange, book icon, "Browse & discover"
- **Pantry:** Blue, package icon, "Track ingredients"
- **Planner:** Green, calendar icon, "Plan your week"
- **Shopping:** Yellow, cart icon, "Your shopping list"
- All have `cursor: pointer` + hover styles for desktop
- 44px+ minimum touch targets

### Utility Links
- Settings button
- Sign Out button

---

## Data Model

Dashboard doesn't have its own tables — it aggregates from:
- `meal_plans` (tonight's dinner)
- `shopping_list` (unchecked count)
- `pantry_items` (expiry check)

---

## Business Rules

1. **Greeting is time-based:** Before noon = Morning, noon-5pm = Afternoon, after 5pm = Evening
2. **Expiry window:** 3 days from today (configurable future)
3. **Tonight's meal:** Filters for today's date + `meal_type = 'main'`, takes first result
4. **Counts are live:** Queries refetch on focus/mount, pull-to-refresh available
5. **No stale data:** TanStack Query with 5-minute stale time

---

## Current State

| Feature | Status | Notes |
|---------|--------|-------|
| Time-based greeting | ✅ Built | Morning/Afternoon/Evening |
| Tonight's dinner widget | ✅ Built | Shows first main meal for today |
| Shopping count | ✅ Built | Unchecked items count |
| Expiry alerts | ✅ Built | Items expiring within 3 days |
| Module navigation cards | ✅ Built | 4 cards with hover + cursor |
| Desktop centering | ✅ Built (Round 7) | maxWidth 800px |
| Pull-to-refresh | ✅ Built | Invalidates all queries |
| Sign out | ✅ Built | Clears session |

---

## Open Questions

### OQ-HUB-01: Recent Activity Feed
Should the dashboard show recent changes? (e.g., "Alex added milk to shopping list 5 min ago")

### OQ-HUB-02: Quick Actions
Should there be quick-action buttons? (e.g., "Quick add to shopping list" without navigating away)

### OQ-HUB-03: Customizable Widgets
Should users be able to rearrange or hide widgets?
