# Open Questions 🤔

Tracked questions that need user decisions before implementation.

---

## OQ-1: Pantry "Staples" Concept

**Context:** User wants non-perishable items to be tracked differently — not as counted inventory but as "things I keep in stock." These items should be used when making recipes but explicitly verified during meal planning.

**Options:**
1. **Tag-based**: Add a "staple" flag to pantry items. Staples skip quantity tracking, show as "in stock" or "not in stock"
2. **Separate list**: New "Staples" section distinct from perishable pantry. Two views: Staples (salt, flour, oil) vs Perishables (milk, chicken, veggies)
3. **Hybrid**: Pantry items have a "type" field — `perishable` (track quantity/expiry) or `staple` (binary in-stock, verified during planning)

**Impact:** Database schema change, pantry UI rework, recipe ingredient matching, meal plan verification flow.

**Status:** ⏳ Awaiting user input

---

## OQ-2: Shopping List Autocomplete & Item Profiles

**Context:** User wants autocomplete when adding shopping items, sourced from common supermarket items AND history. Each item should build a profile over time with notes, pictures, aisle info, and taxonomy classification for aisle guessing.

**Questions:**
1. Where should the item taxonomy come from? (USDA food database? Custom seed list? User-built?)
2. How detailed should store/aisle info be at launch? (Just category? Specific aisle number? Per-store?)
3. Should item profiles be per-household or global?

**Impact:** New `item_profiles` table, autocomplete API endpoint, taxonomy seed data, shopping UI rework.

**Status:** ⏳ Awaiting user input

---

## OQ-3: Recipe Chat with AI

**Context:** User wants recipe creation via conversation with an AI agent, not manual forms. Two sources: (1) chat-based recipe crafting from requirements + ingredients, (2) saving favorites from meal plans.

**Questions:**
1. Which LLM provider to use? (Gemini, Claude, OpenAI — or multi-provider per D6?)
2. Should the chat happen in-app or redirect to an external agent?
3. What's the conversation flow? (User describes what they want → agent proposes → user refines → save?)

**Impact:** New chat UI, LLM integration, recipe creation pipeline.

**Status:** ⏳ Awaiting user input

---

## OQ-4: Infrastructure Blockers

**Context:** 6 scenarios remain blocked on infrastructure.

**Questions:**
1. Is Supabase Realtime running on the NAS Docker? (blocks INV-08, SHOP-08)
2. Are Gemini/OpenAI API keys available? (blocks VIS-01-03, IMG-01)
3. Can the backend reach external URLs? (blocks RCP-02 URL scraping)

**Status:** ⏳ Awaiting user input

---

## Answered Questions (Memorialized)

### AQ-1: Recipe Creation Method
**Decision:** No manual recipe creation. Only via AI conversation or meal plan favorites.
**Implemented:** Round 7 — removed manual entry form, added "Chat with AI" placeholder.

### AQ-2: Cooking Mode
**Decision:** Parked. Remove from active roadmap. Keep only PDF output + prompt copy.
**Implemented:** Round 7 — removed all cooking mode entry points.

### AQ-3: Voice Input on Shopping
**Decision:** Remove voice input button from shopping list.
**Implemented:** Round 7 — removed button.
