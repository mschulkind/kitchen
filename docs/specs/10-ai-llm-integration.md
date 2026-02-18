# 10 — AI / LLM Integration 🧠

> Cross-cutting AI capabilities: recipe chat, meal plan generation, ingredient parsing, substitutions, and the multi-provider adapter.

---

## Overview

AI is woven through the Kitchen app at multiple levels. It's not a single feature — it's an enabler for recipes (chat creation), planning (smart generation), shopping (categorization), and cooking (substitution hints). This spec covers the shared AI infrastructure: provider abstraction, prompt engineering patterns, context management, and the Ollama-first development approach.

**Fun fact:** 🐋 Whale brains weigh up to 9kg and have more neocortical neurons than humans. Our LLM integration aspires to similar culinary intelligence, if not quite the same hardware. 🧠

---

## Architecture

### Multi-Provider Adapter (Decision D6)
```
                    ┌──────────────┐
                    │   LLM Router │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────▼──────┐  ┌─────▼──────┐  ┌──────▼──────┐
   │   Ollama    │  │   Gemini   │  │   OpenAI    │
   │  (dev/self) │  │  (cloud)   │  │  (cloud)    │
   └─────────────┘  └────────────┘  └─────────────┘
```

### Provider Interface
```python
class LLMProvider(Protocol):
    async def generate(self, prompt: str, system: str, **kwargs) -> str: ...
    async def generate_structured(self, prompt: str, schema: dict, **kwargs) -> dict: ...
    async def stream(self, prompt: str, system: str, **kwargs) -> AsyncIterator[str]: ...
```

### Current LLM Touchpoints

| Feature | Where | What AI Does | Status |
|---------|-------|-------------|--------|
| Recipe Chat | `/api/v1/recipes/chat` | Conversational recipe creation | 🔴 Not started |
| Meal Plan Gen | `/api/v1/planner/generate` | Generate 3 thematic plan options | ⚠️ Mock only |
| Ingredient Parsing | `/api/v1/recipes/parse-*` | Parse "1 large onion, diced" → structured | ✅ Built (rule-based) |
| Category Guessing | Shopping add item | Assign grocery category from name | ✅ Built (keyword) |
| Substitution Hints | Cooking context | "Use fish sauce instead of soy" | ⚠️ Mock only |
| Recipe Scoring | `/api/v1/planner/score-recipes` | Rate recipes by pantry match | ✅ Built (algorithmic) |
| Image Generation | `/api/v1/recipes/*/generate-image` | Create recipe photos | ⏸️ Parked |
| Vision Analysis | `/api/v1/vision/analyze` | Identify food from photo | ⏸️ Parked |

---

## Ollama Integration (Development)

### Setup
- **Model:** TBD — likely Llama 3.1 8B or Mistral 7B for development
- **Hosting:** Local or NAS Docker container
- **API:** HTTP at `http://{host}:11434/api/generate`
- **Context window:** 8K-32K tokens depending on model

### Configuration
```python
# src/api/app/core/config.py
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # ollama | gemini | openai
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
```

### Adapter Pattern
```python
class OllamaProvider:
    async def generate(self, prompt, system, **kwargs):
        response = await httpx.post(f"{self.base_url}/api/generate", json={
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "format": kwargs.get("format", None),  # "json" for structured
        })
        return response.json()["response"]
    
    async def stream(self, prompt, system, **kwargs):
        async with httpx.stream("POST", f"{self.base_url}/api/generate", json={
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": True,
        }) as response:
            async for line in response.aiter_lines():
                data = json.loads(line)
                if not data.get("done"):
                    yield data["response"]
```

---

## Prompt Engineering

### System Prompt Template (Recipe Chat)
```
You are a creative home cook assistant for a family kitchen app.

HOUSEHOLD CONTEXT:
- Adults: {adults_count}, Kids: {kids_count}
- Dietary: {dietary_restrictions}
- Dislikes: {dislikes}
- Preferred cooking style: {style_preferences}

CURRENT PANTRY ({item_count} items):
{pantry_items_formatted}

RULES:
1. Suggest recipes using available pantry items when possible
2. Always include a vegetable component
3. Respect dietary restrictions and dislikes
4. Format recipe proposals as structured JSON
5. Calculate pantry match percentage
6. Suggest substitutions for missing ingredients
7. Keep instructions concise and actionable
```

