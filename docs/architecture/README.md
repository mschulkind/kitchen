# 🏗️ Architecture — Technical Design & Decisions

> How the Kitchen app is designed: data flows, UX patterns, and the reasoning behind key decisions.

---

## Documents

| Document | Purpose |
|----------|---------|
| [Design System](design-system.md) | Core tech stack, data models, API design, LLM integration, collaboration architecture, testing strategy |
| [UX Flows](ux-flow.md) | Primary user flows with wireframes and sequence diagrams |
| [Planning Algorithm & UX](planning-algorithm-and-ux.md) | The "Choose Your Own Adventure" meal planning algorithm, Slot Machine, Tweak Bar |
| [Recipe Format Design](recipe-format-design.md) | PDF recipe card format with interleaved timelines |
| [E2E Test Plan](e2e-test-plan.md) | Playwright "Strict Mode" testing philosophy and coverage matrix |
| [Phase 0 Workflow](phase0-workflow.md) | The original conversational (markdown-driven) meal planning flow |
| [Decisions](decisions/) | Decision logs organized by phase |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Expo Frontend                      │
│  (React Native Web + Tamagui + TanStack Query)       │
│                                                       │
│  Hub → Recipes → Planner → Shopping → Inventory       │
└──────────────────────┬────────────────────────────────┘
                       │ REST API
┌──────────────────────▼────────────────────────────────┐
│                   FastAPI Backend                       │
│  (Clean Architecture: Routes → Services → Repos)       │
│                                                        │
│  Domains: recipes, pantry, planning, shopping, cooking │
└──────────────────────┬─────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          │            │            │
   ┌──────▼──────┐ ┌──▼───┐ ┌─────▼─────┐
   │  Supabase   │ │ LLM  │ │ Supabase  │
   │  PostgreSQL │ │ (AI) │ │ Realtime  │
   │  (Data)     │ │      │ │ (WS)     │
   └─────────────┘ └──────┘ └───────────┘
```

## Key Design Decisions

| Decision | Choice | Reference |
|----------|--------|-----------|
| UI Framework | Tamagui (compiles to native) | [design-system.md](design-system.md) |
| Navigation | Hub & Spoke (not bottom tabs) | [design-system.md](design-system.md) |
| Database | Supabase (PostgreSQL + Realtime) | [design-system.md](design-system.md) |
| Auth | Google OAuth via Supabase Auth | [decisions/](decisions/) |
| LLM Dev | Ollama (local, self-hosted) | [design-system.md](design-system.md) |
| LLM Prod | Multi-provider (Gemini/Claude/OpenAI) | Spec #10 |
| Hosting | Self-hosted Docker on Synology NAS | [decisions/](decisions/) |
| Offline | Optimistic UI + Last-Write-Wins | [design-system.md](design-system.md) |
| Testing | Playwright "Strict Mode" + pytest | [e2e-test-plan.md](e2e-test-plan.md) |
