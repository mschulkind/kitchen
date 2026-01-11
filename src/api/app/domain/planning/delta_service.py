"""Delta Service - The Brain of the Kitchen. 🧠

Compares recipe requirements against inventory to calculate
exactly what's missing and what's assumed.

Fun fact: The concept of "mise en place" (everything in its place)
originated in French professional kitchens in the 19th century! 👨‍🍳
"""

from difflib import SequenceMatcher

from src.api.app.domain.pantry.models import PantryItem
from src.api.app.domain.planning.converter import UnitConverter
from src.api.app.domain.planning.models import (
    ComparisonResult,
    DeltaItem,
    DeltaStatus,
)
from src.api.app.domain.recipes.models import ParsedIngredient, RecipeIngredient


class DeltaService:
    """Service for comparing recipes to inventory. 🔍

    The core "delta" engine that calculates what's missing,
    what's available, and what can be assumed.

    Example:
        >>> service = DeltaService()
        >>> result = service.calculate_missing(recipe_ingredients, pantry_items)
        >>> print(f"Need to buy: {len(result.shopping_list_items)} items")
    """

    # Items commonly assumed to be in any kitchen (staples)
    ASSUMED_STAPLES = frozenset({
        "salt", "pepper", "black pepper", "water", "ice",
        "cooking spray", "oil", "vegetable oil",
    })

    # Minimum similarity score for fuzzy matching (0.0 - 1.0)
    FUZZY_MATCH_THRESHOLD = 0.7

    def __init__(self, converter: UnitConverter | None = None) -> None:
        """Initialize the delta service.

        Args:
            converter: Optional unit converter (creates one if not provided).
        """
        self.converter = converter or UnitConverter()

    def calculate_missing(
        self,
        recipe_ingredients: list[RecipeIngredient | ParsedIngredient],
        pantry_items: list[PantryItem],
        *,
        include_staples_in_assumptions: bool = True,
    ) -> ComparisonResult:
        """Calculate what's missing to make a recipe.

        Args:
            recipe_ingredients: Parsed ingredients from a recipe.
            pantry_items: Current inventory items.
            include_staples_in_assumptions: Whether to assume common staples.

        Returns:
            ComparisonResult with categorized items.
        """
        result = ComparisonResult(total_ingredients=len(recipe_ingredients))

        # Build pantry lookup by normalized name
        pantry_lookup = self._build_pantry_lookup(pantry_items)

        for ingredient in recipe_ingredients:
            delta = self._compare_single_ingredient(
                ingredient,
                pantry_lookup,
                include_staples_in_assumptions,
            )

            # Categorize by status
            match delta.status:
                case DeltaStatus.HAS_ENOUGH:
                    result.have_enough.append(delta)
                case DeltaStatus.PARTIAL:
                    result.partial.append(delta)
                case DeltaStatus.MISSING:
                    result.missing.append(delta)
                case DeltaStatus.ASSUMED:
                    result.assumptions.append(delta)
                case DeltaStatus.UNIT_MISMATCH:
                    result.unresolved.append(delta)

        return result

    def _compare_single_ingredient(
        self,
        ingredient: RecipeIngredient | ParsedIngredient,
        pantry_lookup: dict[str, list[PantryItem]],
        include_staples: bool,
    ) -> DeltaItem:
        """Compare a single ingredient against pantry.

        Args:
            ingredient: The recipe ingredient to check.
            pantry_lookup: Pantry items indexed by normalized name.
            include_staples: Whether to assume common staples.

        Returns:
            DeltaItem with comparison result.
        """
        item_name = ingredient.item_name.lower().strip()
        recipe_qty = ingredient.quantity
        recipe_unit = ingredient.unit

        # Check if this is an assumed staple
        if include_staples and self._is_staple(item_name):
            return DeltaItem(
                item_name=ingredient.item_name,
                recipe_quantity=recipe_qty,
                recipe_unit=recipe_unit,
                status=DeltaStatus.ASSUMED,
                notes="Common kitchen staple",
            )

        # Try to find matching pantry item
        match = self._find_pantry_match(item_name, pantry_lookup)

        if match is None:
            # Not in pantry at all
            return DeltaItem(
                item_name=ingredient.item_name,
                recipe_quantity=recipe_qty,
                recipe_unit=recipe_unit,
                delta_quantity=recipe_qty,
                delta_unit=recipe_unit,
                status=DeltaStatus.MISSING,
            )

        pantry_item, match_confidence = match

        # Have the item - now compare quantities
        return self._calculate_delta(
            ingredient,
            pantry_item,
            match_confidence,
        )

    def _calculate_delta(
        self,
        ingredient: RecipeIngredient | ParsedIngredient,
        pantry_item: PantryItem,
        match_confidence: float,
    ) -> DeltaItem:
        """Calculate the quantity delta between recipe and pantry.

        Args:
            ingredient: Recipe ingredient requirement.
            pantry_item: Matched pantry item.
            match_confidence: Confidence of the name match.

        Returns:
            DeltaItem with calculated delta.
        """
        recipe_qty = ingredient.quantity
        recipe_unit = ingredient.unit
        pantry_qty = pantry_item.quantity
        pantry_unit = pantry_item.unit

        # If no quantities, we can't calculate - assume we have enough
        if recipe_qty is None:
            return DeltaItem(
                item_name=ingredient.item_name,
                recipe_quantity=None,
                recipe_unit=recipe_unit,
                inventory_quantity=pantry_qty,
                inventory_unit=pantry_unit,
                status=DeltaStatus.HAS_ENOUGH,
                confidence=match_confidence,
                matched_pantry_item_id=pantry_item.id,
                notes="No quantity specified in recipe",
            )

        if pantry_qty is None:
            # Have it but don't know how much
            return DeltaItem(
                item_name=ingredient.item_name,
                recipe_quantity=recipe_qty,
                recipe_unit=recipe_unit,
                inventory_quantity=None,
                inventory_unit=pantry_unit,
                status=DeltaStatus.HAS_ENOUGH,
                confidence=match_confidence * 0.8,  # Lower confidence
                matched_pantry_item_id=pantry_item.id,
                notes="Pantry quantity unknown - please verify",
            )

        # Both have quantities - try to compare
        # Normalize units
        recipe_unit_norm = self.converter.unit_registry.normalize_unit(
            recipe_unit or "count"
        )
        pantry_unit_norm = self.converter.unit_registry.normalize_unit(
            pantry_unit or "count"
        )

        # Same unit - simple subtraction
        if recipe_unit_norm == pantry_unit_norm:
            delta = recipe_qty - pantry_qty
            return self._make_delta_item(
                ingredient,
                pantry_item,
                delta,
                recipe_unit_norm,
                match_confidence,
            )

        # Try to convert pantry to recipe units
        conversion = self.converter.convert(
            pantry_qty,
            pantry_unit_norm,
            recipe_unit_norm,
            ingredient=ingredient.item_name,
        )

        if conversion.success and conversion.value is not None:
            delta = recipe_qty - conversion.value
            return self._make_delta_item(
                ingredient,
                pantry_item,
                delta,
                recipe_unit_norm,
                match_confidence,
            )

        # Unit mismatch - can't compare
        return DeltaItem(
            item_name=ingredient.item_name,
            recipe_quantity=recipe_qty,
            recipe_unit=recipe_unit,
            inventory_quantity=pantry_qty,
            inventory_unit=pantry_unit,
            status=DeltaStatus.UNIT_MISMATCH,
            confidence=match_confidence,
            matched_pantry_item_id=pantry_item.id,
            notes=f"Cannot convert {pantry_unit} to {recipe_unit}",
        )

    def _make_delta_item(
        self,
        ingredient: RecipeIngredient | ParsedIngredient,
        pantry_item: PantryItem,
        delta: float,
        unit: str,
        confidence: float,
    ) -> DeltaItem:
        """Create a DeltaItem from calculated values."""
        if delta <= 0:
            # Have enough
            status = DeltaStatus.HAS_ENOUGH
            delta_qty = None
        else:
            # Need to buy some
            status = DeltaStatus.PARTIAL if pantry_item.quantity else DeltaStatus.MISSING
            delta_qty = delta

        return DeltaItem(
            item_name=ingredient.item_name,
            recipe_quantity=ingredient.quantity,
            recipe_unit=ingredient.unit,
            inventory_quantity=pantry_item.quantity,
            inventory_unit=pantry_item.unit,
            delta_quantity=delta_qty,
            delta_unit=unit if delta_qty else None,
            status=status,
            confidence=confidence,
            matched_pantry_item_id=pantry_item.id,
        )

    def _build_pantry_lookup(
        self,
        pantry_items: list[PantryItem],
    ) -> dict[str, list[PantryItem]]:
        """Build a lookup dictionary from pantry items.

        Groups items by normalized name for efficient lookup.
        """
        lookup: dict[str, list[PantryItem]] = {}
        for item in pantry_items:
            key = item.name.lower().strip()
            if key not in lookup:
                lookup[key] = []
            lookup[key].append(item)
        return lookup

    def _find_pantry_match(
        self,
        ingredient_name: str,
        pantry_lookup: dict[str, list[PantryItem]],
    ) -> tuple[PantryItem, float] | None:
        """Find best matching pantry item for an ingredient.

        Uses exact match first, then fuzzy matching.
        Aggregates multiple pantry items with the same name into one.

        Args:
            ingredient_name: Normalized ingredient name.
            pantry_lookup: Pantry items indexed by name.

        Returns:
            Tuple of (PantryItem, confidence) or None if no match.
        """
        # Exact match
        if ingredient_name in pantry_lookup:
            items = pantry_lookup[ingredient_name]
            aggregated = self._aggregate_pantry_items(items)
            return (aggregated, 1.0)

        # Fuzzy match
        best_match: tuple[PantryItem, float] | None = None
        best_score = 0.0

        for pantry_name, items in pantry_lookup.items():
            score = self._similarity_score(ingredient_name, pantry_name)
            if score >= self.FUZZY_MATCH_THRESHOLD and score > best_score:
                best_score = score
                aggregated = self._aggregate_pantry_items(items)
                best_match = (aggregated, score)

        return best_match

    def _aggregate_pantry_items(self, items: list[PantryItem]) -> PantryItem:
        """Aggregate multiple pantry items with same name into one.

        Combines quantities when units are compatible.
        Uses the first item as the base and aggregates quantities.

        Args:
            items: List of pantry items with the same name.

        Returns:
            A single PantryItem with aggregated quantity.
        """
        if len(items) == 1:
            return items[0]

        # Use first item as base
        base = items[0]
        base_unit = self.converter.unit_registry.normalize_unit(base.unit or "count")
        total_quantity = base.quantity or 0

        # Try to add quantities from other items
        for item in items[1:]:
            if item.quantity is None:
                continue

            item_unit = self.converter.unit_registry.normalize_unit(
                item.unit or "count"
            )

            if item_unit == base_unit:
                # Same unit - simple addition
                total_quantity += item.quantity
            else:
                # Try to convert
                conversion = self.converter.convert(
                    item.quantity,
                    item_unit,
                    base_unit,
                    ingredient=base.name,
                )
                if conversion.success and conversion.value is not None:
                    total_quantity += conversion.value
                # If conversion fails, skip this item (can't aggregate)

        # Return a new PantryItem with aggregated quantity
        return PantryItem(
            id=base.id,
            household_id=base.household_id,
            name=base.name,
            quantity=total_quantity,
            unit=base.unit,
            location=base.location,
            expiry_date=base.expiry_date,
            notes=base.notes,
            is_staple=base.is_staple,
            created_at=base.created_at,
            updated_at=base.updated_at,
        )

    def _similarity_score(self, a: str, b: str) -> float:
        """Calculate similarity between two strings.

        Uses SequenceMatcher for basic fuzzy matching.
        Could be upgraded to use trigrams or Levenshtein.
        """
        return SequenceMatcher(None, a, b).ratio()

    def _is_staple(self, item_name: str) -> bool:
        """Check if an item is a common kitchen staple."""
        # Check exact match or if any staple is contained in the name
        return item_name in self.ASSUMED_STAPLES or any(
            staple in item_name for staple in self.ASSUMED_STAPLES
        )

    def get_staples_list(self) -> list[str]:
        """Get list of items assumed to be staples."""
        return sorted(self.ASSUMED_STAPLES)
