# Phase 11: Recipe Imagery 🖼️

**Status**: 🚧 Documented (Google Nano Banana Integration)
**Priority**: 🟡 Nice-to-Have (Visual Polish)
**Estimated Effort**: 2 days
**Dependencies**: Phase 2 (Recipe Engine), Google Gemini API

**Goal**: Automatically generate appetizing cover images for every recipe using Google's **Nano Banana** (Gemini 2.5 Flash Image).

## 11.1 The Concept

We will leverage Google's native image generation capabilities, specifically the **Nano Banana** model (Gemini 2.5 Flash Image), to create high-quality, consistent food photography for our recipes.

**Why Nano Banana?**

1.  **Unified Stack**: We already use Gemini for Vision and Planning.
2.  **Blazing Speed**: Optimized for low-latency generation.
3.  **Conversational Control**: Allows for easy prompt refinement.

*Target Model*: `gemini-2.5-flash-image` (Nano Banana) via the Google AI SDK.

## 11.2 Technical Architecture

### Components

1.  **New Route**: `POST /api/v1/recipes/{id}/generate-image`
    - Triggers the generation process using the existing `GOOGLE_API_KEY`.
2.  **Generation Logic**:
    - Uses the `generate_content` method with an image generation configuration.
    - Prompts are built from recipe titles, descriptions, and ingredients.
3.  **Storage Pipeline**:
    - Resulting image bytes are uploaded to Supabase Storage (`recipe-images` bucket).
    - The `image_url` in the `recipes` table is updated with the public signed URL.

### Prompt Engineering

*Template*: "A high-end, professional food photography shot of {title}. {description}. Overhead view, beautifully plated, natural lighting, bokeh background, 4k resolution, appetizing colors."

## 11.3 Implementation Plan

### Phase 11A: Infrastructure (Backend)

- [x] **Env Vars**: `GOOGLE_API_KEY` (Already present).
- [ ] **Supabase Storage**: Create `recipe-images` bucket (Public).
- [ ] **Service**: Implement `src/api/app/domain/images/service.py` using the `google-generativeai` library.

### Phase 11B: API & Backfill

- [ ] **Endpoint**: Add `generate-image` endpoint to `recipes.py` router.
- [ ] **Backfill Script**: Create `src/api/scripts/generate_all_recipe_images.py` to process the imported legacy recipes.

### Phase 11C: Frontend Integration

- [ ] **UI**: Update `RecipeCard` and `RecipeDetail` to render the `image_url`.
- [ ] **Placeholders**: Show a themed placeholder while the image is being generated.

## 11.4 Cost & Limits 💸

- **Gemini API**: Monitor usage within the free/pay-as-you-go tiers.
- **Batching**: Process backfills in small batches to respect rate limits.

## 11.5 Testing

- [ ] **Unit**: Mock the Gemini image response to test the storage upload logic.
- [ ] **Integration**: Generate an image for a "Test Taco" recipe and verify the URL is valid.
