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

- [ ] **Prompt Content**:
  - Input: Recipe "Tacos" (needs Cheese). Pantry has "Cheddar".
  - Assert: Output string mentions "You have Cheddar" in context section.
- [ ] **Decrement Logic**:
  - Input: Recipe uses 1lb Beef. Pantry has 2lb.
  - Action: Mark Cooked.
  - Assert: Pantry has 1lb remaining.

### Phase 10B Tests (E2E)

- [ ] **Copy Flow**:
    1. Open Recipe.
    2. Tap "Copy for AI".
    3. Verify Clipboard content (Mock).
- [ ] **Cook Flow**:
    1. Tap "Mark as Cooked".
    2. Navigate to Inventory.
    3. Verify quantities reduced.
