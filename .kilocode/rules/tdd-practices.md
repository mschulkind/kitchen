# TDD Practices

- **Test-First Workflow**: Write tests before implementation code. Start with unit tests for core functions (e.g., recipe matching algorithm), then integration tests for flows like meal planning to shopping list.
- **Fast Test Guidelines**: Ensure test suites run in under 1 second. Use mocking for external dependencies (e.g., LLM calls), parallel execution where possible, and avoid slow I/O in tests. Aim for 80%+ code coverage on critical paths like inventory verification.
- **Test Structure**: Backend tests in `tests/` mirroring source structure; frontend tests colocated with components. Include end-to-end tests for key UX flows using tools like Playwright if needed.