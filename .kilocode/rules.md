# Project Rules and Guidelines

## Tech Stack

- **Frontend**: React Native with Expo for cross-platform mobile app (iOS/Android), focusing on touch-friendly UI (big buttons, simple gestures for shared lists).
- **Backend/Database**: Supabase (PostgreSQL with realtime subscriptions via WebSockets for instant multiuser sync on meal plans, inventory, shopping lists).
- **Realtime Collaboration**: Supabase for live updates (e.g., checkmarks on shared checklists propagate instantly); support multiuser with integrated auth (email/social logins), presence tracking (online indicators), and role-based permissions (owner/editor/viewer).
- **Auth & Security**: Supabase Auth for user management and invites; row-level security for shared resources.
- **Offline/Optimistic Updates**: Supabase client SDK for mobile offline handling (queue changes, sync on reconnect with simple conflict alerts).
- **Notifications**: Expo Notifications triggered by Supabase Edge Functions for change alerts (e.g., "Collaborator added item").
- **LLM Integration**: Integrate an LLM agent (e.g., via OpenAI API or local model like Ollama) for dynamic recipe suggestions and customizations.
- **Other Tools**: Git for version control; emphasize modern best practices like containerization (Docker) if deployment requires it.

## TDD Practices
- **Test-First Workflow**: Write tests before implementation code. Start with unit tests for core functions (e.g., recipe matching algorithm), then integration tests for flows like meal planning to shopping list.
- **Fast Test Guidelines**: Ensure test suites run in under 1 second. Use mocking for external dependencies (e.g., LLM calls), parallel execution where possible, and avoid slow I/O in tests. Aim for 80%+ code coverage on critical paths like inventory verification.
- **Test Structure**: Backend tests in `tests/` mirroring source structure; frontend tests colocated with components. Include end-to-end tests for key UX flows using tools like Playwright if needed.

