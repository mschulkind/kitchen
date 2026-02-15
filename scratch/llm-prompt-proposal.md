# Proposal: Finalized LLM Prompt Examples

This document presents a set of 4 finalized LLM prompt examples for the meal suggestion feature, based on the requirements in [`docs/plans/development-todo.md`](../docs/plans/development-todo.md) and the initial exploration in [`docs/plans/decisions/phase-1/llm-prompts.md`](../docs/plans/decisions/phase-1/llm-prompts.md).

The chosen approach is **Few-Shot Prompts**, which provides a good balance of reliability, cost-effectiveness, and control over the output format. The prompts are designed to return structured JSON, which is essential for easy integration with the application's frontend and backend.

---

## Proposed LLM Prompts

### 1. Basic Meal Plan Generation

This prompt generates a multi-day meal plan that optimizes for ingredient reuse, a core goal from the [`docs/plans/development-todo.md`](../docs/plans/development-todo.md) and [`docs/plans/brief.md`](../docs/plans/brief.md).

- **Prompt:**

```text
  "You are a meal planning assistant. Generate a {days}-day meal plan for {servings} people, using as many of these pantry items as possible: {pantry_list} and garden items: {garden_list}. Prioritize ingredient reuse and simple recipes (under 45min prep). Exclude {diet_restrictions}. Output a valid JSON object with the structure: {days: [{day: 'Day 1', recipe_name: string, ingredients_used: string[], new_shopping_list_items: string[], instructions: string}]}"
  ```

- **Purpose:** The main workhorse for creating efficient, multi-day meal plans.

### 2. Recipe Substitution & Customization

This prompt allows users to cook even if they are missing ingredients, which improves usability.

- **Prompt:**

  ```text

- **Purpose:** Handles missing ingredients gracefully, preventing interruptions to the cooking process.

### 3. Low-Waste Plan with Leftovers

This prompt directly addresses the waste-reduction goal by intelligently incorporating leftovers into new meals.

- **Prompt:**

```text
  "You are a waste-reduction assistant. Create a 3-day meal plan that minimizes food waste. Use leftovers from these previous meals: {previous_meals} and items from the current pantry: {pantry_list}. Focus on {cuisine_pref} recipes and adhere to {diet_prefs}. Output a valid JSON object with the structure: {days: [{day: string, recipe_name: string, uses_leftovers_from: string[], shopping_list_additions: string[]}]}"
  ```

- **Purpose:** Provides smart, economical meal planning that makes the most of available food.

### 4. Garden Surplus Optimization

This prompt helps users utilize their fresh garden produce, a key feature mentioned in the [`docs/plans/brief.md`](../docs/plans/brief.md).

- **Prompt:**

  ```text

- **Purpose:** Encourages the use of fresh, seasonal ingredients and connects the app to the user's gardening hobby.