### Structured Output Schema (Recipe Proposal)
```json
{
  "proposals": [
    {
      "title": "Honey Garlic Chicken Thighs",
      "description": "Crispy chicken with a sweet-savory glaze",
      "prep_time_minutes": 10,
      "cook_time_minutes": 25,
      "servings": 4,
      "ingredients": [
        {"item_name": "chicken thighs", "quantity": 4, "unit": "pieces", "in_pantry": true},
        {"item_name": "honey", "quantity": 3, "unit": "tbsp", "in_pantry": true},
        {"item_name": "soy sauce", "quantity": 2, "unit": "tbsp", "in_pantry": false}
      ],
      "instructions": [
        "Pat chicken thighs dry and season with salt and pepper",
        "Heat oil in a large skillet over medium-high heat",
        "..."
      ],
      "pantry_match_percent": 85,
      "missing_items": ["soy sauce"],
      "substitutions": [{"missing": "soy sauce", "substitute": "coconut aminos"}],
      "tags": ["quick", "kid-friendly"]
    }
  ]
}
```

### Context Window Management
1. **System prompt:** ~500 tokens (fixed)
2. **Pantry snapshot:** ~200-500 tokens (variable, summarize if large)
3. **Conversation history:** Last 10 messages, ~2000 tokens
4. **User message:** ~100 tokens
5. **Response budget:** ~2000 tokens
6. **Total:** ~3000-5000 tokens per turn (fits in 8K context)

**Truncation strategy:** If pantry > 50 items, group by location and show counts. If history > 10 messages, summarize older ones.

---

## Business Rules

1. **Ollama for development** — no cloud API costs during dev
2. **Provider is configurable** — env var switches between Ollama/Gemini/OpenAI
3. **Structured output required** — AI responses must be parseable JSON for recipe saving
4. **Graceful degradation** — if LLM unavailable, show error + suggest URL import instead
5. **Context is fresh** — pantry snapshot taken at conversation start, refreshed on demand
6. **No hallucinated ingredients** — AI should flag when it suggests something not in pantry
7. **Rate limiting** — max N requests per household per hour (configurable)
8. **Prompt versioning** — system prompts stored as templates, versioned for A/B testing

---

## Current State

| Feature | Status | Notes |
|---------|--------|-------|
| Provider abstraction | ❌ Not built | Need interface + adapters |
| Ollama adapter | ❌ Not built | Pending Ollama availability |
| Gemini adapter | ⚠️ Partial | Image gen exists, needs generalization |
| OpenAI adapter | ❌ Not built | Future |
| Structured output | ❌ Not built | Need JSON schema enforcement |
| Streaming support | ❌ Not built | SSE/WebSocket |
| Context management | ❌ Not built | Pantry snapshot + history |
| Prompt templates | ❌ Not built | System prompt versioning |
| Mock provider | ✅ Built | Returns fake data for testing |
| Ingredient parsing | ✅ Built | Rule-based, could be LLM-enhanced |
| Category guessing | ✅ Built | Keyword-based |
| Recipe scoring | ✅ Built | Algorithmic |

---

## 📊 Recipe Scoring Algorithm

> From the original phase-05 spec and planning-algorithm-and-ux.md — the math behind smart recipe selection.

### Scoring Dimensions

Each recipe in the database is scored across multiple dimensions when generating meal plans:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| **Pantry Match** | 40% | What % of ingredients does the user already have? |
| **Spoilage Urgency** | 20% | Does it use ingredients that are about to expire? |
| **Effort Match** | 15% | Does prep/cook time match the user's request? |
| **Preference Match** | 15% | Does it align with dietary prefs, cuisine biases, favorites? |
| **Novelty** | 10% | Has the user cooked this recently? Variety bonus for new recipes. |

### Scoring Formula

