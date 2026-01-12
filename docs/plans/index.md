# Planning Documents Index 📋

**Last Updated**: January 11, 2026

## Table of Contents

- [Overview](#overview)
- [🚨 Start Here](#-start-here)
- [Documents](#documents)
- [Decision Logs](#decision-logs)
- [Navigation Notes](#navigation-notes)

This index serves as a central hub for all planning, outlines, specifications, and decisions in the Personalized Dinner & Shopping App project. It is maintained in the `docs/plans/` directory, which is git-tracked for version control.

## Overview

The planning phase focuses on establishing the foundational architecture, UX flows, and technical decisions to ensure the app is efficient, user-friendly, and aligned with the project brief. Key themes include intelligent meal planning, dynamic inventory tracking, intuitive verification, and optimized shopping lists, with a mobile-first approach. Phase 1 (core decisions) and Phase 1.5 (realtime multiuser) are complete; Phase 3 (infrastructure) and Phase 4 (implementation prep) finalized, ready for coding transition.

## 🚨 Start Here

### [open-questions.md](open-questions.md) ⭐ NEW

**Summary**: Unresolved decisions needing your input before development can proceed. Covers architecture choices, platform priorities, LLM strategy, and MVP scope. **Answer these first!**

### [central-plan.md](central-plan.md)

**Summary**: Master 10-phase roadmap with architecture overview and testing strategy. The single source of truth for what gets built when.

### [frontend-redesign.md](frontend-redesign.md) ⭐ NEW

**Summary**: Comprehensive spec for the transition to a Hub & Spoke navigation model, screens, and technical architecture for the mobile app.

### [frontend-tasks.md](frontend-tasks.md) ⭐ NEW

**Summary**: Detailed checklist for implementing the frontend redesign, broken down by phases.

### [e2e-test-plan.md](e2e-test-plan.md) ⭐ NEW

**Summary**: Strategy and status for "Strict Mode" Playwright tests across all phases.

## Documents

### [project-phases.md](project-phases.md)

**Summary**: A detailed, phased development plan focused on delivering a usable MVP as quickly as possible. Outlines a 12-week roadmap from a bare-bones MVP to a polished V1, with clear milestones, tasks, and phased decision-making.

### [planning-mode.md](planning-mode.md) **Summary**: Configuration spec for the new 'planning' mode, detailing capabilities for conversational spec-building, file updates, git workflows, and integration with the app's architecture

### [brief.md](brief.md)

**Summary**: The core project brief, outlining a **multi-platform strategy** for a private app targeting both a desktop web app (for Linux testing) and a native Android app via a shared codebase with `react-native-web`.
24 |
25 | ### [design-system.md](design-system.md)
26 | **Summary**: Comprehensive technical design including tech stack (Supabase DB/auth, React Native/Expo frontend, FastAPI backend), data models (PantryItem, ShoppingListItem, Recipe, MealPlan, Substitutions with Pydantic schemas), LLM integration (prompt templates for personalization), ingredient optimization algorithm, collaboration architecture (realtime, presence, conflicts, notifications), API endpoint sketches, testing strategy (TDD pyramid, 80% coverage), and offline handling. Updated for Phase 4 completion.

### [ux-flow.md](ux-flow.md)

**Summary**: Detailed user experience flows for primary (meal plan → verification → shopping) and multiuser scenarios, with text wireframes, interactions (drag/swipe for lists, modals for verification), Mermaid diagrams (verification sequence, shopping interactions), accessibility notes (ARIA, touch targets), and mobile considerations (gestures, offline UX). Refined categorical UI and verification flow.

### [hosting.md](hosting.md)

**Summary**: Hosting strategy with primary self-hosted Raspberry Pi (Docker Compose for frontend/backend/Supabase), local dev setup (Overmind with Procfile.dev for multi-service runs), cloud alternatives (Vercel/Heroku), PWA deployment, CI/CD (GitHub Actions), and offline sync mechanisms (IndexedDB queue, optimistic updates, LWW resolution). Phase 3 complete.

### [development-todo.md](development-todo.md)

**Summary**: Ordered checklist for planning phases (0-4), now fully completed: Core decisions (tech stack, DB/auth), design foundations (optimization algorithm), realtime multiuser (integration, auth, conflicts, notifications, testing), UX refinements (shopping lists, verification flow), infrastructure (hosting/offline), and implementation prep (Procfile.dev, models, API sketches, testing). Ready for development transition.

### [../docs/db-research.md](../docs/db-research.md)

**Summary**: Research and recommendations for database options tailored to the app's offline-first PWA needs, evaluating SQLite, IndexedDB, PouchDB, Supabase, and PostgreSQL; recommends Supabase for realtime/multiuser with local caching.

## Decision Logs

This section contains detailed documentation for key technical and architectural decisions.

- [**Phase 1: Ingredient Optimization Algorithm**](decisions/phase-1/ingredient-optimization.md): Heuristic scoring for pantry matching/substitutions, with nutritional categories, pseudocode, examples, and integration into data models.

- [**Phase 1.5: Realtime Integration**](decisions/phase-1.5/realtime-integration.md): Supabase channels/subscriptions for shopping_lists, meal_plans, inventory_items with filters, optimistic updates (React Query), IndexedDB queuing, Expo background sync, error handling (reconnects).

- [**Phase 1.5: Auth and Presence**](decisions/phase-1.5/auth-and-presence.md): Supabase Auth (email/social), presence tracking with user metadata/avatars, RLS policies for all models (shopping_lists, inventory_items, meal_plans), invite flows, mobile UX (large buttons, alerts).

- [**Phase 1.5: Conflict Resolution and Offline**](decisions/phase-1.5/conflict-resolution-and-offline.md): LWW with timestamps, optimistic rollback, Zustand queue with AsyncStorage/Expo, sync manager (NetInfo), TDD examples for unit/integration (sync handlers, multiuser conflicts).

- [**Phase 1.5: Notifications**](decisions/phase-1.5/notifications.md): Supabase Edge Functions triggered by DB changes (insert/update/delete on key tables), Expo push with multi-user iteration (memberships), deep links, client listeners for foreground/background, UX alerts, TDD for end-to-end flow.

- [**Phase 1.5: Multiuser Testing**](decisions/phase-1.5/multiuser-testing.md): Testing pyramid (unit/integration/E2E with Vitest/RTL/Detox), scenarios for invites/edits/conflicts/offline/notifications, pseudocode examples, coverage 80%+, device matrix, manual plan.

## Navigation Notes

- Use relative links for easy navigation within the `plans/` directory.
- As new documents are added or updated, this index will be revised to include summaries and links.
- For temporary research or data dumps, refer to the [docs/index.md](../docs/index.md).

## TODOs

- Planning phase complete; transition to implementation (code mode).
- Archive completed decisions if needed; review for v1.0 post-coding.
