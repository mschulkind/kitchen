# 🍳 Kitchen MVP: Phase 0 Flow → In-App Experience

> **Goal:** Beeline to running the proven STK/Phase 0 meal planning flow entirely in the app, with real-time multi-user collaboration (you + your wife on your phones, debating dinner with an AI sous chef).

---

## 📍 Where We Are Today

### What Works (Phase 0 — the CLI/Agent Flow)
You've run **20+ successful meal plans** through the phase0 markdown flow. The workflow is proven:

1. **Request** → "3 dinners this week, use the chicken, kids are picky"
2. **Options** → Agent pitches 4-5 themed strategies (Efficiency Path, Global Tour, etc.)
3. **Verification** → Ingredient checklist cross-referenced against stock lists
4. **Final Plan** → Day-by-day recipes + consolidated shopping list + PDFs

This works *beautifully* as a human↔agent conversation. The value prop is validated.

### What's Built in the App
- ✅ Pantry/Inventory CRUD (replaces `stock_lists/`)
- ✅ Recipe management (view, import, edit, manual entry)
- ✅ Meal Planner UI (week view, add/remove meals)
- ✅ Shopping Lists (categorized, checkable)
- ✅ Cooking Mode (step-by-step, wake lock)
- ✅ 409 backend tests, 66 frontend tests
- ✅ Auth, Settings, Dashboard

### The Gap
- 🔴 **Zero real AI** — all LLM touchpoints are mocked
- 🔴 **No conversational flow** — can't have the phase0 "discussion" in the app
- 🔴 **No multi-user sync** — WebSocket 404, can't see changes in real-time
- 🔴 **No pantry-aware generation** — planner doesn't know what you have

---

## 🎯 The MVP: "Dinner Discussion" Mode

### What It Is
A focused chat-based experience where **two people on their phones** can have a conversation with an AI about what's for dinner — and the AI knows their pantry, preferences, and constraints. The exact phase0 flow, but live, collaborative, and in the app.

### The User Story (The Moment We're Designing For)

> 🐋 It's 4:30 PM. You're at your desk, your wife is picking up the kids. She texts "what's for dinner?" Instead of the usual "idk what do you want" death spiral, you both open Kitchen.
>
> You tap **"Plan Dinner"** and type: *"Use the chicken thighs in the fridge, something the kids will eat, under 45 mins."*
>
> Within seconds, the AI responds with 3 themed options — each showing what you already have vs. what you'd need to buy. Your wife sees the same options appear on her phone in real-time.
>
> She taps on Option B. "This one, but can we swap the broccoli for brussels sprouts? We have those."
>
> The AI adjusts. You both see the updated recipe. You tap "Looks good" → the ingredients you don't have flow into a shared shopping list. She grabs them on the way home. You start prepping.
>
> Total time from "what's for dinner" to "here's the plan": 3 minutes.

### The 4 Steps (Mapped from Phase 0)

| Phase 0 (CLI) | MVP (App) | How |
|:---|:---|:---|
| `01-request.md` | **Chat message** | User types constraints in chat. AI reads pantry + preferences automatically. |
| `02-options.md` | **Strategy cards in chat** | AI responds with 3 themed options as tappable cards. Both users see them live. |
| `03-verification.md` | **Inline ingredient checklist** | Tap an option → see ingredients with ✅/❌ from pantry. Mark corrections inline. |
| `04-final-plan.md` | **"Lock it in" action** | Tap "Use this plan" → recipes saved, shopping list generated, meal added to planner. |

---

## 🏗️ Technical Architecture (Minimal Viable Slice)

### What We Build (and What We Skip)

| Build | Skip (for now) |
|:---|:---|
| Single LLM provider (Claude API via Anthropic SDK) | Multi-provider adapter, Ollama, provider switching |
| Simple chat UI (message list + input) | Streaming tokens, fancy recipe cards |
| Supabase Realtime for chat sync | Presence indicators, typing indicators |
| Pantry snapshot → LLM context | Expiry-aware scoring, spoilage urgency |
| 3-option generation with structured JSON | Slot machine, tweak bar, lock/spin |
| Ingredient checklist with pantry cross-ref | Auto-substitution negotiation |
| One-tap "Lock it in" → shopping list | PDF generation, cooking mode integration |

