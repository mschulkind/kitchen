# 05 — AI Recipe Chat 🤖🍳

> Create recipes through conversation with an AI. Describe what you want, what you have, and let the AI propose, refine, and save recipes for you.

---

## Overview

This is the primary way users create new recipes in the Kitchen app. Instead of filling out forms, users have a natural conversation with an AI assistant. They describe constraints ("I have chicken thighs and broccoli, make something quick"), preferences ("my kids don't like spicy"), and context ("we're having guests"). The AI proposes recipes, the user refines them, and the final version is saved to their collection.

This is the most complex feature in the app and the core differentiator.

**Fun fact:** 🐋 If whales had AI recipe chat, every conversation would end with "How about krill? Again? Fine, krill it is." We aim for more variety. 🍽️

---

## User Stories

### US-CHAT-01: Start a Recipe Conversation
**As a** user who wants a new recipe,
**I want to** open a chat and describe what I'm looking for,
**So that** an AI can help me craft the perfect dish.

### US-CHAT-02: Use Pantry Context
**As a** user who wants to cook with what I have,
**I want to** the AI to know what's in my pantry,
**So that** it suggests recipes using available ingredients.

### US-CHAT-03: Specify Constraints
**As a** user with dietary needs or preferences,
**I want to** tell the AI about restrictions (vegetarian, kid-friendly, under 30 min, no mushrooms),
**So that** recipes fit my actual needs.

### US-CHAT-04: Refine Proposals
**As a** user reviewing an AI proposal,
**I want to** say "swap the broccoli for green beans" or "make it spicier,"
**So that** the recipe evolves to match what I actually want.

### US-CHAT-05: Save Recipe to Collection
**As a** user who likes a proposed recipe,
**I want to** save it to my recipe collection with one tap,
**So that** I can cook it later or add it to a meal plan.

### US-CHAT-06: Generate Multiple Options
**As a** user who wants choices,
**I want to** the AI to propose 2-3 options,
**So that** I can pick the one that sounds best.

### US-CHAT-07: Use Conversation History
**As a** user returning to a chat,
**I want to** see our previous conversation,
**So that** I can continue refining or start from where I left off.

### US-CHAT-08: Recipe from Leftovers
**As a** user with leftover ingredients from a previous meal,
**I want to** tell the AI what I have left over,
**So that** it suggests creative ways to use them up.

---

## User Flows

### Flow: New Recipe Conversation
1. User taps "+" on Recipes → selects "Chat with AI"
2. Chat screen opens with welcome message:
   > "Hey! 👋 What are you in the mood for? I can see your pantry and help you craft something great."
3. User types: "Something quick with chicken thighs, my kids are picky"
4. AI responds with 2-3 recipe proposals (summary cards):
   - 🍗 **Honey Garlic Chicken** — 25 min, 4 servings, pantry match: 85%
   - 🍝 **Chicken Alfredo** — 30 min, 4 servings, pantry match: 70%
   - 🥗 **Teriyaki Chicken Bowl** — 20 min, 4 servings, pantry match: 60%
5. User taps a proposal to expand it → sees ingredients, brief instructions
6. User says "I like the honey garlic but can you swap soy sauce for coconut aminos?"
7. AI adjusts and presents updated recipe
8. User taps "Save to Recipes" → recipe created with full structured data
9. Recipe appears in collection, ready for meal planning

### Flow: Pantry-Aware Suggestion
1. User opens chat
2. Types: "What can I make with what's in my fridge?"
3. AI queries pantry items → filters to fridge location
4. AI proposes recipes maximizing ingredient usage
5. Shows pantry match percentage and what's missing for each
6. User picks one → refines → saves

### Flow: Refine & Iterate
1. AI proposes a recipe
2. User: "Too much work, simplify it"
3. AI: Reduces steps, removes complex techniques
4. User: "Add a side dish"
5. AI: Suggests complementary side using remaining pantry items
6. User: "Perfect, save both"
7. Two recipes saved to collection

### Flow: Save as Favorite from Meal Plan
1. User cooks a meal from the planner
2. After cooking, prompt: "How was it? Save as favorite?"
3. User taps "Save as Favorite" → recipe flagged in collection
4. Favorites get priority in future meal plan generation

---

## UI Behavior

### Chat Screen
- **Message list:** Scrollable conversation history
- **User messages:** Right-aligned, colored bubbles
- **AI messages:** Left-aligned, with avatar icon
- **Recipe proposal cards:** Inline in chat, expandable:
  - Title + emoji
  - Time + servings + pantry match %
  - Expand to see ingredients + brief instructions
  - "Save to Recipes" button on each card
