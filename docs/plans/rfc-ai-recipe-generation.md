# RFC: AI Recipe Generation Feature 🤖🍳

> **Status:** Draft
> **Author:** Kitchen Team
> **Date:** 2025-07-18
> **Specs:** [05-recipe-ai-chat](../specs/05-recipe-ai-chat.md), [10-ai-llm-integration](../specs/10-ai-llm-integration.md)
> **Research:** [Strategic Direction Report](../research/strategic-direction-report.md), [Feature Reference Index](../research/feature-reference-index.md)

---

## Problem Statement

Kitchen's core value proposition is: **take preferences + pantry + constraints → dynamically generate recipes with an LLM**. This is Stage ② of the four-stage flywheel (Preferences → Generation → Shopping → Store Nav) and is the engine that makes everything else work.

Today, recipe generation is fully mocked. The plan generator returns hardcoded theme options. There is no LLM integration. This is the single most important feature to build.

**Fun fact:** 🐋 Sperm whales can hold their breath for 90 minutes while hunting in the deep ocean. We need our AI to generate a recipe faster than that. Shouldn't be hard. 🕐

---

## Competitive Context

| Competitor | How They Generate | Our Advantage |
|-----------|------------------|---------------|
| **ChefGPT** | PantryChef mode: all-in vs gourmet. User selects ingredients, utensils, time, skill level. LLM fine-tuned on recipe corpus. | Our Tweak Bar sliders + Adventure themes make it **fun**, not clinical. Plus we connect to pantry/shopping/planning. |
| **DishGen** | Chat-based iteration. "Make it spicier." "Swap chicken for tofu." 15 free recipes/month, premium unlimited. | We do this AND connect to meal planning and shopping. Full loop. |
| **SideChef** | Photo-based ingredient scanning → recipe matching. Adaptive pacing during cooking. B2B focus. | Consumer-focused, no hardware lock-in, household collaboration. |
| **SuperCook** | Database matching (NOT AI generation). Finds existing recipes that use your ingredients. | We CREATE novel recipes. LLM generates unique combinations, not just lookups. |
| **Ollie** | Black-box AI planning. User sets constraints, AI decides everything. No transparency. | Tweak Bar gives transparency. Slot Machine gives control. User sees WHY recipes were chosen. |

### What We Steal From Each
- **ChefGPT:** "All-In" vs "Gourmet" mode → Our "Pantry Challenge" vs "Fresh + Shopping" toggle
- **DishGen:** Chat-based iteration with natural language refinement → Our Micro-Direction concept
- **SideChef:** Multi-recipe timeline coordination → Our interleaved cooking timeline
- **Ollie:** Constraint-based planning with family awareness → Our household profile system

---

## Architecture

### High-Level Flow

```
                    ┌──────────────────────────────────────────────────┐
                    │                  FRONTEND                        │
                    │                                                  │
                    │  ┌─────────┐   ┌──────────┐   ┌──────────────┐ │
                    │  │ Chat UI │   │  Quick    │   │  Planner     │ │
                    │  │ (conv.) │   │  Generate │   │  Integration │ │
                    │  └────┬────┘   └─────┬─────┘   └──────┬───────┘ │
                    └───────┼──────────────┼────────────────┼──────────┘
                            │              │                │
                            ▼              ▼                ▼
                    ┌──────────────────────────────────────────────────┐
                    │              POST /api/v1/recipes/chat            │
                    │              POST /api/v1/recipes/generate        │
                    │              POST /api/v1/planner/generate-ai     │
                    └───────────────────────┬──────────────────────────┘
                                            │
                    ┌───────────────────────┼──────────────────────────┐
                    │                GENERATION ENGINE                  │
                    │                                                   │
                    │  ┌────────────┐  ┌─────────────┐  ┌───────────┐ │
                    │  │  Context   │  │   Prompt    │  │   Output  │ │
                    │  │  Builder   │  │   Engine    │  │   Parser  │ │
                    │  │            │  │             │  │           │ │
                    │  │ • pantry   │  │ • system    │  │ • JSON    │ │
                    │  │ • prefs    │  │ • few-shot  │  │   schema  │ │
                    │  │ • history  │  │ • user msg  │  │ • retry   │ │
                    │  │ • scores   │  │ • templates │  │ • Pydantic│ │
                    │  └─────┬──────┘  └──────┬──────┘  └─────┬─────┘ │
                    │        │                │                │       │
                    └────────┼────────────────┼────────────────┼───────┘
                             │                │                │
                    ┌────────┼────────────────┼────────────────┼───────┐
                    │        ▼                ▼                ▼       │
                    │              LLM PROVIDER ADAPTER                 │
                    │                                                   │
                    │  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
                    │  │ Anthropic│  │  OpenAI  │  │  Gemini  │       │
                    │  │ (Claude) │  │ (GPT-4o) │  │ (1.5Pro) │       │
                    │  └──────────┘  └──────────┘  └──────────┘       │
                    └──────────────────────────────────────────────────┘
```