### System Architecture

```
┌─────────────────────────────────────────────────────┐
│  Phone A (You)          Phone B (Wife)              │
│  ┌───────────┐          ┌───────────┐               │
│  │ Chat UI   │◄────────►│ Chat UI   │               │
│  │ (Expo)    │  Supabase│ (Expo)    │               │
│  └─────┬─────┘  Realtime└─────┬─────┘               │
│        │                      │                      │
│        └──────────┬───────────┘                      │
│                   ▼                                  │
│          ┌────────────────┐                          │
│          │  FastAPI        │                          │
│          │  /api/v1/chat   │                          │
│          │                 │                          │
│          │  ┌────────────┐ │                          │
│          │  │ Context    │ │  ┌──────────────┐       │
│          │  │ Builder    │─┼─►│ Claude API   │       │
│          │  │ (pantry +  │ │  │ (Anthropic)  │       │
│          │  │  prefs +   │ │  └──────────────┘       │
│          │  │  history)  │ │                          │
│          │  └────────────┘ │                          │
│          └────────┬────────┘                          │
│                   │                                   │
│          ┌────────▼────────┐                          │
│          │   Supabase      │                          │
│          │   (PostgreSQL)  │                          │
│          │   - chat_sessions│                         │
│          │   - chat_messages│                         │
│          │   - pantry_items │                         │
│          │   - recipes      │                         │
│          └─────────────────┘                          │
└─────────────────────────────────────────────────────┘
```

### New Backend Components

#### 1. LLM Service (`src/api/app/domain/llm/`)
```python
# Minimal: just Claude, just what we need
class ClaudeProvider:
    async def generate_meal_options(self, context: PlanningContext) -> MealOptions
    async def refine_option(self, context: PlanningContext, feedback: str) -> MealOption
    async def chat(self, context: PlanningContext, message: str) -> ChatResponse
```

#### 2. Planning Context Builder (`src/api/app/domain/planning/`)
```python
class ContextBuilder:
    async def build(self, household_id: str, request: str) -> PlanningContext:
        # Fetch pantry items → format as inventory summary
        # Fetch preferences → format as constraints
        # Fetch chat history → format as conversation
        # Return assembled prompt context
```

#### 3. Chat Session API (`src/api/app/routes/chat.py`)
```
POST /api/v1/chat/sessions          → Create new planning session
POST /api/v1/chat/sessions/:id/msg  → Send message (triggers LLM)
GET  /api/v1/chat/sessions/:id      → Get session with messages
POST /api/v1/chat/sessions/:id/lock → "Lock it in" → create meal + shopping list
```

#### 4. Database Tables (2 new)
```sql
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id UUID REFERENCES households(id),
    created_by UUID REFERENCES auth.users(id),
    title TEXT,
    status TEXT DEFAULT 'active',  -- active | completed
    context JSONB,                 -- pantry snapshot at session start
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id),
    user_id UUID,                  -- null for AI messages
    role TEXT NOT NULL,             -- 'user' | 'assistant' | 'system'
    content TEXT NOT NULL,
    metadata JSONB,                -- meal options, ingredient lists, etc.
    created_at TIMESTAMPTZ DEFAULT now()
);
```

### New Frontend Components

#### 1. Chat Screen (`src/mobile/app/(app)/chat/`)
- Message list with user/AI bubbles
- Text input bar
- Strategy cards rendered inline (tappable)
- Ingredient checklist view (when option tapped)
- "Lock it in" button

#### 2. Realtime Sync Hook
```typescript
// Both phones subscribe to the same chat session
const useChatSync = (sessionId: string) => {
  useEffect(() => {
    const channel = supabase
      .channel(`chat:${sessionId}`)
      .on('postgres_changes', {
        event: 'INSERT',
        table: 'chat_messages',
        filter: `session_id=eq.${sessionId}`
      }, (payload) => {
        queryClient.invalidateQueries({ queryKey: ['chat', sessionId] });
      })
      .subscribe();
    return () => supabase.removeChannel(channel);
  }, [sessionId]);
};
```

