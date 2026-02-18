# 🗺️ Roadmap — Where We Are & Where We're Going

> The single source of truth for Kitchen app priorities, status, and vision.
> **Last Updated:** 2026-02-18

---

## 📊 Implementation Status

### Feature Readiness Matrix

| Feature Area | Backend | Frontend | Tests | Real Data | Status |
|-------------|---------|----------|-------|-----------|--------|
| 🔐 Auth & Accounts | ✅ | ✅ | ✅ | ✅ Google OAuth | **Production Ready** |
| 🏠 Dashboard Hub | ✅ | ✅ | ✅ | ✅ Live queries | **Production Ready** |
| 📦 Pantry Inventory | ✅ | ✅ | ✅ | ✅ CRUD works | **Needs Staples Feature** |
| 📖 Recipes (browse/import) | ✅ | ✅ | ✅ | ✅ URL import | **Production Ready** |
| 🤖 AI Recipe Chat | ❌ | ❌ | ❌ | ❌ | **Not Started** |
| 📅 Meal Planning | ✅ | ✅ | ✅ | ⚠️ Mock AI gen | **UI Complete, AI Mock** |
| 🛒 Shopping Lists | ✅ | ✅ | ✅ | ✅ Manual items | **Needs Autocomplete** |
| ⚙️ Settings | ✅ | ✅ | ✅ | ✅ | **Production Ready** |
| 🔄 Realtime Sync | ⚠️ | ⚠️ | ⚠️ | ⚠️ WS 404 | **Partially Wired** |
| 🧠 LLM Integration | ❌ | N/A | ❌ | ❌ | **Architecture Needed** |
| 🎰 Slot Machine Refinement | ✅ Refiner service | ⚠️ Basic lock/unlock | ❌ | ❌ | **Needs Full UI** |

### Test Health
- **Backend:** 409 tests passing ✅
- **Frontend:** 66 tests passing ✅
- **QA Scenarios:** 52/58 passing (90%) ✅
- **Bugs Fixed:** 23 across 7 QA rounds 🐛

---

## 🎯 Active Priorities

### Priority 1: AI Foundation 🧠
> *The core differentiator — everything else gets better once AI works.*

