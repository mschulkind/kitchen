# Phase 9: Voice Control 🗣️

**Status**: ✅ Backend Ready (Frontend Not Required)
**Priority**: 🟡 Nice-to-Have (Great for messy hands)  
**Estimated Effort**: 1 week  
**Dependencies**: Phase 7 (Shopping list API to add items)  
**Blocks**: None (convenience feature)

> 💡 **Tip**: Platform choice matters! See [Open Questions Q11](open-questions.md#q11-voice-assistant-platform).

**Goal**: Hands-free kitchen management via external integration (Google Home / Home Assistant).

## 9.1 Technical Architecture

### Modules

- **`src/api/routes/hooks.py`**: The Webhook receiver.
- **`src/api/domain/voice/parser.py`**: NLP logic.

## 9.2 Implementation Details (Granular Phases)

### Phase 9A: Webhook & NLP

- **Goal**: Accept text from Google Home/HA.
- **Tasks**:
    1. **API**: `POST /hooks/add-item?key=SECRET` (Complete).
    2. **NLP**: Simple parser to split "Milk and Eggs" -> `["Milk", "Eggs"]` (Complete).
    3. **Action**: Add to Shopping List (Unchecked).

### Phase 9B: Automation Setup (User Side)

- **Goal**: Connect the dots.
- **Tasks**:
    1. **Docs**: [Google Home Setup Guide](../guides/voice-assistant-setup.md) created.
    2. **Automation**: "Hey Google, add {text} to shopping list" -> Calls Webhook via IFTTT or HA.

## 9.3 Testing Plan

### Phase 9A Tests (API)

- [x] **Parsing**:
  - Input: "Add bread and 2 milks".
  - Assert: `[{item: "bread"}, {item: "milk", qty: 2}]`.
- [x] **Security**:
  - Input: Request without `?key`.
  - Assert: 401 Unauthorized.

### Phase 9A Tests (Integration)

- [x] **Webhook Call**:
  - Call Webhook with valid key and text.
  - Verify items appear in shopping list. (Tested in `phase9-voice.spec.ts` API tests).
