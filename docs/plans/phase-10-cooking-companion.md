# Phase 10: The Chef's Companion 👨‍🍳

**Status**: 🚧 In Progress (Backend ✅, Frontend 🚧)
**Priority**: 🟡 Nice-to-Have ("Copy for AI" is a quick win!)  
**Estimated Effort**: 1 week  
**Dependencies**: Phase 2 (Recipe data), Phase 1 (Pantry data for context)  
**Blocks**: None (final polish feature)

**Goal**: Execution and Cooking support.

## 10.1 Technical Architecture

### Modules

- **`src/api/domain/cooking/prompt_builder.py`**: Context formatting.
- **`src/mobile/app/cooking/[recipeId].tsx`**: The "Active Cooking" view.

## 10.2 Implementation Details (Granular Phases)

### Phase 10A: Prompt Builder & Logic

- **Goal**: Generate context for External LLM.
- **Tasks**:
    1. **Service**: `CookingService.get_context(recipe_id)`.
    2. **Logic**: Fetch Recipe + Related Pantry Items + User Prefs.
    3. **Format**: Return Markdown block optimized for Gemini/Claude.

### Phase 10B: Cooking UI

- **Goal**: Active use in kitchen.
- **Tasks**:
    1. **Screen**: `app/cooking/[id].tsx`.
    2. **Views**: "Mise-en-place" (Checklist) vs "Step-by-Step" (Large Text).
    3. **Action**: "Copy Context" button (Calls 10A).
    4. **Action**: "Mark Cooked" (Decrements Inventory).

## 10.3 Testing Plan

### Phase 10A Tests (Unit)

- [ ] **Prompt Content Construction**:
  - Input: Recipe "Tacos" (needs Cheese). Pantry has "Cheddar".
  - **Action**: Call `PromptBuilder.build()`.
  - **Assert**: Output string contains:
    - "RECIPE: Tacos"
    - "MY INVENTORY CONTEXT: ... Cheddar"
  - *Note*: We do not call the LLM here; we just verify the context we *would* send.
- [ ] **Decrement Logic**:
  - Input: Recipe uses 1lb Beef. Pantry has 2lb.
  - Action: Mark Cooked.
  - Assert: Pantry has 1lb remaining.

### Phase 10B Tests (E2E)

1.  **Cooking Flow**:
    - **Go to**: Recipe Detail.
    - **Click**: "Start Cooking".
    - **Verify**: Large Text Mode activates.
    - **Action**: Click "Next Step".
    - **Action**: Click "Mark as Cooked".
    - **Verify**: Navigation to Inventory (or Success Toast).
    - **Verify**: Inventory quantities reduced.

2.  **Timers & Scaling**:
    - **Action**: Click on "2 Servings". Change to "4".
    - **Verify**: Ingredient quantities double.
    - **Action**: Click on a timer link "10 mins" in text.
    - **Verify**: Timer starts counting down.
