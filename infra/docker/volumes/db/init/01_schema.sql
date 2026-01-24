-- Kitchen Database Schema 🗄️
-- Initial migration for Phase 1: Foundation & Inventory
--
-- Fun fact: PostgreSQL was created in 1996 at UC Berkeley! 🎓

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text matching

-- =============================================================================
-- Users & Households
-- =============================================================================

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY, -- Matches auth.users(id)
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Households (groups of users sharing inventory)
CREATE TABLE IF NOT EXISTS public.households (
    id UUID PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
    name TEXT NOT NULL,
    owner_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Household members (many-to-many with roles)
CREATE TABLE IF NOT EXISTS public.household_members (
    id UUID PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
    household_id UUID NOT NULL REFERENCES public.households(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'editor', 'viewer')),
    joined_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    UNIQUE(household_id, user_id)
);

-- =============================================================================
-- Pantry Items (Phase 1 Core)
-- =============================================================================

-- Storage locations enum
CREATE TYPE pantry_location AS ENUM ('pantry', 'fridge', 'freezer', 'counter', 'garden');

-- Pantry items table
CREATE TABLE IF NOT EXISTS public.pantry_items (
    id UUID PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
    household_id UUID NOT NULL REFERENCES public.households(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    quantity NUMERIC(10, 3) NOT NULL CHECK (quantity >= 0),
    unit TEXT NOT NULL,
    location pantry_location NOT NULL DEFAULT 'pantry',
    expiry_date DATE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Index for fast name searches (using trigram for fuzzy matching)
CREATE INDEX IF NOT EXISTS idx_pantry_items_name_trgm 
    ON public.pantry_items USING gin (name gin_trgm_ops);

-- Index for household lookups
CREATE INDEX IF NOT EXISTS idx_pantry_items_household 
    ON public.pantry_items(household_id);

-- Index for expiry date (find expiring items)
CREATE INDEX IF NOT EXISTS idx_pantry_items_expiry 
    ON public.pantry_items(expiry_date) 
    WHERE expiry_date IS NOT NULL;

-- =============================================================================
-- Row Level Security (RLS)
-- =============================================================================

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.households ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.household_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pantry_items ENABLE ROW LEVEL SECURITY;

-- Users can read/update their own profile
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- Household policies
CREATE POLICY "Members can view their households" ON public.households
    FOR SELECT USING (
        id IN (
            SELECT household_id FROM public.household_members
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Owners can update their households" ON public.households
    FOR UPDATE USING (owner_id = auth.uid());

CREATE POLICY "Users can create households" ON public.households
    FOR INSERT WITH CHECK (owner_id = auth.uid());

-- Household members policies
CREATE POLICY "Members can view household members" ON public.household_members
    FOR SELECT USING (
        household_id IN (
            SELECT household_id FROM public.household_members
            WHERE user_id = auth.uid()
        )
    );

-- Pantry items policies (CRITICAL for data isolation!)
CREATE POLICY "Members can view pantry items" ON public.pantry_items
    FOR SELECT USING (
        household_id IN (
            SELECT household_id FROM public.household_members
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Editors can insert pantry items" ON public.pantry_items
    FOR INSERT WITH CHECK (
        household_id IN (
            SELECT household_id FROM public.household_members
            WHERE user_id = auth.uid() AND role IN ('owner', 'editor')
        )
    );

CREATE POLICY "Editors can update pantry items" ON public.pantry_items
    FOR UPDATE USING (
        household_id IN (
            SELECT household_id FROM public.household_members
            WHERE user_id = auth.uid() AND role IN ('owner', 'editor')
        )
    );

CREATE POLICY "Editors can delete pantry items" ON public.pantry_items
    FOR DELETE USING (
        household_id IN (
            SELECT household_id FROM public.household_members
            WHERE user_id = auth.uid() AND role IN ('owner', 'editor')
        )
    );

-- =============================================================================
-- Triggers for updated_at
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_households_updated_at
    BEFORE UPDATE ON public.households
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pantry_items_updated_at
    BEFORE UPDATE ON public.pantry_items
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Development Seed Data
-- =============================================================================

-- Only run in development!
DO $$
BEGIN
    -- Create a default household for development
    INSERT INTO public.households (id, name, owner_id)
    VALUES (
        '00000000-0000-0000-0000-000000000001',
        'Development Household',
        '00000000-0000-0000-0000-000000000000'  -- Will fail without auth user
    )
    ON CONFLICT DO NOTHING;
EXCEPTION
    WHEN foreign_key_violation THEN
        -- Expected in dev without auth user
        NULL;
END $$;

COMMENT ON TABLE public.pantry_items IS 'Inventory items stored in the household pantry, fridge, freezer, etc.';
COMMENT ON COLUMN public.pantry_items.quantity IS 'Amount of the item. Use with unit for full measurement.';
COMMENT ON COLUMN public.pantry_items.unit IS 'Unit of measurement (e.g., kg, count, ml, bunch)';

-- =============================================================================
-- Realtime Publication 📡
-- Enable realtime subscriptions for collaborative features
-- =============================================================================
CREATE PUBLICATION IF NOT EXISTS supabase_realtime;
ALTER PUBLICATION supabase_realtime ADD TABLE pantry_items;
