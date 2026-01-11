# Kitchen Project: Central Development Plan 🍳

**Last Updated**: January 11, 2026  
**Current Status**: Phase 0 (Workflow Validation) ✅ | Phase 1 (Foundation) 🚧 Pending

## Overview

This is the central planning document for moving the Kitchen project from its current "Phase 0" (Markdown & Script-based workflow) to a fully functional, AI-integrated web and mobile application.

> 📋 **See Also**: [Open Questions](open-questions.md) for decisions needing your input

The core goal is to preserve the high-quality "Agent-driven" planning experience while reducing the friction of data entry and providing **precise, reliable** execution tools.

## Architecture & Tech Stack

To support the "Heavy AI" requirements (planning, vision) alongside "Realtime App" requirements (sync, lists), we will use a hybrid stack following **Clean Architecture** principles, deployed as a self-hosted Docker stack.

### 1. Frontend: Expo (React Native Web)

- **Role**: The UI layer.
- **Priority**: **Web First** (PWA), then Android.
- **Key Libraries**:
  - `expo-router`: File-based routing.
  - `tanstack-query`: Server state management & caching.
  - `tamagui`: Performance-focused universal UI components (Native + Web).
  - `zustand`: Client state management (minimal).

### 2. Backend: Supabase (Self-Hosted via Docker)

- **Role**: The Source of Truth.
- **Components**: PostgreSQL, GoTrue (Auth), Realtime (WebSockets), Storage.
- **Host**: Synology NAS (Docker Compose).
- **Core Requirement**: **Realtime Multi-User Sync**.
  - **All** shared views (Inventory, Meal Plans, Shopping Lists) must use Supabase Realtime subscriptions.
  - Updates made by User A (e.g., checking an item, changing a plan slot) must reflect instantly on User B's device.

### 3. Backend: Python Service (The "Chef's Brain")

- **Role**: The Intelligence Layer.
- **Framework**: **FastAPI** (Async, Typed).
- **LLM Strategy**: **Multi-Provider Adapter**.
  - Flexible interface supporting **Gemini**, **Claude**, and **OpenAI**.
  - Configurable per feature (e.g., Vision -> Gemini, Planning -> Claude).
- **Responsibilities**:
  - **Vision Processing**: Image -> JSON inventory.
  - **Planning Agent**: The "Phase 0" logic.
  - **Scraping**: Fetching and parsing recipes.

---

## 10-Phase Implementation Roadmap

The project is broken down into granular, testable phases. Each phase delivers a usable piece of functionality.

### Phase Overview Table

