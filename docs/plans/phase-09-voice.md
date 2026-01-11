# Phase 9: Voice Assistant Integration 🎙️

**Status**: 🚧 Not Started  
**Priority**: 🟢 Defer (Phone typing is fine for MVP)  
**Estimated Effort**: 1 week  
**Dependencies**: Phase 7 (Shopping list API to add items)  
**Blocks**: None (convenience feature)

> 💡 **Tip**: Platform choice matters! See [Open Questions Q11](open-questions.md#q11-voice-assistant-platform).

**Goal**: Hands-free kitchen management.

## 9.1 Technical Architecture

### Modules

- **`src/api/routes/hooks.py`**: The Webhook receiver.
- **`src/api/domain/voice/parser.py`**: NLP logic.

## 9.2 Implementation Details

### The NLP Parser

- **Input**: "Add milk and two bananas".
- **Step 1**: Split compound sentences ("and").
- **Step 2**: Extract `(item, qty)`.
  - "milk" -> `{item: "milk", qty: 1, unit: "default"}`
  - "two bananas" -> `{item: "banana", qty: 2, unit: "count"}`
- **Step 3**: Call `ShoppingService.add_item`.

### Security

- **API Key**: The webhook URL must include a secret key in the query param `?key=xyz` to prevent unauthorized additions.

## 9.3 Testing Plan

### Unit Tests

- `test_parse_simple`: "Add bread" -> OK.
- `test_parse_compound`: "Add bread and butter" -> Adds 2 items.
- `test_parse_quantities`: "Add 5 apples" -> Qty 5.

### Security Test

- Attempt to call webhook without Key -> 401 Unauthorized.