### Three Entry Points into Generation

The AI serves three distinct user intents through one shared engine:

| Entry Point | Intent | Input | Output |
|-------------|--------|-------|--------|
| **Chat** (`/recipes/chat`) | "Help me figure out what to make" | Conversational messages + pantry context | Streaming chat with inline recipe proposal cards |
| **Quick Generate** (`/recipes/generate`) | "Just give me ideas NOW" | Preferences + pantry + constraints | 3 recipe proposals (no conversation) |
| **Planner Generate** (`/planner/generate-ai`) | "Plan my whole week" | Date range + constraints + Tweak Bar weights | 3 Adventure Path options, each with full week of meals |

All three share the same Context Builder, Prompt Engine, and LLM Provider. The difference is the prompt template and output schema.

---

## Component Design

### 1. LLM Provider Adapter

Pluggable multi-provider interface. Matches existing vision adapter pattern in `src/api/app/domain/vision/service.py`.

```python
# src/api/app/domain/llm/provider.py

from typing import Protocol, AsyncIterator

class LLMProvider(Protocol):
    """Swappable LLM provider interface."""
    
    async def generate(
        self, 
        messages: list[dict],  # [{"role": "system"|"user"|"assistant", "content": "..."}]
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: dict | None = None,  # JSON schema enforcement
    ) -> str: ...
    
    async def stream(
        self, 
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]: ...


class AnthropicProvider:
    """Claude adapter. Preferred for recipe generation (creative + structured)."""
    # Uses anthropic SDK
    # Supports response_format via tool_use for structured output
    
class OpenAIProvider:
    """GPT-4o adapter. Fallback provider."""
    # Uses openai SDK  
    # Supports response_format={"type": "json_schema", "json_schema": ...}

class GeminiProvider:
    """Gemini adapter. Already partially built for vision."""
    # Uses google-generativeai SDK
    # Supports response_mime_type="application/json"
```

**Provider selection strategy:**
- Recipe chat & generation: Claude (best at creative structured output)
- Vision tasks: Gemini (already built, good at image analysis)
- Fallback: OpenAI GPT-4o (most reliable structured JSON)
- Configuration via `LLM_PROVIDER_RECIPES` env var

### 2. Context Builder

Assembles all the context an LLM needs to generate a good recipe.

```python
# src/api/app/domain/llm/context.py

@dataclass
class RecipeGenerationContext:
    """Everything the LLM needs to know to generate recipes."""
    
    # Household info
    household_id: UUID
    household_size: int | None = None
    dietary_restrictions: list[str] = field(default_factory=list)
    dislikes: list[str] = field(default_factory=list)
    cuisine_preferences: list[str] = field(default_factory=list)
    
    # Pantry state (snapshot at request time)
    pantry_items: list[PantryItemSnapshot] = field(default_factory=list)
    expiring_soon: list[PantryItemSnapshot] = field(default_factory=list)  # within 3 days
    staples: list[str] = field(default_factory=list)  # always-available items
    
    # Constraints for this specific request
    max_prep_time_minutes: int | None = None
    max_cook_time_minutes: int | None = None
    effort_level: float = 0.5       # 0=lazy, 1=chef mode (from Tweak Bar)
    adventurousness: float = 0.5    # 0=safe, 1=wild (from Tweak Bar)
    pantry_priority: float = 0.5    # 0=buy fresh, 1=empty fridge (from Tweak Bar)
    health_priority: float = 0.5    # 0=comfort, 1=clean eating (from Tweak Bar)
    
    # Conversation history (chat mode only)
    message_history: list[dict] | None = None
    
    # Planning context (planner mode only)
    date_range: tuple[date, date] | None = None
    meals_per_day: list[str] | None = None
    locked_meals: list[dict] | None = None  # Meals already chosen (Slot Machine)
    
    # Learning signals
    favorite_recipe_ids: list[UUID] = field(default_factory=list)
    recently_cooked: list[str] = field(default_factory=list)  # titles, last 14 days


@dataclass
class PantryItemSnapshot:
    name: str
    quantity: float | None
    unit: str | None
    location: str  # fridge, freezer, pantry, counter, garden
    expiry_date: date | None
    is_staple: bool
    days_until_expiry: int | None


class ContextBuilder:
    """Assembles RecipeGenerationContext from database state."""
    
    def __init__(self, pantry_repo, recipe_repo, profile_repo):
        self.pantry_repo = pantry_repo
        self.recipe_repo = recipe_repo
        self.profile_repo = profile_repo
    
    async def build(
        self, household_id: UUID, overrides: dict | None = None
    ) -> RecipeGenerationContext:
        """Fetch pantry, preferences, history → build context."""
        # 1. Fetch pantry items
        # 2. Fetch household profile (dietary, dislikes, preferences)
        # 3. Fetch recently cooked recipes (last 14 days)
        # 4. Fetch favorite recipe titles (for variety avoidance)
        # 5. Identify expiring items (within 3 days)
        # 6. Apply any overrides from the request
        ...
```

