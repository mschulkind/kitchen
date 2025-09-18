# Phase 0 Conversational Meal Planning Workflow

## Table of Contents
- [Overview](#overview)
- [The Workflow: A Step-by-Step Guide](#the-workflow-a-step-by-step-guide)
  - [Step 1: The Request](#step-1-the-request)
  - [Step 2: The Options](#step-2-the-options)
  - [Step 3: The Verification](#step-3-the-verification)
  - [Step 4: The Final Plan](#step-4-the-final-plan)
- [File Structure](#file-structure)

## Overview
This document serves as a comprehensive guide for an agent to execute the "Phase 0" markdown-driven conversational meal planning flow. The purpose of this flow is to test and refine the core LLM-driven value proposition of the app without any UI, using only markdown files.

## The Workflow: A Step-by-Step Guide

This is an iterative process involving a "human" user and an "agent" (the LLM).

### Step 1: The Request
1.  **Human's Role**: The human initiates the process by creating a new plan directory within `phase0_flow/plans/`, for example: `phase0_flow/plans/YYYY-MM-DD_my-plan/`.
2.  **Human's Role**: Inside this new directory, the human creates a `01-request.md` file. In this file, they specify the number of days and portions for the meal plan. The agent should assume that the human has already populated their stock lists (`phase0_flow/stock_lists/`) and preferences (`phase0_flow/general_preferences/`).
3.  **Agent's Role**: The agent's job begins when asked to process this request. The agent reads the `01-request.md` file, as well as all files in `phase0_flow/stock_lists/` and `phase0_flow/general_preferences/` to gather all necessary context.

### Step 2: The Options
1.  **Agent's Role**: The agent generates 4-5 high-level meal plan summaries based on the human's request, stock, and preferences.
2.  **Agent's Role**: The agent creates a new file, `02-options.md`, in the same plan directory (`phase0_flow/plans/YYYY-MM-DD_my-plan/`). This file should contain the generated options, each with a theme and a list of key new ingredients that would need to be purchased.
3.  **Human's Role**: The human reviews the `02-options.md` file and chooses one plan by marking it with an `[x]`.

### Step 3: The Verification
1.  **Agent's Role**: Once the human has made a choice, the agent is prompted again. The agent reads the selected option from `02-options.md`. Based on this choice, it generates a detailed, categorized list of *all* ingredients required for the entire plan.
2.  **Agent's Role**: The agent creates a `03-verification.md` file in the plan directory. This file contains the complete ingredient checklist. The agent should pre-emptively check (`[x]`) any items it believes the user has based on the `stock_lists`.
3.  **Human's Role**: The human reviews the `03-verification.md` file, correcting any inaccuracies and confirming exactly what is on hand. The human can also suggest substitutions in this file.

### Step 4: The Final Plan
1.  **Agent's Role**: The agent is prompted a final time. It reads the verified ingredient list from `03-verification.md`.
2.  **Agent's Role**: Based on this final, verified list, the agent generates the complete meal plan. This includes day-by-day recipes with detailed instructions and a final, consolidated shopping list containing *only* the items the human needs to purchase.
3.  **Agent's Role**: The agent creates the `04-final-plan.md` file in the plan directory, containing this complete output.
4.  **Human's Role**: The human can now use this final plan to cook and shop.

## File Structure
- `phase0_flow/`
  - `stock_lists/`
    - `pantry.md`
    - `fridge.md`
    - `freezer.md`
    - `garden.md` (optional)
  - `general_preferences/`
    - `staple_meals.md`
    - `likes_and_dislikes.md`
    - `kid_meals_rules.md` (optional)
  - `plans/`
    - `YYYY-MM-DD_my-plan/`
      - `01-request.md`
      - `02-options.md`
      - `03-verification.md`
      - `04-final-plan.md`