# 11 — Parking Lot ⏸️

> Features that are designed or partially built but deliberately deferred from the active roadmap.

---

## Overview

Not everything needs to ship now. This document tracks features that were explored, partially built, or planned but then consciously parked. They're not deleted — they're preserved here so we know what exists and can reactivate them when the time is right.

**Fun fact:** 🐋 Whales can hold their breath for up to 90 minutes. These features can hold theirs indefinitely. 🫁

---

## 🅿️ P1: Cooking Mode (Step-by-Step)

### What Was Built
- Full-screen immersive cooking experience (`recipes/[id]/cook.tsx`)
- Step-by-step instruction display with large text
- Mise-en-place checklist (ingredient prep tracking)
- Progress bar (orange, shows step completion)
- Left/right tap zones for navigation (25% screen width each)
- "Cooking Complete" screen with completion tracking
- `last_cooked_at` timestamp recording

### Backend Support
- `GET /cooking/context/{recipe_id}` — ingredients vs. inventory comparison
- `POST /cooking/export/{recipe_id}` — formatted text for clipboard/AI
- `GET /cooking/mise-en-place/{recipe_id}` — prep task list
- `GET /cooking/steps/{recipe_id}` — individual step cards
- `POST /cooking/mark-cooked` — deduct inventory quantities
- `POST /cooking/session/{recipe_id}` — create cooking session

### Why Parked
User decision: "Let's back burner cooking mode for now." The only desired functionality is:
1. **PDF output** — printable recipe card
2. **Prompt copy** — formatted text to paste into another AI for help while cooking

### What to Keep
- `cook.tsx` route exists but all entry points removed (Round 7)
- Backend endpoints still functional
- Could be reactivated by adding nav buttons back
- Context export (`POST /cooking/export`) covers the "prompt copy" use case

### Reactivation Cost: Low
Just add navigation buttons back to recipe detail screen.

---

## 🅿️ P2: Vision / Image Scanning

### What Was Built
- `scan-result.tsx` — staging screen for detected items
- Confidence bars per detected item (color-coded)
- Edit/delete per detected item before confirming
- "Confirm All" button → batch insert to pantry
- Backend `POST /vision/analyze` endpoint
- Mock detection with 5 sample items

### Backend Support
- `POST /vision/analyze` — run vision model on image URL
- `POST /vision/confirm` — batch confirm detected items → pantry
- `POST /vision/quick-scan` — convenience with location context
- Google Gemini adapter (with mock fallback)

### Why Parked
User decision: "Backburner image processing (for adding things)." Needs API keys and the value proposition is unclear at household scale (faster to just type items).

### Reactivation Cost: Medium
Need Gemini or Ollama vision model, real image capture flow, and user testing to validate the UX.

---

## 🅿️ P3: AI Image Generation

### What Was Built
- "Generate with AI" button on recipe detail (placeholder area)
- Backend `POST /recipes/{id}/generate-image` endpoint
- Gemini-powered image generation with professional food photography prompt
- Image URL stored in `recipes.image_url`

### Why Parked
User decision: "Backburner image generation." Resource-intensive and not core to meal planning workflow.

### Reactivation Cost: Low-Medium
Button exists, backend works. Need API key + model access.

---

## 🅿️ P4: Voice Commands

### What Was Built
- Webhook endpoints for voice assistants (Google Home, Alexa)
- `POST /hooks/add-item` — add items via voice
- `POST /hooks/voice` — general voice command processing
- Intent parsing: ADD_ITEM, REMOVE_ITEM, CHECK_ITEM, ADD_PANTRY, ASK_INVENTORY
- Multi-item extraction ("bread and milk" → 2 items)
- Natural language responses for TTS

### Current Status
Voice is **built and functional** but has no in-app UI (webhooks only). The shopping list voice button was removed per user feedback. Voice commands work via external assistants (Google Home, Alexa) that call the webhook endpoints.

### Why Semi-Parked
Not fully parked — webhook endpoints are live. The in-app voice button was removed because it added clutter without enough value (typing is faster on a phone). External voice assistant integration remains active.

### Reactivation Cost: N/A
Already functional via webhooks. Just needs external assistant configuration.

---

## 🅿️ P5: Manual Recipe Creation

