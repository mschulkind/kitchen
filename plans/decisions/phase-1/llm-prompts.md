# Decision: Develop LLM Prompt Examples for Meal Suggestions

## Overview
This decision focuses on crafting effective prompts for the LLM integration to generate personalized meal suggestions based on inventory, preferences, and optimization goals. Prompts will drive features like recipe generation that maximizes pantry use, minimizes waste, and accommodates dietary needs. Integration with Supabase for storing user history and fine-tuning context.

## Options
- **Option 1: Zero-Shot Prompts (Simple, Direct)**
  - Basic structure: "Generate a [number] meal ideas using these ingredients: [list]. Consider [diet prefs], optimize for nutrition and ease."
  - No examples provided to the LLM; relies on model knowledge.

- **Option 2: Few-Shot Prompts (With Examples)**
  - Include 1-3 sample input-output pairs: e.g., Input: "Pantry: chicken, rice; Low-carb" → Output: "Stir-fry with cauliflower rice...".
  - Builds reliability for consistent formatting (e.g., JSON output with recipe steps, shopping additions).

- **Option 3: Chain-of-Thought Prompts (Reasoning-Focused)**
  - Encourage step-by-step reasoning: "Step 1: Analyze available ingredients. Step 2: Match to user prefs. Step 3: Suggest substitutions if needed. Output in structured format."
  - Useful for complex optimizations like expiry-aware suggestions.

## Pros/Cons
- **Zero-Shot**:
  - Pros: Concise, fast; low token usage for cost efficiency.
  - Cons: Variable quality; may not handle edge cases (e.g., rare ingredients) well.

- **Few-Shot**:
  - Pros: Improves accuracy and consistency; easier to control output format.
  - Cons: Higher token cost; requires curating good examples upfront.

- **Chain-of-Thought**:
  - Pros: Better for reasoning tasks like substitutions; transparent for debugging.
  - Cons: Longer prompts/responses; potential for verbose outputs needing post-processing.

## Questions for User
- Preferred LLM provider (e.g., OpenAI GPT-4, local Ollama for privacy/offline)?
- Key focus areas for prompts (e.g., emphasize waste reduction, family-sized meals, or quick prep times)?
- Output format: Structured JSON (for easy parsing in app) or natural language?
- How many examples per prompt type (e.g., 3-5 for few-shot)?

## Next Steps
Select approach and develop 3-5 sample prompts; integrate into design-system.md LLM section and ux-flow.md for verification flow. Reference: [plans/design-system.md](../design-system.md), [plans/ux-flow.md](../ux-flow.md), [plans/brief.md](../brief.md).

*Decision Pending - Awaiting User Input*