### 3. Prompt Engine

Transforms context + user intent into LLM messages.

```python
# src/api/app/domain/llm/prompts.py

RECIPE_SYSTEM_PROMPT = """You are a creative, friendly chef assistant for Kitchen.

HOUSEHOLD CONTEXT:
- Household size: {household_size} people
- Dietary restrictions: {restrictions}
- Dislikes: {dislikes}
- Cuisine preferences: {cuisines}

CURRENT PANTRY ({pantry_count} items):
{pantry_formatted}

⚠️ EXPIRING SOON (use these first!):
{expiring_formatted}

ALWAYS-AVAILABLE STAPLES:
{staples_formatted}

RECENTLY COOKED (avoid repeats):
{recently_cooked}

STYLE SETTINGS:
- Effort level: {effort_label} ({effort_value}/10)
- Adventurousness: {adventure_label} ({adventure_value}/10)
- Pantry priority: {pantry_label} ({pantry_value}/10)
- Health priority: {health_label} ({health_value}/10)

RULES:
1. Propose 2-3 options when asked for recipe ideas
2. For each recipe, calculate what % of ingredients come from the pantry
3. Flag missing ingredients clearly
4. Suggest substitutions for missing items using what's in the pantry
5. Respect dietary restrictions absolutely — never violate these
6. Respect dislikes — avoid these unless explicitly asked
7. Prioritize expiring items when pantry_priority is high
8. When effort is low, keep recipes under 30 min with simple techniques
9. When adventurousness is high, suggest cuisines and techniques the user hasn't tried
10. Be encouraging, use food emojis, keep it fun 🎉
11. Always return recipe data as structured JSON when saving

OUTPUT FORMAT for recipe proposals:
Return a JSON object matching this schema:
{output_schema}
"""

QUICK_GENERATE_USER = """Give me {count} recipe ideas for {meal_type}.
{user_directive}"""

PLANNER_SYSTEM_ADDENDUM = """
PLANNING MODE:
You are generating a {days}-day meal plan. For each day, suggest a main dish{side_note}.
Create {num_options} distinct "Adventure Path" options:
- Each path should have a clear theme and personality
- Paths should feel MEANINGFULLY different from each other  
- Write a 1-2 sentence "pitch" for each path explaining why it's great
- Calculate total estimated shopping items for each path
- Calculate inventory usage % for each path

LOCKED MEALS (do not change these):
{locked_meals_formatted}
"""

REROLL_USER = """Re-roll {slot} for {date}.
Directive: {directive}
Keep these locked: {locked_summary}
Current theme: {current_theme}
Remaining pantry after locked meals: {remaining_pantry}"""
```

### 4. Output Parser

Validates and converts LLM output into app data structures.

```python
# src/api/app/domain/llm/output_parser.py

class RecipeProposal(BaseModel):
    """Structured recipe proposal from LLM output."""
    title: str
    description: str
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    difficulty: str  # "Easy" | "Moderate" | "Advanced"
    cuisine: str | None = None
    tags: list[str] = []
    ingredients: list[ProposalIngredient]
    instructions: list[str]
    pantry_match_percent: int  # 0-100
    missing_items: list[str]
    substitutions: list[Substitution] = []
    why_this_recipe: str  # LLM explains why it chose this

class ProposalIngredient(BaseModel):
    item_name: str
    quantity: float | None
    unit: str | None
    notes: str | None = None
    in_pantry: bool
    pantry_status: str  # "have" | "low" | "missing" | "expiring"

class Substitution(BaseModel):
    missing: str
    substitute: str
    rationale: str

class RecipeProposalSet(BaseModel):
    """Top-level response: 2-3 recipe proposals."""
    proposals: list[RecipeProposal]
    context_summary: str  # "Based on your chicken thighs and expiring broccoli..."

class PlanAdventurePath(BaseModel):
    """One complete meal plan option."""
    id: str
    title: str  # "The Efficiency Route"
    emoji: str  # "🏠"
    pitch: str  # "Roast chicken Monday, tacos Tuesday, soup Wednesday..."
    theme: str  # "efficiency" | "variety" | "healthy" | "adventure" | "comfort"
    days: list[PlanDay]
    total_shopping_items: int
    inventory_usage_percent: int
    estimated_difficulty: str

class PlanDay(BaseModel):
    date: str  # ISO date
    main: RecipeProposal
    side: RecipeProposal | None = None

class OutputParser:
    """Parse and validate LLM JSON output."""
    
    async def parse_proposals(self, raw: str) -> RecipeProposalSet:
        """Parse LLM output into RecipeProposalSet. Retry on failure."""
        # 1. Strip markdown code fences if present
        # 2. Parse JSON
        # 3. Validate against Pydantic schema
        # 4. If parse fails, send error back to LLM for self-correction (1 retry)
        # 5. If still fails, raise structured error
        ...
        
    async def parse_plan_options(self, raw: str) -> list[PlanAdventurePath]:
        """Parse LLM output into adventure path options."""
        ...
    
    def proposal_to_create_dto(self, proposal: RecipeProposal) -> CreateRecipeDTO:
        """Convert a proposal into a saveable recipe."""
        return CreateRecipeDTO(
            title=proposal.title,
            servings=proposal.servings,
            prep_time_minutes=proposal.prep_time_minutes,
            cook_time_minutes=proposal.cook_time_minutes,
            description=proposal.description,
            instructions=proposal.instructions,
            tags=proposal.tags + ["ai-generated"],
            ingredient_texts=[
                f"{i.quantity or ''} {i.unit or ''} {i.item_name}"
                f"{', ' + i.notes if i.notes else ''}".strip()
                for i in proposal.ingredients
            ],
        )
```

