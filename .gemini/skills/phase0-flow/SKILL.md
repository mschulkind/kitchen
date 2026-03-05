---
name: phase0-flow
description: A markdown-driven conversational meal planning workflow that results in verified shopping lists and PDF recipes.
---

# Phase 0 Conversational Meal Planning Workflow

This skill guides you through the "Phase 0" markdown-driven conversational meal planning flow. The goal is to produce a complete meal plan, a verified shopping list, and PDF recipes without a UI.

## Lingo & Shortcuts 🗣️

- **STK (Shop the Kitchen)**: A request where **NO shopping** is allowed. Every ingredient MUST be verified against `phase0_flow/stock_lists/`. If a user says "STK," ensure the final shopping list is empty.
- **Low-GI**: Focus on fiber, protein, and non-starchy vegetables. Minimize refined carbs (white rice, white pasta, flour) and sugar. Check recent plans for this established pattern.
- **Kid Pull**: Explicitly marking a step in the recipe to remove a portion for picky eaters before spicing/saucing.
- **Shortcut: "1 night phase0 STK plan"**: When triggered, bypass the typical 3-5 meal variety and focus on a single, high-quality, zero-shopping meal for tonight.

## Overview

- **Tone**: Use plenty of emojis to make the process fun and engaging! 🥳
- **Agent's Role**: You are responsible for creating, editing, and deleting markdown files in `phase0_flow/plans/`. You must commit changes after each step.
- **Tools**: Use standard file operations. For PDF generation, use the `just` command.

## Workflow Steps

### Step 1: The Request

1.  **Context**: The user has either created a `01-request.md` in a new plan directory (e.g., `phase0_flow/plans/YYYY-MM-DD_my-plan/`) OR provided a request via chat.
2.  **Action**:
    -   If the request was via chat, **create the plan directory** and `01-request.md` with the request details.
    -   Read `01-request.md` (or the chat history).
    -   Read `phase0_flow/stock_lists/` and `phase0_flow/general_preferences/`.
    -   **Read recent plans**: Check `phase0_flow/plans/` (last 1-2 plans) to understand:
        -   Naming conventions (e.g., `YYYY-MM-DD_title`).
        -   **Dietary/Health goals**: Look for repeating themes like "Low-GI" or "Heart Healthy."
        -   Formatting style for recipes and plans.
3.  **Goal**: Understand the user's needs, constraints, and current inventory.

### Step 2: The Options

1.  **Action**: Generate 4-5 high-level meal plan summaries based on the request.
    -   **Check Dislikes**: explicitly check `general_preferences/process.md` (or similar) for dislikes (e.g., mushrooms, olives) and ensure options respect them.
2.  **Output**: Create `02-options.md` in the plan directory.
    -   Each option should have a theme.
    -   List key *new* ingredients to buy for each option.
3.  **Commit**: Commit the changes.
4.  **Interaction**: **STOP EXECUTION.** Present the options to the user in chat and ask them to choose one. Do not proceed to Step 3 until the user has made a choice.

### Step 3: Ingredient Verification & Provisional Recipes

1.  **Trigger**: User selects an option.
2.  **Action**: Create a comprehensive ingredient checklist AND provisional recipes for the selected plan.
3.  **Output 1**: Create `03-verification.md`.
    -   List *all* ingredients required for the plan.
    -   Categorize them (Produce, Dairy, Pantry, etc.).
    -   Pre-check (`[x]`) items you believe are in stock based on `stock_lists`.
    -   Leave unknown/out-of-stock items unchecked (`[ ]`).
4.  **Output 2**: Create individual recipe files in a `recipes/` subdirectory.
    -   **Format Decision**:
        -   **Markdown (`.md`)**: Good for simple plans. Use standard headers.
        -   **JSON (`.json`)**: REQUIRED for high-quality "templated" PDF generation (Time/Ingredients columns). Use this if the user asks for "templated" or "nice" PDFs.
    -   These are "provisional" drafts to ensure all spices, garnishes, and techniques are documented.
5.  **Commit**: Commit the changes.
6.  **Interaction**: **STOP EXECUTION.** Ask the user to review the provisional recipes and `03-verification.md`. Do not proceed to Step 4 until the user confirms the ingredients and recipes.

### Step 4: Shopping List Verification

*Crucial Step: Ensure nothing is missed!*

1.  **Trigger**: User confirms inventory.
2.  **Action**:
    -   Read the updated `03-verification.md`.
    -   **Cross-Reference**: Explicitly check *every single ingredient* in the planned recipes against the user's verified inventory.
    -   Identify any discrepancies or missing items.
