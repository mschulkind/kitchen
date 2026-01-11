# Open Questions: Kitchen Project 🤔

**Last Updated**: January 11, 2026

This document captures unresolved decisions and areas where your input is needed to move forward. Each question includes context and options where applicable.

---

## ✅ Decisions Recorded

### D1: UI Component Library -> Tamagui
- **Decision**: Use **Tamagui** for the UI layer.
- **Date**: 2026-01-11
- **Reasoning**: Performance-focused, compiles to native styles, and provides a sophisticated design system for cross-platform (Web/Android/iOS) consistency. User confirmed preference for better long-term outcome over learning curve.
- **Impact**: Affects all mobile/web component development. Requires setup of Tamagui compiler in the monorepo.

### D2: LLM Strategy -> Cloud Only (Flexible)
- **Decision**: Start with Cloud APIs (OpenAI, Gemini, Claude). Defer local LLM.
- **Date**: 2026-01-11
- **Reasoning**: Prioritize quality and API freedom over privacy/offline initially. Allows mixing best-in-class models (e.g., Gemini for vision, Claude for planning).
- **Impact**: Backend must support API Key management for multiple providers.

### D3: Platform Priority -> Web First (Synology Host)
- **Decision**: Target **Desktop/Mobile Web** first. Android later.
- **Date**: 2026-01-11
- **Reasoning**: Faster iteration loop. The app will be built with Expo (React Native Web) to ensure the Android build is possible later, but the primary test target is a browser.
- **Impact**: E2E tests should run in Headless Chrome/Playwright.

### D4: Hosting -> Self-Hosted Docker (Synology)
- **Decision**: Full stack must be Dockerized for Synology NAS.
- **Date**: 2026-01-11
- **Reasoning**: User requirement for data ownership and local infrastructure.
- **Impact**:
    - Need `docker-compose.yml` for the whole stack.
    - **Supabase**: Must use the Self-Hosted Docker setup (or a lighter Postgres+PostgREST alternative if Supabase is too heavy for the NAS). *Assumption: We will try full Supabase first.*

### D5: UX Feature -> "Slot Machine" (Phase 6)
- **Decision**: Keep the detailed "Slot Machine" (Lock/Spin) UI.
- **Date**: 2026-01-11
- **Reasoning**: Core differentiator.
- **Impact**: Phase 6 remains a major UI effort.

### D6: LLM Provider -> Multi-Adapter
- **Decision**: Build adapters for Gemini, Claude, and OpenAI.
- **Date**: 2026-01-11
- **Reasoning**: User wants to experiment. Different models excel at different tasks (Vision vs Reasoning).
- **Impact**: Codebase must use a `LLMProvider` interface, not hardcode SDKs.

### D7: Parsing Strategy -> Structured JSON
- **Decision**: Enforce JSON output at the generation step.
- **Date**: 2026-01-11
- **Reasoning**: "Don't guess." If we generate the recipe, we should generate the data structure too.
- **Impact**: Prompt Engineering must be strict about JSON schemas.

### D8: Store Intel -> Single Store (Shaws)
- **Decision**: Support Shaws, configurable by Zip Code.
- **Date**: 2026-01-11
- **Reasoning**: MVP scope constraint.
- **Impact**: Phase 8 Scraper focuses solely on Shaws/Albertsons API.

---

## Table of Contents

- [🏗️ Architecture & Tech Stack](#️-architecture--tech-stack)
- [📱 Platform & UX Priorities](#-platform--ux-priorities)
- [🧠 AI/LLM Strategy](#-aillm-strategy)
- [🛒 Store Intelligence (Phase 8)](#-store-intelligence-phase-8)
- [🎤 Voice Integration (Phase 9)](#-voice-integration-phase-9)
- [📊 Data & Content](#-data--content)
- [🚀 Development Prioritization](#-development-prioritization)

---

### D9: Router -> Expo Router
- **Decision**: Use **Expo Router**.
- **Date**: 2026-01-11
- **Reasoning**: Best for Web-First (PWA) deep linking and file-based organization.
- **Impact**: App structure will follow `app/` directory convention.

### D10: Store Data Strategy -> API First
- **Decision**: Reverse-engineer Shaw's API.
- **Date**: 2026-01-11
- **Reasoning**: Most accurate data. Fallback to crowdsourcing if blocked.
- **Impact**: Phase 8 requires significant research/scraping work.

### D11: Voice Platform -> Google Home + HA
- **Decision**: Use Home Assistant as the bridge if possible, or direct Google Actions.
- **Date**: 2026-01-11
- **Reasoning**: User has HA and Google Home devices.
- **Impact**: Phase 9 integration target defined.

### D12: Recipe Storage -> Structured Only
- **Decision**: Scrape on-demand, extract JSON, discard raw text/HTML (keep URL).
- **Date**: 2026-01-11
- **Reasoning**: "Don't store the fluff." Focus on data we can use for math/planning.
- **Impact**: Database `recipes` table might not need `source_markdown` column, or it's optional.

### D13: Inventory Init -> Lazy Discovery
- **Decision**: No "Big Bang" scan. Use "Lazy Discovery" during recipe verification.
- **Date**: 2026-01-11
- **Reasoning**: "Discovery via Verification" reduces friction. If a recipe needs Cumin and user says "I have it", add it to the pantry then.
- **Impact**: The "Verification" UI (Phase 3/5) needs a "Add to Pantry permanently" toggle for items found during checks.

### D15: Phase Granularity -> Execution Splitting
- **Decision**: Keep the 10 High-Level Phases in docs, but execute in smaller chunks (e.g., Phase 1A Backend, Phase 1B Frontend).
- **Date**: 2026-01-11
- **Reasoning**: Prevents documentation sprawl while ensuring small, testable PRs.
- **Impact**: "Definition of Done" for a Phase requires both parts.

### D16: Timeline -> AI Flow
- **Decision**: No deadlines. Optimize for continuous iteration.
- **Date**: 2026-01-11
- **Reasoning**: "My LLM works long hours."
- **Impact**: Focus on TDD and correctness over rushing.

---

## Table of Contents

- [🏗️ Architecture & Tech Stack](#️-architecture--tech-stack)
- [📱 Platform & UX Priorities](#-platform--ux-priorities)
- [🧠 AI/LLM Strategy](#-aillm-strategy)
- [🛒 Store Intelligence (Phase 8)](#-store-intelligence-phase-8)
- [🎤 Voice Integration (Phase 9)](#-voice-integration-phase-9)
- [📊 Data & Content](#-data--content)
- [🚀 Development Prioritization](#-development-prioritization)

---

## 🏗️ Architecture & Tech Stack

*All questions answered.*

---

## 📱 Platform & UX Priorities

*All questions answered.*

---

## 🧠 AI/LLM Strategy

*All questions answered.*

---

## 🛒 Store Intelligence (Phase 8)

*All questions answered.*

---

## 🎤 Voice Integration (Phase 9)

*All questions answered.*

---

## 📊 Data & Content

*All questions answered.*

---

## 🚀 Development Prioritization

*All questions answered.*

## 📝 How to Answer

For each question, you can respond with:

- A clear decision (e.g., "Q1: Let's go with Tamagui")
- More context (e.g., "Q9: Actually we shop at Market Basket, not Shaw's")
- "Defer" (e.g., "Q11: Voice can wait, let's skip it for MVP")

I'll update the planning docs based on your answers! 🚀