### 5. Recipe Generation Service

The orchestrator that ties it all together.

```python
# src/api/app/domain/llm/service.py

class RecipeGenerationService:
    """Orchestrates AI recipe generation across all entry points."""
    
    def __init__(self, provider, context_builder, output_parser, recipe_service):
        self.provider = provider
        self.context_builder = context_builder
        self.parser = output_parser
        self.recipe_service = recipe_service
    
    # ── Entry Point 1: Chat (Streaming) ──
    async def chat(
        self, 
        household_id: UUID, 
        chat_id: UUID,
        user_message: str,
        tweak_bar: TweakBarSettings | None = None,
    ) -> AsyncIterator[str]:
        """Streaming conversational recipe generation."""
        ctx = await self.context_builder.build(household_id, tweak_bar)
        history = await self._get_chat_history(chat_id)
        messages = self._build_chat_messages(ctx, history, user_message)
        async for chunk in self.provider.stream(messages, temperature=0.8):
            yield chunk
        # Save messages to DB (user + full assistant response)
        
    # ── Entry Point 2: Quick Generate ──
    async def quick_generate(
        self,
        household_id: UUID,
        meal_type: str = "dinner",
        count: int = 3,
        directive: str | None = None,
        tweak_bar: TweakBarSettings | None = None,
    ) -> RecipeProposalSet:
        """Non-conversational: return N recipe proposals immediately."""
        ctx = await self.context_builder.build(household_id, tweak_bar)
        messages = self._build_quick_messages(ctx, meal_type, count, directive)
        raw = await self.provider.generate(
            messages, 
            temperature=0.8,
            response_format=RecipeProposalSet.model_json_schema(),
        )
        return await self.parser.parse_proposals(raw)
    
    # ── Entry Point 3: Planner ──
    async def generate_plan_options(
        self,
        household_id: UUID,
        start_date: date,
        end_date: date,
        constraints: list[str],
        tweak_bar: TweakBarSettings | None = None,
        locked_meals: list[dict] | None = None,
        num_options: int = 3,
    ) -> list[PlanAdventurePath]:
        """Generate N distinct meal plan 'Adventure Paths'."""
        ctx = await self.context_builder.build(household_id, tweak_bar)
        ctx.date_range = (start_date, end_date)
        ctx.locked_meals = locked_meals
        
        scored = await self._score_existing_recipes(ctx)
        messages = self._build_planner_messages(ctx, constraints, scored, num_options)
        raw = await self.provider.generate(
            messages,
            temperature=0.9,  # Higher creativity for distinct paths
            max_tokens=8192,
        )
        return await self.parser.parse_plan_options(raw)
    
    # ── Entry Point 4: Slot Machine Reroll ──
    async def reroll_slot(
        self,
        household_id: UUID,
        plan_id: UUID,
        date: str,
        slot: str,  # "main" | "side" | "both"
        directive: str | None = None,
    ) -> RecipeProposal:
        """Reroll a single slot in a meal plan (the 🎰 spin)."""
        ctx = await self.context_builder.build(household_id)
        current_plan = await self._get_current_plan(plan_id)
        remaining_pantry = self._subtract_locked_meals(
            ctx.pantry_items, current_plan
        )
        messages = self._build_reroll_messages(
            ctx, current_plan, date, slot, directive, remaining_pantry
        )
        raw = await self.provider.generate(messages, temperature=0.9)
        proposals = await self.parser.parse_proposals(raw)
        return proposals.proposals[0]
    
    # ── Save Proposal as Recipe ──
    async def save_proposal(
        self,
        household_id: UUID,
        proposal: RecipeProposal,
    ) -> Recipe:
        """Convert an AI proposal into a saved recipe."""
        dto = self.parser.proposal_to_create_dto(proposal)
        return await self.recipe_service.create_recipe(household_id, dto)
```

---

## API Design

### New Endpoints

