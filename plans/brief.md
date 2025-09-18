Project Summary: Personalized Dinner & Shopping App
This document outlines a preliminary design for a personal-use app to manage dinner recipes, meal planning, and grocery shopping. The primary goal is to create a highly usable, efficient tool that streamlines the process of cooking, tailored to the user's specific tastes, pantry inventory, and gardening habits.

Key Features & User Experience
Intelligent Meal Planning: The app will generate a coherent meal plan for a set number of days (e.g., 4 days) by selecting recipes that are efficient from an ingredient standpoint. The app will prioritize recipes that share ingredients, use up garden surpluses, and incorporate leftovers (e.g., roast chicken one night, chicken soup the next).

Dynamic Inventory Tracking: An internal data model will track pantry staples and fresh garden produce. The recipe selection algorithm will heavily favor recipes that use ingredients the user already has on hand, giving extra weight to common staples like milk and butter.

Intuitive Verification Interface: A core user experience will be the ingredient verification process. A "Categorical Checklist" UI will be implemented, grouping ingredients by their physical location in the kitchen (Pantry, Fridge, Freezer, Garden). This makes it easy for the user to confirm what they already have on hand.

Optimized Shopping List: After verification, the app will generate a final, definitive shopping list. This list will be sorted by average grocery store layout (e.g., Produce, Dairy, Meat) to optimize the in-store shopping trip. The final list will only show items the user needs to purchase.

Technical Architecture
Backend: The backend will be responsible for the core logic, including recipe selection, inventory management, and shopping list generation. It will include a PantryItem data model and a ShoppingListItem data model.

LLM Integration: An LLM agent will be integrated into the backend to provide dynamic capabilities, such as suggesting new recipes based on current ingredients, offering recipe variety, and customizing recipes on the fly.

This preliminary design document captures the core vision for the app, emphasizing usability and efficiency as the primary design drivers.

## Development Strategy: Phased Mobile-First Approach

To balance speed-to-market with a high-quality native mobile experience, we will adopt a two-phased development strategy. This approach prioritizes validating the core application logic and user flows before committing to a full-featured native build.

### Phase 1: Headless Backend & Progressive Web App (PWA)

1.  **Backend First:** The initial focus will be on building a robust, "headless" backend using Supabase. This includes the database schema, core business logic for meal planning and inventory, user authentication, and LLM integration.
2.  **Lightweight PWA:** A simple Progressive Web App will be developed using React to serve as the initial frontend. This PWA will be installable on mobile devices and support offline functionality, allowing us to test and validate the primary user experience—from meal planning to ingredient verification and shopping list generation—with real users quickly.

### Phase 2: Full-Featured React Native App

1.  **Native Build:** Once the backend is battle-tested and the core flows are validated, development will begin on a full-featured mobile application using React Native for both iOS and Android.
2.  **Enhanced UX:** This phase will focus on creating a polished, native user experience, incorporating features like push notifications, seamless animations, and deeper integration with device hardware.
3.  **PWA Maintenance:** The PWA can be maintained as a simple web-based alternative for users who prefer not to download a dedicated application.

This phased strategy mitigates risk, allows for early user feedback, and ensures the final native application is built on a solid, proven foundation.