- **Input bar:** Text input + send button, bottom of screen
- **Context indicator:** Small badge showing "Using your pantry" when pantry data is active
- **Max-width:** 800px (desktop)

### Recipe Proposal Card (Inline)
```
┌─────────────────────────────────┐
│ 🍗 Honey Garlic Chicken        │
│ 25 min · 4 servings · 85% match│
│                                 │
│ [Expand ▼]                      │
│                                 │
│ Ingredients:                    │
│ · 4 chicken thighs ✅ (have)    │
│ · 3 tbsp honey ✅ (have)        │
│ · 2 tbsp soy sauce ⚠️ (low)    │
│ · 4 cloves garlic ✅ (have)     │
│                                 │
│ [Save to Recipes] [Modify]      │
└─────────────────────────────────┘
```

### Conversation Starters (Empty State)
When chat opens, show suggestion chips:
- "Use up what's expiring"
- "Quick weeknight dinner"
- "Something new and adventurous"
- "Meal prep for the week"
- "Kid-friendly dinner"

---

## Data Model

### `recipe_chats` Table (NEW)
```
recipe_chats
├── id: uuid (PK)
├── household_id: uuid (FK → households)
├── user_id: uuid (FK → auth.users)
├── title: text (auto-generated or user-named)
├── status: text ('active' | 'completed' | 'archived')
├── context: jsonb (pantry snapshot, preferences, constraints)
├── created_at: timestamp
└── updated_at: timestamp
```

### `recipe_chat_messages` Table (NEW)
```
recipe_chat_messages
├── id: uuid (PK)
├── chat_id: uuid (FK → recipe_chats)
├── role: text ('user' | 'assistant' | 'system')
├── content: text (message text)
├── metadata: jsonb (optional: recipe proposals, tool calls)
├── created_at: timestamp
└── updated_at: timestamp
```

### `recipe_proposals` Table (NEW, optional — could be in metadata)
```
recipe_proposals
├── id: uuid (PK)
├── message_id: uuid (FK → recipe_chat_messages)
├── title: text
├── summary: text
├── prep_time_minutes: integer
├── cook_time_minutes: integer
├── servings: integer
├── ingredients: jsonb[]
├── instructions: jsonb[]
├── pantry_match_percent: float
├── saved_as_recipe_id: uuid (FK → recipes, null until saved)
├── created_at: timestamp
└── updated_at: timestamp
```

---

## Technical Architecture

### LLM Integration
- **Development:** Ollama (local, self-hosted)
- **Production:** Multi-provider adapter (Gemini, Claude, OpenAI — per D6)
- **Backend endpoint:** `POST /api/v1/recipes/chat`
- **Streaming:** SSE or WebSocket for real-time token streaming
- **Context window:** System prompt + pantry snapshot + conversation history + user preferences

### System Prompt Design
The AI should:
1. Know the user's pantry contents (injected as context)
2. Know dietary preferences and dislikes (from user profile/settings)
3. Know household composition (adults, kids)
4. Respond with structured recipe data (not just text)
5. Calculate pantry match percentage
6. Suggest substitutions for missing ingredients
7. Support iterative refinement

### API Flow
```
Frontend                    Backend                     LLM
   │                           │                         │
   │ POST /recipes/chat        │                         │
   │ { message, chat_id }      │                         │
   │ ─────────────────────────>│                         │
   │                           │ Build prompt:           │
   │                           │ - system + pantry       │
   │                           │ - history + user msg    │
   │                           │ ────────────────────────>│
   │                           │                         │
   │                           │ <── streaming response ──│
   │ <── SSE stream ───────────│                         │
   │                           │                         │
   │ (render incrementally)    │ Parse structured output │
   │                           │ Save message + proposals│
   │                           │                         │
```

---

## Business Rules

1. **No recipe creation without AI** — the only path to new recipes is chat or URL import
2. **Pantry context is automatic** — AI always has access to current pantry state
3. **Recipes must be structured** — AI output is parsed into proper ingredient/instruction format before saving
4. **Conversation history preserved** — users can return to old chats
5. **Multiple proposals per turn** — AI should offer 2-3 options when proposing recipes
6. **Pantry match scoring** — each proposal shows what % of ingredients user already has
7. **Saved recipes are first-class** — once saved, they're identical to URL-imported recipes
8. **Preference learning** — over time, AI should learn user preferences (likes, dislikes, past favorites)

---

## Current State

