# Full QA Cycle Skill 🐋💦

A comprehensive workflow for auditing, testing, fixing, and roadmapping the Kitchen app.
Think of it as a whale doing a full belly-flop across every feature. Splashy but thorough.

## Overview

This skill orchestrates a **3-phase QA cycle**:

1. **Phase 1: Feature Discovery & Tracker Creation** — Trace every user flow, form scenarios, create a central tracker document with phases and prioritization.
2. **Phase 2: Manual QA Execution** — Walk through each scenario as a real user (browser-based), recording pass/fail/bug status. Fix bugs inline, committing after each logical fix.
3. **Phase 3: Roadmap Synthesis** — Aggregate results into a real-world readiness assessment and forward-looking roadmap.

## Phase 1: Feature Discovery & Tracker Creation

### Steps

1. **Explore the full codebase** — frontend routes, API endpoints, domain services, components, hooks, infra.
2. **Enumerate every user flow** — group by feature domain (Auth, Pantry, Recipes, Planner, Shopping, Vision, Cooking, Voice, Settings).
3. **Create `docs/qa/user-flow-tracker.md`** with:
   - Scenario ID, description, preconditions, steps, expected result
   - Status column: `⬜ Untested | ✅ Pass | ❌ Fail | 🐛 Bug Filed | 🔧 Fixed`
   - Priority: `P0 Critical | P1 High | P2 Medium | P3 Low`
   - Phase grouping matching the project's phase structure
4. **Prioritize** scenarios based on:
   - P0: Auth, basic navigation, data persistence (can you use the app at all?)
   - P1: Core CRUD flows (pantry, recipes, shopping lists)
   - P2: AI/LLM-powered features (planner generation, vision, cooking context)
   - P3: Nice-to-haves (voice, store intelligence, imagery)

## Phase 2: Manual QA Execution

### Approach

- **Act like a real user** — use the browser, click buttons, fill forms, navigate.
- **Start the full stack** — `just up` for Docker services, `just dev-frontend` for Expo web, `just dev-api` if running API locally.
- **Test in priority order** — P0 first, then P1, P2, P3.
- **For each scenario**:
  1. Navigate to the relevant screen
  2. Execute the steps
  3. Verify expected behavior
  4. Record result in tracker
  5. If bug found:
     - Document the bug (what happened vs. what should happen)
     - Investigate root cause
     - Fix the bug (minimal, surgical change)
     - Verify the fix
     - Commit with descriptive message
     - Re-test the scenario
     - Update tracker status to 🔧 Fixed or ✅ Pass

### Testing Tools

- **Browser**: Chrome DevTools for UI interaction, network inspection, console errors
- **API**: Direct HTTP calls via curl for backend verification
- **Database**: Supabase Studio for data inspection
- **Logs**: `just logs` or container logs for backend errors

### Bug Fix Guidelines

- Fix **only** the bug at hand — no scope creep
- Commit after each logical fix with format: `fix(phase-X): description`
- Run `just check` before committing (lint + test)
- If a fix requires schema changes, document them

## Phase 3: Roadmap Synthesis

### Deliverables

1. **Update `docs/qa/user-flow-tracker.md`** with final status for all scenarios
2. **Create summary section** at top of tracker:
   - Total scenarios tested / passed / failed / blocked
   - Per-phase readiness percentage
   - Critical bugs remaining
3. **Roadmap recommendations**:
   - What's production-ready now?
   - What needs fixes before launch?
   - What's deferred / future work?
   - Suggested next sprint priorities

## Conventions

- All QA artifacts go in `docs/qa/`
- Use the `manual-qa` skill for individual scenario execution when possible
- Commit messages follow project convention: `fix(phase-X):`, `test:`, `docs:`
- Include `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` in all commits
- Have fun with it 🐋 — if you're not slightly damp, you're doing it wrong
