"""Seed Pantry Staples. 🥫

Populates the pantry with common staples (Salt, Oil, Spices).

Usage:
    uv run python scripts/seed_staples.py --household-id "UUID"
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import TypedDict
from uuid import UUID

from supabase import acreate_client

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.api.app.core.config import get_settings
from src.api.app.domain.pantry.models import CreatePantryItemDTO, PantryLocation
from src.api.app.domain.pantry.repository import PantryRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StapleItem(TypedDict):
    name: str
    quantity: int
    unit: str
    location: str


STAPLES: list[StapleItem] = [
    {"name": "Kosher Salt", "quantity": 1, "unit": "box", "location": "pantry"},
    {"name": "Black Pepper", "quantity": 1, "unit": "jar", "location": "pantry"},
    {"name": "Olive Oil", "quantity": 1, "unit": "bottle", "location": "pantry"},
    {"name": "Vegetable Oil", "quantity": 1, "unit": "bottle", "location": "pantry"},
    {"name": "All-Purpose Flour", "quantity": 1, "unit": "bag", "location": "pantry"},
    {"name": "Granulated Sugar", "quantity": 1, "unit": "bag", "location": "pantry"},
    {"name": "White Rice", "quantity": 1, "unit": "bag", "location": "pantry"},
    {"name": "Pasta", "quantity": 2, "unit": "box", "location": "pantry"},
    {"name": "Soy Sauce", "quantity": 1, "unit": "bottle", "location": "fridge"},
    {"name": "Butter", "quantity": 1, "unit": "lb", "location": "fridge"},
    {"name": "Eggs", "quantity": 12, "unit": "count", "location": "fridge"},
    {"name": "Milk", "quantity": 1, "unit": "gallon", "location": "fridge"},
]

async def seed_data(household_id: UUID) -> None:
    """Main seed logic."""
    settings = get_settings()

    # Use Service Role Key to bypass RLS
    supabase = await acreate_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )

    try:
        repo = PantryRepository(supabase)
        logger.info(f"Seeding staples for household {household_id}...")

        for item in STAPLES:
            # Check duplication
            existing = await repo.search_by_name(household_id, item["name"], limit=1)
            if existing and existing[0].name.lower() == item["name"].lower():
                logger.info(f"  - Already exists: {item['name']}")
                continue

            dto = CreatePantryItemDTO(
                name=item["name"],
                quantity=float(item["quantity"]),
                unit=item["unit"],
                location=PantryLocation(item["location"]),
                notes="Seeded staple"
            )

            created = await repo.create(household_id, dto)
            logger.info(f"  - Created: {created.name}")

    finally:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed pantry staples.")
    parser.add_argument("--household-id", type=UUID, required=True, help="Target Household UUID")

    args = parser.parse_args()

    asyncio.run(seed_data(args.household_id))
