# Phase 2: Visual Pantry (The "Magic")

**Goal**: Remove the friction of inventory management by using Computer Vision (LLM-based) to ingest grocery items. This is the "Wow" feature that differentiates the app.

## 2.1 Image Upload Pipeline

### Mobile (Frontend)
- Implement Camera view using `expo-camera`.
- Features:
    - "Quick Snap": Take a photo of a receipt, a fridge shelf, or a pantry shelf.
    - "Upload": Select from gallery.
- Logic:
    - Upload image to Supabase Storage bucket (`inbox-images`).
    - Generate a unique path: `{household_id}/{timestamp}_{random}.jpg`.
    - Return `image_path` to the UI.

### API (Backend)
- Endpoint: `POST /v1/vision/analyze`
    - Payload: `{ image_path: string }`
- Alternative: Supabase Storage Webhook (triggers an Edge Function -> calls Python API). *Decision: Keep it simple first, explicit API call from client.*

## 2.2 The Vision Agent (Python)

This service translates pixels into structured `PantryItem` candidates.

### Tech Stack
- **LLM**: GPT-4o (best for vision) or Gemini 1.5 Pro.
- **Library**: `langchain` or raw client with Pydantic structured output.

### Logic
1.  **Retrieve Image**: Download from Supabase Storage.
2.  **Preprocessing**: Resize/compress if necessary to save tokens/latency.
3.  **Prompting**:
    > "Analyze this image. Identify all food items. For each item, estimate the quantity and expire date if visible. Categorize them into [Produce, Dairy, ...]. Return a JSON list."
4.  **Parsing**: Validate response against `List[PantryItemCandidate]` Pydantic model.

## 2.3 Verification UI (Staging Area)

We never trust the AI 100%. Users must confirm changes.

### Staging Table
- **`pantry_staging`**
    - `id`: UUID
    - `household_id`: UUID
    - `image_url`: String
    - `detected_items`: JSONB (Array of candidates)
    - `status`: Enum (pending, reviewed, committed)

### UI Flow
1.  User takes photo -> Uploads -> API processes.
2.  App navigates to "Review Scan" screen.
3.  **Split View**:
    - Top: The Image (zoomable).
    - Bottom: List of detected items with edit controls.
4.  **Actions**:
    - Swipe to delete (False positive).
    - Tap to rename.
    - "Add All to Pantry" button.

## 2.4 Categorization & Learning

- **Auto-Categorization**: The LLM suggests the category (e.g., "Yogurt" -> Dairy).
- **Feedback Loop**: If the user corrects "Tomatoes" from "Pantry" to "Produce", store this preference (conceptually) or just update the item.

## Definition of Done (Phase 2)
- [ ] Camera integration in Expo app.
- [ ] Supabase Storage bucket configured with RLS.
- [ ] Python service capable of sending images to LLM and parsing JSON.
- [ ] "Staging" UI for reviewing and committing items to the main inventory.
- [ ] End-to-end flow: Photo -> Pantry Update takes < 15 seconds.
