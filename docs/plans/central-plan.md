# Kitchen Project: Central Development Plan

## Overview

This is the central planning document for moving the Kitchen project from its current "Phase 0" (Markdown & Script-based workflow) to a fully functional, AI-integrated web and mobile application.

The core goal is to preserve the high-quality "Agent-driven" planning experience while reducing the friction of data entry (inventory management) and plan execution (shopping/cooking).

## Architecture & Tech Stack

To support the "Heavy AI" requirements (planning, vision) alongside "Realtime App" requirements (sync, lists), we will use a hybrid stack following **Clean Architecture** principles.

### 1. Frontend: Expo (React Native)
- **Role**: The UI layer. Handles user interactions, camera access, and offline sync.
- **Targets**: iOS, Android, Web (Responsive).
- **Key Libraries**:
    - `expo-router`: File-based routing.
    - `tanstack-query`: Server state management & caching.
    - `gluestack-ui` or `tamagui`: Universal UI components.
    - `zustand`: Client state management (minimal).

### 2. Backend: Supabase (Data Layer)
- **Role**: The Source of Truth.
- **PostgreSQL**: Relational data (Pantry, Recipes, Plans).
- **Auth**: User management & Row Level Security (RLS).
- **Storage**: Image hosting for Vision API.
- **Realtime**: WebSockets for instant list updates.

### 3. Backend: Python Service (The "Chef's Brain")
- **Role**: The Intelligence Layer. Handles logic that requires heavy computation or LLM interaction.
- **Framework**: **FastAPI** (Async, Typed).
- **Deployment**: Containerized (Docker) on Render/Railway/Fly.io.
- **Responsibilities**:
    - **Vision Processing**: Image -> JSON inventory.
    - **Planning Agent**: The "Phase 0" logic (Request -> Plan).
    - **Scraping**: Fetching and parsing recipes.
- **Design Pattern**:
    - **Dependency Injection**: Services injected into Routes.
    - **Pydantic Models**: Strict data validation sharing types with Frontend (via codegen or spec).

---

## Implementation Roadmap

The project is divided into 4 sequential phases, prioritized by **value delivered to the user**.

### [Phase 1: The Foundation](phase-1-foundation.md)
**Focus**: Repository setup, Database Schema, and Migration.
- Establish the `src/mobile` and `src/api` monorepo.
- Define `pantry_items`, `recipes`, `households` tables.
- Migrate existing Markdown data to Supabase.
- **Deliverable**: A basic app that shows your current inventory (read-only or basic CRUD).

### [Phase 2: Visual Pantry (The "Magic")](phase-2-vision.md)
**Focus**: Reducing data entry friction.
- Implement Camera -> API -> LLM pipeline.
- Create the "Staging Area" UI for verifying scanned items.
- **Deliverable**: Snap a photo of a receipt or shelf, and see your digital pantry update.

### [Phase 3: The Planner Agent](phase-3-planning.md)
**Focus**: Porting the core value proposition.
- Migrate `main.py` logic to FastAPI endpoints.
- Build the "Plan Wizard" UI (Request -> Select -> Verify).
- **Deliverable**: Generate full meal plans and shopping lists within the app.

### [Phase 4: Execution & Realtime](phase-4-execution.md)
**Focus**: The in-store and in-kitchen experience.
- Realtime shopping list (multi-user).
- Offline capabilities.
- "5-Way" Recipe Views (Mise-en-place, Chef's Shorthand).
- **Deliverable**: A robust companion for the actual cooking process.

---

## Testing Strategy (TDD)

We strictly follow **Test-Driven Development**.

- **Backend (Python)**:
    - **Tool**: `pytest`.
    - **Unit Tests**: Mock LLM calls and DB calls. Test logic in isolation.
    - **Integration Tests**: Use a local Supabase instance (or Dockerized Postgres) to test API endpoints.
    - **Performance**: Tests must run in < 1s (exclude slow integration tests from default watch mode).

- **Frontend (TS)**:
    - **Tool**: `vitest` + `react-native-testing-library`.
    - **Unit**: Test components and hooks.
    - **Integration**: Test flows (Navigation, Form submission).

## Continuous Integration
- GitHub Actions will run on every push:
    - Lint (Ruff/ESLint).
    - Type Check (MyPy/TSC).
    - Test Suites.

## Open Decisions

- **LLM Cost Control**: Caching strategies for repeated queries?
- **Recipe Parser**: How to handle unstructured scraped text reliably? (Hybrid approach: keep raw text, try to parse JSON).
- **Offline Sync Conflict Resolution**: "Last Write Wins" for V1.