```
# Conversational recipe chat (streaming)
POST /api/v1/recipes/chat
  Body: { chat_id?, message, tweak_bar? }
  Response: SSE stream (text/event-stream)
  Events: { type: "token"|"proposal"|"done"|"error", data: ... }

# Quick recipe generation (non-streaming)
POST /api/v1/recipes/generate  
  Body: { meal_type?, count?, directive?, tweak_bar? }
  Response: { proposals: [...], context_summary: "..." }

# Save a proposal as a recipe
POST /api/v1/recipes/from-proposal
  Body: { proposal: RecipeProposal }
  Response: { recipe: Recipe }

# AI-powered plan generation (replaces mock generator)
POST /api/v1/planner/generate-ai
  Body: { start_date, end_date, constraints[], tweak_bar?, locked_meals?, num_options? }
  Response: { options: [PlanAdventurePath, ...] }

# Slot Machine reroll  
POST /api/v1/planner/{plan_id}/reroll
  Body: { date, slot, directive? }
  Response: { proposal: RecipeProposal, alternatives: [...] }

# Chat history
GET  /api/v1/recipes/chats
  Response: { chats: [...] }
GET  /api/v1/recipes/chats/{chat_id}
  Response: { chat: ..., messages: [...] }
```

### Tweak Bar Settings (shared across all endpoints)

```python
class TweakBarSettings(BaseModel):
    """Algorithm weight overrides from the Tweak Bar UI."""
    effort: float = Field(0.5, ge=0, le=1)         # 0=lazy, 1=chef mode
    adventurousness: float = Field(0.5, ge=0, le=1) # 0=safe, 1=wild
    pantry_priority: float = Field(0.5, ge=0, le=1) # 0=buy fresh, 1=empty fridge
    health: float = Field(0.5, ge=0, le=1)          # 0=comfort, 1=clean eating
```

---

## Data Model Changes

### New Tables

```sql
-- Household preferences (persistent across sessions)
CREATE TABLE household_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id UUID NOT NULL UNIQUE,
    household_size INT DEFAULT 2,
    dietary_restrictions TEXT[] DEFAULT '{}',    -- ['vegetarian', 'nut-free']
    dislikes TEXT[] DEFAULT '{}',                -- ['cilantro', 'mushrooms']
    cuisine_preferences TEXT[] DEFAULT '{}',     -- ['Italian', 'Mexican']
    default_servings INT DEFAULT 4,
    default_effort FLOAT DEFAULT 0.5,
    default_adventurousness FLOAT DEFAULT 0.5,
    default_pantry_priority FLOAT DEFAULT 0.5,
    default_health FLOAT DEFAULT 0.5,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Chat conversations
CREATE TABLE recipe_chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    household_id UUID NOT NULL,
    user_id UUID NOT NULL,
    title TEXT,                              -- Auto-generated from first message
    status TEXT DEFAULT 'active',            -- active | completed | archived
    pantry_snapshot JSONB,                   -- Frozen pantry at chat start
    tweak_bar_settings JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Chat messages
CREATE TABLE recipe_chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID NOT NULL REFERENCES recipe_chats(id) ON DELETE CASCADE,
    role TEXT NOT NULL,                      -- 'user' | 'assistant' | 'system'
    content TEXT NOT NULL,
    proposals JSONB,                        -- Structured recipe proposals (if any)
    token_count INT,                        -- For context window management
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Track recipe origin
ALTER TABLE recipes ADD COLUMN source_chat_id UUID REFERENCES recipe_chats(id);
ALTER TABLE recipes ADD COLUMN source_type TEXT DEFAULT 'import';
-- source_type: 'import' | 'ai_chat' | 'ai_quick' | 'ai_plan' | 'manual'
```

### Migration Notes
- `household_profiles` has sensible defaults — created lazily on first AI use
- `recipe_chats` + `recipe_chat_messages` follow standard chat pattern
- `recipes.source_type` tracks how recipes enter the system (analytics)
- Pantry snapshot in chat avoids stale context during long conversations

---

## Frontend Design

### Chat Screen (`/recipes/chat/[chatId]`)

