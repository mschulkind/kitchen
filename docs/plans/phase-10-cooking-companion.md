# Phase 10: The Chef's Companion 👨‍🍳

**Status**: 🚧 Not Started  
**Priority**: 🟡 Nice-to-Have ("Copy for AI" is a quick win!)  
**Estimated Effort**: 1 week  
**Dependencies**: Phase 2 (Recipe data), Phase 1 (Pantry data for context)  
**Blocks**: None (final polish feature)

**Goal**: Execution and Cooking support.

## 10.1 Technical Architecture

### Modules

- **`src/api/domain/cooking/prompt_builder.py`**: Context formatting.
- **`src/mobile/app/cooking/[recipeId].tsx`**: The "Active Cooking" view.

## 10.2 Implementation Details

### "Copy for AI" Context Builder

- **Template**:

```text
RECIPE: {recipe.title}
SERVES: {recipe.servings}

INGREDIENTS:
{recipe.ingredients.map(i => `- ${i.raw_text}`).join('\n')}

INSTRUCTIONS:
{recipe.instructions}

MY INVENTORY CONTEXT (Potential Subs):
{related_pantry_items}

USER QUESTION:
[Paste your question here]
```

### Consumption Logic

- **"Mark as Cooked"**:
  - Iterate recipe ingredients.
  - Call `DeltaService`.
  - Decrement `PantryItem.quantity`.
  - *Safety*: If decrement < 0, set to 0 (don't error).

## 10.3 Testing Plan

### Unit Tests

- `test_prompt_builder`: Verify the output string contains all necessary sections and handles missing inventory gracefully.
- `test_consumption_logic`: Verify pantry quantities are reduced correctly.
