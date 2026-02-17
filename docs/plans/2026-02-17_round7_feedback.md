# RFC: Round 7 — User Feedback Implementation

**Date**: 2026-02-17
**Status**: Approved (user-driven feedback)

## Summary

Implement 15 changes based on direct user manual QA feedback. Prioritized by impact and dependency.

## Changes

### Group A: Quick Fixes (no dependencies)

1. **AUTH-FIX**: Google login dev bypass doesn't persist — `router.replace('/(app)')` without setting a session means `getSession()` returns null on refresh. Fix: create a dev session or skip auth check in dev mode.

2. **SETTINGS-PHASE**: Remove version/phase text from settings page (lines 128-134).

3. **VOICE-BTN**: Remove voice input button from shopping list (lines 278-287).

4. **CURSOR**: Add `cursor: pointer` to all interactive cards/buttons for desktop. HubCard and all Card components with `onPress`.

5. **PREP-BUG**: Fix "0" appearing after "10 min prep" — the `&&` check treats `0` as falsy for `cook_time_minutes`, showing `0` as the raw value. Fix: use explicit null/undefined checks.

6. **PLANNER-PAST**: Don't allow navigating to past weeks. Disable back button when `weekOffset <= 0`.

### Group B: UI Replacements

7. **CONFIRM-MODAL**: Replace `window.confirm()` with custom Tamagui Dialog in PantryItemCard and recipe detail delete.

8. **RECIPE-SOURCES**: Remove manual recipe creation. Replace FAB action sheet with two options: "Chat with AI" (conversation) and keep URL import. Remove `recipes/new.tsx` route.

9. **RECIPE-EMPTY**: Update empty state text to reflect new recipe sources.

### Group C: Desktop Polish

10. **DESKTOP-PASS**: Add max-width containers, proper spacing, hover states, cursor:pointer throughout. Make app usable on desktop.

### Group D: Cooking Mode Parking Lot

11. **COOK-DISABLE**: Remove cooking mode navigation. Remove "Start Cooking" buttons. Keep recipe detail but remove cook route entry points.

### Group E: Planner UX Simplification

12. **PLANNER-UX**: Simplify planner — remove confusing wizard FAB, clarify buttons, make linear flow obvious.

## Out of Scope (Noted for Future)

- Pantry "staples" redesign (needs deeper research)
- Shopping autocomplete with item profiles
- These are tracked as open questions.

## Open Questions

See OPEN_QUESTIONS.md