```
┌──────────────────────────────────────────┐
│ ← AI Recipe Chat              ⚙️ Tweaks │
├──────────────────────────────────────────┤
│                                          │
│  🤖 Hey! 👋 What are you in the mood    │
│  for? I can see 23 items in your pantry  │
│  and your broccoli expires tomorrow! 🥦  │
│                                          │
│  ┌─ Quick Starts ──────────────────────┐ │
│  │ 🔥 Use what's expiring              │ │
│  │ ⚡ Quick weeknight dinner            │ │
│  │ 🌍 Something adventurous            │ │
│  │ 👶 Kid-friendly                     │ │
│  └──────────────────────────────────────┘ │
│                                          │
│                   Quick with chicken  👤 │
│                                          │
│  🤖 Here are 3 ideas using your chicken  │
│  thighs:                                 │
│                                          │
│  ┌──────────────────────────────────────┐ │
│  │ 🍗 Honey Garlic Chicken             │ │
│  │ 25 min · 4 servings · 87% pantry    │ │
│  │                                      │ │
│  │ "Uses your expiring broccoli as a    │ │
│  │  side. Only missing: soy sauce"      │ │
│  │                                      │ │
│  │ ▼ Show ingredients                   │ │
│  │                                      │ │
│  │ [💾 Save Recipe] [✏️ Modify]         │ │
│  └──────────────────────────────────────┘ │
│  ┌──────────────────────────────────────┐ │
│  │ 🌮 Chicken Tinga Tacos              │ │
│  │ 30 min · 4 servings · 72% pantry    │ │
│  │ ...                                  │ │
│  └──────────────────────────────────────┘ │
│                                          │
│         Make the first one spicier 👤    │
│                                          │
│  🤖 Done! Swapped regular soy sauce for │
│  chili garlic sauce (you have some in    │
│  the pantry! 🌶️)                        │
│  ┌──────────────────────────────────────┐ │
│  │ 🍗 Spicy Honey Garlic Chicken       │ │
│  │ 25 min · 4 servings · 92% pantry    │ │
│  │ [💾 Save Recipe] [✏️ Modify]         │ │
│  └──────────────────────────────────────┘ │
│                                          │
├──────────────────────────────────────────┤
│ [Message input...                ] [Send]│
└──────────────────────────────────────────┘
```

### Proposal Card (Expanded)

```
┌──────────────────────────────────────────┐
│ 🍗 Honey Garlic Chicken                 │
│ 25 min · 4 servings · 87% pantry match  │
│                                          │
│ "Uses your chicken thighs and the        │
│  broccoli that expires tomorrow"         │
│                                          │
│ Ingredients:                             │
│ ✅ 4 chicken thighs (have: fridge)       │
│ ✅ 3 tbsp honey (have: pantry)           │
│ ⚠️ 2 tbsp soy sauce (low!)              │
│ ✅ 4 cloves garlic (have: counter)       │
│ 🥦 1 head broccoli (EXPIRING!)          │
│ ❌ 1 tbsp sesame seeds (missing)         │
│    💡 Sub: crushed peanuts (you have!)   │
│                                          │
│ [💾 Save to Recipes] [🛒 Add Missing]   │
└──────────────────────────────────────────┘
```

### Tweak Bar (Slide-over panel from ⚙️ icon)

```
┌──────────────────────────────────────────┐
│ ⚙️ Generation Settings                  │
│                                          │
│ Effort                                   │
│ 😴 ─────────●─────────── 👨‍🍳             │
│    Lazy            Chef Mode             │
│                                          │
│ Adventurousness                          │
│ 🏠 ────●──────────────── 🌍             │
│    Safe              Wild                │
│                                          │
│ Pantry Priority                          │
│ 🛒 ──────────────●────── 🧹             │
│    Buy Fresh      Empty Fridge           │
│                                          │
│ Health                                   │
│ 🍔 ─────────●─────────── 🥗             │
│    Comfort        Clean Eating           │
│                                          │
│ [Reset to Defaults] [Save as My Default] │
└──────────────────────────────────────────┘
```

### Quick Generate (on Recipes screen)

A floating action button or prominent card on the recipes list:

```
┌──────────────────────────────────────────┐
│ ✨ Generate Recipe Ideas                 │
│                                          │
│ What kind of meal?                       │
│ [Dinner ▼]                               │
│                                          │
│ Any special requests?                    │
│ [e.g., "pasta night" or "use the fish"] │
│                                          │
│        [✨ Generate 3 Ideas]             │
└──────────────────────────────────────────┘
```

---

## Prompt Engineering Details

### Few-Shot Example (included in system prompt for reliable structured output)

```json
{
  "proposals": [
    {
      "title": "Lemon Herb Chicken Thighs",
      "description": "Crispy-skinned chicken with a bright lemon herb pan sauce.",
      "prep_time_minutes": 10,
      "cook_time_minutes": 25,
      "servings": 4,
      "difficulty": "Easy",
      "cuisine": "Mediterranean",
      "tags": ["quick", "one-pan", "kid-friendly"],
      "ingredients": [
        {"item_name": "chicken thighs", "quantity": 4, "unit": "pieces",
         "in_pantry": true, "pantry_status": "have"},
        {"item_name": "lemon", "quantity": 1, "unit": "whole",
         "in_pantry": true, "pantry_status": "expiring"},
        {"item_name": "fresh thyme", "quantity": 4, "unit": "sprigs",
         "in_pantry": false, "pantry_status": "missing"}
      ],
      "instructions": [
        "Pat chicken thighs dry and season generously with salt and pepper",
        "Heat olive oil in a large oven-safe skillet over medium-high heat",
        "Sear chicken skin-side down for 6 minutes until golden and crispy",
        "Flip, add lemon slices and thyme, transfer to 400°F oven for 15 min"
      ],
      "pantry_match_percent": 78,
      "missing_items": ["fresh thyme"],
      "substitutions": [
        {"missing": "fresh thyme", "substitute": "dried Italian herbs",
         "rationale": "Use 1 tsp dried herbs instead of fresh sprigs"}
      ],
      "why_this_recipe": "Uses your chicken thighs and the lemon expiring in 2 days."
    }
  ],
  "context_summary": "Based on 23 pantry items. Lemon and broccoli expire soon."
}
```

