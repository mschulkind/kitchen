# Frontend Implementation Tasks 📝

> 🧭 **Navigation**: [Redesign Plan](frontend-redesign.md) | [E2E Test Plan](e2e-test-plan.md) | [Central Plan](central-plan.md) | [Planning Index](index.md)

This task list tracks the execution of the [Frontend Redesign Plan](./frontend-redesign.md).

## 1. Setup & Navigation Redesign (Phase 2A)

### Router Refactor

- [x] **Directory Structure**: Create `src/mobile/app/(auth)` and `src/mobile/app/(app)`.
- [x] **Root Layout**: Update `src/mobile/app/_layout.tsx` to handle Auth state and switch between stacks.
- [x] **Auth Stack**: Create `src/mobile/app/(auth)/_layout.tsx` (Stack).
- [x] **App Stack**: Create `src/mobile/app/(app)/_layout.tsx` (Stack).
- [x] **Cleanup**: Delete `src/mobile/app/(tabs)`.

### Core Screens

- [x] **Landing Page**: Implement `src/mobile/app/(auth)/landing.tsx`
  - [x] Hero Section
  - [x] Sign In Button (Mock auth for now if needed)
- [x] **The Hub**: Implement `src/mobile/app/(app)/index.tsx`
  - [x] Bento Grid Layout
  - [x] Navigation Links to `recipes`, `pantry`, `shopping`, `planner`.

### Core Components

- [x] **Screen Wrapper**: Create `src/mobile/components/Layout/Screen.tsx`.
- [x] **Hub Card**: Create `src/mobile/components/Modules/HubCard.tsx`.

## 2. Test Hardening (Phase 2B)

- [x] **Recipes E2E**: Rewrite `tests/web/e2e/phase2-recipes.spec.ts`.
  - [x] Remove `|| true`
  - [x] Ensure strict element selection
  - [x] Add test for Manual Entry flow
  - [x] Add test for Import URL flow
- [ ] **Delta E2E**: Rewrite `tests/web/e2e/phase3-delta.spec.ts` (Strict Mode).
- [ ] **Vision E2E**: Rewrite `tests/web/e2e/phase4-vision.spec.ts` (Strict Mode).
- [x] **Planner E2E**: Rewrite `tests/web/e2e/phase5-planner.spec.ts` (Strict Mode).
- [ ] **Refiner E2E**: Create `tests/web/e2e/phase6-refiner.spec.ts` (Strict Mode).
- [ ] **Shopping E2E**: Rewrite `tests/web/e2e/phase7-shopping.spec.ts` (Strict Mode).

## 3. Recipe Feature (Phase 2C)

### List & Entry

- [x] **Recipe List**: Implement `src/mobile/app/(app)/recipes/index.tsx`.
  - [x] Search Bar
  - [x] Recipe Card Component
- [x] **Import Flow**:
  - [x] Create `ImportRecipeDialog` component.
  - [x] Implement URL pasting and API trigger.
- [x] **Manual Entry**: Implement `src/mobile/app/(app)/recipes/new.tsx`.
  - [x] Dynamic Ingredients Input
  - [x] Dynamic Steps Input

### Detail & Cooking

- [x] **Detail View**: Implement `src/mobile/app/(app)/recipes/[id].tsx`.
  - [x] Parallax Header
  - [x] Ingredient/Step Lists
- [x] **Cooking Mode**: Implement `src/mobile/app/(app)/recipes/[id]/cook.tsx`.
  - [x] Wake Lock integration
  - [x] Large Step Carousel
- [x] **Stock Check**: Implement `src/mobile/app/(app)/recipes/[id]/check-stock.tsx`.

## 4. Other Modules

- [x] **Planner Grid**: Implement `src/mobile/app/(app)/planner/index.tsx`.
- [x] **Planner Generator**: Implement `src/mobile/app/(app)/planner/new.tsx`.
- [x] **Slot Machine**: Implement Lock/Spin UI in `planner/index.tsx`.
- [ ] **Vision Staging**: Implement `src/mobile/app/(app)/inventory/scan-result.tsx`.
- [ ] **Shopping List**: Implement `src/mobile/app/(app)/shopping/index.tsx` (with Aisle Groups).

## 5. Responsive & Polish (Phase 2D)

- [ ] **Desktop Layout Audit**: Verify all screens on wide viewport (>1024px).
- [ ] **Hub Adaptation**: Ensure Grid widgets reflow correctly (2-3 columns).
- [ ] **Recipe List Adaptation**: Switch to Grid or Multi-column list on desktop.
- [ ] **Form Constraints**: Wrap forms (Planner, Recipes) in `maxWidth` containers to prevent stretching.
- [ ] **Navigation Check**: Ensure back buttons/navigation works without physical hardware buttons.
