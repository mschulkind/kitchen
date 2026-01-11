"""Recipe API routes. 📖

REST endpoints for recipe management and ingestion.
Handles CRUD operations, URL ingestion, and ingredient parsing.

Fun fact: The average cookbook has about 150 recipes! 📚
"""

from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.api.app.db.session import get_supabase
from src.api.app.domain.recipes.models import (
    CreateRecipeDTO,
    IngestRecipeRequest,
    IngestRecipeResponse,
    ParsedIngredient,
    Recipe,
    UpdateRecipeDTO,
)
from src.api.app.domain.recipes.parser import IngredientParser
from src.api.app.domain.recipes.repository import RecipeRepository
from src.api.app.domain.recipes.service import (
    RecipeAlreadyExistsError,
    RecipeNotFoundError,
    RecipeService,
)

router = APIRouter(prefix="/recipes", tags=["Recipes 📖"])


async def get_recipe_service() -> AsyncGenerator[RecipeService, None]:
    """Dependency injection for RecipeService."""
    async with get_supabase() as supabase:
        repository = RecipeRepository(supabase)
        parser = IngredientParser()
        yield RecipeService(repository, parser)


# TODO: Replace with actual auth - get from JWT token
async def get_current_household_id() -> UUID:
    """Get the current user's household ID.

    This is a placeholder until auth is implemented.
    """
    return UUID("00000000-0000-0000-0000-000000000001")


class RecipeListResponse(BaseModel):
    """Paginated recipe list response."""

    recipes: list[Recipe]
    total: int
    page: int
    per_page: int


class ParseIngredientRequest(BaseModel):
    """Request to parse ingredient text."""

    text: str = Field(min_length=1, max_length=500)


class ParseIngredientsRequest(BaseModel):
    """Request to parse multiple ingredient texts."""

    texts: list[str] = Field(min_length=1, max_length=100)


@router.get("", response_model=RecipeListResponse)
async def list_recipes(
    service: Annotated[RecipeService, Depends(get_recipe_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=50)] = 20,
    tags: Annotated[list[str] | None, Query()] = None,
) -> RecipeListResponse:
    """List all recipes for the current household.

    Supports pagination and optional tag filtering.
    """
    recipes, total = await service.list_recipes(
        household_id,
        page=page,
        per_page=per_page,
        tags=tags,
    )
    return RecipeListResponse(
        recipes=recipes,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/search")
async def search_recipes(
    service: Annotated[RecipeService, Depends(get_recipe_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
    q: Annotated[str, Query(min_length=1, max_length=100)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[Recipe]:
    """Search recipes by title. 🔍"""
    return await service.search_recipes(household_id, q, limit=limit)


@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(
    recipe_id: UUID,
    service: Annotated[RecipeService, Depends(get_recipe_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> Recipe:
    """Get a single recipe by ID with ingredients."""
    try:
        return await service.get_recipe(recipe_id, household_id)
    except RecipeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe {recipe_id} not found",
        ) from None


@router.post("", response_model=Recipe, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    dto: CreateRecipeDTO,
    service: Annotated[RecipeService, Depends(get_recipe_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> Recipe:
    """Create a new recipe manually.

    For URL ingestion, use POST /recipes/ingest instead.
    """
    try:
        return await service.create_recipe(household_id, dto)
    except RecipeAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Recipe from {e.url} already exists",
        ) from None


@router.post("/ingest", response_model=IngestRecipeResponse)
async def ingest_recipe(
    request: IngestRecipeRequest,
    service: Annotated[RecipeService, Depends(get_recipe_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> IngestRecipeResponse:
    """Ingest a recipe from a URL. 🌐

    Fetches the page, extracts recipe data, and parses ingredients.
    """
    try:
        return await service.ingest_from_url(household_id, str(request.url))
    except RecipeAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Recipe already exists",
                "existing_id": str(e.existing_recipe.id),
            },
        ) from None


@router.patch("/{recipe_id}", response_model=Recipe)
async def update_recipe(
    recipe_id: UUID,
    dto: UpdateRecipeDTO,
    service: Annotated[RecipeService, Depends(get_recipe_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> Recipe:
    """Update an existing recipe. ✏️"""
    try:
        return await service.update_recipe(recipe_id, household_id, dto)
    except RecipeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe {recipe_id} not found",
        ) from None


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: UUID,
    service: Annotated[RecipeService, Depends(get_recipe_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> None:
    """Delete a recipe. 🗑️"""
    try:
        await service.delete_recipe(recipe_id, household_id)
    except RecipeNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recipe {recipe_id} not found",
        ) from None


# =========================================================================
# Ingredient Parsing Endpoints (Phase 2B)
# =========================================================================


@router.post("/parse-ingredient", response_model=ParsedIngredient)
async def parse_single_ingredient(
    request: ParseIngredientRequest,
) -> ParsedIngredient:
    """Parse a single ingredient string. 🧪

    Converts text like "1 large onion, diced" into structured data.
    """
    parser = IngredientParser()
    return parser.parse(request.text)


@router.post("/parse-ingredients", response_model=list[ParsedIngredient])
async def parse_multiple_ingredients(
    request: ParseIngredientsRequest,
) -> list[ParsedIngredient]:
    """Parse multiple ingredient strings. 🧪

    Batch parsing for efficiency.
    """
    parser = IngredientParser()
    return [parser.parse(text) for text in request.texts]
