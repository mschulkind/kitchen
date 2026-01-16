# Manual Testing Session Log

**Date**: 2026-01-16
**Status**: In Progress

## 🧪 Testing Protocol (Draft for Skill)

*Standards and best practices discovered during this session.*

1.  **Philosophy**: **MVP over Prototype**. Avoid mocks where possible. Build real, persistent flows (e.g., real Auth, real DB data) to verify the actual product.
2.  **Environment Setup**:
    - Ensure `just up` (Backend) and `just web` (Frontend) are running.
    - For **Expo Go** (Physical Device): Run `EXPO_PUBLIC_SUPABASE_URL=http://<LAN_IP>:8000 npx expo start`. `localhost` will not work on the phone.
3.  **Logs Analysis**:
    - Backend logs are captured in `logs/backend.log`.
    - Frontend logs are captured in `logs/frontend.log`.
    - The Agent can parse these files to debug errors reported during manual testing.
4.  **Strict Mode Testing**:
    - Verify elements exist *before* interacting.
    - Use specific data attributes (`testID`) over generic text matching where possible.
5.  **Web First**:
    - Test logic and flows on **Web** (`http://localhost:8081` or `:8200`) first.
    - Use Mobile (Expo Go) only for native features (Camera, Haptics) or final layout polish. This allows the Agent to use Playwright/Logs for faster debugging.

## 🐛 Bugs Fixed (On-the-fly)

*Non-blocking bugs fixed immediately during the session.*

- **Planner Manual Entry**: The Planner previously only allowed "New Plan" (AI Generation). Implemented `planner/add.tsx` and updated the calendar to allow manual recipe selection for specific slots.
- **Import Error (Lucide Icons)**: Fixed a breaking bug where `planner/add.tsx` was incorrectly importing from `@tanstack/lucide-icons` instead of `@tamagui/lucide-icons`, causing a blank screen.
- **Auth Alignment (Google Only)**: Removed email/password signup and login. Implemented unified "Sign in with Google" flow to align with `phase-01-foundation.md` and the central development plan.

## NB / Design / Feature Request Backlog

*Items to implement in bulk at the end of the session.*

- **Auth Flow**: "Get Started" on Landing Page currently mocks a login. User wants to actually Create Account/Sign In immediately. Need to implement `login.tsx` / `signup.tsx` and wire up Supabase Auth.
