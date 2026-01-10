# Decision: Compile Testing Strategy Outline

## Overview
This decision outlines the TDD strategy for the app, covering unit, integration, and E2E tests for frontend (React Native/Vitest), backend (FastAPI/pytest), and realtime features (Supabase). Align with rules.md for fast tests (<1s run) and 80% coverage on critical paths like sync and LLM integrations.

## Options
- **Option 1: Basic TDD (Unit + Integration)**
  - Unit: Test core functions (e.g., ingredient optimization algorithm) with mocks.
  - Integration: Test API endpoints with Supabase test DB.
  - Tools: pytest for backend, Vitest for frontend; no E2E.

- **Option 2: Full Stack with E2E**
  - Unit/Integration as above, plus E2E for flows (e.g., meal plan to shopping list) using Detox for mobile.
  - Include realtime tests (e.g., simulate multiuser via WebSocket mocks).

- **Option 3: CI/CD Integrated Testing**
  - All levels, with coverage reports; add load tests for sync.
  - Tools: GitHub Actions for CI; mock LLM calls to avoid costs.

## Pros/Cons
- **Basic TDD**:
  - Pros: Quick to implement; focuses on core reliability.
  - Cons: Misses UI/realtime edge cases; harder to catch integration bugs.

- **Full Stack E2E**:
  - Pros: End-to-end confidence; validates user flows.
  - Cons: Flaky tests; longer run times; mobile-specific setup.

- **CI/CD Integrated**:
  - Pros: Automated quality gate; scalable for team dev.
  - Cons: Overhead for local runs; dependency on CI env.

## Questions for User
- Coverage goals (e.g., 80% overall or 90% for sync/LLM)?
- Include E2E for mobile (Detox) or limit to unit/integration?
- Mock external services (LLM, Supabase) or use test instances?
- Test realtime multiuser scenarios (e.g., how many simulated users)?

## Next Steps
Phased checklist in design-system.md; link to rules.md. Reference: [plans/design-system.md](../design-system.md), [.kilocode/rules/rules.md](../../../.kilocode/rules/rules.md), [plans/brief.md](../brief.md).

*Decision Pending - Awaiting User Input*