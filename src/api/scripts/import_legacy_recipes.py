"""Legacy Recipe & Plan Importer. 📦

Imports structured JSON data (recipes.json, plan.json) from Phase 0 folders
into the Supabase database.

Usage:
    uv run python scripts/import_legacy_recipes.py --input-dir "path/to/plan" --household-id "UUID"
"""

import argparse
import asyncio
import json
import logging
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from supabase import acreate_client
from src.api.app.core.config import get_settings
from src.api.app.domain.planner.models import MealType, PlanStatus
from src.api.app.domain.planner.repository import PlannerRepository
from src.api.app.domain.recipes.models import CreateRecipeDTO, ParsedIngredient
from src.api.app.domain.recipes.repository import RecipeRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_ingredient_string(raw: str) -> ParsedIngredient:
    """Heuristic parser for ingredient strings. 🧅"""
    # specific match for "2-3 lbs Chuck Roast..." -> qty=2.5? No, just take first number
    # Regex for start number: ^(\d+(?:\.\d+)?(?:-\d+)?)?\s*([a-zA-Z]+)?\s*(.*)$
    
    # Very simple fallback: use whole string as item_name
    qty = None
    unit = None
    name = raw

    # basic quantity extraction (e.g. "2 cups")
    match = re.match(r"^(\d+(?:\.\d+)?)\s*([a-zA-Z]+)?\s+(.+)$", raw)
    if match:
        try:
            qty = float(match.group(1))
            possible_unit = match.group(2)
            name = match.group(3)
            
            common_units = ["cup", "cups", "tbsp", "tsp", "oz", "lb", "lbs", "g", "kg", "ml", "l", "can", "cans", "clove", "cloves"]
            if possible_unit and possible_unit.lower().rstrip("s") in common_units:
                unit = possible_unit
            else:
                # if unit not recognized, maybe it's part of the name
                # e.g. "2 Large Onions" -> qty=2, unit=None, name="Large Onions"
                name = f"{possible_unit} {name}" if possible_unit else name
                unit = None
        except ValueError:
            pass

    return ParsedIngredient(
        raw_text=raw,
        quantity=qty,
        unit=unit,
        item_name=name.strip(),
        confidence=0.8
    )


async def import_data(input_dir: Path, household_id: UUID) -> None:
    """Main import logic."""
    recipes_file = input_dir / "recipes" / "recipes.json"
    plan_file = input_dir / "plan.json"

    if not recipes_file.exists():
        logger.error(f"Recipes file not found: {recipes_file}")
        return

    # Use Service Role Key to bypass RLS policies (avoid recursion error)
    settings = get_settings()
    logger.info(f"Using Supabase URL: {settings.supabase_url}")
    logger.info(f"Service Key (prefix): {settings.supabase_service_role_key[:10]}...")
    
    supabase = await acreate_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )

    try:
        recipe_repo = RecipeRepository(supabase)
        planner_repo = PlannerRepository(supabase)

        # 1. Import Recipes
        logger.info(f"Loading recipes from {recipes_file}...")
        with open(recipes_file) as f:
            recipes_data = json.load(f)

        recipe_map: dict[str, UUID] = {}

        for r_data in recipes_data:
            title = r_data["title"]
            logger.info(f"Processing recipe: {title}")

            # Check duplication
            existing = await recipe_repo.search_by_title(household_id, title, limit=1)
            if existing and existing[0].title == title:
                logger.info(f"  - Already exists: {existing[0].id}")
                recipe_map[title] = existing[0].id
                continue

            # Create Recipe
            dto = CreateRecipeDTO(
                title=title,
                servings=r_data.get("servings"),
                prep_time_minutes=r_data.get("prep_time_minutes"),
                cook_time_minutes=r_data.get("cook_time_minutes"),
                description=r_data.get("description"),
                instructions=r_data.get("instructions"),
                tags=["Legacy Import"],
            )
            
            recipe = await recipe_repo.create(household_id, dto)
            logger.info(f"  - Created: {recipe.id}")
            recipe_map[title] = recipe.id

            # Create Ingredients
            raw_ingredients = r_data.get("ingredients", [])
            parsed_ingredients = [parse_ingredient_string(s) for s in raw_ingredients]
            if parsed_ingredients:
                await recipe_repo.add_ingredients(recipe.id, parsed_ingredients)
                logger.info(f"  - Added {len(parsed_ingredients)} ingredients")

        # 2. Import Plan
        if not plan_file.exists():
            logger.warning("No plan.json found, skipping plan import.")
            return

        logger.info(f"Loading plan from {plan_file}...")
        with open(plan_file) as f:
            plan_data = json.load(f)

        # Create Plan
        start_date = date.fromisoformat(plan_data["start_date"])
        end_date = date.fromisoformat(plan_data["end_date"])
        
        plan = await planner_repo.create_plan(
            household_id=household_id,
            name=plan_data["name"],
            start_date=start_date,
            end_date=end_date,
            constraints=[plan_data.get("theme", "Legacy Import")]
        )
        logger.info(f"Created Plan: {plan.name} ({plan.id})")

        # Create Slots (only Dinner for now as per JSON)
        await planner_repo.create_slots(plan.id, start_date, end_date, [MealType.DINNER])
        slots = await planner_repo._get_slots(plan.id) # Access internal for ease
        
        # Map Plan JSON to Slots
        for day in plan_data["days"]:
            day_date = date.fromisoformat(day["date"])
            for meal in day["meals"]:
                meal_type = meal["type"].lower() # "dinner"
                recipe_title = meal.get("recipe_title")
                notes = meal.get("notes")

                # Find matching slot
                slot = next((s for s in slots if s.date == day_date and s.meal_type == meal_type), None)
                if not slot:
                    logger.warning(f"No slot found for {day_date} {meal_type}")
                    continue

                recipe_id = recipe_map.get(recipe_title)
                if recipe_id:
                    await planner_repo.update_slot(
                        slot.id, 
                        plan.id, 
                        household_id, 
                        recipe_id=recipe_id, 
                        recipe_title=recipe_title,
                        notes=notes
                    )
                    logger.info(f"  - Linked '{recipe_title}' to {day_date}")
                else:
                    logger.warning(f"  - Recipe not found for plan: '{recipe_title}'")
                    # Still add notes/title even if no link
                    await planner_repo.update_slot(
                        slot.id, 
                        plan.id, 
                        household_id, 
                        recipe_title=recipe_title,
                        notes=notes
                    )

        # Activate the plan
        await planner_repo.update_status(plan.id, household_id, PlanStatus.ACTIVE)
        logger.info("Plan marked as ACTIVE.")
        
    finally:
        # Supabase-py client doesn't need explicit close or uses a different method
        # The underlying http client might, but typically it's handled by garbage collection in scripts
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import legacy Phase 0 data.")
    parser.add_argument("--input-dir", type=Path, required=True, help="Path to plan directory")
    parser.add_argument("--household-id", type=UUID, required=True, help="Target Household UUID")
    
    args = parser.parse_args()
    
    asyncio.run(import_data(args.input_dir, args.household_id))
