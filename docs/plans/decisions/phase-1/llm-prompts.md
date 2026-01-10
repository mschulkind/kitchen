# Decision: Develop LLM Prompt Examples for Meal Suggestions

## Overview
This decision focuses on crafting effective prompts for the LLM integration to generate personalized meal suggestions based on inventory, preferences, and optimization goals. Prompts will drive features like recipe generation that maximizes pantry use, minimizes waste, and accommodates dietary needs. Integration with Supabase for storing user history and fine-tuning context.

## Final Decision: Approved
- **Date**: 2025-09-18
- **Decision**: The project will adopt a **Few-Shot Prompting** strategy. The following four prompts are approved and will be integrated into the [`plans/design-system.md`](../design-system.md).

---

## Finalized LLM Prompts

### 1. Basic Meal Plan Generation
This prompt generates a multi-day meal plan that optimizes for ingredient reuse, a core goal from the [`plans/brief.md`](../brief.md).

- **Prompt:**
  ```
  "You are a meal planning assistant. Generate a {days}-day meal plan for {servings} people, using as many of these pantry items as possible: {pantry_list} and garden items: {garden_list}. Prioritize ingredient reuse and simple recipes (under 45min prep). Exclude {diet_restrictions}. Output a valid JSON object with the structure: {days: [{day: 'Day 1', recipe_name: string, ingredients_used: string[], new_shopping_list_items: string[], instructions: string}]}"
  ```
- **Purpose:** The main workhorse for creating efficient, multi-day meal plans.

### 2. Recipe Substitution & Customization
This prompt allows users to cook even if they are missing ingredients, which improves usability.

- **Prompt:**
  ```
  "You are a recipe customization assistant. The user wants to make '{recipe_name}' which requires {full_ingredients_list}. They only have these items from their pantry: {available_pantry}. Suggest logical substitutions for the missing ingredients. Consider dietary preferences: {prefs}. Output a valid JSON object with the structure: {original_recipe: string, substitutions: [{original: string, substitute: string, rationale: string}], adjusted_instructions: string, nutritional_notes: string}"
  ```
- **Purpose:** Handles missing ingredients gracefully, preventing interruptions to the cooking process.

### 3. Low-Waste Plan with Leftovers
This prompt directly addresses the waste-reduction goal by intelligently incorporating leftovers into new meals.

- **Prompt:**
  ```
  "You are a waste-reduction assistant. Create a 3-day meal plan that minimizes food waste. Use leftovers from these previous meals: {previous_meals} and items from the current pantry: {pantry_list}. Focus on {cuisine_pref} recipes and adhere to {diet_prefs}. Output a valid JSON object with the structure: {days: [{day: string, recipe_name: string, uses_leftovers_from: string[], shopping_list_additions: string[]}]}"
  ```
- **Purpose:** Provides smart, economical meal planning that makes the most of available food.

### 4. Garden Surplus Optimization
This prompt helps users utilize their fresh garden produce, a key feature mentioned in the [`plans/brief.md`](../plans/brief.md).

- **Prompt:**
  ```
  "You are a garden-to-table assistant. Suggest 2-3 simple recipes that make the most of a garden surplus. The user has: {garden_items_with_quantities}. Supplement with common pantry staples: {pantry_staples}. Respect these dietary restrictions: {diet_restrictions}. Output a valid JSON object with the structure: {recipes: [{recipe_name: string, key_garden_ingredients: string[], full_ingredient_list: string[], instructions: string, prep_time_minutes: int}]}"
  ```
- **Purpose:** Encourages the use of fresh, seasonal ingredients and connects the app to the user's gardening hobby.

---

## Next Steps
The approved prompts are to be integrated into the LLM section of [`plans/design-system.md`](../design-system.md) and referenced in the verification flow of [`plans/ux-flow.md`](../ux-flow.md).