| Task | Spec | Effort | Notes |
|------|------|--------|-------|
| Build LLM provider abstraction | [#10](../specs/10-ai-llm-integration.md) | Medium | Interface + Ollama adapter |
| Wire Ollama to NAS/local | [#10](../specs/10-ai-llm-integration.md) | Small | Docker container or local install |
| Build recipe chat (basic) | [#05](../specs/05-recipe-ai-chat.md) | Large | Chat UI + backend + streaming |
| Replace mock plan generator | [#06](../specs/06-meal-planning.md) | Medium | Wire real LLM to plan generation |
| Wire recipe scoring algorithm | [#10](../specs/10-ai-llm-integration.md) | Small | Already built, needs frontend connection |

### Priority 2: Data Quality 📦
> *Make the existing features more useful with better data.*

| Task | Spec | Effort | Notes |
|------|------|--------|-------|
| Pantry staples flag | [#03](../specs/03-pantry-inventory.md) | Small | `is_staple` boolean + filter view |
| Recipe favorites | [#04](../specs/04-recipes.md) | Small | Star icon + filter + plan weighting |
| Shopping autocomplete | [#07](../specs/07-shopping-lists.md) | Medium | USDA taxonomy + fuzzy matching |
| Recipe tags/categories | [#04](../specs/04-recipes.md) | Small | Tag system for filtering |

### Priority 3: Infrastructure 🔧
> *Unblock the remaining test failures and enable real-world usage.*

| Task | Spec | Effort | Notes |
|------|------|--------|-------|
| Fix Realtime WebSocket | [#09](../specs/09-realtime-multiuser.md) | Medium | Debug WS 404, verify multi-user |
| Reconcile meal plan data models | [#06](../specs/06-meal-planning.md) | Medium | Frontend/backend table mismatch |
| Recipe URL import testing | [#04](../specs/04-recipes.md) | Small | Now that internet is available |

---

## 🔮 Vision: What's Next After Core AI

### Phase A: Smart Planning (After AI foundation works)
- **Slot Machine UI** — Full component-level lock/spin per the [spec](../specs/06-meal-planning.md#-the-slot-machine-granular-meal-refinement)
- **Card Stack Theme Selection** — Horizontal scroll of strategy cards with narrative pitches
- **Tweak Bar** — Sliders for Adventurousness, Effort, Pantry Usage, Health
- **Leftover Chain Planning** — AI suggests multi-day ingredient reuse (roast chicken → soup)
- **Context Export** — "Copy for AI" button for external LLM cooking help

### Phase B: Recipe Intelligence (After planning works)
- **Recipe PDF Export** — Beautiful printable cards with interleaved main+side timelines
- **Recipe Scaling** — Adjust servings, smart ingredient recalculation
- **Can/Package Size Tracking** — "1 can (14.5 oz) diced tomatoes"
- **Time-Based Filtering** — Quick filter for under 30 min, under 1 hour
- **Ingredient Confidence Review** — Show low-confidence parsed ingredients for user correction

### Phase C: Shopping Intelligence
- **Per-Store Aisle Mapping** — Configure aisle numbers for your store
- **Item Profiles** — Brand preferences, notes, photos per item
- **Purchase History** — Track what you buy, suggest repeat items
- **USDA Taxonomy** — Rich autocomplete with consumer-friendly names

### Phase D: Engagement & Delight 🎮
> *Inspired by apps like Mealime, Kitmate, Recipe Roulette, and Duolingo.*

- **Tinder-Style Recipe Swiping** — Swipe right to add to plan, left to skip. AI learns preferences.
- **Cooking Streaks** — Track consecutive days cooking at home. Badges: "Week Warrior 🏅", "Month Master 🎖️"
- **Family Voting** — Household members vote on proposed meals (👍/👎). "Dad's Pick of the Week" 🏆
- **Ingredient Challenges** — "Pantry Challenge": cook only with what you have. "Use It or Lose It": 3 expiring items.
- **Achievement System** — Badges for milestones (first import, 10th meal cooked, "Pasta Master" after 10 pasta dishes)
- **Global Tour** — Cook one dish from a different country each week, track your culinary passport 🌍

### Phase E: Advanced Features (Long-term)
- **Batch Cooking / Meal Prep Mode** — Unified prep timeline for multiple recipes
- **Multi-Household Support** — Switch between households
- **Smart Home Integration** — Kitchen timers, smart oven presets
- **Grocery Delivery Integration** — Export to Instacart, Amazon Fresh
- **Community Recipes** — Share recipes between households
- **Reactivate Cooking Mode** — Step-by-step with wake lock (code exists, entry points removed)
- **Reactivate Vision Scanning** — Photo-to-pantry (code exists, needs API key)
- **Reactivate Image Generation** — AI recipe photos (code exists, needs API key)

---

## 📈 Progress Timeline

| Date | Milestone |
|------|-----------|
| Dec 2025 | Project kickoff, Phase 0 markdown prototyping |
| Jan 2026 | Backend API for all 10 phases completed |
| Jan 12 | Frontend redesign to Hub & Spoke complete |
| Jan 16 | QA Round 1: Initial manual testing, first bugs found |
| Jan 19 | QA Round 2: OAuth & persistence blockers identified |
| Feb 16 | QA Rounds 3-6: 23 bugs fixed, quick wins + autonomous fixes |
| Feb 17 | QA Round 7: User feedback implementation, UI polish |
| Feb 18 | Documentation reorganization, idea consolidation |
| **Next** | **AI foundation: LLM provider + recipe chat** |

---

## 🤔 Key Open Questions

These decisions need to be made to move forward. Full list in [OPEN_QUESTIONS.md](../../OPEN_QUESTIONS.md) and in each spec.

| ID | Question | Impact |
|----|----------|--------|
| OQ-CHAT-01 | Which Ollama model? (Llama 3 vs Mistral) | Affects all AI features |
| OQ-AI-01 | How does backend access Ollama? (Same NAS? Docker?) | Blocks AI dev |
| OQ-PLN-01 | Reconcile meal plan data models (frontend vs backend) | Blocks plan AI |
| OQ-PLN-05 | Main + Side dish pairing: separate slots or bundled? | Affects Slot Machine UI |
| OQ-PLN-07 | Which gamification feature first? | Engagement priority |
| OQ-SHOP-01 | How to curate USDA data to ~2-5K items? | Blocks autocomplete |

---

## 💡 Competitive Landscape & Inspiration

> Research from similar apps (Mealime, Paprika, Whisk/Samsung Food, Eat This Much, MealPrepPro, Kitmate, Recipe Roulette)

| Feature | Who Does It Well | Our Take |
|---------|-----------------|----------|
| Pantry-aware planning | Kitmate, SuperCook | ✅ Built — pantry + scoring algorithm |
| AI recipe chat | Kitmate, Julia | 🔴 Our #1 priority — conversational creation |
| Smart grocery lists | Mealime, Whisk | ✅ Built — category grouping, realtime sync |
| Recipe import from URL | Paprika | ✅ Built — scraper pipeline |
| Offline-first | Paprika | 🟡 Optimistic UI built, needs polish |
| Social/family features | Whisk (Samsung Food) | 🟡 Realtime sync built, voting is future |
| Gamification | Recipe Roulette, Duolingo-style | ⏸️ Great ideas in spec, not yet built |
| Batch cooking | MealPrepPro | ⏸️ Future — "Prep Day" mode |
| Macro/nutrition | Eat This Much | ❌ Not in scope (personal cooking app) |
| Grocery delivery | Mealime, Whisk | ⏸️ Future — export to Instacart etc. |

### What Makes Kitchen Different
1. **Self-hosted** — Your data stays on your NAS, not in someone's cloud
2. **"Choose Your Own Adventure"** — AI proposes themed plan strategies, not just random meals
3. **Slot Machine refinement** — Granular lock/spin per dish component
4. **Leftover chains** — Multi-day ingredient reuse as a first-class concept
5. **Context Export** — Seamless hand-off to external AI for cooking help
6. **Open source, personal use** — No subscription, no ads, no data selling