### LLM Prompt Strategy

Use the **proven phase0 prompts** — they already work. The system prompt assembles:

1. **Household context** (from settings/preferences)
2. **Current pantry** (from inventory, grouped by location)
3. **General preferences** (from `process.md` equivalent data — likes, dislikes, kids, composition rules)
4. **Conversation history** (from chat_messages)

The key prompt for Option Generation:
```
You are a meal planning assistant for a family kitchen.

HOUSEHOLD: {household_context}
PANTRY: {pantry_snapshot}
PREFERENCES: {preferences}

The user wants to plan meals. Generate 3 themed options.
For each option:
- A fun theme name with emoji
- Brief description of the strategy
- List of meals with estimated times
- Which pantry items it uses
- What new items would need to be purchased

Respond in JSON: { "options": [...] }
```

---

## 📋 Implementation Plan (Ordered by Dependency)

### Phase A: Foundation (Get AI Talking)
1. **LLM Provider** — Claude adapter with `generate()` and `generate_structured()`
2. **Context Builder** — Fetch pantry + preferences, format for LLM
3. **Chat API** — Sessions + messages CRUD, POST triggers LLM
4. **Basic prompt** — Port the proven phase0 system prompt

**Milestone:** `curl POST /api/v1/chat/sessions/123/msg -d '{"content":"plan 3 dinners, use the chicken"}' → AI responds with 3 options`

### Phase B: Chat UI (Get It On Screen)
5. **Chat screen** — Message list, input bar, basic styling
6. **Strategy cards** — Render AI options as tappable cards in the chat
7. **Navigation** — "Plan Dinner" button on dashboard → chat

**Milestone:** Open app → tap "Plan Dinner" → type request → see AI options on screen

### Phase C: Multi-User Sync (Both Phones)
8. **Supabase Realtime** — Fix WebSocket config OR use polling fallback
9. **Chat subscription** — Both users see new messages appear live
10. **Shared interaction** — Either user can tap options, send messages

**Milestone:** You type on your phone, wife sees it on hers. She picks an option, you see the selection.

### Phase D: Lock It In (Complete the Loop)
11. **Ingredient checklist** — Show what's in pantry vs. what's needed
12. **"Lock it in" action** — Selected option → create recipes + shopping list
13. **Shopping list generation** — Only items not in pantry

**Milestone:** Full flow: Request → Options → Pick → Shopping list. The phase0 loop, in app, collaborative.

---

## 🗺️ Post-MVP Roadmap

### Wave 1: Polish the Core Loop 🌊
*Make the MVP experience delightful.*

| Feature | Description | Why |
|:---|:---|:---|
| **Streaming responses** | Token-by-token AI responses via SSE | Feels alive, not waiting |
| **Rich recipe cards** | Expandable cards with ingredients, time, pantry match % | Better decision-making |
| **Typing indicators** | Show when AI is thinking, when partner is typing | Social presence |
| **Conversation starters** | Smart chips: "Use what's expiring", "Quick weeknight", "Adventurous" | Reduce blank-page anxiety |
| **Session history** | Browse past planning conversations | "What did we decide last Tuesday?" |

### Wave 2: The Intelligence Layer 🧠
*Make the AI smarter about YOUR kitchen.*

| Feature | Description | Why |
|:---|:---|:---|
| **Expiry-aware suggestions** | "Your spinach expires tomorrow — let's use it!" | Reduce waste (unique differentiator) |
| **Leftovers chaining** | "You'll have leftover chicken — here's what to do with it tomorrow" | Multi-day intelligence |
| **Taste memory** | Post-meal 👍/😐/👎 ratings that inform future suggestions | Personalization flywheel |
| **Substitution negotiation** | "I don't have soy sauce" → "Use coconut aminos, same amount" | In-conversation flexibility |
| **Kid meal extraction** | Auto-suggest deconstructed kid portions from adult meals | Family-specific value |

### Wave 3: The Adventure UX 🎮
*The "Choose Your Own Adventure" experience from the design docs.*

