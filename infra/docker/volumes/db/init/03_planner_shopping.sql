-- Kitchen Database Schema: Phase 5 & 7 - Planner & Shopping 🛒
--
-- Fun fact: The first shopping cart was invented in 1937 and was originally a folding chair with a basket! 🛒

-- =============================================================================
-- Meal Plans (Phase 5)
-- note: Currently storing 'slots' directly in 'meal_plans' table for simplicity.
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.meal_plans (
    id UUID PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
    household_id UUID NOT NULL REFERENCES public.households(id) ON DELETE CASCADE,
    recipe_id UUID REFERENCES public.recipes(id) ON DELETE SET NULL,
    date DATE NOT NULL,
    meal_type TEXT NOT NULL DEFAULT 'main', -- 'main', 'lunch', 'breakfast'
    locked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Index for date range queries (Planner View)
CREATE INDEX IF NOT EXISTS idx_meal_plans_date 
    ON public.meal_plans(date);

-- Index for household
CREATE INDEX IF NOT EXISTS idx_meal_plans_household 
    ON public.meal_plans(household_id);

-- =============================================================================
-- Shopping List (Phase 7)
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.shopping_list (
    id UUID PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
    household_id UUID NOT NULL REFERENCES public.households(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    quantity NUMERIC(10, 3) DEFAULT 1,
    unit TEXT,
    checked BOOLEAN DEFAULT FALSE,
    category TEXT DEFAULT 'Other',
    aisle_hint TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Index for efficient sorting/filtering
CREATE INDEX IF NOT EXISTS idx_shopping_list_household 
    ON public.shopping_list(household_id);

-- =============================================================================
-- Row Level Security (RLS)
-- =============================================================================

ALTER TABLE public.meal_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shopping_list ENABLE ROW LEVEL SECURITY;

-- Meal Plans Policies
CREATE POLICY "Members can view meal plans" ON public.meal_plans
    FOR SELECT USING (
        household_id IN (
            SELECT household_id FROM public.household_members
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Editors can manage meal plans" ON public.meal_plans
    FOR ALL USING (
        household_id IN (
            SELECT household_id FROM public.household_members
            WHERE user_id = auth.uid() AND role IN ('owner', 'editor')
        )
    );

-- Shopping List Policies
CREATE POLICY "Members can view shopping list" ON public.shopping_list
    FOR SELECT USING (
        household_id IN (
            SELECT household_id FROM public.household_members
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Editors can manage shopping list" ON public.shopping_list
    FOR ALL USING (
        household_id IN (
            SELECT household_id FROM public.household_members
            WHERE user_id = auth.uid() AND role IN ('owner', 'editor')
        )
    );

-- =============================================================================
-- Triggers
-- =============================================================================

CREATE TRIGGER update_meal_plans_updated_at
    BEFORE UPDATE ON public.meal_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shopping_list_updated_at
    BEFORE UPDATE ON public.shopping_list
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
