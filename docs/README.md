# 📖 Kitchen App — Documentation Hub

> Your guide to understanding, building, and extending the Kitchen app. 🍳
> **Last Updated:** 2026-02-18

---

## 🗂️ Documentation Structure

| Directory | Purpose | Start Here |
|-----------|---------|------------|
| [**specs/**](specs/) | Feature specifications — what each feature SHOULD be | [specs/index.md](specs/index.md) |
| [**guides/**](guides/) | How-to guides for development, testing, deployment | [guides/README.md](guides/README.md) |
| [**architecture/**](architecture/) | Technical architecture, design system, UX flows, decisions | [architecture/README.md](architecture/README.md) |
| [**roadmap/**](roadmap/) | Current status, priorities, and future vision | [roadmap/README.md](roadmap/README.md) |
| [**qa/**](qa/) | QA tracking, test results, manual testing logs | [qa/README.md](qa/README.md) |
| [**obsolete/**](obsolete/) | Archived docs — kept for reference, may be deleted | [obsolete/README.md](obsolete/README.md) |

---

## 🚀 Quick Links

### For Developers (Human & Agent)
- **"What should I build next?"** → [Roadmap & Priorities](roadmap/README.md)
- **"How does feature X work?"** → [Feature Specs](specs/index.md)
- **"How do I set up the project?"** → [Development Guide](guides/development.md)
- **"What's the overall architecture?"** → [Architecture](architecture/README.md)
- **"What's the current test status?"** → [QA Tracker](qa/user-flow-tracker.md)

### For Decision-Making
- **"What decisions have been made?"** → [Architecture Decisions](architecture/decisions/)
- **"What's still undecided?"** → [Open Questions](../OPEN_QUESTIONS.md)
- **"What's parked for later?"** → [Parking Lot Spec](specs/11-parking-lot.md)

---

## 🐋 What Is Kitchen?

Kitchen is a **personal meal planning & grocery shopping app** for households that want to:
- 🧠 **Plan meals with AI** — "Choose Your Own Adventure" themed plans with a slot-machine refinement UX
- 📦 **Track pantry inventory** — Know what you have, what's expiring, what's a staple
- 🛒 **Generate smart shopping lists** — Only buy what you need, sorted by store aisle
- 👨‍👩‍👧 **Collaborate in real-time** — Multiple household members sharing lists, plans, and inventory
- 🤖 **Chat with AI to create recipes** — Describe what you want, AI crafts it using your pantry

### Tech Stack
- **Frontend:** Expo (React Native Web) + Tamagui UI
- **Backend:** FastAPI (Python) + Clean Architecture
- **Database:** Supabase (PostgreSQL + Realtime WebSockets)
- **AI:** Ollama (dev) → Multi-provider (Gemini/Claude/OpenAI)
- **Deployment:** Self-hosted Docker on Synology NAS

### Current Status (Feb 2026)
- ✅ **90% of core scenarios passing** (52/58 QA scenarios)
- ✅ **409 backend tests + 66 frontend tests**
- ✅ **7 rounds of QA completed**, 23 bugs fixed
- 🔴 **AI features not yet wired** (mock data only)
- 🟡 **Realtime sync partially working**

---

## 📐 Documentation Conventions

- **Emojis everywhere** 🎉 — Fun docs are read docs
- **Whale facts** 🐋 — Because why not
- **Specs are truth** — If it's not in a spec, it doesn't exist yet
- **Open Questions are explicit** — Decisions waiting are tagged with `OQ-` prefixes
- **Agent-friendly** — Clear structure, consistent formatting, no ambiguity