```python
def score_recipe(recipe, pantry, preferences, request):
    # Pantry match: % of ingredients available
    pantry_score = matching_ingredients / total_ingredients
    
    # Spoilage: bonus for using expiring items
    spoilage_score = sum(
        1.0 / max(days_until_expiry(item), 1)  
        for item in matching_expiring_items
    ) / total_ingredients
    
    # Effort: penalty for mismatch with requested effort level
    effort_score = 1.0 - abs(recipe.effort_level - request.effort) / max_effort
    
    # Preference: bonus for matching cuisine, dietary, favorites
    pref_score = (
        cuisine_match * 0.4 + 
        dietary_match * 0.4 + 
        is_favorite * 0.2
    )
    
    # Novelty: penalty for recently cooked
    novelty_score = min(days_since_last_cooked / 14, 1.0)
    
    return (
        pantry_score * 0.40 +
        spoilage_score * 0.20 +
        effort_score * 0.15 +
        pref_score * 0.15 +
        novelty_score * 0.10
    )
```

### Scoring Context

The Tweak Bar sliders (from spec 06) directly modify these weights. "Empty Fridge" mode cranks Pantry Match to 60%. "Wild" mode cranks Novelty to 30%.

---

## 🔮 Prompt Templates Library

> From the original design-system.md — standardized prompts for all AI interactions.

### 1. Basic Meal Plan Generation
```
You are a meal planning assistant. Generate a {days}-day meal plan for 
{servings} people, using as many of these pantry items as possible: 
{pantry_list} and garden items: {garden_list}. Prioritize ingredient 
reuse and simple recipes (under 45min prep). Exclude {diet_restrictions}. 
Output valid JSON: {days: [{day, recipe_name, ingredients_used, 
new_shopping_list_items, instructions}]}
```

### 2. Recipe Substitution & Customization
```
You are a recipe customization assistant. The user wants to make 
'{recipe_name}' which requires {full_ingredients_list}. They only have: 
{available_pantry}. Suggest substitutions for missing ingredients. 
Consider dietary preferences: {prefs}. Output JSON: {original_recipe, 
substitutions: [{original, substitute, rationale}], adjusted_instructions, 
nutritional_notes}
```

### 3. Low-Waste Plan with Leftovers
```
You are a waste-reduction assistant. Create a 3-day meal plan that 
minimizes food waste. Use leftovers from: {previous_meals} and pantry: 
{pantry_list}. Focus on {cuisine_pref} recipes. Output JSON: {days: 
[{day, recipe_name, uses_leftovers_from, shopping_list_additions}]}
```

### 4. Garden Surplus Optimization
```
You are a garden-to-table assistant. Suggest 2-3 recipes using garden 
surplus: {garden_items_with_quantities}. Supplement with staples: 
{pantry_staples}. Respect: {diet_restrictions}. Output JSON: {recipes: 
[{recipe_name, key_garden_ingredients, full_ingredient_list, instructions, 
prep_time_minutes}]}
```

### 5. Ingredient Parser (LLM-Enhanced)
```
Parse this ingredient line into structured data. Return JSON:
{quantity, unit, item_name, notes, section, confidence}

Input: "{raw_ingredient_text}"
Examples:
- "1 large onion, diced" → {quantity: 1, unit: "large", item_name: "onion", notes: "diced"}
- "2 cans (14.5 oz) diced tomatoes" → {quantity: 2, unit: "can (14.5 oz)", item_name: "diced tomatoes"}
```

---

## Open Questions

### OQ-AI-01: Ollama Access
How will the backend access Ollama? Same NAS? Separate machine? Docker service?

### OQ-AI-02: Model Selection
Which Ollama model for recipe generation? Llama 3.1 8B (fast, less creative) vs Mistral 7B (creative, slower)?

### OQ-AI-03: Structured Output Reliability
How do we ensure the LLM returns valid JSON? Retry on parse failure? Use tool/function calling mode?

### OQ-AI-04: Token Budget
How many tokens per conversation turn? More tokens = better responses but slower and more resource-intensive.

### OQ-AI-05: LLM for Ingredient Parsing
Should we replace the rule-based ingredient parser with an LLM parser? More accurate but slower and costs resources.

### OQ-AI-06: Caching
Should we cache LLM responses? (e.g., same pantry + same query = cached result)

### OQ-AI-07: Fine-Tuning vs. Prompting
Should we fine-tune a small model on recipe data for better structured output? Or is prompt engineering sufficient?

### OQ-AI-08: Multi-Model Strategy
Should different features use different models? (e.g., fast/cheap model for categorization, powerful model for recipe chat)
