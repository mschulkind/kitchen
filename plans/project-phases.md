# Phased Development Plan: From MVP to V1

## Table of Contents
- [Overview](#overview)
- [Guiding Principles](#guiding-principles)
- [Phase 0: Markdown-Driven MVP (Weeks 0-1)](#phase-0-markdown-driven-mvp-weeks-0-1)
- [Phase 1: The Bare-Bones MVP (Weeks 1-3)](#phase-1-the-bare-bones-mvp-weeks-1-3)
- [Phase 2: The "I Can Actually Cook With This" MVP (Weeks 4-6)](#phase-2-the-i-can-actually-cook-with-this-mvp-weeks-4-6)
- [Phase 3: Multi-User &amp; Realtime (Weeks 7-9)](#phase-3-multi-user--realtime-weeks-7-9)
- [Phase 4: V1 Polish &amp; Future-Proofing (Weeks 10-12)](#phase-4-v1-polish--future-proofing-weeks-10-12)
- [Phased Planning Decisions](#phased-planning-decisions)

## Overview
This document outlines a phased approach to developing the Personalized Dinner &amp; Shopping App. The goal is to deliver a usable Minimum Viable Product (MVP) as quickly as possible so you can start cooking with it, then iteratively add features. Each phase has a clear focus, dependencies, and a timeline.

## Guiding Principles
- **Speed to Value**: Get a working, cookable-from version of the app in your hands ASAP.
- **Manual First**: Test the core LLM value proposition through a markdown-based interface before writing any code.
- **Minimum Viable UX**: The initial UX will be rough but functional. We'll polish it in later phases.
- **Phased Decisions**: We'll make just-in-time decisions for each phase, avoiding over-planning.

---

## Phase 0: Markdown-Driven MVP (Weeks 0-1)
**Goal**: A conversational, markdown-based workflow to simulate and refine the meal planning process.
**Milestone**:
- **Week 0: Conversational Flow**: Create and test the full back-and-forth flow using the `phase0_flow/` directory, from request to final plan.

**Outcome of Phase 0**: You can collaboratively create a meal plan through a series of markdown files, proving the value and logic of the core LLM interaction before any code is written.

---

## Phase 1: The Bare-Bones MVP (Weeks 1-3)
**Goal**: A single-user, web-based app that can generate a meal plan and shopping list. The core logic will be in place, even if the UI is just buttons and text.

| Milestone | Key Tasks | Decisions to Make |
| :--- | :--- | :--- |
| **Week 1: Project Setup** | - Set up `Procfile.dev` for local dev. <br> - Basic FastAPI backend & React frontend. <br> - Supabase project setup (local). | - Finalize `Procfile.dev` content. <br> - Consolidate basic data models (`PantryItem`, `ShoppingListItem`). |
| **Week 2: Core Logic** | - Implement backend logic for meal plan generation (simple version, no LLM yet). <br> - Create basic data models in Supabase. <br> - Basic API endpoints for creating/viewing a meal plan. | - Finalize API endpoint sketches for core MVP. |
| **Week 3: Functional UI** | - "Ugly but functional" React UI to trigger meal plan generation. <br> - Display the generated meal plan and shopping list. | - N/A |

**Outcome of Phase 1**: You can run the app locally, click a button, and get a basic meal plan and shopping list. No inventory tracking, no LLM, no fancy UI.

---

## Phase 2: The "I Can Actually Cook With This" MVP (Weeks 4-6)
**Goal**: Integrate the core "smart" features: inventory tracking and LLM-powered suggestions. This makes the app genuinely useful for daily cooking.

| Milestone | Key Tasks | Decisions to Make |
| :--- | :--- | :--- |
| **Week 4: Inventory** | - Implement inventory verification flow. <br> - UI for categorical checklist. <br> - Backend logic to adjust shopping list based on inventory. | - Finalize meal planning verification flow. |
| **Week 5: LLM Integration** | - Integrate LLM for recipe suggestions. <br> - Use approved LLM prompts. <br> - Fallback for when LLM is unavailable. | - N/A (Decision already made) |
| **Week 6: PWA & Offline** | - Set up PWA with service worker. <br> - Basic offline support for viewing shopping list. | - Finalize offline sync mechanism. |

**Outcome of Phase 2**: The app is now a PWA, works offline for the shopping list, and generates smart meal plans based on your pantry. It's ready for real-world use.

---

## Phase 3: Multi-User &amp; Realtime (Weeks 7-9)
**Goal**: Add the collaborative features that make the app sharable.

| Milestone | Key Tasks | Decisions to Make |
| :--- | :--- | :--- |
| **Week 7: Auth & Presence** | - Implement Google Social Login. <br> - Add presence indicators to the UI. | - N/A (Decision already made) |
| **Week 8: Realtime Sync** | - Implement realtime sync for shopping lists. <br> - Set up Supabase channels. <br> - Test with multiple users. | - N/A (Decision already made) |
| **Week 9: Conflict Resolution** | - Implement Last-Write-Wins for conflicts. <br> - UI for showing collaborators' changes. | - N/A (Decision already made) |

**Outcome of Phase 3**: You can now share your shopping list with someone else, and see their updates in real-time.

---

## Phase 4: V1 Polish &amp; Future-Proofing (Weeks 10-12)
**Goal**: Refine the UI/UX, solidify the testing strategy, and prepare for long-term maintenance.

| Milestone | Key Tasks | Decisions to Make |
| :--- | :--- | :--- |
| **Week 10: UI/UX Polish** | - Refine the categorical UI for shopping lists. <br> - Improve mobile-first design and accessibility. | - Finalize UI for categorical shopping. |
| **Week 11: Testing** | - Implement full testing strategy (Unit, Integration, E2E). <br> - Set up CI/CD with GitHub Actions. | - Finalize testing strategy details. |
| **Week 12: Deployment** | - Deploy to self-hosted Raspberry Pi. <br> - Document deployment process. | - N/A (Decision already made) |

**Outcome of Phase 4**: The app is now a polished V1 product, deployed and ready for use, with a solid foundation for future features.

---

## Phased Planning Decisions
To keep us moving fast, we'll only focus on the decisions needed for the current phase. Here's how the pending decisions map to our new phases:

| Phase | Decisions to Make |
| :--- | :--- |
| **Phase 1** | - `plans/decisions/phase-4/procfile-dev.md` <br> - `plans/decisions/phase-4/data-models-consolidation.md` <br> - `plans/decisions/phase-4/api-endpoint-sketches.md` |
| **Phase 2** | - `plans/decisions/phase-1/meal-planning-verification.md` <br> - `plans/decisions/phase-3/offline-sync-mechanisms.md` |
| **Phase 4** | - `plans/decisions/phase-1/ui-categorical-shopping.md` <br> - `plans/decisions/phase-4/testing-strategy-outline.md` |

This plan gets us to a usable product in ~6 weeks, with full V1 features in ~3 months.