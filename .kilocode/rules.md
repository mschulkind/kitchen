# Project Rules and Guidelines

## Tech Stack Choices
- **Backend**: Python with FastAPI (preferred for its speed and async support) or Flask as a lightweight alternative. Use for core logic including recipe selection, inventory management, and shopping list generation.
- **Frontend**: TypeScript for type-safe logic, React for UI components, Vite for fast builds and development server.
- **Styling**: Tailwind CSS for utility-first, responsive design that aligns with mobile-first principles.
- **Database**: SQLite for local development and simple persistence (e.g., storing pantry inventory, recipes); consider PostgreSQL for production if scaling to cloud hosting.
- **Testing**: pytest for Python backend (aim for sub-second test runs with fast fixtures); Vitest or Jest for TypeScript/React frontend tests.
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

  
  ### Git Workflow

- Always commit and push after a logical set of changes, such as after completing any subtask, feature, or even a single file update like rules.md modifications. This applies to all phases, including planning—do not wait for major milestones.
- For AI-assisted changes (e.g., via Kilo Code modes), the assistant will confirm readiness, but the user must execute the git add ., commit, and push commands manually if automated tools are unavailable in the current mode.
- Err on the side of more commits than fewer, but ensure each commit is logical and meaningful (e.g., atomic changes with descriptive messages like "Add PantryItem model and tests").
- After completing any major planning or implementation phase, commit and push everything to main.
- If at any time you discover unstaged or uncommitted changes while working on something else, immediately commit those changes with a good summary message that includes a note of when and during what task you found them (e.g., 'Commit orphaned changes from initial setup found during planning review on 2025-09-17'). This prevents loss of work and maintains a clean history.


### Documentation & Visualization
- All project documentation and planning will be viewed on GitHub, so structure markdown files for optimal rendering there, following GitHub Markdown best practices to enhance readability for remote review (e.g., use clear headings, lists, and code blocks).
- Incorporate lots of diagrams using GitHub-supported formats like Mermaid for flowcharts, architecture diagrams, wireframes, etc., to visualize UX flows, data models, system architecture, and other key concepts (e.g., meal planning flow or DB schema).
- Place Mermaid diagrams in dedicated code blocks (```mermaid ... ```) within planning files to ensure proper rendering on GitHub, improving communication of complex ideas like user journeys or component interactions.


TODO: Review and expand as tech decisions solidify (link to plans/design-system.md).