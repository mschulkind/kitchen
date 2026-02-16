"""Planner API routes. 📅

REST endpoints for meal plan generation and management.
The "Choose Your Own Adventure" planner interface.

Fun fact: 70% of people decide what to eat less than an hour before the meal! 🤔
"""

from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.app.db.session import get_supabase
from src.api.app.domain.pantry.repository import PantryRepository
from src.api.app.domain.planner.models import (
    CreatePlanRequest,
    MealPlan,
    MealSlot,
    PlanOptionsResponse,
    PlanSummary,
    RecipeScore,
    SelectOptionRequest,
)
from src.api.app.domain.planner.repository import PlannerRepository
from src.api.app.domain.planner.service import PlannerService, PlanNotFoundError
from src.api.app.domain.recipes.repository import RecipeRepository

router = APIRouter(prefix="/planner", tags=["Planner 📅"])


async def get_planner_service() -> AsyncGenerator[PlannerService]:
    """Dependency injection for PlannerService."""
    async with get_supabase() as supabase:
        repository = PlannerRepository(supabase)
        yield PlannerService(repository)


async def get_recipes_for_planning() -> list:
    """Get all recipes for planning.

    In production, this would be a dependency.
    """
    async with get_supabase() as supabase:
        repository = RecipeRepository(supabase)
        recipes, _ = await repository.get_all_by_household(
            UUID("a0000000-0000-0000-0000-000000000001"),
            page=1,
            per_page=200,  # Get all
        )
        # Fetch ingredients for each
        for recipe in recipes:
            recipe.ingredients = await repository._get_ingredients(recipe.id)
        return recipes


async def get_pantry_items() -> list:
    """Get all pantry items for planning.

    In production, this would be a dependency.
    """
    async with get_supabase() as supabase:
        repository = PantryRepository(supabase)
        items, _ = await repository.get_all_by_household(
            UUID("a0000000-0000-0000-0000-000000000001"),
            page=1,
            per_page=500,  # Get all
        )
        return items


# TODO: Replace with actual auth
async def get_current_household_id() -> UUID:
    """Get the current user's household ID."""
    return UUID("a0000000-0000-0000-0000-000000000001")


# =========================================================================
# Plan Generation
# =========================================================================


@router.post("/generate", response_model=PlanOptionsResponse)
async def generate_plan_options(
    request: CreatePlanRequest,
    service: Annotated[PlannerService, Depends(get_planner_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> PlanOptionsResponse:
    """Generate meal plan options. 🎲

    Returns 3 thematic options for the user to choose from.
    This is the "Choose Your Own Adventure" interface.
    """
    # Get recipes and pantry items
    recipes = await get_recipes_for_planning()
    pantry_items = await get_pantry_items()

    if len(recipes) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need at least 3 recipes to generate a plan. Add more recipes first!",
        )

    return await service.generate_options(
        household_id,
        request,
        recipes,
        pantry_items,
    )


@router.post("/score-recipes", response_model=list[RecipeScore])
async def score_recipes(
    service: Annotated[PlannerService, Depends(get_planner_service)],
    _household_id: Annotated[UUID, Depends(get_current_household_id)],
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[RecipeScore]:
    """Score all recipes against current inventory. 📊

    Returns recipes sorted by how much of the ingredients you have.
    Useful for "What can I cook now?" feature.
    """
    recipes = await get_recipes_for_planning()
    pantry_items = await get_pantry_items()

    scores = await service.score_recipes(recipes, pantry_items)
    return scores[:limit]


# =========================================================================
# Plan Management
# =========================================================================


@router.get("/plans", response_model=list[PlanSummary])
async def list_plans(
    service: Annotated[PlannerService, Depends(get_planner_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
    include_archived: Annotated[bool, Query()] = False,
) -> list[PlanSummary]:
    """List all meal plans for the household."""
    return await service.list_plans(
        household_id,
        include_archived=include_archived,
    )


@router.get("/plans/active", response_model=MealPlan | None)
async def get_active_plan(
    service: Annotated[PlannerService, Depends(get_planner_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> MealPlan | None:
    """Get the current active meal plan.

    Returns None if no active plan.
    """
    return await service.get_active_plan(household_id)


@router.get("/plans/{plan_id}", response_model=MealPlan)
async def get_plan(
    plan_id: UUID,
    service: Annotated[PlannerService, Depends(get_planner_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> MealPlan:
    """Get a meal plan by ID with all meal slots."""
    try:
        return await service.get_plan(plan_id, household_id)
    except PlanNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {plan_id} not found",
        ) from None


@router.post("/plans", response_model=MealPlan, status_code=status.HTTP_201_CREATED)
async def create_plan(
    request: CreatePlanRequest,
    selected: SelectOptionRequest,
    service: Annotated[PlannerService, Depends(get_planner_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> MealPlan:
    """Create a new meal plan from a selected option. ✅

    Call POST /planner/generate first to get options,
    then call this with the selected option ID.
    """
    return await service.create_plan(household_id, request, selected)


@router.post("/plans/{plan_id}/activate", response_model=MealPlan)
async def activate_plan(
    plan_id: UUID,
    service: Annotated[PlannerService, Depends(get_planner_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> MealPlan:
    """Set a plan as the active plan. ✨

    Only one plan can be active at a time.
    """
    try:
        return await service.activate_plan(plan_id, household_id)
    except PlanNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {plan_id} not found",
        ) from None


@router.post("/plans/{plan_id}/complete", response_model=MealPlan)
async def complete_plan(
    plan_id: UUID,
    service: Annotated[PlannerService, Depends(get_planner_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> MealPlan:
    """Mark a plan as completed. ✅

    Typically called at the end of the week.
    """
    try:
        return await service.complete_plan(plan_id, household_id)
    except PlanNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {plan_id} not found",
        ) from None


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: UUID,
    service: Annotated[PlannerService, Depends(get_planner_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> None:
    """Delete a meal plan. 🗑️"""
    try:
        await service.delete_plan(plan_id, household_id)
    except PlanNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan {plan_id} not found",
        ) from None


# =========================================================================
# Meal Slots (Phase 6 prep)
# =========================================================================


@router.post("/plans/{plan_id}/slots/{slot_id}/lock")
async def lock_slot(
    plan_id: UUID,
    slot_id: UUID,
    service: Annotated[PlannerService, Depends(get_planner_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> MealSlot:
    """Lock a meal slot. 🔒

    Locked slots won't change when re-spinning the plan.
    Phase 6 "Slot Machine" feature.
    """
    slot = await service.lock_slot(slot_id, plan_id, household_id)
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found",
        )
    return slot


@router.post("/plans/{plan_id}/slots/{slot_id}/unlock")
async def unlock_slot(
    plan_id: UUID,
    slot_id: UUID,
    service: Annotated[PlannerService, Depends(get_planner_service)],
    household_id: Annotated[UUID, Depends(get_current_household_id)],
) -> MealSlot:
    """Unlock a meal slot. 🔓

    Unlocked slots can be changed when re-spinning.
    """
    slot = await service.unlock_slot(slot_id, plan_id, household_id)
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found",
        )
    return slot
