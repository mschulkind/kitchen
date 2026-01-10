# Kitchen Project: Agent Instructions

This document consolidates the project-specific rules and guidelines for AI agents working on the Kitchen project.

## Table of Contents

- [Project Structure and Practices](#project-structure-and-practices)
- [Tech Design Rules](#tech-design-rules)
- [Documentation Guidelines](#documentation-guidelines)
- [Recipe Scraping Guidelines](#recipe-scraping-guidelines)

## Project Structure and Practices

### Directory Usage

- **`docs/plans/`**: Git-tracked for planning, outlines, specs, and decisions. Use `index.md` for navigation.
- **`context/`**: Gitignored for research, data, temporary notes, and references. Use `index.md` for organization.
- **`src/`**: Source code (Python backend, TS/React frontend). Tests should be separate but parallel.
- **General**: All paths are relative to the project root. Use clear naming and READMEs.

### TDD Practices

- **Test-First Workflow**: Write tests before implementation. Start with unit tests, followed by integration tests for application flows.
- **Fast Tests**: Keep test suites under 1 second. Mock external dependencies (e.g., LLM calls) and avoid slow I/O. Aim for 80%+ code coverage on critical paths.
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

## Documentation Guidelines

- **Engaging Style**: Use lots of emojis and include fun facts throughout all documentation to make it engaging and enjoyable to read. 🍳👨‍🍳
- **Structure**: Follow standard markdown formatting with clear headings, lists, and sections.
- **Attribution**: Always include source attribution when applicable to respect original content creators.

## Recipe Scraping Guidelines

*Note: Detailed recipe scraping skills are maintained in [/.claude/skills/recipe-scraping.md](.claude/skills/recipe-scraping.md).*

- **Primary Tool**: Use firecrawl-local MCP server for scraping recipe content from URLs.
- **Organization**: Store scraped recipes in `phase0_flow/recipes/<site>/` where `<site>` is the domain name with hyphens.
- **Metadata**: Include the original source URL at the top of each recipe file.
- **Formatting**: Use standard markdown with `# Title`, `### Ingredients`, `### Instructions`.
