# Development TODO: The 11-Phase Roadmap 📋

> 🧭 **Navigation**: [Central Plan](central-plan.md) | [Frontend Tasks](frontend-tasks.md) | [E2E Test Plan](e2e-test-plan.md)

This document tracks the high-level execution of the 11-Phase Roadmap.

## Phase 1: Foundation & Inventory (Essential) 🔴

- [x] **Monorepo Setup**: FastAPI + Expo + Docker.
- [x] **Database Schema**: Users, Households, Pantry Items.
- [x] **Backend API**: CRUD endpoints for Pantry.
- [x] **Frontend UI**: Inventory List, Add/Edit Forms.
- [x] **E2E Tests**: Inventory management flows.

## Phase 2: Recipe Engine (Essential) 🔴

- [x] **Scraper**: Firecrawl integration for recipe URL ingestion.
- [x] **Parser**: Ingredient string to structured JSON logic.
- [x] **Data Models**: Recipe, Ingredient, Instruction tables.
- [x] **Frontend UI**: Recipe List, Manual Entry, Import Dialog.
- [x] **E2E Tests**: Recipe creation and import flows.

## Phase 3: Delta Engine (Essential) 🔴

- [x] **Comparator Logic**: Recipe Ingredients vs. Pantry Stock algorithm.
- [x] **Backend API**: `check-stock` endpoint.
- [x] **Frontend UI**: "Check Stock" modal with "Missing" vs "Have" sections.
- [x] **E2E Tests**: Lazy discovery flow ("I have this").

## Phase 4: Visual Pantry (Nice-to-Have) 🟡

- [x] **Vision Agent**: Gemini 1.5 Flash integration for image analysis.
- [x] **Backend API**: Image upload and processing endpoints.
- [x] **Frontend UI**: Camera capture and "Staging Area" for verification.
- [x] **E2E Tests**: Scan flow mock tests.

## Phase 5: Planner Core (Essential) 🔴

- [x] **Algorithm**: Inventory-aware plan generation.
- [x] **Backend API**: Plan generation endpoints.
- [x] **Frontend UI**: Week Calendar View, Generator Form.
- [x] **E2E Tests**: Plan creation and viewing.

## Phase 6: Slot Machine (Nice-to-Have) 🟡

- [x] **Refiner Logic**: Lock/Spin mechanics.
- [x] **Backend API**: Slot update endpoints.
- [x] **Frontend UI**: Lock icons, Spin buttons (integrated in Planner).
- [x] **E2E Tests**: Interaction tests.

## Phase 7: Shopping List (Essential) 🔴

- [x] **Aggregator**: Plan + Ad-hoc items -> Shopping List.
- [x] **Realtime**: Supabase subscriptions for sync.
- [x] **Frontend UI**: Checklist with smart sorting.
- [x] **E2E Tests**: Add, check, clear completed flows.

## Phase 8: Store Intelligence (Defer) 🟢

- [x] **Backend Models**: Stores, Aisles, Mappings.
- [ ] **Scraper**: Shaws/Generic aisle data fetcher.
- [ ] **Sorter Logic**: Aisle-based sorting algorithm.
- [ ] **Frontend UI**: Store selector, Aisle headers.

## Phase 9: Voice Integration (Defer) 🟢

- [x] **Webhook API**: `POST /hooks/add-item` endpoint.
- [x] **NLP**: Command parser.
- [ ] **Docs**: Setup guide for Google Home (Completed).
- [x] **Frontend UI**: Scoped out (External only).

## Phase 10: Chef's Companion (Nice-to-Have) 🟡

- [x] **Backend API**: Recipe step tracking.
- [x] **Frontend UI**: "Cooking Mode" (Large text, Wake lock).
- [ ] **Inventory Decrement**: "Mark Cooked" logic.

## Phase 11: Recipe Imagery (Nice-to-Have) 🟡

- [ ] **Backend API**: Generation endpoint (Nano Banana).
- [ ] **Worker**: Background image generation task.
- [ ] **Frontend UI**: Display generated images.