### What Was Built
- `recipes/new.tsx` — full recipe creation form
- Title, servings, prep/cook time inputs
- Dynamic ingredient rows (add/remove)
- Dynamic instruction steps (add/remove)
- Validation (title required, ≥1 ingredient, ≥1 step)
- `POST /api/v1/recipes` backend endpoint

### Why Parked
User decision: "I don't want to ever create a new recipe myself. Sources should only be from an agent." Replaced by:
1. URL import (already built)
2. AI chat creation (spec #05, not yet built)

### Current State
- Route exists (`recipes/new.tsx`) but no navigation points to it
- Action sheet shows "Chat with AI (Coming Soon)" instead of manual entry
- Backend `POST /recipes` endpoint still works (used by AI chat in future)

### Reactivation Cost: Very Low
Just add a menu option pointing to `recipes/new.tsx`.

---

## 🅿️ P6: Store Intelligence (Advanced)

### What Was Built
- Preferred store text input in Settings
- Backend `GET /shopping/lists/{id}/sorted` — aisle-sorted shopping list
- Basic category-based aisle estimation

### What's Planned but Not Built
- Per-store aisle mapping
- Store floor plan optimization
- Category → aisle learning from user behavior
- Multi-store support

### Why Semi-Parked
Basic store preference is built. Advanced intelligence (aisle learning, multi-store) needs more infrastructure and is lower priority than AI recipe creation.

### Reactivation Cost: Medium
Need store data model, per-store aisle config, learning algorithm.

---

## 🅿️ P7: Recipe PDF Output (Planned)

> From recipe-format-design.md — beautiful printable recipe cards.

### Concept
- Generate PDF recipe cards with professional food-magazine layout
- Include mise-en-place checklists, interleaved timelines for main + side
- Color-coded sections (orange = active cooking, blue = prep, green = resting)
- Countdown timer cues embedded as text
- QR code back to in-app recipe
- Backend: Jinja2 templates → WeasyPrint PDF generation

### API (Planned)
```
GET /api/v1/recipes/{id}/pdf
GET /api/v1/recipes/{id}/pdf?side_recipe_id={uuid}&include_shopping=true
```

### Reactivation Cost: Medium
Need template design, WeasyPrint integration, and font/styling choices.

---

## 🅿️ P8: Batch Cooking / Meal Prep Mode (Idea)

> Inspired by MealPrepPro and the original brief's "leftovers" vision.

### Concept
- "Prep Day" mode: select multiple recipes, get a unified prep timeline
- Shared prep steps consolidated ("dice onions for recipes A, B, and C at once")
- Container portioning guide ("divide into 4 containers, 3 for freezer")
- Automatic scaling for batch sizes
- Integrates with leftover chain tracking in planner

### Reactivation Cost: High
Significant new feature, but aligns well with existing recipe + planner infrastructure.

---

## 🅿️ P9: Smart Home / IoT Integration (Idea)

> Inspired by Whisk (Samsung Food) and smart kitchen trends.

### Concept
- Integration with smart kitchen timers
- Oven temperature presets sent to smart oven
- Smart fridge inventory sync (if supported)
- Google Home / Alexa voice assistant integration (webhook base already exists)

### Reactivation Cost: High
Depends on specific devices, but webhook infrastructure is already built.

---

## Summary

| Feature | Code Exists | Backend | Entry Points | Reactivation |
|---------|-------------|---------|-------------|-------------|
| Cooking Mode | ✅ cook.tsx | ✅ 6 endpoints | ❌ Removed | Low |
| Vision Scanning | ✅ scan-result.tsx | ✅ 3 endpoints | ✅ FAB exists | Medium |
| Image Generation | ✅ Button on detail | ✅ 1 endpoint | ✅ Placeholder | Low-Medium |
| Voice Commands | ✅ Webhook routes | ✅ 3 endpoints | ❌ Button removed | N/A (works) |
| Manual Recipe | ✅ new.tsx | ✅ POST endpoint | ❌ Removed from menu | Very Low |
| Store Intelligence | ⚠️ Basic only | ✅ Sort endpoint | ✅ Settings input | Medium |
| Recipe PDF | ❌ | ❌ | ❌ | Medium |
| Batch Cooking | ❌ | ❌ | ❌ | High |
| Smart Home / IoT | ⚠️ Webhooks | ✅ Voice endpoints | ❌ | High |
