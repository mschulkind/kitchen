# 📚 Kitchen App — Feature Specifications

> **Purpose:** Central directory for all feature specs. Each spec documents what a feature SHOULD be — user stories, flows, UI behavior, data models, open questions, and future ideas.
> **Last Updated:** 2026-02-18

---

## How to Read These Specs

Each spec follows a consistent structure:
- **Overview** — What is this feature and why does it exist?
- **User Stories** — Who wants what and why?
- **User Flows** — Step-by-step walkthrough of each interaction
- **UI Behavior** — What the user sees, what happens on click/tap
- **Data Model** — What gets stored and where
- **Business Rules** — Validation, constraints, edge cases
- **Current State** — What's built vs. what's planned
- **Future Ideas** — Vision features, research-inspired concepts
- **Open Questions** — Decisions still needed

---

## Feature Areas

| # | Spec | Description | Status |
|---|------|-------------|--------|
| 01 | [Auth & Accounts](01-auth-accounts.md) | Login, sessions, household membership | 🟢 Mostly built |
| 02 | [Dashboard](02-dashboard.md) | Hub screen, quick stats, navigation | 🟢 Built |
| 03 | [Pantry & Inventory](03-pantry-inventory.md) | Item tracking, locations, staples, expiry | 🟡 Needs staples feature |
| 04 | [Recipes](04-recipes.md) | Browse, view, import, edit, favorites, scaling, PDF | 🟢 Mostly built |
| 05 | [AI Recipe Chat](05-recipe-ai-chat.md) | Conversational recipe creation with LLM | 🔴 Not started |
| 06 | [Meal Planning](06-meal-planning.md) | Weekly plans, AI generation, Slot Machine, gamification | 🟡 UI built, gen is mock |
| 07 | [Shopping Lists](07-shopping-lists.md) | Shared lists, autocomplete, store intelligence | 🟡 Needs autocomplete |
| 08 | [Settings](08-settings.md) | Preferences, household, store config | 🟢 Built |
| 09 | [Realtime & Multi-user](09-realtime-multiuser.md) | Live sync, presence, collaboration | 🟡 Partially wired |
| 10 | [AI / LLM Integration](10-ai-llm-integration.md) | Multi-provider adapter, scoring, prompts | 🔴 Architecture needed |
| 11 | [Parking Lot](11-parking-lot.md) | Deferred: cooking mode, vision, images, PDF, batch cooking | ⏸️ Parked |

---

## Prioritization

### 🔴 Now (Active Development)
1. **AI Recipe Chat** (#05) — Core differentiator, needs LLM integration
2. **LLM Provider Abstraction** (#10) — Foundation for all AI features
3. **Pantry Staples** (#03) — Simple flag, high user value
4. **Shopping Autocomplete** (#07) — USDA taxonomy + item profiles

### 🟡 Next (After core AI works)
5. **Meal Plan AI Generation** (#06) — Replace mock with real LLM, wire up scoring
6. **Slot Machine Refinement** (#06) — Granular lock/spin per component
7. **Recipe Favorites** (#04) — Star system, planner integration
8. **Realtime Sync** (#09) — Infrastructure now available

### 🔵 Later (Polish & Expansion)
9. **Recipe PDF Export** (#04, #11) — Printable recipe cards
10. **Recipe Scaling** (#04) — Adjust servings, recalculate ingredients
11. **Store Intelligence** (#07) — Per-store aisle mapping
12. **Leftover Chain Planning** (#06) — Multi-day ingredient reuse
13. **Multi-household** (#01) — Currently single-household

### ⏸️ Parked (Not on active roadmap)
- Cooking Mode (#11) — Only PDF export + prompt copy
- Vision Scanning (#11) — Backburnered per user decision
- Image Generation (#11) — Backburnered per user decision
- Gamification (#06) — Cooking streaks, recipe swiping, family voting (great ideas, not yet prioritized)
- Batch Cooking (#11) — Meal prep mode (future)
- Grocery Delivery Integration (#07) — Export to Instacart etc. (future)
