# Development TODO: Phased MVP Development

## Table of Contents

- [Purpose](#purpose)
- [Phase 0: Markdown-Driven MVP (Weeks 0-1)](#phase-0-markdown-driven-mvp-weeks-0-1)
- [Phase 1: The Bare-Bones MVP (Weeks 1-3)](#phase-1-the-bare-bones-mvp-weeks-1-3)
- [Phase 2: The "I Can Actually Cook With This" MVP (Weeks 4-6)](#phase-2-the-i-can-actually-cook-with-this-mvp-weeks-4-6)
- [Phase 3: Multi-User & Realtime (Weeks 7-9)](#phase-3-multi-user--realtime-weeks-7-9)
- [Phase 4: V1 Polish & Future-Proofing (Weeks 10-12)](#phase-4-v1-polish--future-proofing-weeks-10-12)

## Purpose

This to-do list is aligned with the [Phased Development Plan](project-phases.md). It breaks down the work into actionable items for each phase, with a focus on getting to a usable product as quickly as possible.

---

## Phase 0: Markdown-Driven MVP (Weeks 0-1)

**Goal**: A conversational, markdown-based workflow to simulate and refine the meal planning process.

- pending: **Conversational Flow Setup**
  - pending: Create a new directory `phase0_flow/`.
  - pending: Create templates for the conversational flow within `phase0_flow/`.
- pending: **Example Generation**
  - pending: Walk through a full conversational example in the `phase0_flow/plans/` directory.

---

## Phase 1: The Bare-Bones MVP (Weeks 1-3)

**Goal**: A single-user, web-based app that can generate a meal plan and shopping list.

- pending: **Project Setup**
  - pending: Create `Procfile.dev` for Overmind. (Decision needed: [decisions/phase-4/procfile-dev.md](decisions/phase-4/procfile-dev.md))
  - pending: Basic FastAPI backend structure.
  - pending: Basic React frontend structure.
  - pending: Initialize local Supabase project.
- pending: **Core Logic**
  - pending: Implement simple meal plan generation logic (no LLM).
  - pending: Create initial data models in Supabase. (Decision needed: [decisions/phase-4/data-models-consolidation.md](decisions/phase-4/data-models-consolidation.md))
  - pending: Create basic API endpoints. (Decision needed: [decisions/phase-4/api-endpoint-sketches.md](decisions/phase-4/api-endpoint-sketches.md))
- pending: **Functional UI**
  - pending: Create a simple React component to trigger meal plan generation.
  - pending: Display the meal plan and shopping list as plain text.

---

## Phase 2: The "I Can Actually Cook With This" MVP (Weeks 4-6)

**Goal**: Integrate inventory tracking and LLM suggestions.

- pending: **Inventory**
  - pending: Implement the inventory verification flow. (Decision needed: [decisions/phase-1/meal-planning-verification.md](decisions/phase-1/meal-planning-verification.md))
  - pending: Build the UI for the categorical checklist.
  - pending: Update backend logic to adjust the shopping list based on inventory.
- pending: **LLM Integration**
  - pending: Integrate OpenAI/Ollama for recipe suggestions.
  - pending: Implement the approved LLM prompts.
  - pending: Create a fallback mechanism for when the LLM is unavailable.
- pending: **PWA & Offline**
  - pending: Configure the app as a PWA with a service worker.
  - pending: Implement basic offline support for viewing the shopping list. (Decision needed: [decisions/phase-3/offline-sync-mechanisms.md](decisions/phase-3/offline-sync-mechanisms.md))

---

## Phase 3: Multi-User & Realtime (Weeks 7-9)

**Goal**: Add collaborative features.

- pending: **Auth & Presence**
  - pending: Implement Google Social Login via Supabase Auth.
  - pending: Add presence indicators to the UI.
- pending: **Realtime Sync**
  - pending: Implement realtime sync for shopping lists using Supabase channels.
  - pending: Test with multiple simulated users.
- pending: **Conflict Resolution**
  - pending: Implement Last-Write-Wins for conflict resolution.
  - pending: Add UI cues to show collaborators' changes.

---

## Phase 4: V1 Polish & Future-Proofing (Weeks 10-12)

**Goal**: Refine UI/UX and solidify testing.

- pending: **UI/UX Polish**
  - pending: Refine the categorical UI for shopping lists. (Decision needed: [decisions/phase-1/ui-categorical-shopping.md](decisions/phase-1/ui-categorical-shopping.md))
  - pending: Improve mobile-first design and accessibility.
- pending: **Testing**
  - pending: Implement the full testing strategy (Unit, Integration, E2E). (Decision needed: [decisions/phase-4/testing-strategy-outline.md](decisions/phase-4/testing-strategy-outline.md))
  - pending: Set up CI/CD pipeline with GitHub Actions.
- pending: **Deployment**
  - pending: Deploy the application to the self-hosted Raspberry Pi.
  - pending: Document the entire deployment process.

## Change Log

- 2025-09-19: Cleaned up to follow markdown documentation format, converting checklists to status-prefixed bullets and adding changelog.
