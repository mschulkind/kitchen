# Kitchen Project: Agent Instructions

This document consolidates the project-specific rules and guidelines for AI agents working on the Kitchen project.

## Table of Contents

- [Project Structure and Practices](#project-structure-and-practices)
- [Tech Design Rules](#tech-design-rules)
- [Implementation Patterns](#implementation-patterns)
- [Development Workflow](#development-workflow)
- [Documentation Guidelines](#documentation-guidelines)
- [Recipe Scraping Guidelines](#recipe-scraping-guidelines)

## Project Structure and Practices

### Directory Usage

- **`docs/plans/`**: Git-tracked for planning, outlines, specs, and decisions. Use `index.md` for navigation.
- **`context/`**: Gitignored for research, data, temporary notes, and references. Use `index.md` for organization.
- **`scratch/`**: Git-tracked for temporary developer notes, draft code, and experimental snippets.
- **`src/api/`**: Python FastAPI backend following Clean Architecture.
- **`src/mobile/`**: Expo (React Native Web) frontend with Tamagui UI.
- **`infra/docker/`**: Docker Compose and container configurations for self-hosted deployment.
- **`tests/`**: Backend tests mirroring `src/api` structure.
- **General**: All paths are relative to the project root. Use clear naming and READMEs.

### Safety & File Deletion

- **No `rm`**: Never use the `rm` command to delete files, as it is blocked by the auto-approver for safety.
- **Trash Directory**: To "delete" a file, move it to the `trash/` directory at the project root (e.g., `mv path/to/file trash/`). This allows for manual review and recovery if needed.

### TDD Practices

- **Test-First Workflow**: Write tests before implementation. Start with unit tests, followed by integration tests for application flows.
- **Fast Tests**: Keep test suites under 1 second. Mock external dependencies (e.g., LLM calls) and avoid slow I/O.
- **Coverage**: Maintain **80%+ code coverage** on critical paths. Run `just coverage` to verify.
- **Test Structure**: Place backend tests in `tests/`, mirroring the source structure. Co-locate frontend tests with components. Use E2E tests for key user flows.

## Tech Design Rules

### Tech Stack

- **Frontend**: React Native with Expo for cross-platform mobile app (iOS/Android), focusing on touch-friendly UI (big buttons, simple gestures for shared lists).
- **Backend/Database**: Supabase (PostgreSQL with realtime subscriptions via WebSockets for instant multiuser sync on meal plans, inventory, shopping lists).
- **Realtime Collaboration**: Supabase for live updates (e.g., checkmarks on shared checklists propagate instantly); support multiuser with integrated auth (email/social logins), presence tracking (online indicators), and role-based permissions (owner/editor/viewer).
- **Auth & Security**: Supabase Auth for user management and invites; row-level security for shared resources.
- **Offline/Optimistic Updates**: Supabase client SDK for mobile offline handling (queue changes, sync on reconnect with simple conflict alerts).
- **Notifications**: Expo Notifications triggered by Supabase Edge Functions for change alerts (e.g., "Collaborator added item").
- **Other Tools**: Git for version control; emphasize modern best practices like containerization (Docker) if deployment requires it.

### Mobile-First Principles

- **UX Focus**: Design for mobile/on-the-go use with large touch targets (min 44x44px), minimal navigation (e.g., bottom tabs or gesture-based), and simple, intuitive interfaces that "just work."
- **Responsiveness**: Use Tailwind's mobile-first breakpoints; test on various screen sizes. Prioritize offline capability (e.g., service workers for PWA, local storage for inventory).
- **Accessibility**: Ensure high contrast, semantic HTML in React, and keyboard navigation support. Flows like ingredient verification should use categorical checklists for quick scanning.
- **Performance**: Optimize for low latency; lazy-load non-essential components, use efficient data fetching (e.g., TanStack Query for React).

## Implementation Patterns

### Backend (FastAPI) - Clean Architecture

The backend follows Domain-Driven Design with clear separation:

```
src/api/app/
├── core/           # Configuration, logging, shared utilities
├── db/             # Database session management (Supabase client)
├── domain/         # Business logic organized by domain
│   └── <domain>/
│       ├── models.py      # Pydantic DTOs (NOT database models)
│       ├── service.py     # Business logic, validation rules
│       └── repository.py  # Database access layer
└── routes/         # FastAPI routers (thin, delegate to services)
```

**Key Principles:**

- **DTOs over ORM**: Use Pydantic models for all data transfer. No SQLAlchemy models.
- **Repository Pattern**: All DB access goes through repository classes.
- **Service Layer**: Business logic lives in services, not routes.
- **Dependency Injection**: Use FastAPI's `Depends()` for loose coupling.

### Frontend (Expo) - Component Architecture

```
src/mobile/
├── app/                    # Expo Router pages (file-based routing)
│   ├── (tabs)/             # Tab navigator screens
│   └── <feature>/[id].tsx  # Dynamic routes
├── components/             # Reusable UI components
├── hooks/                  # Custom React hooks (realtime, queries)
└── lib/                    # API clients, Supabase config
```

**Key Principles:**

- **Tamagui Components**: Use Tamagui for all UI (compiles to native styles).
- **TanStack Query**: All server state via `useQuery`/`useMutation`.
- **Realtime Subscriptions**: Use `useInventorySubscription` pattern for live updates.
- **Mobile-First**: Design for touch (44px min targets), then scale up.

### Realtime Pattern (Critical for Multi-User)

```typescript
// Pattern: Realtime subscription that invalidates TanStack Query cache
useEffect(() => {
  const channel = supabase
    .channel(`table:${id}`)
    .on('postgres_changes', { event: '*', table: 'table_name' }, () => {
      queryClient.invalidateQueries({ queryKey: ['table', id] });
    })
    .subscribe();
  return () => supabase.removeChannel(channel);
}, [id]);
```

## Development Workflow

### Pre-Commit Checklist

- [ ] **Run `just check`**: You MUST run `just check` (lint + test) before every commit. Never commit broken or unlinted code.
- [ ] **Verify Coverage**: Ensure `just coverage` still shows 80%+ on critical paths.

### Common Commands (justfile)

```bash
just check          # Run lint + test
just test           # Run pytest
just up             # Start Docker stack
just down           # Stop Docker stack
just dev-api        # Run API locally (no Docker)
just mobile-web     # Start Expo for web (primary target)
```

### Commit Conventions

- **feat(phase-X)**: New feature for a specific phase
- **fix(phase-X)**: Bug fix
- **docs**: Documentation updates
- **test**: Test additions/changes
- **refactor**: Code restructuring without behavior change

### Decision References

When implementing, reference decisions from `docs/plans/open-questions.md`:

- **D4**: Self-hosted Docker on Synology
- **D6**: Multi-provider LLM adapter (Gemini, Claude, OpenAI)
- **D13**: Lazy Discovery - add items to pantry during verification

## Documentation Guidelines

- **Engaging Style**: Use lots of emojis and include fun facts throughout all documentation to make it engaging and enjoyable to read. 🍳👨‍🍳
- **Structure**: Follow standard markdown formatting with clear headings, lists, and sections.
- **Attribution**: Always include source attribution when applicable to respect original content creators.
- **Recipe Formats**: When generating or updating recipes, explicitly address the "Main" and the "Side(s)" (or Companions). Ensure the execution formats (especially Mise-en-place and Timeline) clearly show how to interleave the preparation of the main dish and the side dish so they finish at the same time.

## Recipe Scraping Guidelines

*Note: Detailed recipe scraping skills are maintained in [/.claude/skills/recipe-scraping.md](.claude/skills/recipe-scraping.md).*

- **Primary Tool**: Use firecrawl-local MCP server for scraping recipe content from URLs.
- **Organization**: Store scraped recipes in `phase0_flow/recipes/<site>/` where `<site>` is the domain name with hyphens.
- **Metadata**: Include the original source URL at the top of each recipe file.
- **Formatting**: Use standard markdown with `# Title`, `### Ingredients`, `### Instructions`.

# Levity

- Don't be afraid to be funny.
- Respond like you're a whale who has temporarily forgotten he's a whale and wonders why he's all wet.