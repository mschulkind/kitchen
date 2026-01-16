"""Import Legacy Pantry Stock. 🥫

Imports items from phase0_flow/stock_lists/pantry.json.

Usage:
    uv run python scripts/import_legacy_pantry.py --input-file "path/to/pantry.json" --household-id "UUID"
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from uuid import UUID

from supabase import acreate_client

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from src.api.app.core.config import get_settings
from src.api.app.domain.pantry.models import CreatePantryItemDTO, PantryLocation
from src.api.app.domain.pantry.repository import PantryRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def import_pantry(input_file: Path, household_id: UUID) -> None:
    """Main import logic."""
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        return

    settings = get_settings()

    # Use Service Role Key to bypass RLS
    supabase = await acreate_client(settings.supabase_url, settings.supabase_service_role_key)

    try:
        repo = PantryRepository(supabase)
        logger.info(f"Importing pantry for household {household_id}...")

        with open(input_file) as f:
            items = json.load(f)

        for item in items:
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
                notes="Legacy Import",
            )

            created = await repo.create(household_id, dto)
            logger.info(f"  - Created: {created.name} in {created.location}")

    finally:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import legacy pantry items.")
    parser.add_argument("--input-file", type=Path, required=True, help="Path to pantry.json")
    parser.add_argument("--household-id", type=UUID, required=True, help="Target Household UUID")

    args = parser.parse_args()

    asyncio.run(import_pantry(args.input_file, args.household_id))
