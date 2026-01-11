"""Cooking API routes. 👨‍🍳

REST endpoints for cooking assistance and context export.

Fun fact: The "mise en place" philosophy can reduce cooking stress by 50%! 🧘
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from src.api.app.db.session import get_supabase
from src.api.app.domain.cooking.models import (
    ContextExportRequest,
    ContextExportResponse,
    CookingSession,
    MarkCookedRequest,
    MarkCookedResponse,
    MiseEnPlaceItem,
    RecipeStep,
)
from src.api.app.domain.cooking.service import CookingService
from src.api.app.domain.pantry.repository import PantryRepository
from src.api.app.domain.recipes.repository import RecipeRepository

router = APIRouter(prefix="/cooking", tags=["Cooking 👨‍🍳"])


async def get_cooking_service() -> CookingService:
    """Dependency injection for CookingService."""
    return CookingService()


# TODO: Replace with actual auth
async def get_current_household_id() -> UUID:
    """Get the current user's household ID."""
    return UUID("00000000-0000-0000-0000-000000000001")


class CookingContextResponse(BaseModel):
    """Full cooking context response."""

    recipe_title: str
    ingredients: list[str]
    instructions: list[str]
    available_ingredients: list[str]
    missing_ingredients: list[str]
    substitution_hints: list[str]


@router.get("/context/{recipe_id}", response_model=CookingContextResponse)
async def get_cooking_context(
    recipe_id: UUID,
    service: Annotated[CookingService, Depends(get_cooking_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> CookingContextResponse:
    """Get cooking context for a recipe. 📋

    Returns recipe info with inventory comparison for AI assistance.
    """
    # Fetch recipe and pantry items
    async with get_supabase() as supabase:
        recipe_repo = RecipeRepository(supabase)
        pantry_repo = PantryRepository(supabase)

        recipe = await recipe_repo.get_by_id(recipe_id, household_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe {recipe_id} not found",
            )

        recipe.ingredients = await recipe_repo._get_ingredients(recipe_id)
        pantry_items, _ = await pantry_repo.get_all_by_household(household_id)

    context = await service.get_cooking_context(recipe, pantry_items)

    return CookingContextResponse(
        recipe_title=context.recipe_title,
        ingredients=context.ingredients,
        instructions=context.instructions,
        available_ingredients=context.available_ingredients,
        missing_ingredients=context.missing_ingredients,
        substitution_hints=context.substitution_hints,
    )


@router.post("/export/{recipe_id}", response_model=ContextExportResponse)
async def export_cooking_context(
    recipe_id: UUID,
    request: ContextExportRequest,
    service: Annotated[CookingService, Depends(get_cooking_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> ContextExportResponse:
    """Export cooking context for clipboard. 📋

    Returns formatted context for pasting into AI assistants.
    """
    async with get_supabase() as supabase:
        recipe_repo = RecipeRepository(supabase)
        pantry_repo = PantryRepository(supabase)

        recipe = await recipe_repo.get_by_id(recipe_id, household_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe {recipe_id} not found",
            )

        recipe.ingredients = await recipe_repo._get_ingredients(recipe_id)
        pantry_items, _ = await pantry_repo.get_all_by_household(household_id)

    return await service.export_context(recipe, pantry_items, request)


@router.get("/mise-en-place/{recipe_id}", response_model=list[MiseEnPlaceItem])
async def get_mise_en_place(
    recipe_id: UUID,
    service: Annotated[CookingService, Depends(get_cooking_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> list[MiseEnPlaceItem]:
    """Get mise en place checklist for a recipe. ✅

    Returns prep tasks to complete before cooking.
    """
    async with get_supabase() as supabase:
        recipe_repo = RecipeRepository(supabase)

        recipe = await recipe_repo.get_by_id(recipe_id, household_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe {recipe_id} not found",
            )

        recipe.ingredients = await recipe_repo._get_ingredients(recipe_id)

    return await service.get_mise_en_place(recipe)


@router.get("/steps/{recipe_id}", response_model=list[RecipeStep])
async def get_recipe_steps(
    recipe_id: UUID,
    service: Annotated[CookingService, Depends(get_cooking_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> list[RecipeStep]:
    """Get recipe as step-by-step cards. 👣

    Returns individual steps for step-by-step cooking view.
    """
    async with get_supabase() as supabase:
        recipe_repo = RecipeRepository(supabase)

        recipe = await recipe_repo.get_by_id(recipe_id, household_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe {recipe_id} not found",
            )

    return await service.get_recipe_steps(recipe)


@router.post("/mark-cooked", response_model=MarkCookedResponse)
async def mark_recipe_cooked(
    request: MarkCookedRequest,
    service: Annotated[CookingService, Depends(get_cooking_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> MarkCookedResponse:
    """Mark a recipe as cooked and update inventory. ✅

    Decrements pantry quantities based on recipe ingredients.
    """
    async with get_supabase() as supabase:
        recipe_repo = RecipeRepository(supabase)
        pantry_repo = PantryRepository(supabase)

        recipe = await recipe_repo.get_by_id(request.recipe_id, household_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe {request.recipe_id} not found",
            )

        recipe.ingredients = await recipe_repo._get_ingredients(request.recipe_id)
        pantry_items, _ = await pantry_repo.get_all_by_household(household_id)

    return await service.mark_cooked(recipe, pantry_items, request)


@router.post("/session/{recipe_id}", response_model=CookingSession)
async def start_cooking_session(
    recipe_id: UUID,
    service: Annotated[CookingService, Depends(get_cooking_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
    servings: Annotated[int, Query(ge=1, le=20)] = 2,
) -> CookingSession:
    """Start a new cooking session. 🍳

    Returns a session object for tracking cooking progress.
    """
    async with get_supabase() as supabase:
        recipe_repo = RecipeRepository(supabase)

        recipe = await recipe_repo.get_by_id(recipe_id, household_id)
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recipe {recipe_id} not found",
            )

    return await service.start_cooking_session(recipe, servings)
