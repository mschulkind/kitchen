# 🧪 QA — Quality Assurance & Testing

> Tracking manual QA results, bug fixes, and test coverage across the Kitchen app.

---

## Documents

| Document | Purpose |
|----------|---------|
| [User Flow Tracker](user-flow-tracker.md) | **Central QA tracker** — 58 scenarios, pass/fail status, bug log |
| [logs/](logs/) | Historical manual testing session logs |

---

## Current Status (Feb 2026)

| Metric | Value |
|--------|-------|
| **Total Scenarios** | 58 |
| **Passing** | 52 (90%) |
| **Failing/Blocked** | 6 (10%) |
| **Bugs Found & Fixed** | 23 |
| **QA Rounds Completed** | 7 |
| **Backend Tests** | 409 passing |
| **Frontend Tests** | 66 passing |

### Blockers (5 remaining)
1. Realtime WebSocket — 404 on connection (Supabase config)
2. Gemini API key — Needed for vision/image features
3. Recipe URL import — Needs internet + scraper testing
4. Schema misalignment — Frontend/backend meal plan data models differ
5. AI features — All using mock data, need real LLM wiring

---

## Running QA

### Automated Tests
```bash
just check          # Lint + test (fast, always run before commit)
just test           # Backend pytest only
just coverage       # Coverage report
```

### Manual QA
See the [Manual QA Guide](../guides/manual-qa-guide.md) for a 30-minute click-by-click walkthrough of all features.

The [User Flow Tracker](user-flow-tracker.md) is the source of truth for what's passing and what's not.

---

## QA Session Logs

| Date | Session | Key Findings |
|------|---------|-------------|
| 2026-01-16 | [Log 1](logs/manual_testing_log.md) | Early testing protocol, first bugs found |
| 2026-01-19 | [Log 2](logs/manual_testing_log_2026-01-19.md) | OAuth & pantry persistence blockers identified |
| 2026-02-16+ | Rounds 3-7 | 23 bugs fixed, 90% pass rate achieved |
