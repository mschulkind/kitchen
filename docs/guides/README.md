# 🔧 Guides — How-To Documentation

> Practical guides for developing, testing, deploying, and operating the Kitchen app.

---

## Available Guides

| Guide | Purpose |
|-------|---------|
| [Development Setup](development.md) | Local environment, Docker, backend/frontend dev, migrations |
| [Authentication Setup](authentication-setup.md) | Google OAuth configuration for local & production |
| [Data Loading](data-loading.md) | Database seeding, legacy recipe imports, backups |
| [Hosting on Synology](hosting-synology.md) | Full NAS deployment with Docker, HTTPS, Backblaze B2 |
| [Mobile Testing](mobile-testing.md) | Android emulator + Maestro E2E testing |
| [Testing Strategy](testing-strategy.md) | TDD practices, unit/integration/E2E approach |
| [Voice Assistant Setup](voice-assistant-setup.md) | Google Home/Alexa integration via IFTTT & Home Assistant |
| [Manual QA Guide](manual-qa-guide.md) | 30-minute click-by-click walkthrough of all features |

---

## Quick Start

1. **New developer?** Start with [Development Setup](development.md)
2. **Setting up auth?** See [Authentication Setup](authentication-setup.md)
3. **Deploying to NAS?** See [Hosting on Synology](hosting-synology.md)
4. **Running QA?** See [Manual QA Guide](manual-qa-guide.md)

---

## Common Commands

```bash
just check          # Run lint + test (always before commit!)
just test           # Run pytest
just up             # Start Docker stack
just down           # Stop Docker stack
just dev-api        # Run API locally (no Docker)
just mobile-web     # Start Expo for web
just coverage       # Check test coverage
```
