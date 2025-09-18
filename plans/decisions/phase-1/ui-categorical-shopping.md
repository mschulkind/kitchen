# Decision: Refine Categorical UI for Shopping Lists

## Overview
This decision outlines the approach to implementing categorical organization for shopping lists in the mobile-first PWA. Categories (e.g., Produce, Dairy, Meat) will help users scan and complete lists efficiently, aligned with store layouts for quick shopping. The UI must support touch interactions, drag-to-reorder, and sync with realtime collaboration.

## Options
- **Option 1: Fixed Categories with Drag-and-Drop Reordering**
  - Predefined categories based on common grocery layouts (Produce, Dairy, Bakery, Meat, Frozen, etc.).
  - Users can drag items between categories; categories are collapsible accordions.
  - Integration: Auto-categorize new items via LLM or user input.

- **Option 2: User-Customizable Categories**
  - Allow users to create/edit categories (e.g., add "Garden Fresh" for home-grown items).
  - Supports favorites or presets, with drag-to-reorder within and between categories.
  - Integration: Sync custom categories across devices via Supabase.

- **Option 3: Hybrid with Store Layout Mapping**
  - Fixed base categories mapped to user-selected store (e.g., Whole Foods vs. Local Market).
  - AI-assisted sorting based on inventory/shopping history; manual overrides via swipe gestures.

## Pros/Cons
- **Fixed Categories**:
  - Pros: Simple, fast setup; consistent for multiuser sharing; reduces decision fatigue.
  - Cons: Less flexible for unique needs (e.g., dietary-specific groups); may not fit all stores.

- **User-Customizable**:
  - Pros: Personalized; adapts to user habits (e.g., keto-focused categories).
  - Cons: Complexity in UI for editing; potential sync conflicts in collaboration.

- **Hybrid**:
  - Pros: Balances simplicity and personalization; leverages LLM for smart defaults.
  - Cons: Requires store data integration; higher dev effort for mapping.

## Questions for User
- What primary categories should be default (e.g., include "Pantry Staples" or focus on perishables)?
- Preferred interaction: Drag-and-drop, swipe-to-categorize, or voice input via Expo?
- How important is store-specific layout mapping (e.g., for major chains vs. local)?
- Any accessibility needs (e.g., voice-over support for categories)?

## Next Steps
Once decided, update ux-flow.md with wireframes (Mermaid diagrams) and design-system.md with component specs. Reference: [plans/ux-flow.md](../ux-flow.md), [plans/design-system.md](../design-system.md).

*Decision Pending - Awaiting User Input*