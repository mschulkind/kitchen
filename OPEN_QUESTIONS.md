# Open Questions 🤔

Tracked questions that need user decisions before implementation.

---

## ~~OQ-1: Pantry "Staples" Concept~~ → Answered ✅

Moved to Answered Questions below.

---

## ~~OQ-2: Shopping List Autocomplete & Item Profiles~~ → Answered ✅

Moved to Answered Questions below.

---

## OQ-3: Recipe Chat with AI → Needs Full Spec 📋

**Context:** User wants recipe creation via conversation with an AI agent, not manual forms. Two sources: (1) chat-based recipe crafting from requirements + ingredients, (2) saving favorites from meal plans.

**Decision:** This is complex enough to warrant its own feature spec. See `docs/specs/05-recipe-ai-chat.md` for the full treatment.

**Key constraints from user:**
- Use Ollama for development (local LLM)
- Multi-provider support long-term (Gemini, Claude, OpenAI per D6)
- Backburner image generation and image processing for now
- Focus on LLM generation of recipe plans first

**Status:** 🔄 Being specced out in `docs/specs/05-recipe-ai-chat.md`

---

## ~~OQ-4: Infrastructure Blockers~~ → Answered ✅

Moved to Answered Questions below.

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

### AQ-4: Pantry Staples (was OQ-1)
**Decision:** Use a tag/checkbox (`is_staple`) on pantry items. Add a sort/filter view that splits staples from non-staples. NOT a separate list — just a boolean flag with a view option.
**Status:** To be implemented. See `docs/specs/03-pantry-inventory.md`.

### AQ-5: Shopping Autocomplete & Item Profiles (was OQ-2)
**Decision:**
- Use USDA database for taxonomy, but only user-friendly common names ("Bananas" not technical descriptions)
- Include aisle numbers where possible
- Categorization via KNN-style classification — specific enough that category predicts aisle
- Global profiles are minimal seed data, not user-editable
- Per-household overrides allowed for specific fields (notes, preferred brand, etc.)
**Status:** To be implemented. See `docs/specs/07-shopping-lists.md`.

### AQ-6: Infrastructure (was OQ-4)
**Decision:**
- Supabase Realtime: Now available, should work
- LLM: Use Ollama for development. Backburner image gen and image processing. Focus on LLM recipe generation.
- Internet: Full access available from backend
**Status:** Unblocks realtime testing & recipe URL import. Vision/image features remain parked.
