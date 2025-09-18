# Development TODO: Phased MVP Development

## Table of Contents
- [Overview](#overview)
- [Phase 0: Markdown-Driven MVP (Weeks 0-1)](#phase-0-markdown-driven-mvp-weeks-0-1)
- [Phase 1: The Bare-Bones MVP (Weeks 1-3)](#phase-1-the-bare-bones-mvp-weeks-1-3)
- [Phase 2: The "I Can Actually Cook With This" MVP (Weeks 4-6)](#phase-2-the-i-can-actually-cook-with-this-mvp-weeks-4-6)
- [Phase 3: Multi-User &amp; Realtime (Weeks 7-9)](#phase-3-multi-user--realtime-weeks-7-9)
- [Phase 4: V1 Polish &amp; Future-Proofing (Weeks 10-12)](#phase-4-v1-polish--future-proofing-weeks-10-12)

## Overview
This to-do list is aligned with the [Phased Development Plan](project-phases.md). It breaks down the work into actionable items for each phase, with a focus on getting to a usable product as quickly as possible.

---

## Phase 0: Markdown-Driven MVP (Weeks 0-1)
**Goal**: A conversational, markdown-based workflow to simulate and refine the meal planning process.

- [ ] **Conversational Flow Setup**
    - [ ] Create a new directory `phase0_flow/`.
    - [ ] Create templates for the conversational flow within `phase0_flow/`.
- [ ] **Example Generation**
    - [ ] Walk through a full conversational example in the `phase0_flow/plans/` directory.

---

## Phase 1: The Bare-Bones MVP (Weeks 1-3)
**Goal**: A single-user, web-based app that can generate a meal plan and shopping list.

- [ ] **Project Setup**
    - [ ] Create `Procfile.dev` for Overmind. (Decision needed: [`decisions/phase-4/procfile-dev.md`](decisions/phase-4/procfile-dev.md))
    - [ ] Basic FastAPI backend structure.
    - [ ] Basic React frontend structure.
    - [ ] Initialize local Supabase project.
- [ ] **Core Logic**
    - [ ] Implement simple meal plan generation logic (no LLM).
    - [ ] Create initial data models in Supabase. (Decision needed: [`decisions/phase-4/data-models-consolidation.md`](decisions/phase-4/data-models-consolidation.md))
    - [ ] Create basic API endpoints. (Decision needed: [`decisions/phase-4/api-endpoint-sketches.md`](decisions/phase-4/api-endpoint-sketches.md))
- [ ] **Functional UI**
    - [ ] Create a simple React component to trigger meal plan generation.
    - [ ] Display the meal plan and shopping list as plain text.

---

## Phase 2: The "I Can Actually Cook With This" MVP (Weeks 4-6)
**Goal**: Integrate inventory tracking and LLM suggestions.

- [ ] **Inventory**
    - [ ] Implement the inventory verification flow. (Decision needed: [`decisions/phase-1/meal-planning-verification.md`](decisions/phase-1/meal-planning-verification.md))
    - [ ] Build the UI for the categorical checklist.
    - [ ] Update backend logic to adjust the shopping list based on inventory.
- [ ] **LLM Integration**
    - [ ] Integrate OpenAI/Ollama for recipe suggestions.
    - [ ] Implement the approved LLM prompts.
    - [ ] Create a fallback mechanism for when the LLM is unavailable.
- [ ] **PWA & Offline**
    - [ ] Configure the app as a PWA with a service worker.
    - [ ] Implement basic offline support for viewing the shopping list. (Decision needed: [`decisions/phase-3/offline-sync-mechanisms.md`](decisions/phase-3/offline-sync-mechanisms.md))

---

## Phase 3: Multi-User &amp; Realtime (Weeks 7-9)
**Goal**: Add collaborative features.

- [ ] **Auth & Presence**
    - [ ] Implement Google Social Login via Supabase Auth.
    - [ ] Add presence indicators to the UI.
- [ ] **Realtime Sync**
    - [ ] Implement realtime sync for shopping lists using Supabase channels.
    - [ ] Test with multiple simulated users.
- [ ] **Conflict Resolution**
    - [ ] Implement Last-Write-Wins for conflict resolution.
    - [ ] Add UI cues to show collaborators' changes.

---

## Phase 4: V1 Polish &amp; Future-Proofing (Weeks 10-12)
**Goal**: Refine UI/UX and solidify testing.

- [ ] **UI/UX Polish**
    - [ ] Refine the categorical UI for shopping lists. (Decision needed: [`decisions/phase-1/ui-categorical-shopping.md`](decisions/phase-1/ui-categorical-shopping.md))
    - [ ] Improve mobile-first design and accessibility.
- [ ] **Testing**
    - [ ] Implement the full testing strategy (Unit, Integration, E2E). (Decision needed: [`decisions/phase-4/testing-strategy-outline.md`](decisions/phase-4/testing-strategy-outline.md))
    - [ ] Set up CI/CD pipeline with GitHub Actions.
- [ ] **Deployment**
    - [ ] Deploy the application to the self-hosted Raspberry Pi.
    - [ ] Document the entire deployment process.