| Phase | Name | Priority | Status | Est. Effort |
|-------|------|----------|--------|-------------|
| 1 | [Foundation & Inventory](phase-01-foundation.md) | 🔴 Essential | 🚧 In Progress (1A ✅, 1B ✅, 1C 🚧) | 2-3 weeks |
| 2 | [Recipe Engine](phase-02-recipe-engine.md) | 🔴 Essential | ✅ Complete | 2-3 weeks |
| 3 | [Delta Engine](phase-03-delta-engine.md) | 🔴 Essential | ✅ Complete | 2-3 weeks |
| 4 | [Visual Pantry](phase-04-vision.md) | 🟡 Nice-to-Have | ✅ Complete (Backend) | 1-2 weeks |
| 5 | [Planner Core](phase-05-planner-core.md) | 🔴 Essential | ✅ Complete (Backend) | 2-3 weeks |
| 6 | [Slot Machine](phase-06-planner-advanced.md) | 🟡 Nice-to-Have | ✅ Complete (Backend) | 1-2 weeks |
| 7 | [Shopping List](phase-07-shopping-list.md) | 🔴 Essential | ✅ Complete (Backend) | 1-2 weeks |
| 8 | [Store Intelligence](phase-08-store-intelligence.md) | 🟢 Defer | ✅ Complete (Backend) | 1-2 weeks |
| 9 | [Voice Integration](phase-09-voice.md) | 🟢 Defer | ✅ Complete (Backend) | 1 week |
| 10 | [Chef's Companion](phase-10-cooking-companion.md) | 🟡 Nice-to-Have | ✅ Complete (Backend) | 1 week |

**MVP Target**: Phases 1, 2, 3, 5, 7 (~10-14 weeks)  
**Backend Status**: Phases 2-10 backend complete! 🎉

---

### [Phase 1: Foundation & Inventory CRUD](phase-01-foundation.md)

**Goal**: Get the app running and manually track stock.

- Monorepo setup (Expo + FastAPI).
- Supabase Schema: `users`, `households`, `pantry_items`.
- Basic UI: List, Add, Edit, Delete Pantry Items.

### [Phase 2: The Recipe Engine](phase-02-recipe-engine.md)

**Goal**: Reliable recipe data ingestion and **Unit Standardization**.

- Scraper logic (Firecrawl).
- **Ingredient Parser**: Converts "1 large onion" -> `{ item: "onion", qty: 1, unit: "count" }`.
- **Unit Registry**: A Python library (e.g., `pint`) to handle `cups` to `ml` conversions.

### [Phase 3: The "Delta" Engine (The Math)](phase-03-delta-engine.md)

**Goal**: Precise tracking of what is needed vs. what is owned.

- **The Comparator**: API endpoint that takes a Recipe + Inventory and outputs `MissingIngredients`.
- **Logic**: Handles fuzzy matching ("Kosher Salt" == "Salt") and unit conversion (Recipe needs "200g flour", Pantry has "1 kg").
- **Deliverable**: A "Can I Cook This?" checker.

### [Phase 4: Visual Pantry (Vision)](phase-04-vision.md)

**Goal**: Reduce data entry friction.

- Camera -> Supabase Storage -> Python Vision Agent.
- "Staging Area" UI for verifying scanned items before committing to DB.

### [Phase 5: The "Adventure" Planner (Core)](phase-05-planner-core.md)

**Goal**: The "Choose Your Own Adventure" Logic.

- Algorithm: Inventory-aware recipe search.
- "The Pitch": AI generates 3 thematic paths (e.g., "Efficiency", "Global Tour").
- Basic Selection UI.

### [Phase 6: The "Slot Machine" (Refinement)](phase-06-planner-advanced.md)

**Goal**: Granular control over the plan.

- UI: Locking specific meals or components (Main vs Side).
- "Spin" logic with text directives ("Make it spicy").

### [Phase 7: Shopping List Core](phase-07-shopping-list.md)

**Goal**: A functional, syncable list.

- Aggregation: Plan -> Delta Engine -> Shopping List.
- Manual "Add Item".
- Realtime Sync (Supabase) for multi-user checking.

### [Phase 8: Store Intelligence (Shaws)](phase-08-store-intelligence.md)

**Goal**: Optimized traversal of the local supermarket.

- **Scraper**: Fetch product data and **Aisle Locations** from Shaws (or generic grocer API).
- **Sorter**: Auto-sort the shopping list by Aisle (e.g., "Aisle 4: Baking" before "Aisle 12: Frozen").

### [Phase 9: Voice Assistant Integration](phase-09-voice.md)

**Goal**: Hands-free kitchen management.

- **Webhook**: Endpoint accepting text from Google Assistant / IFTTT.
- Logic: "Add milk" -> Parses "milk" -> Adds to Shopping List.

### [Phase 10: The Chef's Companion](phase-10-cooking-companion.md)

**Goal**: Cooking execution.

- "Copy for AI" Prompt Generator (Context Export).
- "5-Way" Recipe Views (Mise-en-place, etc).
- Consumption: "Mark as Cooked" decrements inventory.

---

## Testing Strategy 🧪

- **Critical Path**: The **Delta Engine** (Phase 3) requires the highest test coverage (Unit + Property-based testing) because "messing this up is very annoying."
- **TDD**: Write the "Recipe needs 500g, have 1lb" test case *before* writing the conversion logic.
- **Coverage Target**: 80%+ on Phases 2-3 (Recipe Engine, Delta Engine)
- **Test Framework**: `pytest` (backend) + `vitest` (frontend) + `Maestro` (E2E mobile)
