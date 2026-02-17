# 08 — Settings & Preferences ⚙️

> User profile, household management, dietary preferences, store configuration, and app settings.

---

## Overview

Settings is the backstage of the Kitchen app. It shows account info, household details, and user preferences that influence behavior across the entire app — from dietary restrictions (affects AI recipe suggestions) to preferred store (affects shopping list sorting) to notification preferences.

**Fun fact:** 🐋 Whale preferences are pretty simple: warm water for calving, cold water for eating. Our settings page is slightly more complex. 🌊

---

## User Stories

### US-SET-01: View Account Info
**As a** user,
**I want to** see my email and sign-in status,
**So that** I know which account I'm using.

### US-SET-02: Set Preferred Store
**As a** user who shops at a specific store,
**I want to** set my preferred store,
**So that** shopping lists can be optimized for that store's layout.

### US-SET-03: Manage Household
**As a** household owner,
**I want to** see household members and manage access,
**So that** the right people have the right permissions.

### US-SET-04: Set Dietary Preferences
**As a** user with dietary restrictions,
**I want to** set my household's dietary profile (vegetarian, allergies, dislikes),
**So that** AI suggestions respect these constraints automatically.

### US-SET-05: Notification Preferences
**As a** user,
**I want to** control which notifications I receive,
**So that** I'm not overwhelmed but don't miss important alerts.

### US-SET-06: Sign Out
**As a** user,
**I want to** sign out of my account,
**So that** my data is secure on shared devices.

---

## User Flows

### Flow: Set Preferred Store
1. User navigates to Settings
2. Scrolls to "Preferred Store" section
3. Types store name (e.g., "Trader Joe's")
4. Taps "Save" → stored in AsyncStorage
5. Confirmation: "✅ Saved!" (fades after 2 seconds)

### Flow: Sign Out
1. User taps "Sign Out" on Settings page
2. `supabase.auth.signOut()` called
3. Session cleared, cache cleared
4. Redirect to Landing page

---

## UI Behavior

### Settings Screen
- **Account section:**
  - User email (read-only)
  - Sign-in status badge (green "Active")
- **Household section:**
  - Household name
  - Member count
  - "Manage" button (future — not yet functional)
- **Preferences section:**
  - Expiry notifications toggle
  - Dark mode toggle (cosmetic placeholder)
- **Preferred Store:**
  - Text input with placeholder "e.g. Trader Joe's"
  - "Save Store" button → "✅ Saved!" feedback
- **About section:**
  - App version
- **Max-width:** 700px (desktop)

---

## Data Model

### Local Storage (AsyncStorage)
```
PREFERRED_STORE_KEY → string (store name)
```

### Future: `household_preferences` Table
```
household_preferences
├── id: uuid (PK)
├── household_id: uuid (FK)
├── dietary_restrictions: text[] (vegetarian, gluten-free, etc.)
├── dislikes: text[] (mushrooms, olives, etc.)
├── preferred_store_id: uuid (FK → stores, future)
├── preferred_store_name: text
├── notification_expiry: boolean
├── notification_shopping: boolean
├── notification_planning: boolean
├── adults_count: integer
├── kids_count: integer
├── default_servings: integer
├── created_at: timestamp
└── updated_at: timestamp
```

---

## Business Rules

1. **Store name persists locally** — AsyncStorage for now, should move to DB
2. **Dark mode is cosmetic** — toggle exists but app is forced to light theme
3. **Household management is placeholder** — shows info but can't edit yet
4. **No phase/version info shown** — removed in Round 7 per user request

---

## Current State

| Feature | Status | Notes |
|---------|--------|-------|
| Account info display | ✅ Built | Email + status badge |
| Preferred store input | ✅ Built | AsyncStorage persistence |
| Sign out | ✅ Built | Clears session |
| Household info display | ✅ Built | Name + member count |
| Desktop layout | ✅ Built (Round 7) | maxWidth 700px |
| Version/phase removed | ✅ Done (Round 7) | Per user feedback |
| **Dietary preferences** | ❌ Not built | Need UI + DB table |
| **Household management** | ❌ Not built | Invite, roles, remove |
| **Notification settings** | ❌ Not built | Toggle placeholders exist |
| **Store moved to DB** | ❌ Not done | Still in AsyncStorage |
| **Dark mode (real)** | ❌ Not built | Just a toggle |

---

## Open Questions

### OQ-SET-01: Dietary Profile Scope
Should dietary preferences be per-user or per-household? (e.g., one person is vegetarian, others aren't)

### OQ-SET-02: Dislikes List
How does the "dislikes" list work? Free-text tags? Ingredient picker? How does it feed into AI recipe generation?

### OQ-SET-03: Household Servings Default
Should settings include a default servings count? (e.g., "We usually cook for 4") This could pre-fill recipe scaling.

### OQ-SET-04: Store Persistence
Should preferred store move from AsyncStorage to the database? (Needed for multi-device support)