## Directory Usage Rules
- **plans/**: Git-tracked directory for all planning, outlines, specs, and decisions (e.g., brief.md, design-system.md). Maintain an index.md for navigation.
- **context/**: Gitignored; for dumping research, data, temporary notes, and references (e.g., API docs, recipe datasets). Use index.md to organize and link content.
- **scratch/**: Gitignored; strictly for temporary files during development (e.g., quick prototypes, debug outputs). No long-term storage or commits; clean up or abandon as needed.
- **src/** or similar: For source code (backend in Python, frontend in TS/React). Keep tests separate but parallel.
- **General**: All paths relative to project root (/home/matt/code/kitchen). Use clear naming and READMEs in subdirs for clarity.

### Mode-Specific File Permissions
- architect (architect): edit_file restricted to *.md
- code (code): edit_file restricted to *.ts,*.js,*.py,*.md
- ask (ask): edit_file unrestricted
- debug (debug): edit_file restricted to *.ts,*.js,*.py
- orchestrator (orchestrator): edit_file unrestricted
- planning (planning): edit_file restricted to plans/*.md

## Mobile-First Principles
- **UX Focus**: Design for mobile/on-the-go use with large touch targets (min 44x44px), minimal navigation (e.g., bottom tabs or gesture-based), and simple, intuitive interfaces that "just work."
- **Responsiveness**: Use Tailwind's mobile-first breakpoints; test on various screen sizes. Prioritize offline capability (e.g., service workers for PWA, local storage for inventory).
- **Accessibility**: Ensure high contrast, semantic HTML in React, and keyboard navigation support. Flows like ingredient verification should use categorical checklists for quick scanning.
- **Performance**: Optimize for low latency; lazy-load non-essential components, use efficient data fetching (e.g., TanStack Query for React).

## Other Relevant Rules
- **Data Models**: Define clear models like PantryItem (with location: Pantry/Fridge/Freezer/Garden, quantity, expiry) and ShoppingListItem (sorted by store layout: Produce/Dairy/Meat/etc.).
- **LLM Usage**: Prompt engineering focused on efficiency – e.g., generate recipes that maximize ingredient reuse and garden surpluses. Log interactions for debugging but respect privacy (local-first where possible).
- **Version Control**: Commit planning docs to git; ignore temp/research dirs. Use branches for major decisions (e.g., tech stack finalization).
- **Best Practices**: Emphasize usability and efficiency per brief. No auth needed for personal use, but consider PWA install prompts. Follow Python PEP 8 and TS ESLint standards.

## Todo List Usage for Multistep Processes

- For any task that involves multiple steps, especially complex, iterative, or long-running processes, immediately initialize a todo list using the `update_todo_list` tool with a single-level markdown checklist in the intended execution order.
- Status options: [ ] for pending (not started), [x] for completed (fully finished), [-] for in progress (currently being worked on).
- Update the todo list after each step or set of related steps to reflect progress: mark completed items as [x], set the next as [-] if starting it, and add new actionable items discovered during execution.
- This applies to **all modes**, including but not limited to code, architect, debug, and especially planning mode, to ensure structured, trackable progress and prevent loss of context in multistep workflows.
- In **planning mode**, integrate this built-in tool with existing project todo handling (e.g., plans/development-todo.md for user-facing todos): use `update_todo_list` for AI-internal multistep planning (e.g., iterative spec updates), while updating the .md file for overall project milestones via "todo" commands.
- Do not remove unfinished todos unless irrelevant; only mark as completed when fully accomplished without unresolved issues. If blocked, keep as [-] and add a resolution todo.
- When the entire task is complete (all todos [x]), use `attempt_completion` to finalize.

  
  ### Git Workflow

- Always commit and push after a logical set of changes, such as after completing any subtask, feature, or even a single file update like rules.md modifications. This applies to all phases, including planning—do not wait for major milestones.
- For AI-assisted changes (e.g., via Kilo Code modes), in modes that permit execute_command (e.g., Code, Debug, potentially Ask), automatically run git status to check for changes, then git add ., commit with descriptive message, and push at the end of each subtask that modifies tracked files. This ensures seamless version control without manual intervention where possible; fallback to manual for restricted modes like Architect/Orchestrator, where the assistant will confirm readiness but the user must execute the git add ., commit, and push commands.
- Err on the side of more commits than fewer, but ensure each commit is logical and meaningful (e.g., atomic changes with descriptive messages like "Add PantryItem model and tests").
- After completing any major planning or implementation phase, commit and push everything to main.
- If at any time you discover unstaged or uncommitted changes while working on something else, immediately commit those changes with a good summary message that includes a note of when and during what task you found them (e.g., 'Commit orphaned changes from initial setup found during planning review on 2025-09-17'). This prevents loss of work and maintains a clean history.
- Treat both code changes (e.g., .py, .ts, .js files with implementation or tests) and markdown documentation updates (e.g., .md files in plans/ for specs, outlines, or decisions) as equally worthy of individual commits and pushes, since they both represent meaningful progress in the iterative TDD and planning workflow.


### Documentation &amp; Visualization
- All project documentation and planning will be viewed on GitHub, so structure markdown files for optimal rendering there, following GitHub Markdown best practices to enhance readability for remote review (e.g., use clear headings, lists, and code blocks).
- Incorporate lots of diagrams using GitHub-supported formats like Mermaid for flowcharts, architecture diagrams, wireframes, etc., to visualize UX flows, data models, system architecture, and other key concepts (e.g., meal planning flow or DB schema).
- Place Mermaid diagrams in dedicated code blocks (```mermaid ... ```) within planning files to ensure proper rendering on GitHub, improving communication of complex ideas like user journeys or component interactions.

### Response Formatting
See [.kilocode/response-style.md](.kilocode/response-style.md) for guidelines on structured, readable outputs.

TODO: Review and expand as tech decisions solidify (link to plans/design-system.md).