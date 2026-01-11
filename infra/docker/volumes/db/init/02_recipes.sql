-- Kitchen Database Schema: Phase 2 - Recipe Engine 📖
-- Migration for recipes and ingredients tables
--
-- Fun fact: The oldest known recipe is a 4,000-year-old Sumerian beer recipe! 🍺

-- =============================================================================
-- Recipes Table (Phase 2A)
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.recipes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    household_id UUID NOT NULL REFERENCES public.households(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    source_url TEXT,
    source_domain TEXT,  -- Extracted for attribution (e.g., "seriouseats.com")
    servings INTEGER,
    prep_time_minutes INTEGER,
    cook_time_minutes INTEGER,
    total_time_minutes INTEGER,
    description TEXT,
    instructions JSONB,  -- Array of instruction steps
    tags TEXT[],  -- e.g., ["vegetarian", "quick", "mexican"]
    raw_markdown TEXT,  -- Optional per D12 (structured only)
    is_parsed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Index for source URL deduplication
CREATE UNIQUE INDEX IF NOT EXISTS idx_recipes_source_url 
    ON public.recipes(household_id, source_url) 
    WHERE source_url IS NOT NULL;

-- Index for searching recipes
CREATE INDEX IF NOT EXISTS idx_recipes_title_trgm 
    ON public.recipes USING gin (title gin_trgm_ops);

-- Index for tag filtering
CREATE INDEX IF NOT EXISTS idx_recipes_tags 
    ON public.recipes USING gin (tags);

-- =============================================================================
-- Recipe Ingredients Table (Phase 2B)
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.recipe_ingredients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recipe_id UUID NOT NULL REFERENCES public.recipes(id) ON DELETE CASCADE,
    raw_text TEXT NOT NULL,  -- Original text: "1 large onion, diced"
    quantity NUMERIC(10, 3),  -- Parsed: 1.0
    unit TEXT,  -- Normalized: "count"
    item_name TEXT NOT NULL,  -- Normalized: "onion"
    notes TEXT,  -- Extracted: "large, diced"
    section TEXT,  -- For grouped ingredients (e.g., "For the sauce")
    sort_order INTEGER DEFAULT 0,
    confidence NUMERIC(3, 2),  -- Parser confidence (0.0 - 1.0)
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Index for recipe lookup
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_recipe 
    ON public.recipe_ingredients(recipe_id);

-- Index for ingredient name search (for Delta Engine - Phase 3)
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_item_trgm 
    ON public.recipe_ingredients USING gin (item_name gin_trgm_ops);

-- =============================================================================
-- Row Level Security (RLS)
-- =============================================================================

ALTER TABLE public.recipes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recipe_ingredients ENABLE ROW LEVEL SECURITY;

-- Recipes policies
CREATE POLICY "Members can view recipes" ON public.recipes
    FOR SELECT USING (
        household_id IN (
            SELECT household_id FROM public.household_members
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Editors can insert recipes" ON public.recipes
    FOR INSERT WITH CHECK (
        household_id IN (
            SELECT household_id FROM public.household_members
            WHERE user_id = auth.uid() AND role IN ('owner', 'editor')
        )
    );

CREATE POLICY "Editors can update recipes" ON public.recipes
    FOR UPDATE USING (
        household_id IN (
            SELECT household_id FROM public.household_members
            WHERE user_id = auth.uid() AND role IN ('owner', 'editor')
        )
    );

CREATE POLICY "Editors can delete recipes" ON public.recipes
    FOR DELETE USING (
        household_id IN (
            SELECT household_id FROM public.household_members
            WHERE user_id = auth.uid() AND role IN ('owner', 'editor')
        )
    );

-- Recipe ingredients policies (inherit from recipe ownership)
CREATE POLICY "Members can view ingredients" ON public.recipe_ingredients
    FOR SELECT USING (
        recipe_id IN (
            SELECT r.id FROM public.recipes r
            JOIN public.household_members hm ON r.household_id = hm.household_id
            WHERE hm.user_id = auth.uid()
        )
    );

CREATE POLICY "Editors can manage ingredients" ON public.recipe_ingredients
    FOR ALL USING (
        recipe_id IN (
            SELECT r.id FROM public.recipes r
            JOIN public.household_members hm ON r.household_id = hm.household_id
            WHERE hm.user_id = auth.uid() AND hm.role IN ('owner', 'editor')
        )
    );

-- =============================================================================
-- Triggers
-- =============================================================================

CREATE TRIGGER update_recipes_updated_at
    BEFORE UPDATE ON public.recipes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Comments
-- =============================================================================

COMMENT ON TABLE public.recipes IS 'Ingested recipes with metadata and optional raw content';
COMMENT ON TABLE public.recipe_ingredients IS 'Parsed ingredients with normalized quantities and units';
COMMENT ON COLUMN public.recipe_ingredients.confidence IS 'Parser confidence score (1.0 = rule-based, 0.8 = LLM extracted)';
