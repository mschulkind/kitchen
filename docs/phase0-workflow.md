   1 | # Phase 0 Conversational Meal Planning Workflow
    2 | 
    3 | ## Table of Contents
    4 | - [Overview](#overview)
    5 | - [The Workflow: A Step-by-Step Guide](#the-workflow-a-step-by-step-guide)
    6 |   - [Step 1: The Request](#step-1-the-request)
    7 |   - [Step 2: The Options](#step-2-the-options)
    8 |   - [Step 3: The Verification](#step-3-the-verification)
    9 |   - [Step 4: The Final Plan](#step-4-the-final-plan)
   10 | - [File Structure](#file-structure)
   11 | 
   12 | ## Overview
   13 | This document serves as a comprehensive guide for an agent to execute the "Phase 0" markdown-driven conversational meal planning flow. The purpose of this flow is to test and refine the core LLM-driven value proposition of the app without any UI, using only markdown files.
   14 | 
   15 | ## Human/Agent Interaction Model
   16 | 
   17 | - **Agent's Role**: The agent (LLM) is responsible for all file modifications. This includes creating, editing, and deleting files as required by the workflow. After each step, the agent will commit and push the changes to the repository.
   18 | - **Human's Role**: The human user will interact with the agent via a chat interface. The human will initiate the process and make choices by giving instructions to the agent in the chat. The human will review the agent's work on GitHub.
   19 | 
   20 | ## The Workflow: A Step-by-Step Guide
   21 | 
   22 | This is an iterative process involving a "human" user and an "agent" (the LLM).
   23 | 
   24 | ### Step 1: The Request
   25 | 1.  **Human's Role**: The human initiates the process by creating a new plan directory within `phase0_flow/plans/`, for example: `phase0_flow/plans/YYYY-MM-DD_my-plan/`.
   26 | 2.  **Human's Role**: Inside this new directory, the human creates a `01-request.md` file. In this file, they specify the number of days and portions for the meal plan. The agent should assume that the human has already populated their stock lists (`phase0_flow/stock_lists/`) and preferences (`phase0_flow/general_preferences/`).
   27 | 3.  **Agent's Role**: The agent's job begins when asked to process this request. The agent reads the `01-request.md` file, as well as all files in `phase0_flow/stock_lists/` and `phase0_flow/general_preferences/` to gather all necessary context. After processing, the agent will commit and push any changes.
   28 | 
   29 | ### Step 2: The Options
   30 | 1.  **Agent's Role**: The agent generates 4-5 high-level meal plan summaries based on the human's request, stock, and preferences.
   31 | 2.  **Agent's Role**: The agent creates a new file, `02-options.md`, in the same plan directory (`phase0_flow/plans/YYYY-MM-DD_my-plan/`). This file should contain the generated options, each with a theme and a list of key new ingredients that would need to be purchased. After creating the file, the agent will commit and push it.
   32 | 3.  **Human's Role**: The human reviews the `02-options.md` file on GitHub and tells the agent which plan they choose via the chat interface.
   33 | 
   34 | ### Step 3: The Verification
   35 | 1.  **Agent's Role**: Once the human has made a choice via chat, the agent is prompted again. The agent reads the selected option from `02-options.md`. Based on this choice, it generates a detailed, categorized list of *all* ingredients required for the entire plan.
   36 | 2.  **Agent's Role**: The agent creates a `03-verification.md` file in the plan directory. This file contains the complete ingredient checklist. The agent should pre-emptively check (`[x]`) any items it believes the user has based on the `stock_lists`. After creating the file, the agent will commit and push it.
   37 | 3.  **Human's Role**: The human reviews the `03-verification.md` file on GitHub, and tells the agent about any inaccuracies or substitutions via chat.
   38 | 
   39 | ### Step 4: The Final Plan
   40 | 1.  **Agent's Role**: The agent is prompted a final time. It incorporates the feedback from the human and reads the verified ingredient list from `03-verification.md`.
   41 | 2.  **Agent's Role**: Based on this final, verified list, the agent generates the complete meal plan. This includes day-by-day recipes with detailed instructions and a final, consolidated shopping list containing *only* the items the human needs to purchase.
   42 | 3.  **Agent's Role**: The agent creates the `04-final-plan.md` file in the plan directory, containing this complete output. After creating the file, the agent will commit and push it.
   43 | 4.  **Human's Role**: The human can now use this final plan to cook and shop.
   44 | 
   45 | ## File Structure
   46 | - `phase0_flow/`
   47 |   - `stock_lists/`
   48 |     - `pantry.md`
   49 |     - `fridge.md`
   50 |     - `freezer.md`
   51 |     - `garden.md` (optional)
   52 |   - `general_preferences/`
   53 |     - `staple_meals.md`
   54 |     - `likes_and_dislikes.md`
   55 |     - `kid_meals_rules.md` (optional)
   56 |   - `plans/`
   57 |     - `YYYY-MM-DD_my-plan/`
   58 |       - `01-request.md`
   59 |       - `02-options.md`
   60 |       - `03-verification.md`
   61 |       - `04-final-plan.md`