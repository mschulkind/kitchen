"""Planner repository - Database access layer. 🗄️

Handles all database operations for meal plans and slots.

Fun fact: Database meal plans were one of the first "smart home" features! 📱
"""

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from src.api.app.domain.planner.models import (
    MealPlan,
    MealSlot,
    MealType,
    PlanStatus,
    PlanSummary,
)

if TYPE_CHECKING:
    from supabase import AsyncClient


class PlannerRepository:
    """Repository for meal plan CRUD operations. 📅"""

    PLANS_TABLE = "meal_plans"
    SLOTS_TABLE = "meal_slots"

    def __init__(self, supabase: "AsyncClient") -> None:
        """Initialize repository with Supabase client."""
        self.supabase = supabase

    # =========================================================================
    # Meal Plans
    # =========================================================================

    async def get_by_id(
        self,
        plan_id: UUID,
        household_id: UUID,
        *,
        include_slots: bool = True,
    ) -> MealPlan | None:
        """Get a meal plan by ID.

        Args:
            plan_id: The plan's unique identifier.
            household_id: The household (for RLS).
            include_slots: Whether to fetch slots.

        Returns:
            MealPlan if found, None otherwise.
        """
        result = await (
            self.supabase.table(self.PLANS_TABLE)
            .select("*")
            .eq("id", str(plan_id))
            .eq("household_id", str(household_id))
            .maybe_single()
            .execute()
        )

        if not result.data:
            return None

        plan = MealPlan.model_validate(result.data)

        if include_slots:
            plan.slots = await self._get_slots(plan_id)

        return plan

    async def get_active_plan(
        self,
        household_id: UUID,
    ) -> MealPlan | None:
        """Get the current active plan for a household."""
        result = await (
            self.supabase.table(self.PLANS_TABLE)
            .select("*")
            .eq("household_id", str(household_id))
            .eq("status", PlanStatus.ACTIVE.value)
            .order("created_at", desc=True)
            .limit(1)
            .maybe_single()
            .execute()
        )

        if not result.data:
            return None

        plan = MealPlan.model_validate(result.data)
        plan.slots = await self._get_slots(plan.id)
        return plan

    async def get_all_plans(
        self,
        household_id: UUID,
        *,
        include_archived: bool = False,
    ) -> list[PlanSummary]:
        """Get all meal plans for a household.

        Args:
            household_id: The household.
            include_archived: Include completed/archived plans.

        Returns:
            List of plan summaries.
        """
        query = (
            self.supabase.table(self.PLANS_TABLE)
            .select("*")
            .eq("household_id", str(household_id))
            .order("created_at", desc=True)
        )

        if not include_archived:
            query = query.in_("status", [PlanStatus.DRAFT.value, PlanStatus.ACTIVE.value])

        result = await query.execute()

        summaries = []
        for row in result.data or []:
            # Get slot counts
            slots_result = await (
                self.supabase.table(self.SLOTS_TABLE)
                .select("id, recipe_id")
                .eq("plan_id", row["id"])
                .execute()
            )
            slots = slots_result.data or []
            total = len(slots)
            completed = sum(1 for s in slots if s.get("recipe_id"))

            summaries.append(
                PlanSummary(
                    id=row["id"],
                    name=row["name"],
                    start_date=row["start_date"],
                    end_date=row["end_date"],
                    status=row["status"],
                    total_meals=total,
                    completed_meals=completed,
                    created_at=row["created_at"],
                )
            )

        return summaries

    async def create_plan(
        self,
        household_id: UUID,
        name: str,
        start_date: date,
        end_date: date,
        selected_option_id: str | None = None,
        constraints: list[str] | None = None,
    ) -> MealPlan:
        """Create a new meal plan.

        Args:
            household_id: The household.
            name: Plan name.
            start_date: Start of the plan period.
            end_date: End of the plan period.
            selected_option_id: The chosen option ID.
            constraints: User's constraints.

        Returns:
            The created MealPlan.
        """
        now = datetime.now(UTC)
        plan_id = uuid4()

        data = {
            "id": str(plan_id),
            "household_id": str(household_id),
            "name": name,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "status": PlanStatus.DRAFT.value,
            "selected_option_id": selected_option_id,
            "constraints": constraints or [],
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        result = await self.supabase.table(self.PLANS_TABLE).insert(data).execute()

        plan = MealPlan.model_validate(result.data[0])
        plan.slots = []
        return plan

    async def update_status(
        self,
        plan_id: UUID,
        household_id: UUID,
        status: PlanStatus,
    ) -> MealPlan | None:
        """Update a plan's status.

        Args:
            plan_id: The plan to update.
            household_id: The household.
            status: New status.

        Returns:
            Updated plan or None if not found.
        """
        data = {
            "status": status.value,
            "updated_at": datetime.now(UTC).isoformat(),
        }

        result = await (
            self.supabase.table(self.PLANS_TABLE)
            .update(data)
            .eq("id", str(plan_id))
            .eq("household_id", str(household_id))
            .execute()
        )

        if result.data:
            plan = MealPlan.model_validate(result.data[0])
            plan.slots = await self._get_slots(plan_id)
            return plan
        return None

    async def delete_plan(
        self,
        plan_id: UUID,
        household_id: UUID,
    ) -> bool:
        """Delete a meal plan and all its slots.

        Args:
            plan_id: The plan to delete.
            household_id: The household.

        Returns:
            True if deleted, False if not found.
        """
        # Delete slots first
        await self.supabase.table(self.SLOTS_TABLE).delete().eq("plan_id", str(plan_id)).execute()

        result = await (
            self.supabase.table(self.PLANS_TABLE)
            .delete()
            .eq("id", str(plan_id))
            .eq("household_id", str(household_id))
            .execute()
        )

        return len(result.data or []) > 0

    # =========================================================================
    # Meal Slots
    # =========================================================================

    async def _get_slots(self, plan_id: UUID) -> list[MealSlot]:
        """Get all slots for a plan."""
        result = await (
            self.supabase.table(self.SLOTS_TABLE)
            .select("*")
            .eq("plan_id", str(plan_id))
            .order("date")
            .order("meal_type")
            .execute()
        )

        return [MealSlot.model_validate(row) for row in result.data or []]

    async def create_slots(
        self,
        plan_id: UUID,
        start_date: date,
        end_date: date,
        meal_types: list[MealType],
    ) -> list[MealSlot]:
        """Create meal slots for a plan.

        Creates one slot per day per meal type.

        Args:
            plan_id: The plan.
            start_date: Start of the plan period.
            end_date: End of the plan period.
            meal_types: Which meals to create slots for.

        Returns:
            List of created slots.
        """
        from datetime import timedelta

        slots_data = []
        current = start_date

        while current <= end_date:
            for meal_type in meal_types:
                slots_data.append(
                    {
                        "id": str(uuid4()),
                        "plan_id": str(plan_id),
                        "date": current.isoformat(),
                        "meal_type": meal_type.value,
                        "is_locked": False,
                        "servings": 2,
                    }
                )
            current += timedelta(days=1)

        if not slots_data:
            return []

        result = await self.supabase.table(self.SLOTS_TABLE).insert(slots_data).execute()

        return [MealSlot.model_validate(row) for row in result.data]

    async def update_slot(
        self,
        slot_id: UUID,
        plan_id: UUID,
        household_id: UUID,
        *,
        recipe_id: UUID | None = None,
        recipe_title: str | None = None,
        is_locked: bool | None = None,
        notes: str | None = None,
    ) -> MealSlot | None:
        """Update a meal slot.

        Args:
            slot_id: The slot to update.
            plan_id: The plan it belongs to.
            household_id: The household (for verification).
            recipe_id: New recipe assignment.
            recipe_title: Recipe title (denormalized).
            is_locked: Lock/unlock the slot.
            notes: Slot notes.

        Returns:
            Updated slot or None if not found.
        """
        # Verify plan belongs to household
        plan_check = await (
            self.supabase.table(self.PLANS_TABLE)
            .select("id")
            .eq("id", str(plan_id))
            .eq("household_id", str(household_id))
            .maybe_single()
            .execute()
        )

        if not plan_check.data:
            return None

        data: dict = {}
        if recipe_id is not None:
            data["recipe_id"] = str(recipe_id) if recipe_id else None
        if recipe_title is not None:
            data["recipe_title"] = recipe_title
        if is_locked is not None:
            data["is_locked"] = is_locked
        if notes is not None:
            data["notes"] = notes

        if not data:
            # Nothing to update, just return current
            result = await (
                self.supabase.table(self.SLOTS_TABLE)
                .select("*")
                .eq("id", str(slot_id))
                .eq("plan_id", str(plan_id))
                .maybe_single()
                .execute()
            )
            return MealSlot.model_validate(result.data) if result.data else None

        result = await (
            self.supabase.table(self.SLOTS_TABLE)
            .update(data)
            .eq("id", str(slot_id))
            .eq("plan_id", str(plan_id))
            .execute()
        )

        if result.data:
            return MealSlot.model_validate(result.data[0])
        return None

    async def clear_unlocked_slots(
        self,
        plan_id: UUID,
    ) -> int:
        """Clear recipe assignments from unlocked slots.

        Used when "re-spinning" a plan.

        Args:
            plan_id: The plan.

        Returns:
            Number of slots cleared.
        """
        result = await (
            self.supabase.table(self.SLOTS_TABLE)
            .update({"recipe_id": None, "recipe_title": None})
            .eq("plan_id", str(plan_id))
            .eq("is_locked", False)
            .execute()
        )

        return len(result.data or [])
