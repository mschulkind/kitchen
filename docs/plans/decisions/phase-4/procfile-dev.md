# Decision: Create Procfile.dev for Overmind

## Overview

This decision outlines the configuration of `Procfile.dev` for Overmind to manage local development processes for the PWA app, including frontend (React Native/Expo), backend (FastAPI), and Supabase CLI for realtime features. Overmind will orchestrate starting/stopping services for efficient dev workflow, as referenced in hosting.md.

## Options

- **Option 1: Basic Processes (Frontend + Backend)**
  - frontend: expo start
  - backend: uvicorn main:app --reload
  - No Supabase explicit, assume separate terminal.

- **Option 2: Full Stack with Supabase**
  - frontend: expo start
  - backend: uvicorn main:app --reload
  - supabase: supabase start
  - Enables local Supabase for offline/realtime testing.

- **Option 3: Advanced with Tests and Monitoring**
  - frontend: expo start
  - backend: uvicorn main:app --reload
  - supabase: supabase start
  - tests: pytest watch or vitest --watch (optional hot-reload for TDD).

## Pros/Cons

- **Basic Processes**:
  - Pros: Simple, fast startup; minimal dependencies.
  - Cons: Manual management for Supabase; less integrated testing.

- **Full Stack**:
  - Pros: One-command dev environment; easy realtime simulation.
  - Cons: Longer startup time; requires Supabase CLI installed.

- **Advanced**:
  - Pros: Supports TDD workflow; comprehensive for full dev cycle.
  - Cons: Complexity in config; potential port conflicts.

## Questions for User

- Include Supabase local start in Procfile, or keep separate?
- Add test watcher process (e.g., for pytest or Vitest)?
- Preferred port configs or env vars for processes?
- Integration with other tools (e.g., Docker for backend)?

## Next Steps

Define Procfile.dev content and add to hosting.md; test Overmind setup. Reference: [plans/hosting.md](../hosting.md), [plans/design-system.md](../design-system.md).

*Decision Pending - Awaiting User Input*
