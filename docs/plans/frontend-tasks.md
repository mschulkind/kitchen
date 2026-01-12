# Frontend Implementation Tasks 📝

> 🧭 **Navigation**: [Redesign Plan](frontend-redesign.md) | [E2E Test Plan](e2e-test-plan.md) | [Central Plan](central-plan.md) | [Planning Index](index.md)

This task list tracks the execution of the [Frontend Redesign Plan](./frontend-redesign.md).

## 1. Setup & Navigation Redesign (Phase 2A)

### Router Refactor

- [ ] **Directory Structure**: Create `src/mobile/app/(auth)` and `src/mobile/app/(app)`.
- [ ] **Root Layout**: Update `src/mobile/app/_layout.tsx` to handle Auth state and switch between stacks.
- [ ] **Auth Stack**: Create `src/mobile/app/(auth)/_layout.tsx` (Stack).
- [ ] **App Stack**: Create `src/mobile/app/(app)/_layout.tsx` (Stack).
- [ ] **Cleanup**: Delete `src/mobile/app/(tabs)`.

### Core Screens

- [ ] **Landing Page**: Implement `src/mobile/app/(auth)/landing.tsx`
  - [ ] Hero Section
  - [ ] Sign In Button (Mock auth for now if needed)
- [ ] **The Hub**: Implement `src/mobile/app/(app)/index.tsx`
  - [ ] Bento Grid Layout
  - [ ] Navigation Links to `recipes`, `pantry`, `shopping`, `planner`.

### Core Components

- [ ] **Screen Wrapper**: Create `src/mobile/components/Layout/Screen.tsx`.
- [ ] **Hub Card**: Create `src/mobile/components/Modules/HubCard.tsx`.

## 2. Test Hardening (Phase 2B)

- [ ] **Recipes E2E**: Rewrite `tests/web/e2e/phase2-recipes.spec.ts`.
  - [ ] Remove `|| true`
  - [ ] Ensure strict element selection
  - [ ] Add test for Manual Entry flow
  - [ ] Add test for Import URL flow
- [ ] **Delta E2E**: Rewrite `tests/web/e2e/phase3-delta.spec.ts` (Strict Mode).
- [ ] **Vision E2E**: Rewrite `tests/web/e2e/phase4-vision.spec.ts` (Strict Mode).
- [ ] **Planner E2E**: Rewrite `tests/web/e2e/phase5-planner.spec.ts` (Strict Mode).
- [ ] **Refiner E2E**: Create `tests/web/e2e/phase6-refiner.spec.ts` (Strict Mode).
- [ ] **Shopping E2E**: Rewrite `tests/web/e2e/phase7-shopping.spec.ts` (Strict Mode).

## 3. Recipe Feature (Phase 2C)

### List & Entry

- [ ] **Recipe List**: Implement `src/mobile/app/(app)/recipes/index.tsx`.
  - [ ] Search Bar
  - [ ] Recipe Card Component
- [ ] **Import Flow**:
  - [ ] Create `ImportRecipeDialog` component.
  - [ ] Implement URL pasting and API trigger.
- [ ] **Manual Entry**: Implement `src/mobile/app/(app)/recipes/new.tsx`.
  - [ ] Dynamic Ingredients Input
  - [ ] Dynamic Steps Input

### Detail & Cooking

- [ ] **Detail View**: Implement `src/mobile/app/(app)/recipes/[id].tsx`.
  - [ ] Parallax Header
  - [ ] Ingredient/Step Lists
- [ ] **Cooking Mode**: Implement `src/mobile/app/(app)/recipes/[id]/cook.tsx`.
  - [ ] Wake Lock integration
  - [ ] Large Step Carousel
- [ ] **Stock Check**: Implement `src/mobile/app/(app)/recipes/[id]/check-stock.tsx`.

## 4. Other Modules

- [ ] **Planner Grid**: Implement `src/mobile/app/(app)/planner/index.tsx`.
- [ ] **Planner Generator**: Implement `src/mobile/app/(app)/planner/new.tsx`.
- [ ] **Slot Machine**: Implement Lock/Spin UI in `planner/index.tsx`.
- [ ] **Vision Staging**: Implement `src/mobile/app/(app)/inventory/scan-result.tsx`.
- [ ] **Shopping List**: Implement `src/mobile/app/(app)/shopping/index.tsx` (with Aisle Groups).