| Feature | Status | Notes |
|---------|--------|-------|
| Chat UI | 🔴 Not started | Need chat screen |
| LLM integration | 🔴 Not started | Ollama adapter needed |
| System prompt design | 🔴 Not started | Need prompt engineering |
| Recipe proposals | 🔴 Not started | Structured output parsing |
| Save to collection | 🔴 Not started | Proposal → recipe conversion |
| Conversation persistence | 🔴 Not started | New tables needed |
| Pantry context injection | 🔴 Not started | Query + format for LLM |
| Streaming responses | 🔴 Not started | SSE or WebSocket |
| "Chat with AI" button | ✅ Built (Round 7) | Placeholder, disabled |

---

## 🧑‍🍳 Context Export: The "Chef's Chat" Bridge

> From the original planning-algorithm-and-ux.md — a power-user feature for using external AI assistants while cooking.

### The "Copy for AI" Feature

A prominent "Copy for AI" button on every Recipe and Plan view generates a rich, formatted prompt and copies it to the clipboard. The user can then paste it into their preferred external LLM (Gemini Advanced, ChatGPT, Claude) for real-time cooking help.

### Prompt Format

```text
You are my Sous Chef. Here is what I am cooking:

RECIPE: Chicken Tinga Tacos
- Servings: 4
- Ingredients: [List with user's specific brands/quantities]
- Steps: [Full instructions]

MY INVENTORY CONTEXT:
- I have: [Related pantry items, e.g., "Sour cream (low)"]

CURRENT STATE:
I am about to start. Please be ready to answer questions about 
substitutions, timing, or technique. Wait for my first question.
```

### Use Cases
- "Can I sub greek yogurt for sour cream?"
- "How do I know when the chicken is done?"
- "I'm running behind on the rice — what can I do?"
- "What wine pairs with this?"

### Implementation
- Backend: `POST /cooking/export/{recipe_id}` (already built!)
- Frontend: "Copy for AI" button → clipboard API
- Include pantry context and stock status in the export
- Optional: Include the full meal plan context if cooking multiple dishes

---

## 🧠 Prompt Engineering: System Prompt Design

### Core System Prompt Template

```text
You are a friendly, creative chef assistant for the Kitchen app.

HOUSEHOLD CONTEXT:
- Household size: {household_size}
- Dietary restrictions: {restrictions}
- Dislikes: {dislikes}
- Equipment: {equipment}

PANTRY CONTENTS (current):
{pantry_items_formatted}

CONVERSATION GUIDELINES:
1. Always propose 2-3 options when asked for recipe ideas
2. Calculate pantry match % for each proposal
3. Suggest substitutions for missing ingredients
4. Return structured JSON for recipe data (ingredients with qty/unit/name)
5. Be encouraging and fun — use food emojis
6. If the user seems indecisive, ask focused questions to narrow down
7. Consider ingredient reuse across meals
```

### Specialized Prompt Templates

1. **"Use What's Expiring"**: Prioritize items near expiry date
2. **"Garden Surplus"**: Focus on fresh garden produce
3. **"Low-Waste Leftover"**: Build on previous meals' leftovers
4. **"Budget-Friendly"**: Minimize shopping list additions
5. **"Kid-Friendly"**: Simple flavors, no spice, fun presentation ideas

---

## Open Questions

### OQ-CHAT-01: Ollama Model Selection
Which Ollama model should we use? Llama 3? Mistral? How much context window do we need for pantry + history?

### OQ-CHAT-02: Streaming vs. Batch
Should responses stream token-by-token (better UX) or return as complete messages (simpler)?

### OQ-CHAT-03: Structured Output Format
How do we ensure the LLM returns properly structured recipe data? JSON mode? Function calling? Post-processing?

### OQ-CHAT-04: Conversation Length
How many messages before we truncate history? Should old context be summarized?

### OQ-CHAT-05: Multi-Recipe Conversations
Can a single chat session produce multiple recipes? (e.g., "give me a main and a side")

### OQ-CHAT-06: Preference Persistence
Should user preferences (likes, dislikes) be stored in a profile table or inferred from conversation history?

### OQ-CHAT-07: Offline Behavior
What happens if the LLM is unavailable? Show error? Suggest URL import instead?

### OQ-CHAT-08: Cost / Rate Limiting
For cloud LLMs (production), how do we manage costs? Per-household rate limits?

### OQ-CHAT-09: Conversation Starters
Should the app suggest different conversation starters based on time of day, pantry state, or season? (e.g., "It's Friday — how about something special?" or "Your spinach expires tomorrow — let's use it!")

### OQ-CHAT-10: Recipe Comparison
When AI proposes 2-3 options, should there be a side-by-side comparison view? (Time, difficulty, pantry match, ingredients needed)
