# 🔍 Feature Reference Index

> **Purpose:** When designing a Kitchen feature, look it up here to instantly find how competitors implement the same or similar feature. Use this as a starting point for research and inspiration.
>
> **Last Updated:** 2026-02-18

---

## How to Use This Document

1. Find the feature you're designing in the table of contents
2. Read how each competitor implements it
3. Note the "💡 Kitchen Ideas" for what we should steal/improve
4. Follow the reference links for deeper dives

---

## Table of Contents

- [Recipe Import / Scraping](#recipe-import--scraping)
- [Recipe Organization & Search](#recipe-organization--search)
- [Recipe Display & Cook Mode](#recipe-display--cook-mode)
- [Recipe Scaling](#recipe-scaling)
- [Recipe PDF / Print / Export](#recipe-pdf--print--export)
- [Video-to-Recipe Extraction](#video-to-recipe-extraction)
- [Ingredient Parsing & Substitution](#ingredient-parsing--substitution)
- [Meal Planning Calendar](#meal-planning-calendar)
- [Meal Planning Rules & Filters](#meal-planning-rules--filters)
- [AI Recipe Generation & Suggestions](#ai-recipe-generation--suggestions)
- [Multi-Recipe Timeline Coordination](#multi-recipe-timeline-coordination)
- [Shopping List Basics](#shopping-list-basics)
- [Shopping List — Aisle Mapping & Store Intelligence](#shopping-list--aisle-mapping--store-intelligence)
- [Shopping List — Ingredient Merging](#shopping-list--ingredient-merging)
- [Grocery Delivery Integration](#grocery-delivery-integration)
- [Pantry & Inventory Tracking](#pantry--inventory-tracking)
- [Expiration Tracking & Waste Reduction](#expiration-tracking--waste-reduction)
- [Barcode Scanning](#barcode-scanning)
- [Multi-User / Household Collaboration](#multi-user--household-collaboration)
- [Real-Time Sync](#real-time-sync)
- [Voice-Guided Cooking](#voice-guided-cooking)
- [Smart Appliance Integration](#smart-appliance-integration)
- [Data Import / Migration](#data-import--migration)
- [Webhooks, Notifications & Integrations](#webhooks-notifications--integrations)
- [Gamification & Engagement](#gamification--engagement)
- [Expense Tracking](#expense-tracking)
- [Nutrition & Health Tracking](#nutrition--health-tracking)
- [Offline Support](#offline-support)
- [Self-Hosting & Deployment](#self-hosting--deployment)

---

## Recipe Import / Scraping

How apps get recipes from the web into the app.

### Paprika
- **Browser extension** (best-in-class) clips recipes from any website
- Strips blog fluff, extracts clean structured data
- Also supports manual entry
- **Ref:** [paprikaapp.com](https://www.paprikaapp.com)

### Mealie
- Built-in **URL scraper** using [recipe-scrapers](https://github.com/hhursev/recipe-scrapers) library
- Supports hundreds of sites via ld+json / schema.org microdata
- Also supports manual recipe creation via editor
- **Ref:** [docs.mealie.io/features](https://docs.mealie.io/documentation/getting-started/features/)

### Tandoor
- URL import via **ld+json or microdata** (schema.org/Recipe standard)
- Imports from 20+ other apps (Paprika, Mealie, Nextcloud, CopyMeThat, Mela, Cookmate, etc.)
- PDF import (experimental, uses Puppeteer)
- **Ref:** [docs.tandoor.dev/features/import_export](https://docs.tandoor.dev/features/import_export/)

### Cooked.wiki
- AI-powered extraction that **strips cluttered websites into clean instructions**
- Imports from **YouTube, TikTok, Instagram** video → step-by-step recipe
- Imports from **any file:** Word docs, PDFs, photos of handwritten recipes
- Creates recipes from **voice conversations** ("let Cooked listen to grandma explaining the recipe")
- **Ref:** [cooked.wiki](https://cooked.wiki), [cooked.wiki/pricing](https://cooked.wiki/pricing)

### RecipeOne
- AI captures from **social media screenshots, images, plain text**
- Converts to standardized searchable digital format
- **Ref:** [recipeone.app](https://www.recipeone.app)

### Plan to Eat
- **Browser bookmarklet** ("Recipe Clipper") — save while scrolling
- Manual entry supported
- **Ref:** [plantoeat.com](https://www.plantoeat.com)

### 💡 Kitchen Ideas
- Our firecrawl scraping is solid; consider adding **image/photo recipe capture** (RecipeOne approach)
- Cooked.wiki's **video-to-recipe** and **voice conversation capture** are killer features worth studying
- Tandoor's massive **import compatibility** (20+ formats) is aspirational for migrations

---

## Recipe Organization & Search

### Mealie
- **Three-tier system:** Categories (broad: Breakfast, Dinner), Tags (specific: frozen, leftover), Tools (equipment: pressure cooker)
- **Cookbooks:** saved filtered views combining categories + tags + tools
- Full-text search across all fields
- **Ref:** [docs.mealie.io/features](https://docs.mealie.io/documentation/getting-started/features/)

### Tandoor
- Tags, categories with **batch assignment**
- **Fulltext search** with PostgreSQL TrigramSimilarity (fuzzy matching)
- Quick merge and rename for ingredients, tags, units
- **Ref:** [docs.tandoor.dev](https://docs.tandoor.dev/)

### Paprika
- Categories, tags, search by ingredient
- **Pinning** active recipes for quick switching while cooking
- Cross-reference between recipes
- **Ref:** [paprikaapp.com](https://www.paprikaapp.com)

### Cooked.wiki
- **Automatic organization** — AI categorizes recipes for you
- Public profile for sharing with friends/family
- Personal notes on any recipe
- **Ref:** [cooked.wiki](https://cooked.wiki)

### 💡 Kitchen Ideas
- Mealie's **Cookbooks as saved filtered views** is elegant — worth copying
- Tandoor's **TrigramSimilarity** fuzzy search prevents "couldn't find it" frustration
- Cooked.wiki's **auto-categorization** reduces user work

---

## Recipe Display & Cook Mode

### Paprika
- **Highlight current step** by tapping directions
- **Cross off ingredients** as you prep
- **Screen stays on** during cooking (wake lock)
- **Pin active recipes** to switch between them
- **Auto-detected timers** in directions — tap to start
- **Ref:** [paprikaapp.com](https://www.paprikaapp.com)

### Cooked.wiki
- **Sub-recipe diagrams** — break complex recipes into clickable flowcharts
- **Ingredient sorting by role** — see what's critical vs optional at a glance
- **Complexity gauge** — visual indicator of recipe difficulty
- **AI voice reads the recipe** — hands-free audio walkthrough as a playlist
- **Ref:** [cooked.wiki/pricing](https://cooked.wiki/pricing)

### SideChef
- **Step-by-step voice-guided cooking** — hands-free, pauses when you need it
- **Adaptive pacing** — detects if user is slower, offers tips
- Real-time guidance adjusts to user speed
- **Ref:** [sidechef.com/business/recipe-ai/ai-in-home-cooking](https://www.sidechef.com/business/recipe-ai/ai-in-home-cooking)

### OnlyRecipe
- **"Tap-to-cook" hands-free mode** — minimalist, step-by-step
- Strips everything unnecessary
- **Ref:** [onlyrecipeapp.com](https://onlyrecipeapp.com)

### 💡 Kitchen Ideas
- Paprika's **tap-to-highlight step + cross-off ingredients + auto-timers** is the gold standard for cook mode
- Cooked.wiki's **sub-recipe flowcharts** are brilliant for complex meals (main + sides)
- SideChef's **adaptive pacing** is a differentiator — detect user speed and adjust
- Wake lock (screen stays on) is a MUST for cook mode

---

## Recipe Scaling

### Paprika
- **Automatic serving scaling** — adjust serving count, all ingredients recalculate
- Supports both **fractions and decimals**
- Built-in **metric ↔ imperial conversion**
- **Ref:** [paprikaapp.com](https://www.paprikaapp.com)

### Tandoor
- Supports **fractions or decimals** (user preference)
- Recipe scaling built into recipe display
- **Ref:** [docs.tandoor.dev](https://docs.tandoor.dev/)

### KitchenOwl
- Scaled ingredients in recipes
- **Ref:** [kitchenowl.org](https://kitchenowl.org)

### Dedicated Scaling Apps (2025)
- **Recipe Calculator (iOS):** AI-powered, 140+ ingredient density database for accurate volume↔weight
- **RecipeScaler+ (Android):** Visual scaling cues, smart substitutions, no account required
- Context-aware: doesn't linearly scale "a pinch of salt" or leavening ratios
- **Ref:** [bflux.co/products/recipe-calculator](https://bflux.co/products/recipe-calculator/), [RecipeScaler+ on Play Store](https://play.google.com/store/apps/details?id=com.bwjhub.recipescalerplus)

### 💡 Kitchen Ideas
- Fractions + decimals preference is table stakes
- **Non-linear scaling** (salt, leavening) is the advanced differentiator
- **Volume ↔ weight conversion** using ingredient density database — valuable for baking
- This is a gap for us — ship it soon

---

## Recipe PDF / Print / Export

### Cooked.wiki
- **Beautiful auto-generated printable PDFs** with only essentials
- Available free to all users (not paywalled)
- **Ref:** [cooked.wiki/pricing](https://cooked.wiki/pricing)

### Tandoor
- **PDF exporter** using Puppeteer (renders recipe page → PDF)
- Opt-in via `ENABLE_PDF_EXPORT=1` (downloads Chromium ~140MB)
- Printing views available
- **Ref:** [docs.tandoor.dev/features/import_export](https://docs.tandoor.dev/features/import_export/)

### Paprika
- Print recipes from within the app
- **Ref:** [paprikaapp.com](https://www.paprikaapp.com)

### 💡 Kitchen Ideas
- Cooked.wiki's approach (beautiful, auto-generated, free) is the model
- Our spec calls for **interleaved main+side timelines in PDF** — unique and valuable
- Consider server-side rendering vs Puppeteer (lighter weight options exist)

---

## Video-to-Recipe Extraction

### Cooked.wiki
- **YouTube, TikTok, Instagram → step-by-step recipe**
- AI watches the video and generates structured recipe
- Also supports **voice conversation capture** — record grandma explaining a recipe
- **Ref:** [cooked.wiki](https://cooked.wiki)

### 💡 Kitchen Ideas
- This is genuinely unique and magical — great future feature
- Could be done with Whisper (transcription) + LLM (structuring)
- Huge viral potential ("turn any cooking video into a recipe")

---

## Ingredient Parsing & Substitution

### SideChef
- AI-powered **ingredient substitution suggestions**
- Smart pairing based on flavor profiles and cuisine analysis
- **Ref:** [sidechef.com/business/recipe-ai/ai-in-home-cooking](https://www.sidechef.com/business/recipe-ai/ai-in-home-cooking)

### Mealie
- **Foods database** with 200+ seeded items
- **Units database** with common measurements
- Merge duplicate foods/units
- **Ref:** [docs.mealie.io/features](https://docs.mealie.io/documentation/getting-started/features/)

### Tandoor
- Quick **merge and rename** for ingredients, tags, units
- Structured ingredient parsing
- **Ref:** [docs.tandoor.dev](https://docs.tandoor.dev/)

### Dedicated Scaling Apps
- AI suggests substitutes adjusting proportions (dairy-free swaps, egg replacements, flavor-matched)
- **Ref:** Various (see Recipe Scaling section)

### 💡 Kitchen Ideas
- Our AI chat already handles substitution questions — formalize into a structured feature
- Mealie's **food/unit database seeding** is smart — avoids cold start
- Ingredient normalization (merge "chicken breast" / "boneless skinless chicken") is ongoing work

---

## Meal Planning Calendar

### Mealie
- Calendar view showing previous day + next 6 days
- Toggle through with arrows
- **Random recipe button** for inspiration
- **"Note" entries** for non-recipe items (leftovers, ordering out)
- **Ref:** [docs.mealie.io/features](https://docs.mealie.io/documentation/getting-started/features/)

### Plan to Eat
- **Drag-and-drop** recipes onto calendar days
- Plan for any length of time (week or month)
- **Reusable menus** — save meal plans as templates
- **Ref:** [plantoeat.com](https://www.plantoeat.com)

### Tandoor
- Plan **multiple meals per day**
- Shopping list generation from plan
- **Ref:** [docs.tandoor.dev](https://docs.tandoor.dev/)

### KitchenOwl
- Calendar-based meal planning
- Integrates with shopping lists
- **Ref:** [kitchenowl.org](https://kitchenowl.org)

### Grocy
- Meal planning connected to **inventory deduction**
- One-click "add missing ingredients to shopping list"
- **Due Score** — suggests recipes using ingredients expiring soon
- **Ref:** [grocy.info](https://grocy.info)

### 💡 Kitchen Ideas
- Plan to Eat's **reusable menus** (templates) are popular — consider for our planner
- Mealie's **Note entries** for non-recipe days is smart UX
- Grocy's **Due Score** (cook what's expiring) aligns with our waste-reduction goals
- Our **Slot Machine + Adventure Planner** is wildly differentiated from all of these

---

## Meal Planning Rules & Filters

### Mealie
- **Planner Rules:** restrict random recipe pool by Tags and/or Categories
- Rules can be set for **specific meal types** (Breakfast, Lunch, Dinner, Snack)
- Rules can target **specific days of the week**
- Example: "Breakfast on Monday only shows recipes tagged 'Quick'"
- **Ref:** [docs.mealie.io/features](https://docs.mealie.io/documentation/getting-started/features/)

### Ollie
- AI handles constraints automatically: budget, allergens, variety, time
- Black-box approach — less user control
- **Ref:** [ollie.ai](https://ollie.ai)

### 💡 Kitchen Ideas
- Mealie's per-meal-type, per-day-of-week rules are a **great pattern** to adopt
- Our Tweak Bar sliders (Adventurousness, Effort, Budget) go further than anyone else
- Combine Mealie's structured rules WITH our AI-driven Tweak Bar for best of both worlds

---

## AI Recipe Generation & Suggestions

### SideChef
- **Personalized recommendations** learning from cooking habits over time
- **Ingredients-to-recipe matching** — input/photograph fridge contents, get recipes
- Adapts to taste profiles, dietary needs, cookware available
- **Multi-recipe cooking guidance** — coordinates multiple dishes for simultaneous finish
- **Ref:** [sidechef.com/business/recipe-ai/ai-in-home-cooking](https://www.sidechef.com/business/recipe-ai/ai-in-home-cooking)

### MealFlow
- AI generates **complete meal plans from preferences**
- Handles allergies, budget, time constraints
- Plans entire week including snacks
- **Ref:** [mealflow.ai](https://www.mealflow.ai)

### MealChef
- AI recommends plans matching **dietary objectives**
- **Family voting** on recipe suggestions
- Evolves with family preferences over time
- **Ref:** [mealchef.ai](https://mealchef.ai)

### Cooked.wiki
- AI-first design — all recipes processed through AI for clean structure
- **Ref:** [cooked.wiki](https://cooked.wiki)

### 💡 Kitchen Ideas
- SideChef's **multi-recipe timeline coordination** is exactly our interleaved cooking timeline spec
- Their **ingredients-to-recipe** (photograph fridge) is a compelling future feature
- MealChef's **family voting** validates our spec idea — prioritize it
- Our **multi-LLM approach** (Gemini + Claude + OpenAI) is unique — no one else is provider-agnostic

---

## Multi-Recipe Timeline Coordination

### SideChef
- Users select **multiple dishes + target mealtime**
- System generates **single organized timeline** combining all recipes
- Steps interleaved so everything finishes simultaneously
- "A unique experience SideChef has been working on for many years"
- **Ref:** [sidechef.com/business/recipe-ai/ai-in-home-cooking](https://www.sidechef.com/business/recipe-ai/ai-in-home-cooking)

### 💡 Kitchen Ideas
- This is EXACTLY what our recipe PDF interleaved timeline spec describes
- SideChef has validated this feature — it's a known winner
- We should implement in cook mode AND in PDF export
- Could use LLM to generate timeline from recipe step data

---

## Shopping List Basics

### AnyList
- Real-time shared lists across devices
- Recipe importer → shopping list
- Meal planning calendar integration
- **Ref:** [anylist.com](https://www.anylist.com)

### Mealie
- Add items directly OR link recipes (all ingredients auto-added)
- See linked recipes with ingredients (toggle recipe view)
- Check off items, reorder, add/remove
- **Labels** for categorization (by food type, store, tool, recipe)
- Reorder labels for custom grouping
- **Ref:** [docs.mealie.io/features](https://docs.mealie.io/documentation/getting-started/features/)

### KitchenOwl
- Smart lists with **icons, amounts, and categories**
- Real-time sync across devices
- **Learns your tick-off order** and adapts suggestion ordering
- **Ref:** [kitchenowl.org](https://kitchenowl.org)

### Bring!
- **Visual item icons** (unique in category — beautiful grocery UX)
- Multi-list support
- Store loyalty card storage
- **Ref:** [getbring.com](https://www.getbring.com)

### 💡 Kitchen Ideas
- KitchenOwl's **learning tick-off order** is brilliant — adapts to your store layout automatically
- Bring!'s **visual icons** make shopping lists fun and fast to scan
- Mealie's **recipe linking** (see which recipes need which ingredients) is useful

---

## Shopping List — Aisle Mapping & Store Intelligence

### AnyList
- **Automatic categorization** by grocery aisle (Dairy, Produce, etc.)
- Smart grouping to minimize backtracking
- **Ref:** [anylist.com](https://www.anylist.com)

### Listonic
- **Auto-grouping by store section** — simulates aisle mapping
- Product suggestions based on habits
- **Ref:** [listonic.com](https://listonic.com)

### Grocy
- **Group products by assortment** to optimize store route
- "Never jump from one end to the other again"
- Minimum stock amounts auto-generate list items
- **Ref:** [grocy.info](https://grocy.info)

### SideChef
- **Groups ingredients by store section or availability**
- Minimizes in-store backtracking
- **Ref:** [sidechef.com/business/recipe-ai/ai-in-home-cooking](https://www.sidechef.com/business/recipe-ai/ai-in-home-cooking)

### 💡 Kitchen Ideas
- Our Store Intelligence spec (per-store aisle mapping) goes BEYOND all of these
- KitchenOwl's **learning approach** (observe → adapt) could complement our explicit mapping
- Phase 1: category auto-grouping (AnyList-level). Phase 2: per-store learning. Phase 3: custom aisle mapping.

---

## Shopping List — Ingredient Merging

### Paprika
- **Automatic combination:** `1 egg` + `2 eggs` = `3 eggs`
- Works across multiple recipes on the same list
- **Ref:** [paprikaapp.com](https://www.paprikaapp.com)

### 💡 Kitchen Ideas
- This is table stakes — we need it when adding multiple recipes to a shopping list
- Requires normalized ingredient parsing (units + quantities + ingredient names)

---

## Grocery Delivery Integration

### eMeals
- Push lists to **Walmart, Kroger, Instacart** directly
- "Done for you" automation
- **Ref:** [emeals.com](https://www.emeals.com)

### ChefsCart
- AI meal plans → **Instacart cart in one click**
- **Ref:** [chefscart.ai](https://chefscart.ai)

### SideChef
- **Shoppable recipe journeys** — add ingredients to cart for delivery/pickup
- **AI-powered product matching** (99% accuracy to real store SKUs)
- **Ref:** [sidechef.com/business/recipe-ai/ai-in-home-cooking](https://www.sidechef.com/business/recipe-ai/ai-in-home-cooking)

### APIs Available
- **Instacart:** [Developer Platform](https://docs.instacart.com/developer_platform_api/) — Public API (URL-based) or Partner API (in-app checkout, requires approval)
- **Walmart:** [Developer Portal](https://developer.walmart.com/) — REST API for items, carts, orders
- **Kroger:** [Developer Portal](https://developer.kroger.com/) — Product, cart, location APIs (free tier)

### 💡 Kitchen Ideas
- Start with **Instacart Public API** (URL-based, no approval needed) as MVP
- SideChef's 99% SKU matching is impressive — our AI could help here
- This is a parking lot feature but technically feasible

---

## Pantry & Inventory Tracking

### Grocy
- **Most comprehensive:** tracks groceries, supplies, chores, batteries, medications
- Purchase tracking with barcode scanning
- **Minimum stock levels** with auto-shopping-list generation
- Location-based (fridge, pantry, freezer, etc.)
- Custom fields on any entity
- **Ref:** [grocy.info](https://grocy.info)

### SideChef
- **"My Pantry" feature** — prefill with common staples
- Multiple input methods: manual, barcode, grocery account sync, **camera scan**
- Matches pantry to recipes ("cook with what you have")
- **Ref:** [sidechef.com/business/recipe-ai/ai-in-home-cooking](https://www.sidechef.com/business/recipe-ai/ai-in-home-cooking)

### NoWaste
- Barcode scanning, expiration tracking, smart notifications
- Recipe suggestions for soon-to-expire items
- **Ref:** [nowaste.ai](https://nowaste.ai)

### Mealie
- Foods database seeded with 200+ items
- Unit normalization
- **Ref:** [docs.mealie.io/features](https://docs.mealie.io/documentation/getting-started/features/)

### 💡 Kitchen Ideas
- Our "lazy discovery" (add items during cook verification) is more natural than Grocy's ERP approach
- SideChef's **multiple input methods** (especially camera scan) are compelling
- **Minimum stock levels** (Grocy) + AI suggestions (NoWaste) = powerful combo for us

---

## Expiration Tracking & Waste Reduction

### Grocy
- **"Due Score"** on recipes — indicates which recipes use up expiring ingredients
- Expiration date tracking on all inventory items
- **Ref:** [grocy.info](https://grocy.info)

### NoWaste
- **Smart notifications before items expire**
- AI suggests recipes for soon-to-expire ingredients
- **Ref:** [nowaste.ai](https://nowaste.ai)

### 💡 Kitchen Ideas
- Grocy's **Due Score** directly feeding into our Adventure Planner's scoring algorithm
- "Use It Up" mode: prioritize recipes that consume expiring pantry items
- NoWaste's approach + our AI chat = "what can I make with these 3 things expiring tomorrow?"

---

## Barcode Scanning

### Grocy
- **Camera-based barcode scanning** directly in web browser
- Integration with **Open Food Facts** for product lookup
- Plugin system for additional barcode services
- One-hand, 3-second workflow
- **Ref:** [grocy.info](https://grocy.info)

### Pantry Check
- Phone camera barcode scan → auto product details
- **Ref:** (app stores)

### 💡 Kitchen Ideas
- Open Food Facts integration is free and comprehensive
- Consider as a Phase 2 pantry enhancement
- React Native camera barcode scanning is well-supported

---

## Multi-User / Household Collaboration

### Mealie
- **Groups:** fully isolated tenants (separate recipe pools, users, everything)
- **Households:** subdivisions within a group — share recipes but have separate meal plans, shopping lists, integrations
- Sign-up links or admin-created users
- **Ref:** [docs.mealie.io/features](https://docs.mealie.io/documentation/getting-started/features/)

### KitchenOwl
- Households for collaborative recipes, expenses, shopping lists, meal plans
- Multi-user expense splitting
- **Ref:** [kitchenowl.org](https://kitchenowl.org)

### MealChef
- **Family voting on recipes** — household members vote on weekly meals
- Real-time grocery sync between family members
- **Ref:** [mealchef.ai](https://mealchef.ai)

### Cooked.wiki
- **Public profile** for friends/family sharing
- Social features — see what friends are cooking
- **Ref:** [cooked.wiki](https://cooked.wiki)

### 💡 Kitchen Ideas
- Mealie's **Group → Household** hierarchy is well-designed — study for our multi-tenant model
- MealChef's **family voting** is on our roadmap — validate it's a priority
- Our Supabase real-time gives us OurGroceries-level sync out of the box

---

## Real-Time Sync

### OurGroceries
- "Just works" — instant sync across all devices including smartwatches
- Voice input with smart home devices
- **Ref:** [ourgroceries.com](https://www.ourgroceries.com)

### KitchenOwl
- Real-time sync via native apps + web
- Partial offline with sync on reconnect
- **Ref:** [kitchenowl.org](https://kitchenowl.org)

### 💡 Kitchen Ideas
- We already have Supabase real-time — this is a STRENGTH. Make sure it feels as instant as OurGroceries.

---

## Voice-Guided Cooking

### SideChef
- **Best-in-class** voice-guided step-by-step cooking
- Hands-free, pauses when needed
- **Adaptive pacing** — detects user speed, offers tips when slow
- Integrates with Alexa & Google Home
- **Ref:** [sidechef.com/business/recipe-ai/ai-in-home-cooking](https://www.sidechef.com/business/recipe-ai/ai-in-home-cooking)

### Cooked.wiki
- **AI voices read the recipe as a playlist** — step through while prepping
- **Ref:** [cooked.wiki/pricing](https://cooked.wiki/pricing)

### 💡 Kitchen Ideas
- SideChef's adaptive pacing is the gold standard
- Cooked.wiki's "recipe as playlist" is a simpler MVP approach
- Our Phase 9 voice spec should study both approaches
- Web Speech API or Expo Speech could be our starting point

---

## Smart Appliance Integration

### SideChef
- Smart oven/fridge integration (Samsung, LG)
- Auto-set oven temperatures from recipe
- Send timers to devices
- **Ref:** [sidechef.com/business/recipe-ai/ai-in-home-cooking](https://www.sidechef.com/business/recipe-ai/ai-in-home-cooking)

### Yummly
- Whirlpool ecosystem integration
- Smart oven control
- **Ref:** [yummly.com](https://www.yummly.com)

### KitchenOwl
- **Home Assistant integration** via HACS
- **Ref:** [github.com/TomBursch/kitchenowl-ha](https://github.com/TomBursch/kitchenowl-ha)

### 💡 Kitchen Ideas
- KitchenOwl's **Home Assistant integration** is the self-hosted way to do this
- Rather than vendor-specific APIs, integrate with HA as a bridge to all smart devices
- This is a parking lot item but HA integration is architecturally interesting

---

## Data Import / Migration

### Tandoor (Gold Standard)
Supports importing from **22+ formats:**
- Mealie, Nextcloud Cookbook, Paprika, Chowdown, Safron, ChefTap, Pepperplate, RecipeSage, Domestica, MealMaster, RezKonv, OpenEats, Plan to Eat, CookBook Manager, Cooklang, CopyMeThat, Mela, Cookmate, Rezeptsuite.de, Gourmet, RecetteTek, PDF
- Also supports **exporting** to Default format, RecipeSage, Safron, PDF
- **Ref:** [docs.tandoor.dev/features/import_export](https://docs.tandoor.dev/features/import_export/)

### Mealie
- Imports from: Tandoor, Nextcloud, Paprika, Chowdown, Plan to Eat, RecipeKeeper, CopyMeThat, My Recipe Box, DVO Cook'n X3
- Bulk export in JSON
- **Ref:** [docs.mealie.io/features](https://docs.mealie.io/documentation/getting-started/features/)

### 💡 Kitchen Ideas
- Supporting **Mealie, Tandoor, and Paprika** import covers most self-hosted migrants
- schema.org/Recipe JSON-LD is the universal interchange format — prioritize it
- Export is equally important — never lock in user data

---

## Webhooks, Notifications & Integrations

### Mealie
- **Event-driven notifiers** via [Apprise](https://github.com/caronc/apprise/wiki) — supports hundreds of services
- Events: recipe CRUD, shopping list changes, mealplan creation
- **Scheduled webhooks** on mealplan days with plan data
- **Recipe Actions:** custom URL templates with merge fields (e.g., Bring! integration, HA triggers)
- Open REST API for full programmatic access
- **Ref:** [docs.mealie.io/features](https://docs.mealie.io/documentation/getting-started/features/)

### Tandoor
- API-driven, webhook support
- **Ref:** [docs.tandoor.dev](https://docs.tandoor.dev/)

### KitchenOwl
- **Home Assistant HACS integration**
- REST API
- **Ref:** [github.com/TomBursch/kitchenowl-ha](https://github.com/TomBursch/kitchenowl-ha)

### 💡 Kitchen Ideas
- Mealie's **Recipe Actions** with merge fields is clever — custom integrations without code
- Apprise library for notifications is battle-tested
- Our Supabase Edge Functions could handle event-driven notifications

---

## Gamification & Engagement

### Emerging Patterns (2025)
- **Cooking Streaks** (Duolingo-style) — "Cook 3 days in a row!" (20–30% retention lift)
- **Achievement Badges** — "Low Waste Chef", "Global Explorer", "Meal Prep Master"
- **Skill Tracking** — XP for baking, international dishes, technique mastery
- **Weekly Challenges** — "Zero Waste Week", "Use Up Your Pantry"
- **Family Voting** — household members vote on meals (MealChef)
- **Recipe Roulette** — random spinner (our Slot Machine!)
- **Progress Bars** — visual pantry organization score
- **Leaderboards** — community competition

### Sources
- [Trophy.so — Building Cooking Habits](https://trophy.so/blog/building-cooking-habits-gamification-ideas-for-recipe-apps)
- [Smartico.ai — Gamified Culinary World](https://www.smartico.ai/blog-post/gamified-innovations-reshaping-culinary-world)
- [Studio Krew — App Gamification 2025](https://studiokrew.com/blog/app-gamification-strategies-2025/)

### 💡 Kitchen Ideas
- **Streaks** are our lowest-hanging fruit — easy to implement, proven impact
- **Slot Machine** is our unique take on Recipe Roulette — already designed
- **Family Voting** solves a real pain point — "nobody can agree on dinner"
- Achievement badges are delightful with minimal engineering cost

---

## Expense Tracking

### KitchenOwl (Unique)
- Track expenses after shopping trips
- Divide costs between household members
- Balance management
- **Ref:** [kitchenowl.org](https://kitchenowl.org), [github.com/TomBursch/kitchenowl](https://github.com/TomBursch/kitchenowl)

### 💡 Kitchen Ideas
- Lightweight addition if we ever want it — parking lot
- Could tie into "cost per meal" analysis with AI

---

## Nutrition & Health Tracking

### Eat This Much
- Auto-generated plans based on **calorie/macro goals**
- Multiple diet support (keto, vegan, weight loss)
- **Ref:** [eatthismuch.com](https://www.eatthismuch.com)

### SideChef
- **Learns from wearables, sleep trackers, health apps** (future)
- Suggests meals based on biometrics
- **Ref:** [sidechef.com/business/recipe-ai/ai-in-home-cooking](https://www.sidechef.com/business/recipe-ai/ai-in-home-cooking)

### 💡 Kitchen Ideas
- Not our core focus (we're about cooking joy, not macro counting)
- But basic nutritional info on recipes would be useful
- Apple Health / Google Fit integration could be a differentiator long-term

---

## Offline Support

### KitchenOwl
- **Partial offline** — don't lose your shopping list when signal drops
- Queue changes, sync on reconnect
- **Ref:** [kitchenowl.org](https://kitchenowl.org)

### Paprika
- **Full offline** — all recipes stored locally, no internet needed
- **Ref:** [paprikaapp.com](https://www.paprikaapp.com)

### 💡 Kitchen Ideas
- Offline shopping list is critical (grocery stores have bad WiFi)
- Offline recipe viewing important for cooking (kitchen ≠ great signal)
- Our Supabase client SDK has offline queuing built in

---

## Self-Hosting & Deployment

### Mealie
- **Docker** with included examples for Kubernetes, Unraid, Synology
- Single container deployment
- Automatic backups (zip format)
- **Ref:** [docs.mealie.io](https://docs.mealie.io)

### Tandoor
- **Docker** with Docker Compose examples
- Kubernetes, Unraid, Synology support
- **Ref:** [docs.tandoor.dev](https://docs.tandoor.dev/)

### KitchenOwl
- **Docker** deployment
- Home Assistant add-on
- **Ref:** [docs.kitchenowl.org](https://docs.kitchenowl.org)

### Grocy
- **Docker** or bare-metal PHP
- PWA (installable web app)
- "Install any low-cost device in your kitchen as a 24/7 terminal"
- **Ref:** [grocy.info](https://grocy.info)

### 💡 Kitchen Ideas
- Our Docker Compose + Synology target (Decision D4) aligns with this space
- Mealie's backup strategy is worth studying
- Grocy's "kitchen terminal" idea is fun — a dedicated cheap tablet running Kitchen

---

*Built with 🐋 energy and way too much competitor website browsing.*