| Feature | Description | Why |
|:---|:---|:---|
| **Tweak Bar sliders** | Adventurousness / Effort / Pantry Usage controls | Tactile, fun, unique UX |
| **Slot Machine** | Lock meals you like, spin the rest | Gamification of planning |
| **Strategy Paths** | Full card-stack UI for themed plan selection | Visual storytelling |
| **Multi-day planning** | Plan a whole week with ingredient reuse optimization | Bigger value unlock |
| **"Copy for AI" export** | Clipboard prompt for external LLM cooking help | Bridge to cooking mode |

### Wave 4: The Full Flywheel 🔄
*Connect all the pieces into a self-reinforcing loop.*

| Feature | Description | Why |
|:---|:---|:---|
| **Auto-pantry deduction** | After cooking, ingredients auto-deducted | Keep inventory accurate |
| **Smart restock** | "You're low on olive oil" → auto-add to shopping | Proactive pantry management |
| **Recipe import from chat** | AI-generated recipes saved as first-class recipes | Growing recipe collection |
| **Store-optimized shopping** | Category-sorted lists matching your store's layout | Faster shopping trips |
| **Multi-provider LLM** | Switch between Claude/GPT/Gemini/Ollama | Flexibility, cost control |
| **Offline chat history** | View past plans without connectivity | Cooking doesn't need internet |

### Wave 5: The Social Kitchen 👥
*Multi-household and community features.*

| Feature | Description | Why |
|:---|:---|:---|
| **Household roles** | Owner / Editor / Viewer permissions | Privacy and control |
| **Shared recipe collections** | Share favorites between households | Social discovery |
| **Meal plan templates** | Save and reuse successful plans | Efficiency for regulars |
| **Notification alerts** | "Your partner added items to the shopping list" | Stay in sync |

---

## 🔑 Key Technical Decisions for MVP

### Why Claude API (not Ollama)?
- **Speed to MVP**: No infrastructure setup, just an API key
- **Quality**: Claude excels at structured JSON output and creative cooking content
- **Proven**: The phase0 prompts already work with Claude (that's what's been generating the plans!)
- **Later**: Add Ollama/multi-provider when the UX is validated

### Why Supabase Realtime (not custom WebSocket)?
- **Already there**: Supabase is the database, realtime is built in
- **Simple**: Just subscribe to `chat_messages` table changes
- **Multi-user**: Both phones get INSERT events automatically
- **Fallback**: If Realtime is still broken, polling every 2s works for MVP

### Why Chat UI (not the full Slot Machine)?
- **Fastest path**: Chat is the simplest interactive UI to build
- **Proven pattern**: The phase0 flow IS a conversation — chat maps 1:1
- **Extensible**: Cards, checklists, and actions can all render inside chat bubbles
- **Later**: Slot Machine, Tweak Bar etc. are Wave 3 enhancements

---

## 📊 Scope Estimate

| Phase | New Files | Lines of Code (est.) | Dependencies |
|:---|:---|:---|:---|
| A: Foundation | 6-8 backend | ~500 | `anthropic` pip package |
| B: Chat UI | 4-5 frontend | ~600 | None new |
| C: Multi-User | 1-2 hooks | ~100 | Supabase Realtime (existing) |
| D: Lock It In | 2-3 each side | ~400 | Existing shopping/recipe APIs |
| **Total** | **~15-18 files** | **~1,600 LOC** | **1 new pip dependency** |

---

## 💡 What Makes This Proposal Strong

1. **Proven workflow**: We're not inventing — we're digitizing 20+ successful phase0 runs
2. **Minimal new code**: ~1,600 LOC leveraging everything already built (pantry, recipes, shopping)
3. **The right LLM**: Claude already generates great plans — same brain, new interface
4. **Multi-user from day 1**: The "what's for dinner" conversation IS multi-user by nature
5. **Clear upgrade path**: Each wave adds value without rewriting — chat → cards → slot machine
6. **No infrastructure yak-shaving**: Cloud API + existing Supabase = zero new infra

The fastest distance between "agent generates markdown plans" and "both phones show dinner options" is a chat screen that talks to Claude and syncs through Supabase. Everything else is polish. 🐋✨
