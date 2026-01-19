# Manual QA Session Log - Jan 19, 2026

## Session Details
- **Tester**: Agent (Guided QA)
- **Environment**: Local Dev (Linux)
- **Scope**: New User Experience (Landing -> Signup -> Initial Dashboard -> Pantry Add Item)

## Findings

### 1. OAuth Bypass & Login State
- **Status**: ✅ FIXED (via `devlogin`)
- **Observation**:
    - The "Sign in with Google" button on `/landing` provides a quick bypass but may result in an ephemeral/anonymous session that cannot write data.
    - **Resolution**: Used `/devlogin` with `admin@kitchen.local` (after seeding via `scripts/seed_dev_data.py`). This successfully authenticated as a real user ("Good Afternoon, Dev Admin").
    - **Action Item**: Standardize on using `/devlogin` for manual QA to ensure write permissions.

### 2. Pantry Item Persistence (BLOCKER)
- **Status**: 🔴 FAILED (Confirmed with Auth)
- **Steps**:
    1. Logged in as `admin@kitchen.local` via `/devlogin`.
    2. Navigated to Pantry (`/inventory`).
    3. Entered "Test Apple", selected "Fridge".
    4. Clicked "Save".
    5. **Result**: "Test Apple" did NOT appear in the list.
    6. **Reloaded Page**: List remains empty ("Your pantry is empty").
- **Diagnosis**: 
    - Even with a valid authenticated user (`admin@kitchen.local`), writes to `pantry_items` are failing or being silently ignored.
    - This strongly suggests a **Row Level Security (RLS)** policy issue (e.g., the user is not correctly linked to the household, or the `pantry_items` policy forbids inserts) or a **Database Schema** mismatch (frontend sending fields that don't match the DB).

## Next Steps
1.  **Investigate RLS Policies**: Check Supabase policies for `pantry_items` and `household_members`.
2.  **Debug Network Requests**: Inspect the network tab for the `POST /pantry_items` (or RPC call) to see the specific 40x or 500 error.
3.  **Check Household Linkage**: Ensure `admin@kitchen.local` actually has a `household_id` associated in the database.