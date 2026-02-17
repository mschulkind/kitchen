# 📚 Kitchen App — Feature Specifications Index

> **Purpose:** Central directory for all feature specs. Each spec documents what a feature SHOULD be — user stories, flows, UI behavior, data models, and open questions.
> **Last Updated:** 2026-02-17

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
- **Open Questions** — Decisions still needed

---

## Feature Areas

| # | Spec | Description | Status |
|---|------|-------------|--------|
| 01 | [Auth & Accounts](01-auth-accounts.md) | Login, sessions, household membership | 🟢 Mostly built |
| 02 | [Dashboard](02-dashboard.md) | Hub screen, quick stats, navigation | 🟢 Built |
| 03 | [Pantry & Inventory](03-pantry-inventory.md) | Item tracking, locations, staples, expiry | 🟡 Needs staples feature |
| 04 | [Recipes](04-recipes.md) | Browse, view, import, edit recipes | 🟢 Mostly built |
| 05 | [AI Recipe Chat](05-recipe-ai-chat.md) | Conversational recipe creation with LLM | 🔴 Not started |
| 06 | [Meal Planning](06-meal-planning.md) | Weekly plans, AI generation, locking | 🟡 UI redesigned, gen is mock |
| 07 | [Shopping Lists](07-shopping-lists.md) | Shared lists, autocomplete, item profiles | 🟡 Needs autocomplete |
| 08 | [Settings](08-settings.md) | Preferences, household, store config | 🟢 Built |
| 09 | [Realtime & Multi-user](09-realtime-multiuser.md) | Live sync, presence, collaboration | 🟡 Partially wired |
| 10 | [AI / LLM Integration](10-ai-llm-integration.md) | Cross-cutting AI capabilities | 🔴 Architecture needed |
| 11 | [Parking Lot](11-parking-lot.md) | Deferred features: cooking mode, vision, images | ⏸️ Parked |

---

## Prioritization

### Now (Active Development)
1. **Pantry Staples** (#03) — Simple flag, high user value
2. **AI Recipe Chat** (#05) — Core differentiator, needs Ollama integration
3. **Shopping Autocomplete** (#07) — USDA taxonomy + item profiles
4. **Realtime Sync** (#09) — Infrastructure now available

### Next (After core AI works)
5. **Meal Plan AI Generation** (#06) — Replace mock with real LLM
6. **Recipe URL Import** (#04) — Internet now available
7. **LLM Provider Abstraction** (#10) — Ollama → multi-provider

### Later (Polish & Expansion)
8. **Multi-household** (#01) — Currently single-household
9. **Store Intelligence** (#07) — Per-store aisle mapping
10. **Notifications** (#09) — Push notifications for changes

### Parked (Not on active roadmap)
- Cooking Mode (#11) — Only PDF export + prompt copy
- Vision Scanning (#11) — Backburnered per user decision
- Image Generation (#11) — Backburnered per user decision
