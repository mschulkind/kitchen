"""Recipe service - Business logic layer. 🧠

Orchestrates recipe ingestion, parsing, and management.

Fun fact: The first printed cookbook was published in 1485! 📖
"""

from uuid import UUID

from src.api.app.domain.recipes.models import (
    CreateRecipeDTO,
    IngestRecipeResponse,
    ParsedIngredient,
    Recipe,
    UpdateRecipeDTO,
)
from src.api.app.domain.recipes.parser import IngredientParser
from src.api.app.domain.recipes.repository import RecipeRepository


class RecipeNotFoundError(Exception):
    """Raised when a recipe is not found. 🔍"""

    def __init__(self, recipe_id: UUID) -> None:
        self.recipe_id = recipe_id
        super().__init__(f"Recipe {recipe_id} not found")


class RecipeAlreadyExistsError(Exception):
    """Raised when a recipe URL already exists. 🔄"""

    def __init__(self, url: str, existing_recipe: Recipe) -> None:
        self.url = url
        self.existing_recipe = existing_recipe
        super().__init__(f"Recipe from {url} already exists")


class RecipeService:
    """Service for recipe business logic. 📖

    Coordinates between the API layer, repository, and parser.
    """

    def __init__(
        self,
        repository: RecipeRepository,
        parser: IngredientParser | None = None,
    ) -> None:
        """Initialize service.

        Args:
            repository: The recipe repository instance.
            parser: Optional ingredient parser (created if not provided).
        """
        self.repository = repository
        self.parser = parser or IngredientParser()

    async def get_recipe(
        self,
        recipe_id: UUID,
        household_id: UUID,
        *,
        include_ingredients: bool = True,
    ) -> Recipe:
        """Get a single recipe.

        Args:
            recipe_id: The recipe's ID.
            household_id: The user's household ID.
            include_ingredients: Whether to fetch ingredients.

        Returns:
            The Recipe.

        Raises:
            RecipeNotFoundError: If recipe doesn't exist.
        """
        recipe = await self.repository.get_by_id(
            recipe_id,
            household_id,
            include_ingredients=include_ingredients,
        )
        if not recipe:
            raise RecipeNotFoundError(recipe_id)
        return recipe

    async def list_recipes(
        self,
        household_id: UUID,
        *,
        page: int = 1,
        per_page: int = 20,
        tags: list[str] | None = None,
    ) -> tuple[list[Recipe], int]:
        """List all recipes for a household.

        Args:
            household_id: The household to list recipes for.
            page: Page number (1-indexed).
            per_page: Recipes per page.
            tags: Optional tag filter.

        Returns:
            Tuple of (recipes, total count).
        """
        return await self.repository.get_all_by_household(
            household_id,
            page=page,
            per_page=per_page,
            tags=tags,
        )

    async def create_recipe(
        self,
        household_id: UUID,
        dto: CreateRecipeDTO,
        *,
        ingredient_texts: list[str] | None = None,
    ) -> Recipe:
        """Create a new recipe.

        Args:
            household_id: The household to add the recipe to.
            dto: The recipe data.
            ingredient_texts: Optional raw ingredient strings to parse.

        Returns:
            The created Recipe.

        Raises:
            RecipeAlreadyExistsError: If URL already exists for this household.
        """
        # Check for duplicate URL
        if dto.source_url:
            existing = await self.repository.get_by_url(dto.source_url, household_id)
            if existing:
                raise RecipeAlreadyExistsError(dto.source_url, existing)

        # Normalize title
        dto = CreateRecipeDTO(
            title=dto.title.strip(),
            source_url=dto.source_url,
            servings=dto.servings,
            prep_time_minutes=dto.prep_time_minutes,
            cook_time_minutes=dto.cook_time_minutes,
            description=dto.description,
            instructions=dto.instructions,
            tags=[t.lower().strip() for t in dto.tags] if dto.tags else None,
            raw_markdown=dto.raw_markdown,
        )

        recipe = await self.repository.create(household_id, dto)

        # Parse ingredients if provided
        if ingredient_texts:
            parsed = self.parser.parse_many(ingredient_texts)
            await self.repository.add_ingredients(recipe.id, parsed)
            await self.repository.mark_as_parsed(recipe.id)
            recipe.ingredients = await self.repository._get_ingredients(recipe.id)

        return recipe

    async def update_recipe(
        self,
        recipe_id: UUID,
        household_id: UUID,
        dto: UpdateRecipeDTO,
    ) -> Recipe:
        """Update an existing recipe.

        Args:
            recipe_id: The recipe to update.
            household_id: The user's household ID.
            dto: The fields to update.

        Returns:
            The updated Recipe.

        Raises:
            RecipeNotFoundError: If recipe doesn't exist.
        """
        recipe = await self.repository.update(recipe_id, household_id, dto)
        if not recipe:
            raise RecipeNotFoundError(recipe_id)
        return recipe

    async def delete_recipe(self, recipe_id: UUID, household_id: UUID) -> None:
        """Delete a recipe.

        Args:
            recipe_id: The recipe to delete.
            household_id: The user's household ID.

        Raises:
            RecipeNotFoundError: If recipe doesn't exist.
        """
        deleted = await self.repository.delete(recipe_id, household_id)
        if not deleted:
            raise RecipeNotFoundError(recipe_id)

    async def parse_ingredients(
        self,
        recipe_id: UUID,
        household_id: UUID,
        ingredient_texts: list[str],
        *,
        replace_existing: bool = True,
    ) -> list[ParsedIngredient]:
        """Parse and store ingredients for a recipe.

        Args:
            recipe_id: The recipe to add ingredients to.
            household_id: The user's household ID.
            ingredient_texts: Raw ingredient strings.
            replace_existing: Whether to clear existing ingredients first.

        Returns:
            List of parsed ingredients.

        Raises:
            RecipeNotFoundError: If recipe doesn't exist.
        """
        # Verify recipe exists
        recipe = await self.repository.get_by_id(
            recipe_id,
            household_id,
            include_ingredients=False,
        )
        if not recipe:
            raise RecipeNotFoundError(recipe_id)

        # Clear existing if requested
        if replace_existing:
            await self.repository.clear_ingredients(recipe_id)

        # Parse and store
        parsed = self.parser.parse_many(ingredient_texts)
        await self.repository.add_ingredients(recipe_id, parsed)
        await self.repository.mark_as_parsed(recipe_id)

        return parsed

    async def search_recipes(
        self,
        household_id: UUID,
        query: str,
        *,
        limit: int = 10,
    ) -> list[Recipe]:
        """Search recipes by title.

        Args:
            household_id: The household to search in.
            query: The search query.
            limit: Max results.

        Returns:
            Matching recipes.
        """
        return await self.repository.search_by_title(household_id, query, limit=limit)

    # =========================================================================
    # Ingestion (Phase 2A - Placeholder for Firecrawl integration)
    # =========================================================================

    async def ingest_from_url(
        self,
        household_id: UUID,
        url: str,
        *,
        parse_ingredients: bool = True,
    ) -> IngestRecipeResponse:
        """Ingest a recipe from a URL.

        This is a placeholder for the full Firecrawl integration.
        Currently creates a minimal recipe with the URL.

        Args:
            household_id: The household to add the recipe to.
            url: The recipe URL to scrape.
            parse_ingredients: Whether to parse ingredients after ingestion.

        Returns:
            IngestRecipeResponse with the created recipe.
        """
        # Check for existing
        existing = await self.repository.get_by_url(url, household_id)
        if existing:
            raise RecipeAlreadyExistsError(url, existing)

        # TODO: Implement Firecrawl scraping
        # For now, create a placeholder recipe
        dto = CreateRecipeDTO(
            title=f"Recipe from {url}",  # Placeholder
            source_url=url,
        )

        recipe = await self.repository.create(household_id, dto)

        return IngestRecipeResponse(
            recipe=recipe,
            ingredients_parsed=0,
            source="manual",  # Will be "firecrawl" when implemented
        )
