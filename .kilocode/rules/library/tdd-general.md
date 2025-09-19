# TDD Practices

- **Test-First Workflow**: Write tests before implementation code. Start with unit tests for core functions, then integration tests for key application flows.
- **Fast Test Guidelines**: Ensure test suites run in under 1 second. Use mocking for external dependencies, parallel execution where possible, and avoid slow I/O in tests. Aim for 80%+ code coverage on critical paths.
- **Test Structure**: Backend tests in `tests/` mirroring source structure; frontend tests colocated with components. Include end-to-end tests for key UX flows using tools like Playwright if needed.