3.  **Interaction**: **STOP EXECUTION.** If you find missing items or ambiguities, ask the user for clarification before proceeding. If everything is perfect, you may ask for final confirmation to proceed to generation.

### Step 5: Final Plan & PDFs

1.  **Action**: Generate the final assets. **This step is MANDATORY and must be performed automatically once the user gives the final "go-ahead."**
2.  **Output 1: Markdown Plan**: Create `04-final-plan.md`.
    -   Include the final menu.
    -   Include the **Consolidated Shopping List** (only items strictly needed).
    -   Include full recipes with instructions.
3.  **Output 2: Recipe Files**: Finalize individual recipe files in the `recipes/` subdirectory.
    -   **ALWAYS** create a JSON version of the recipe to enable high-quality PDF generation.
    -   Ensure they match the required JSON structure (Prep, Steps, Meanwhile).
4.  **Output 3: PDFs**: Run the PDF generation command.
    -   Command: `just render-all` (Targets .json files -> templated PDFs).
    -   **Verification**: Confirm the PDF files exist in the `recipes/` directory after the command runs.
5.  **Commit**: Commit all new files (markdown plan, recipe files, and generated PDFs).
6.  **Completion**: Inform the user that the plan and PDFs are ready! 📄✨

## Recipe Standards

### JSON Format (For Templated PDFs)

If using JSON, follow this structure:

```json
{
  "title": "Recipe Name",
  "emoji": "🥘",
  "prep": {
    "ready_to_use": [ {"amount": "1 tsp", "name": "Salt"} ],
    "knife_work": [ {"amount": "1", "name": "Onion", "prep": "diced"} ]
  },
  "steps": [
    {
      "minutes_before_done": 30,
      "duration_minutes": 5,
      "ingredients": [ {"amount": "1 tbsp", "name": "Oil"} ],
      "action_name": "Sauté",
      "action_description": "Cook onions until translucent.",
      "meanwhile": { "ingredients": "Parsley", "action": "chop" }
    }
  ]
}
```

### General Rules

1.  **Prep Completeness**: Every single ingredient listed in the steps (grey boxes) MUST be listed in the top `prep` section (either `ready_to_use` or `knife_work`). This includes spices, oils, water splashes, and garnishes.
2.  **Strict Time Management**: 
    -   **Total Time**: Include all prep (slicing, dicing, measuring) in the total time estimate.
    -   **Step-by-Step Prep**: The first step in the execution table **MUST** be "Mise en Place" and account for all chopping, slicing, and measuring.
    -   **JSON Requirement**:
        ```json
        {
          "minutes_before_done": 45,
          "duration_minutes": 10,
          "ingredients": [ {"amount": "1", "name": "Onion"}, {"amount": "2", "name": "Carrots"} ],
          "action_name": "Mise en Place",
          "action_description": "Dice onion. Slice carrots into coins."
        }
        ```
    -   **Meal Caps**: Standard meals must be **30-45 minutes total**. One "complex" meal per plan can be up to **60 minutes**.
    -   **Layered Flavors**: Achieving deep flavor in short times requires techniques like fond-building, blooming spices, and high-heat roasting.
3.  **Specifics & Guidance**:
    -   **Cans**: MUST include sizes (e.g., "13.5 oz can Coconut Milk", "28 oz can Tomatoes").
### General Rules

1.  **Prep Completeness**: Every single ingredient listed in the steps (grey boxes) MUST be listed in the top `prep` section (either `ready_to_use` or `knife_work`). This includes spices, oils, water splashes, and garnishes.
    -   **Beef/Protein Prep**: Ensure any special prep (e.g., "slice thin against the grain") is explicitly listed in the `knife_work` or `ready_to_use` section AND emphasized in the "Mise en Place" step.
2.  **Workflow Optimization & "Destinations"**:
    -   **Group by Destination**: In the `knife_work` section and the "Mise en Place" step, group ingredients by when they enter the pan.
    -   **Explicit Instructions**: Tell the user *where* to put prepped items to minimize dishes (e.g., "Dice onions and peppers; place in the same bowl as they will be added to the pan together," or "Chop cauliflower and keep on the cutting board to add directly to the pot later").
    -   **Dish Minimization**: Actively look for ways to reduce the number of bowls/tools used. If items can go directly from the board to the pan, say so.
3.  **Strict Time Management**: 

      01-request.md
      02-options.md
      03-verification.md
      04-final-plan.md
      recipes/
        recipe-1.md
        pdfs/
          recipe-1.pdf
```
