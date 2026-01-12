# Phase 9: Voice Control 🗣️

**Status**: 🚧 In Progress (Backend ✅, Frontend 🚧)
**Priority**: 🟡 Nice-to-Have (Great for messy hands)  
**Estimated Effort**: 1 week  
**Dependencies**: Phase 7 (Shopping list API to add items)  
**Blocks**: None (convenience feature)

> 💡 **Tip**: Platform choice matters! See [Open Questions Q11](open-questions.md#q11-voice-assistant-platform).

**Goal**: Hands-free kitchen management.

## 9.1 Technical Architecture

### Modules

- **`src/api/routes/hooks.py`**: The Webhook receiver.
- **`src/api/domain/voice/parser.py`**: NLP logic.

## 9.2 Implementation Details (Granular Phases)

### Phase 9A: Webhook & NLP

- **Goal**: Accept text from Google Home/HA.
- **Tasks**:
    1. **API**: `POST /hooks/add-item?key=SECRET`.
    2. **NLP**: Simple parser to split "Milk and Eggs" -> `["Milk", "Eggs"]`.
    3. **Action**: Add to Shopping List (Unchecked).

### Phase 9B: HA Configuration (User Side)

- **Goal**: Connect the dots.
- **Tasks**:
    1. **Docs**: Create guide for setting up `rest_command` in Home Assistant.
    2. **Automation**: "Hey Google, add {text} to shopping list" -> Calls Webhook.

## 9.3 Testing Plan

### Phase 9A Tests (Unit)

- [ ] **Parsing**:
  - Input: "Add bread and 2 milks".
  - Assert: `[{item: "bread"}, {item: "milk", qty: 2}]`.
- [ ] **Security**:
  - Input: Request without `?key`.
  - Assert: 401 Unauthorized.

### Phase 9A Tests (Integration)

- [ ] **End-to-End**:
  - Call Webhook with valid key and text.
  - Verify item appears in `shopping_list_items` table.
