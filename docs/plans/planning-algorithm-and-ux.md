# Planning Algorithm & User Experience: "The Adventure"

**Goal**: Transform meal planning from a passive "generation" task into an active, enjoyable "Choose Your Own Adventure" game. The user should feel like a Director, and the AI is the Creative Producer pitching ideas.

## 1. The Input Vector (Context)

To generate good options, the Planner needs three layers of context.

### Layer A: The "Hard" Profile (Long-Term Memory)

*Stored in `user_preferences` or `household_settings` table.*

- **Dietary Restrictions**: Vegan, Keto, Gluten-Free, Low-FODMAP.
- **Hard Dislikes**: "No Cilantro", "No Mushrooms", "Hate spicy food".
- **Kitchen Equipment**: "No Sous Vide", "Have Instant Pot", "4-burner stove".
- **Household Size**: Default headcount (e.g., 2 Adults, 1 Toddler).

### Layer B: The "Soft" Vibes (Medium-Term / Seasonal)

*Learned over time or explicitly set.*

- **Staple Meals**: "We usually do Taco Tuesdays."
- **Cuisine Biases**: "We eat 50% Mexican, 30% Italian, 20% American."
- **Seasonal**: "It's Summer, so more salads/grilling, less stew."

### Layer C: The Session Constraints (The "Request")

*Provided at the start of the planning flow.*

- **Timeframe**: "Next 4 days" (Mon-Thu).
- **Events**: "Dining out Wednesday", "Guests on Friday (Total 6 people)".
- **Inventory Goals**: "Use up the rotting spinach", "Clear the freezer".
- **Mood**: "Low effort", "Feeling adventurous", "Comfort food".

---

## 2. The Interaction Model: "Choose Your Own Adventure"

Instead of generating one perfect plan immediately, the AI guides the user through a decision tree.

### Stage 1: The "Pitch" (Theme Selection)

*The AI analyzes inventory + preferences and proposes 3 distinct **Strategies** (The "Adventure Paths").*

> **User**: "Plan for Mon-Thu. Use the chicken."
>
> **AI**: "Okay, here are 3 ways we can play this:"
>
> 1. **The "Efficiency" Path**: Roast the whole chicken on Monday. Tacos on Tuesday. Soup on Wednesday. (Low effort, high reuse).
> 2. **The "Global Tour" Path**: Chicken Curry (Indian) on Mon. Chicken Schnitzel (German) on Tue. (High variety, more prep).
> 3. **The "Healthy/Light" Path**: Poached chicken salads and grain bowls. (Low calorie, fresh).

*User selects: "Let's go with the Global Tour."*

### Stage 2: The "Casting" (Recipe Selection)

*Now we lock in specific meals for the chosen path.*

> **AI**: "Great. For the Curry, I have two ideas based on your pantry:"
>
> - **Option A**: *Thai Green Curry* (You have the paste, need coconut milk).
> - **Option B**: *Butter Chicken* (You have everything, but it takes longer).
>
> **User**: "Option A, please."

### Stage 3: The "Director's Cut" (Refinement)

*The plan is set, but the user tweaks the details.*

- **"Swap"**: "Actually, move the Curry to Wednesday."
- **"Lock"**: "I definitely want Pizza on Friday, build around that."
- **"Regenerate Single Meal"**: "I don't feel like Schnitzel anymore. Give me another German chicken dish."

---

## 3. The Algorithm (Under the Hood)

The backend logic to support this flow.

### Step 1: Inventory & Constraint Retrieval

- Fetch `PantryItems` (Where `quantity > 0`).
- Fetch `UserPreferences`.
- Fetch `Recipes` (Filtered by Tags/Diet).

### Step 2: The "Candidate Pool" Generation

*Use vector search or tagging to find relevant recipes.*

- Score every recipe in the DB based on:
  - **Use-Up Score**: How many pantry items does it use? (Weighted by expiry).
  - **Effort Score**: Prep time vs. User's "Low effort" request.
  - **Preference Match**: Does it fit the "Vibe"?

### Step 3: The Strategy Clustering (The "Magic")

*The LLM takes the top 20 candidates and groups them.*

- **Cluster 1**: Common Ingredient (e.g., "All use Chicken").
- **Cluster 2**: Common Vibe (e.g., "Quick & Easy").
- **Cluster 3**: Novelty (e.g., "Recipes you haven't tried").

### Step 4: The Narrative Generation

The LLM writes the "Pitch" for each path. "Choose this path if you want to save time..."

---

## 4. User Interface Ideas

### The "Card Stack"

- **Visual**: A horizontal scroll of "Strategy Cards".
- **Content**: Large Hero Image + "Why this path?" text + "Inventory Used" progress bar.

### The "Slot Machine" (For Stage 2)

- **Visual**: The 4 days are displayed as columns. Each meal card is split into components (Main, Side, Drink).
- **Interaction**:
  - **Granular Re-rolling**:
    - "Spin" the whole day.
    - "Spin" just the **Main** (keep the Side).
    - "Spin" just the **Side** (keep the Main).
  - **Micro-Direction**: When hitting "Spin", optional text input: "Make it spicy", "Too heavy, something lighter", "Kids won't eat this".
  - **Locking**: Click the "Lock" icon on any component or day to preserve it while randomizing others.
  - **Global Re-roll**: "Shuffle all unlocked slots" based on the chosen path.

### The "Tweak Bar" (Input Controls)

Instead of typing, give the user sliders for the algorithm weights:

- **Adventurousness**: [Safe -------- Wild]
- **Effort**: [Lazy -------- Chef Mode]
- **Pantry Usage**: [Buy Fresh -------- Empty Fridge]

## 5. Cooking Mode: The "Chef's Chat" Bridge

While we will eventually have an in-app assistant, the power user workflow involves using their preferred external LLM (e.g., Gemini Advanced).

### The "Context Export" Feature

- **UI**: A prominent "Copy for AI" button on every Recipe and Plan view.
- **Function**: Generates a rich, specifically formatted prompt block and copies it to the clipboard.
- **Format**:

  ```text
  You are my Sous Chef. Here is what I am cooking:
  
  RECIPE: Chicken Tinga Tacos
  - Servings: 4
  - Ingredients: [List with user's specific brands/quantities]
  - Steps: [Full instructions]
  
  MY INVENTORY CONTEXT:
  - I have: [Related pantry items, e.g., "Sour cream (low)"]
  
  CURRENT STATE:
  I am about to start. Please be ready to answer questions about substitutions, timing, or technique. Wait for my first question.
  ```

- **Goal**: Frictionless hand-off to Gemini for questions like "Can I sub greek yogurt for sour cream?" or "How do I know when the chicken is done?"

## 6. Data Structures for Planning

```typescript
type PlanRequest = {
  dateRange: DateRange;
  attendees: number;
  constraints: string[]; // "No dairy"
  goals: string[]; // "Use spinach"
};

type PlanStrategy = {
  id: string;
  title: string; // "The Comfort Route"
  description: string; // "Hearty meals for a rainy week."
  primary_focus: "efficiency" | "variety" | "speed";
  preview_recipes: RecipeStub[]; // Just names/images
};

type DraftPlan = {
  strategy_id: string;
  days: {
    date: Date;
    meal: Recipe;
    locked: boolean;
    alternatives: Recipe[]; // Pre-fetched options for "Spinning"
  }[];
};
```
