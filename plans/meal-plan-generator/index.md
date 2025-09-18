# Conversational Meal Plan Generator

This directory contains the templates and examples for a conversational, markdown-driven meal planning process. The goal is to simulate the back-and-forth of the app's core LLM-powered logic to refine a meal plan before any code is written.

## The Workflow

The process is a multi-step conversation, with each step captured in a markdown file.

1.  **The Request (`01-request.md`)**: You start by filling out a simple request: how many days, how many portions. You also provide your current pantry and preferences.
2.  **The Options (`02-options.md`)**: Based on your request, I will generate 4-5 high-level meal plan summaries. Each summary will include the theme of the plan (e.g., "Low-Waste Chicken Focus," "Garden Fresh Vegetarian") and a list of the *main* new ingredients you'd have to buy. You then choose one by marking it with an `[x]`.
3.  **The Verification (`03-verification.md`)**: Once you've chosen a plan, I'll generate a detailed list of all ingredients required. You'll go through this list and mark what you already have, and you can suggest substitutions. This is where you steer the plan to use up your pantry items.
4.  **The Final Plan (`04-final-plan.md`)**: Based on your verification, I'll generate the final, detailed meal plan. This will include day-by-day recipes with instructions and a final, consolidated shopping list of only the items you need to buy.

This iterative process ensures the final plan meets all your criteria: your tastes, your pantry, your leftovers, and your garden, all through a simple conversation in text files.