# 01 — Auth & Accounts 🔐

> Handles user identity, session management, household membership, and access control.

---

## Overview

The Kitchen app uses Supabase Auth for identity. Users sign in with Google OAuth (primary) or email/password (dev only). Each user belongs to a household — all data is scoped to the household level. Currently single-household, but designed for multi-household expansion.

**Fun fact:** 🐋 A whale's household can span an entire ocean. Ours just spans a kitchen... for now.

---

## User Stories

### US-AUTH-01: Sign In with Google
**As a** user opening the app for the first time,
**I want to** sign in with my Google account,
**So that** I don't need to create yet another username/password.

### US-AUTH-02: Stay Signed In
**As a** returning user,
**I want to** remain signed in across app restarts,
**So that** I can jump straight to my kitchen dashboard.

### US-AUTH-03: Sign Out
**As a** user who wants to switch accounts or secure my device,
**I want to** sign out,
**So that** my kitchen data isn't accessible to others on this device.

### US-AUTH-04: Dev Login (Development Only)
**As a** developer testing the app,
**I want to** bypass OAuth with a dev login,
**So that** I can test features without configuring Google OAuth.

### US-AUTH-05: Household Membership
**As a** user in a shared kitchen,
**I want to** see data scoped to my household,
**So that** my family's pantry and plans are shared but private from other households.

---

## User Flows

### Flow: First-Time Sign In
1. User opens app → splash screen checks `supabase.auth.getSession()`
2. No session → redirect to Landing page
3. Landing shows hero + feature cards + "Sign in with Google" button
4. User taps Google → OAuth flow → redirect back with session
5. App checks `household_members` for user → routes to Dashboard
6. If no household → (future: create/join household flow)

### Flow: Return Visit
1. User opens app → splash checks session
2. Session exists and valid → redirect to Dashboard
3. Session expired → redirect to Landing (re-auth needed)

### Flow: Sign Out
1. User taps avatar on Dashboard → Settings
2. User taps "Sign Out" → `supabase.auth.signOut()`
3. Session cleared → redirect to Landing

### Flow: Dev Login (Development Only)
1. Dev taps "🛠️ Dev Login" on Landing
2. Signs in via `signInWithPassword` with admin credentials
3. Real session created → redirect to Dashboard
4. Session persists across refreshes ✅

---

## UI Behavior

### Landing Page
- **Hero:** ChefHat icon, "Kitchen" title, "Your smart kitchen companion" subtitle
- **Feature cards:** 3 cards showcasing Smart Pantry, AI Recipes, Auto Shopping
- **Google button:** Full-width, branded, 44px+ touch target
- **Dev button:** Only visible in `__DEV__` mode, clearly marked as dev tool
- **Error display:** Red card below buttons if auth fails
- **Desktop:** Max-width 500px, centered

### Auth Router (app/index.tsx)
- Shows spinner while checking session
- No user interaction — purely automatic routing
- Redirects based on auth state

---

## Data Model

### Supabase Auth (managed by Supabase)
- `auth.users` — User accounts (email, OAuth provider, metadata)
- `auth.sessions` — Active sessions (JWT tokens, expiry)

### Application Tables
```
households
├── id: uuid (PK)
├── name: text
├── created_at: timestamp
└── updated_at: timestamp

household_members
├── id: uuid (PK)
├── household_id: uuid (FK → households)
├── user_id: uuid (FK → auth.users)
├── role: text ('owner' | 'editor' | 'viewer')
├── created_at: timestamp
└── updated_at: timestamp
```

### Hardcoded Dev Values
- **Household ID:** `a0000000-0000-0000-0000-000000000001` ("Dev Kitchen")
- **User ID:** `d0000000-0000-0000-0000-000000000001`

---

## Business Rules

1. **One active session per device** — signing in replaces any existing session
2. **Household scoping** — ALL data queries are filtered by `household_id` (enforced by RLS)
3. **Dev login creates real session** — uses `signInWithPassword`, not a mock bypass
4. **No self-registration** — users must be invited to a household (future)
5. **Google OAuth is primary** — email/password is dev-only, not exposed to end users

---

## Current State

| Feature | Status | Notes |
|---------|--------|-------|
| Google OAuth sign-in | ✅ Built | Supabase OAuth flow |
| Session persistence | ✅ Fixed (Round 7) | Was broken — dev login didn't create real session |
| Sign out | ✅ Built | Clears session, redirects to landing |
| Dev login | ✅ Built | signInWithPassword with admin@kitchen.local |
| Household scoping | ✅ Built | Hardcoded single household |
| Multi-household | ❌ Not built | Design needed |
| Invite flow | ❌ Not built | For adding household members |
| Role-based access | ❌ Not built | Schema exists, not enforced |

---

## Open Questions

### OQ-AUTH-01: Multi-Household Support
When do we need multiple households? What's the UX for creating/joining a household?

### OQ-AUTH-02: Invite Flow
How do users invite family members? Email invite? Share code? QR code?

### OQ-AUTH-03: Role Enforcement
Should viewers be blocked from editing? Or is everyone an editor in a household context?