### Context Window Budget

| Component | Estimated Tokens | Notes |
|-----------|-----------------|-------|
| System prompt | ~600 | Fixed template + rules |
| Pantry snapshot | ~200-800 | Varies by pantry size |
| Preferences/restrictions | ~100 | Short lists |
| Few-shot example | ~400 | One complete example |
| Conversation history | ~2000 max | Last 10 messages, older summarized |
| User message | ~100 | Current turn |
| Response budget | ~3000 | 2-3 proposals with ingredients/instructions |
| **Total** | **~5000-7000** | Fits comfortably in any modern model |

### Truncation Strategy

1. If pantry > 50 items: group by location, show counts, list only the 20 most relevant (expiring + recently used)
2. If conversation > 10 messages: summarize messages 1-N as a single "conversation so far" block, keep last 5 verbatim
3. For planning prompts (which are larger): use 16K+ context models only

---

## Integration with Existing Systems

### Pantry → Generation
- Context Builder queries `pantry_items` table, groups by location, flags expiring
- Staple items marked as "always available" (don't need quantity tracking)
- After a recipe is cooked, pantry deduction updates context for next generation

### Generation → Shopping
- Each proposal includes `missing_items` and `substitutions`
- "Add Missing to Shopping List" button on proposal cards → creates shopping items
- Plan-level shopping: aggregate all missing items across a full week's plan

### Generation → Planner
- `generate_plan_options` returns full PlanAdventurePath objects
- User selects a path → meals inserted into `meal_plans` / `plan_slots`
- Locked meals excluded from reroll context
- Slot Machine reroll uses same generation engine with tighter constraints

### Scoring Algorithm Integration
The existing `RecipeScorer` (50% inventory, 30% spoilage, 20% freshness) is used as **pre-filtering** before the LLM:
1. Score all existing household recipes
2. Top 20 scored recipes included in the LLM prompt as "recipes you already have"
3. LLM can suggest existing recipes OR generate novel ones
4. Hybrid approach gives LLM awareness of the collection while allowing creativity

---

## Unique Kitchen Features (Our Moat 🏰)

### 1. The Tweak Bar
Nobody else has this. ChefGPT has rigid dropdowns. Ollie has no transparency. We give users **four expressive sliders** that directly influence generation:
- **Effort:** Controls recipe complexity, ingredient count, technique difficulty
- **Adventurousness:** Controls cuisine variety, unfamiliar ingredients, fusion recipes
- **Pantry Priority:** The spectrum from "shop for everything" to "use every last item"
- **Health:** From comfort food to nutritionist-approved

These map directly to prompt parameters AND visual feedback. Move a slider, see the results change.

### 2. The Slot Machine 🎰
Meal plan isn't take-it-or-leave-it. Each slot can be independently rerolled:
- Don't like Monday dinner? Tap 🎰, get a new one
- Hold Tuesday, reroll Wednesday
- Add a micro-direction: "something with pasta" → reroll with constraint
- The reroll is context-aware: remaining pantry after locked meals

### 3. Adventure Paths 🗺️
Instead of "here's your meal plan," we present 3 distinct themed paths:
- **The Efficiency Route 🏠** — Maximum pantry usage, minimum shopping
- **The Explorer's Path 🌍** — Try Thai Monday, Peruvian Tuesday, Moroccan Wednesday
- **The Balanced Way ⚖️** — Mix of familiar and new, all nutritionally sound

Each path shows: total shopping items, pantry usage %, difficulty level, and a compelling pitch.

### 4. Pantry-Aware Substitutions
When an ingredient is missing, we don't just say "missing." We check the pantry and suggest specific substitutions:
- ❌ "fresh thyme" → 💡 "You have dried Italian herbs — use 1 tsp instead"
- ❌ "heavy cream" → 💡 "You have coconut cream in the pantry — works for this sauce"

This closes the loop: the AI knows what you HAVE, not just what you NEED.

### 5. Conversation Memory
Each chat starts with a pantry snapshot and builds context over the conversation:
- "Make it spicier" → remembers the base recipe
- "Actually, my kid doesn't like that" → adjusts constraints for this session
- "What about a side dish?" → proposes sides that complement the main AND use pantry

---

## Implementation Plan

### Phase 1: Foundation
1. **LLM Provider adapter** — AnthropicProvider + OpenAIProvider + interface
2. **Context Builder** — fetch pantry, format for prompt
3. **Output Parser** — Pydantic schemas + JSON parsing + retry
4. **Quick Generate endpoint** — simplest entry point, no streaming
5. **Tests** — unit tests for parser, context builder, mock provider

### Phase 2: Chat
6. **Chat data model** — `recipe_chats` + `recipe_chat_messages` tables
7. **Chat endpoint with SSE streaming**
8. **Chat UI** — conversation screen with message bubbles
9. **Proposal cards** — inline recipe cards with expand/save/modify
10. **Save proposal** — proposal → recipe conversion + "ai-generated" tag

### Phase 3: Planner Integration
11. **Replace mock plan generator** — wire LLM to `generate_plan_options`
12. **Tweak Bar UI** — slider component + settings persistence
13. **Adventure Path cards** — update plan preview with LLM pitches
14. **Slot Machine reroll** — wire `reroll_slot` to LLM

### Phase 4: Polish
15. **Smart conversation starters** — context-aware based on pantry + time of day
16. **"Add missing to shopping list"** button on proposals
17. **Household profile management** — dietary, dislikes, cuisines screen
18. **Rate limiting** — per-household token budget tracking
19. **Error handling** — graceful degradation when LLM unavailable

---

## Open Questions

### OQ-RFC-01: LLM Provider for Recipes
**Context:** Claude excels at creative structured output. GPT-4o is most reliable at JSON schema adherence. Gemini is cheapest.
**Question:** Which provider should be primary for recipe generation?
**Recommendation:** Start with Claude (Anthropic). Fall back to GPT-4o if unavailable.

### OQ-RFC-02: Streaming for Chat
**Context:** SSE is simpler than WebSockets for one-way streaming. WebSocket is already partially wired for Supabase realtime.
**Question:** SSE or WebSocket for chat streaming?
**Recommendation:** SSE. Simpler, works with standard HTTP, chat is request-response not bidirectional.

### OQ-RFC-03: Novel Recipes vs. Existing Collection
**Context:** The LLM can generate completely novel recipes OR suggest from the user's existing collection.
**Question:** Prefer existing recipes or novel ones?
**Recommendation:** Hybrid. Include top-scored existing recipes in the prompt. Let LLM choose. Add toggle: "From my collection" vs "Surprise me."

### OQ-RFC-04: Token Cost Management
**Context:** As SaaS, LLM API costs are direct expenses. Single recipe chat turn costs ~$0.01-0.05.
**Question:** How to manage costs? Per-household limits? Tiered pricing?
**Recommendation:** 50 generations/month free tier, unlimited paid. Monitor before optimizing.

### OQ-RFC-05: Pantry Deduction After Cooking
**Context:** When a user cooks a recipe, should pantry auto-deduct ingredients?
**Question:** Auto-deduct (magical but inaccurate) or manual confirmation?
**Recommendation:** Prompt-based: "Used: ✅ chicken ✅ honey ❌ broccoli." One tap to confirm.

---

## Success Metrics

| Metric | Target | How Measured |
|--------|--------|-------------|
| Recipes generated/week | >5 per active household | `source_type = 'ai_*'` count |
| Chat turns to save | <5 messages average | Messages per saved-recipe chat |
| Proposal save rate | >30% of proposals | Proposals saved / proposals shown |
| Pantry match accuracy | >80% agreement | User confirms "in_pantry" flags |
| LLM parse success rate | >95% first attempt | JSON parse failures / total |
| P95 response latency | <8 seconds | Time to first proposal card |
| User satisfaction | >4/5 stars | Post-save rating prompt |

---

## Future Ideas 💡

These are captured from competitive research and spec brainstorming. Not in scope for initial implementation, but design should not preclude them:

- **Flavor Profile Learning:** Track which flavor profiles (sweet, spicy, umami, acidic) get saved vs rejected. Weight future generations accordingly.
- **Seasonal Awareness:** Time-of-year influences ingredient availability and recipe suggestions (pumpkin in fall, gazpacho in summer).
- **Leftover Chain Planning:** Monday's roast chicken → Tuesday's chicken salad → Wednesday's chicken soup. The LLM plans ingredient reuse across the week.
- **Photo-to-Pantry:** Take a photo of your fridge, LLM identifies items, adds to pantry. Already have vision adapter.
- **Collaborative Cooking:** Two households cooking together get merged pantry context.
- **Nutritional Targets:** "I need 150g protein today" → LLM generates to hit macros.
- **Budget Awareness:** Track grocery prices, suggest budget-friendly alternatives.
- **Cooking Skill Progression:** Start with easy recipes, gradually suggest more complex ones as user's history shows growth.
- **Recipe DNA:** Every AI-generated recipe gets a "DNA" fingerprint of cuisine, technique, flavor profile. Use for better recommendations.
- **Meal Prep Mode:** "I have 3 hours on Sunday" → batch cooking plan that yields 5 weeknight dinners.

---

> **Fun fact:** 🐋 Humpback whales "bubble net feed" — they blow bubbles in a circle to corral fish, then swim up through the center with mouths open. Our AI recipe generation is basically the same thing: corral the constraints (pantry, preferences, time), then swim through the middle and grab the best recipe. 🫧
