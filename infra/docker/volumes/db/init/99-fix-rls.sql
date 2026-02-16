-- Fix RLS recursion on household_members
DROP POLICY IF EXISTS "Members can view household members" ON household_members;
CREATE POLICY "Users can see own membership" ON household_members FOR SELECT USING (user_id = auth.uid());

-- Ensure service_role bypasses RLS (Critical for Seeding)
ALTER ROLE service_role WITH BYPASSRLS;

-- Grant permissions to authenticated users (required for RLS to work properly)
GRANT ALL ON users TO authenticated;
GRANT ALL ON household_members TO authenticated;
GRANT ALL ON pantry_items TO authenticated;
GRANT ALL ON households TO authenticated;
GRANT ALL ON recipes TO authenticated;
GRANT ALL ON recipe_ingredients TO authenticated;
GRANT ALL ON meal_plans TO authenticated;
GRANT ALL ON shopping_list TO authenticated;

-- Grant permissions to service_role (Critical for Seeding)
GRANT ALL ON users TO service_role;
GRANT ALL ON household_members TO service_role;
GRANT ALL ON pantry_items TO service_role;
GRANT ALL ON households TO service_role;
GRANT ALL ON recipes TO service_role;
GRANT ALL ON recipe_ingredients TO service_role;
GRANT ALL ON meal_plans TO service_role;
GRANT ALL ON shopping_list TO service_role;

-- Grant permissions to anon role (used by API server with anon key)
GRANT ALL ON users TO anon;
GRANT ALL ON household_members TO anon;
GRANT ALL ON pantry_items TO anon;
GRANT ALL ON households TO anon;
GRANT ALL ON recipes TO anon;
GRANT ALL ON recipe_ingredients TO anon;
GRANT ALL ON meal_plans TO anon;
GRANT ALL ON shopping_list TO anon;
