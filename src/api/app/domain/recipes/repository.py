"""Recipe repository - Database access layer. 🗄️

Handles all database operations for recipes and ingredients.

Fun fact: The average American household has about 30 recipes in regular rotation! 📚
"""

from datetime import datetime
from typing import TYPE_CHECKING
from urllib.parse import urlparse
from uuid import UUID, uuid4

from src.api.app.domain.recipes.models import (
    CreateRecipeDTO,
    ParsedIngredient,
    Recipe,
    RecipeIngredient,
    UpdateRecipeDTO,
)

if TYPE_CHECKING:
    from supabase import AsyncClient


class RecipeRepository:
    """Repository for recipe CRUD operations. 📖"""

    RECIPES_TABLE = "recipes"
    INGREDIENTS_TABLE = "recipe_ingredients"

    def __init__(self, supabase: "AsyncClient") -> None:
        """Initialize repository with Supabase client."""
        self.supabase = supabase

    async def get_by_id(
        self,
        recipe_id: UUID,
        household_id: UUID,
        *,
        include_ingredients: bool = True,
    ) -> Recipe | None:
        """Get a recipe by ID with optional ingredients.

        Args:
            recipe_id: The recipe's unique identifier.
            household_id: The household to scope the query to (RLS).
            include_ingredients: Whether to fetch ingredients.

        Returns:
            Recipe if found, None otherwise.
        """
        result = await (
            self.supabase.table(self.RECIPES_TABLE)
            .select("*")
            .eq("id", str(recipe_id))
            .eq("household_id", str(household_id))
            .maybe_single()
            .execute()
        )

        if not result.data:
            return None

        recipe = Recipe.model_validate(result.data)

        if include_ingredients:
            recipe.ingredients = await self._get_ingredients(recipe_id)

        return recipe

    async def get_by_url(
        self,
        source_url: str,
        household_id: UUID,
    ) -> Recipe | None:
        """Get a recipe by its source URL (for deduplication).

        Args:
            source_url: The original recipe URL.
            household_id: The household to scope the query to.

        Returns:
            Recipe if found, None otherwise.
        """
        result = await (
            self.supabase.table(self.RECIPES_TABLE)
            .select("*")
            .eq("source_url", source_url)
            .eq("household_id", str(household_id))
            .maybe_single()
            .execute()
        )

        if result.data:
            return Recipe.model_validate(result.data)
        return None

    async def get_all_by_household(
        self,
        household_id: UUID,
        *,
        page: int = 1,
        per_page: int = 20,
        tags: list[str] | None = None,
    ) -> tuple[list[Recipe], int]:
        """Get all recipes for a household.

        Args:
            household_id: The household to fetch recipes for.
            page: Page number (1-indexed).
            per_page: Recipes per page.
            tags: Optional tag filter.

        Returns:
            Tuple of (recipes list, total count).
        """
        offset = (page - 1) * per_page

        query = (
            self.supabase.table(self.RECIPES_TABLE)
            .select("*", count="exact")
            .eq("household_id", str(household_id))
            .order("created_at", desc=True)
            .range(offset, offset + per_page - 1)
        )

        if tags:
            # Filter by any matching tag
            query = query.contains("tags", tags)

        result = await query.execute()

        recipes = [Recipe.model_validate(row) for row in result.data]
        total = result.count or 0

        return recipes, total

    async def search_by_title(
        self,
        household_id: UUID,
        query: str,
        *,
        limit: int = 10,
    ) -> list[Recipe]:
        """Search recipes by title (fuzzy match).

        Args:
            household_id: The household to search in.
            query: The search query.
            limit: Max results to return.

        Returns:
            Matching recipes.
        """
        result = await (
            self.supabase.table(self.RECIPES_TABLE)
            .select("*")
            .eq("household_id", str(household_id))
            .ilike("title", f"%{query}%")
            .limit(limit)
            .execute()
        )

        return [Recipe.model_validate(row) for row in result.data]

    async def create(
        self,
        household_id: UUID,
        dto: CreateRecipeDTO,
    ) -> Recipe:
        """Create a new recipe.

        Args:
            household_id: The household this recipe belongs to.
            dto: The recipe data.

        Returns:
            The created Recipe.
        """
        now = datetime.utcnow()

        # Extract domain from URL
        source_domain = None
        if dto.source_url:
            try:
                parsed = urlparse(dto.source_url)
                source_domain = parsed.netloc.replace("www.", "")
            except Exception:
                pass

        data = {
            "id": str(uuid4()),
            "household_id": str(household_id),
            "title": dto.title,
            "source_url": dto.source_url,
            "source_domain": source_domain,
            "servings": dto.servings,
            "prep_time_minutes": dto.prep_time_minutes,
            "cook_time_minutes": dto.cook_time_minutes,
            "total_time_minutes": (
                (dto.prep_time_minutes or 0) + (dto.cook_time_minutes or 0)
                if dto.prep_time_minutes or dto.cook_time_minutes
                else None
            ),
            "description": dto.description,
            "instructions": dto.instructions,
            "tags": dto.tags,
            "raw_markdown": dto.raw_markdown,
            "is_parsed": False,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        result = await (
            self.supabase.table(self.RECIPES_TABLE).insert(data).execute()
        )

        return Recipe.model_validate(result.data[0])

    async def update(
        self,
        recipe_id: UUID,
        household_id: UUID,
        dto: UpdateRecipeDTO,
    ) -> Recipe | None:
        """Update an existing recipe.

        Args:
            recipe_id: The recipe to update.
            household_id: The household (for RLS).
            dto: The fields to update.

        Returns:
            Updated Recipe if found, None otherwise.
        """
        update_data: dict = {"updated_at": datetime.utcnow().isoformat()}

        if dto.title is not None:
            update_data["title"] = dto.title
        if dto.servings is not None:
            update_data["servings"] = dto.servings
        if dto.prep_time_minutes is not None:
            update_data["prep_time_minutes"] = dto.prep_time_minutes
        if dto.cook_time_minutes is not None:
            update_data["cook_time_minutes"] = dto.cook_time_minutes
        if dto.description is not None:
            update_data["description"] = dto.description
        if dto.instructions is not None:
            update_data["instructions"] = dto.instructions
        if dto.tags is not None:
            update_data["tags"] = dto.tags

        # Recalculate total time if prep or cook time changed
        if "prep_time_minutes" in update_data or "cook_time_minutes" in update_data:
            update_data["total_time_minutes"] = (
                (update_data.get("prep_time_minutes") or 0) +
                (update_data.get("cook_time_minutes") or 0)
            ) or None

        result = await (
            self.supabase.table(self.RECIPES_TABLE)
            .update(update_data)
            .eq("id", str(recipe_id))
            .eq("household_id", str(household_id))
            .execute()
        )

        if result.data:
            return Recipe.model_validate(result.data[0])
        return None

    async def delete(self, recipe_id: UUID, household_id: UUID) -> bool:
        """Delete a recipe (cascades to ingredients).

        Args:
            recipe_id: The recipe to delete.
            household_id: The household (for RLS).

        Returns:
            True if deleted, False if not found.
        """
        result = await (
            self.supabase.table(self.RECIPES_TABLE)
            .delete()
            .eq("id", str(recipe_id))
            .eq("household_id", str(household_id))
            .execute()
        )

        return len(result.data) > 0

    async def mark_as_parsed(self, recipe_id: UUID) -> None:
        """Mark a recipe as having parsed ingredients."""
        await (
            self.supabase.table(self.RECIPES_TABLE)
            .update({"is_parsed": True, "updated_at": datetime.utcnow().isoformat()})
            .eq("id", str(recipe_id))
            .execute()
        )

    # =========================================================================
    # Ingredients
    # =========================================================================

    async def _get_ingredients(self, recipe_id: UUID) -> list[RecipeIngredient]:
        """Get all ingredients for a recipe."""
        result = await (
            self.supabase.table(self.INGREDIENTS_TABLE)
            .select("*")
            .eq("recipe_id", str(recipe_id))
            .order("sort_order")
            .execute()
        )

        return [RecipeIngredient.model_validate(row) for row in result.data]

    async def add_ingredients(
        self,
        recipe_id: UUID,
        ingredients: list[ParsedIngredient],
        *,
        section: str | None = None,
    ) -> list[RecipeIngredient]:
        """Add parsed ingredients to a recipe.

        Args:
            recipe_id: The recipe to add ingredients to.
            ingredients: List of parsed ingredients.
            section: Optional section name (e.g., "For the sauce").

        Returns:
            Created RecipeIngredient records.
        """
        now = datetime.utcnow()
        data = []

        for i, ing in enumerate(ingredients):
            data.append({
                "id": str(uuid4()),
                "recipe_id": str(recipe_id),
                "raw_text": ing.raw_text,
                "quantity": ing.quantity,
                "unit": ing.unit,
                "item_name": ing.item_name,
                "notes": ing.notes,
                "section": section,
                "sort_order": i,
                "confidence": ing.confidence,
                "created_at": now.isoformat(),
            })

        result = await (
            self.supabase.table(self.INGREDIENTS_TABLE).insert(data).execute()
        )

        return [RecipeIngredient.model_validate(row) for row in result.data]

    async def clear_ingredients(self, recipe_id: UUID) -> int:
        """Delete all ingredients for a recipe (for re-parsing).

        Args:
            recipe_id: The recipe to clear ingredients for.

        Returns:
            Number of deleted ingredients.
        """
        result = await (
            self.supabase.table(self.INGREDIENTS_TABLE)
            .delete()
            .eq("recipe_id", str(recipe_id))
            .execute()
        )

        return len(result.data)
