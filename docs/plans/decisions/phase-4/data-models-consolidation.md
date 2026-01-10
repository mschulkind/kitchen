# Decision: Review and Consolidate Data Models

## Overview
This decision consolidates core data models (e.g., PantryItem, ShoppingListItem, Recipe, MealPlan) for the app, ensuring they support features like inventory tracking, meal suggestions, and realtime sync. Models will be defined in Supabase PostgreSQL with row-level security, optimized for mobile/offline use per brief.md.

## Options
- **Option 1: Minimal Relational Models**
  - PantryItem: id, name, quantity, unit, expiry_date, location (enum: Pantry/Fridge/etc.), user_id
  - ShoppingListItem: id, name, quantity, category, checked, list_id, user_id
  - Basic foreign keys for lists/plans; no complex joins.

- **Option 2: Enhanced with Relationships and Validation**
  - Add Recipe: id, title, ingredients (jsonb array), instructions, nutrition, tags
  - MealPlan: id, date, recipe_id, servings, notes, shared_with (array of user_ids)
  - Include constraints (e.g., expiry validation), indexes for queries (e.g., by expiry).

- **Option 3: Flexible with JSONB Extensions**
  - Core tables relational, but use jsonb for dynamic fields (e.g., custom nutrition in PantryItem).
  - Supports LLM outputs (e.g., suggested substitutions as jsonb).

## Pros/Cons
- **Minimal Relational**:
  - Pros: Simple schema; fast queries; easy Supabase setup.
  - Cons: Limited extensibility; harder to add features like tags or custom fields later.

- **Enhanced Relational**:
  - Pros: Structured for integrity; supports complex queries (e.g., join for shopping from plans).
  - Cons: Schema rigidity; migration effort for changes.

- **JSONB Flexible**:
  - Pros: Adaptable for personalization (e.g., user-defined fields); good for AI integrations.
  - Cons: Query complexity; potential data inconsistency without validation.

## Questions for User
- Additional fields needed (e.g., photo_url for items, cost_estimate for lists)?
- Prioritize relationships (e.g., many-to-many for recipes and ingredients)?
- Validation rules (e.g., quantity >0, expiry alerts)?
- Offline support: Which fields to prioritize for local storage?

## Next Steps
Finalize schema with Mermaid ER diagram; update design-system.md with models. Reference: [plans/design-system.md](../design-system.md), [plans/brief.md](../brief.md).

*Decision Pending - Awaiting User Input*