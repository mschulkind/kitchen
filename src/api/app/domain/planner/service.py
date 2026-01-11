"""Planner service - Business logic layer. 🧠

Orchestrates meal plan generation and management.

Fun fact: Meal planning can reduce food costs by up to 20%! 💰
"""

from uuid import UUID

from src.api.app.domain.pantry.models import PantryItem
from src.api.app.domain.planner.generator import PlanGenerator
from src.api.app.domain.planner.models import (
    CreatePlanRequest,
    MealPlan,
    MealSlot,
    PlanOptionsResponse,
    PlanStatus,
    PlanSummary,
    RecipeScore,
    ScoringCriteria,
    SelectOptionRequest,
)
from src.api.app.domain.planner.repository import PlannerRepository
from src.api.app.domain.planner.scorer import RecipeScorer
from src.api.app.domain.recipes.models import Recipe


class PlanNotFoundError(Exception):
    """Raised when a meal plan is not found. 🔍"""

    def __init__(self, plan_id: UUID) -> None:
        self.plan_id = plan_id
        super().__init__(f"Meal plan {plan_id} not found")


class PlannerService:
    """Service for meal plan business logic. 📅

    Coordinates plan generation, selection, and management.
    """

    def __init__(
        self,
        repository: PlannerRepository,
        scorer: RecipeScorer | None = None,
        generator: PlanGenerator | None = None,
    ) -> None:
        """Initialize service.

        Args:
            repository: The planner repository instance.
            scorer: Optional recipe scorer.
            generator: Optional plan generator.
        """
        self.repository = repository
        self.scorer = scorer or RecipeScorer()
        self.generator = generator or PlanGenerator(self.scorer)

    # =========================================================================
    # Plan Generation (Phase 5A)
    # =========================================================================

    async def generate_options(
        self,
        _household_id: UUID,
        request: CreatePlanRequest,
        recipes: list[Recipe],
        pantry_items: list[PantryItem],
    ) -> PlanOptionsResponse:
        """Generate plan options for the user.

        The "Choose Your Own Adventure" flow.

        Args:
            _household_id: The household (reserved for future filtering).
            request: Plan configuration.
            recipes: Available recipes.
            pantry_items: Current inventory.

        Returns:
            PlanOptionsResponse with options to choose from.
        """
        return self.generator.generate_options(request, recipes, pantry_items)

    async def score_recipes(
        self,
        recipes: list[Recipe],
        pantry_items: list[PantryItem],
        *,
        criteria: ScoringCriteria | None = None,
    ) -> list[RecipeScore]:
        """Score recipes against current inventory.

        Useful for "Can I Cook This?" feature.

        Args:
            recipes: Recipes to score.
            pantry_items: Current inventory.
            criteria: Optional scoring configuration.

        Returns:
            List of RecipeScore sorted by total score.
        """
        if criteria:
            self.scorer.criteria = criteria
        return self.scorer.score_recipes(recipes, pantry_items)

    # =========================================================================
    # Plan Management (Phase 5B)
    # =========================================================================

    async def get_plan(
        self,
        plan_id: UUID,
        household_id: UUID,
    ) -> MealPlan:
        """Get a meal plan by ID.

        Args:
            plan_id: The plan's ID.
            household_id: The household.

        Returns:
            The MealPlan with slots.

        Raises:
            PlanNotFoundError: If plan doesn't exist.
        """
        plan = await self.repository.get_by_id(plan_id, household_id)
        if not plan:
            raise PlanNotFoundError(plan_id)
        return plan

    async def get_active_plan(
        self,
        household_id: UUID,
    ) -> MealPlan | None:
        """Get the current active plan for a household.

        Args:
            household_id: The household.

        Returns:
            Active MealPlan or None.
        """
        return await self.repository.get_active_plan(household_id)

    async def list_plans(
        self,
        household_id: UUID,
        *,
        include_archived: bool = False,
    ) -> list[PlanSummary]:
        """List all meal plans for a household.

        Args:
            household_id: The household.
            include_archived: Whether to include old plans.

        Returns:
            List of plan summaries.
        """
        return await self.repository.get_all_plans(
            household_id,
            include_archived=include_archived,
        )

    async def create_plan(
        self,
        household_id: UUID,
        request: CreatePlanRequest,
        selected_option: SelectOptionRequest,
    ) -> MealPlan:
        """Create a meal plan from a selected option.

        Args:
            household_id: The household.
            request: Original plan request.
            selected_option: User's selection.

        Returns:
            The created MealPlan.
        """
        # Create the plan
        plan = await self.repository.create_plan(
            household_id,
            f"Meal Plan: {request.start_date.strftime('%b %d')} - {request.end_date.strftime('%b %d')}",
            request.start_date,
            request.end_date,
            selected_option.option_id,
            request.constraints,
        )

        return plan

    async def activate_plan(
        self,
        plan_id: UUID,
        household_id: UUID,
    ) -> MealPlan:
        """Set a plan as the active plan.

        Only one plan can be active at a time.

        Args:
            plan_id: The plan to activate.
            household_id: The household.

        Returns:
            The activated plan.

        Raises:
            PlanNotFoundError: If plan doesn't exist.
        """
        # Deactivate current active plan
        current = await self.repository.get_active_plan(household_id)
        if current and current.id != plan_id:
            await self.repository.update_status(
                current.id,
                household_id,
                PlanStatus.COMPLETED,
            )

        # Activate the new plan
        result = await self.repository.update_status(
            plan_id,
            household_id,
            PlanStatus.ACTIVE,
        )
        if not result:
            raise PlanNotFoundError(plan_id)
        return result

    async def complete_plan(
        self,
        plan_id: UUID,
        household_id: UUID,
    ) -> MealPlan:
        """Mark a plan as completed.

        Args:
            plan_id: The plan to complete.
            household_id: The household.

        Returns:
            The updated plan.

        Raises:
            PlanNotFoundError: If plan doesn't exist.
        """
        result = await self.repository.update_status(
            plan_id,
            household_id,
            PlanStatus.COMPLETED,
        )
        if not result:
            raise PlanNotFoundError(plan_id)
        return result

    async def delete_plan(
        self,
        plan_id: UUID,
        household_id: UUID,
    ) -> None:
        """Delete a meal plan.

        Args:
            plan_id: The plan to delete.
            household_id: The household.

        Raises:
            PlanNotFoundError: If plan doesn't exist.
        """
        deleted = await self.repository.delete_plan(plan_id, household_id)
        if not deleted:
            raise PlanNotFoundError(plan_id)

    # =========================================================================
    # Meal Slots (Phase 6 prep)
    # =========================================================================

    async def update_slot(
        self,
        slot_id: UUID,
        plan_id: UUID,
        household_id: UUID,
        *,
        recipe_id: UUID | None = None,
        is_locked: bool | None = None,
        notes: str | None = None,
    ) -> MealSlot:
        """Update a meal slot.

        Args:
            slot_id: The slot to update.
            plan_id: The plan it belongs to.
            household_id: The household.
            recipe_id: New recipe assignment.
            is_locked: Lock/unlock the slot.
            notes: Update notes.

        Returns:
            Updated MealSlot.
        """
        slot = await self.repository.update_slot(
            slot_id,
            plan_id,
            household_id,
            recipe_id=recipe_id,
            is_locked=is_locked,
            notes=notes,
        )
        if not slot:
            raise PlanNotFoundError(plan_id)
        return slot

    async def lock_slot(
        self,
        slot_id: UUID,
        plan_id: UUID,
        household_id: UUID,
    ) -> MealSlot:
        """Lock a meal slot (Phase 6 feature).

        Locked slots won't be changed by "re-spin".

        Args:
            slot_id: The slot to lock.
            plan_id: The plan.
            household_id: The household.

        Returns:
            Updated MealSlot.
        """
        slot = await self.repository.update_slot(
            slot_id,
            plan_id,
            household_id,
            is_locked=True,
        )
        if not slot:
            raise PlanNotFoundError(plan_id)
        return slot

    async def unlock_slot(
        self,
        slot_id: UUID,
        plan_id: UUID,
        household_id: UUID,
    ) -> MealSlot:
        """Unlock a meal slot.

        Args:
            slot_id: The slot to unlock.
            plan_id: The plan.
            household_id: The household.

        Returns:
            Updated MealSlot.
        """
        slot = await self.repository.update_slot(
            slot_id,
            plan_id,
            household_id,
            is_locked=False,
        )
        if not slot:
            raise PlanNotFoundError(plan_id)
        return slot
