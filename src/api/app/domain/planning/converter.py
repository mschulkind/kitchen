"""Unit Converter - Cross-unit conversions with density support. ⚖️

Handles conversions between weight and volume using ingredient densities.

Fun fact: 1 cup of flour weighs about 120g, but 1 cup of sugar weighs 200g! 🧁
"""

from dataclasses import dataclass

from src.api.app.domain.recipes.unit_registry import UnitRegistry


@dataclass
class ConversionResult:
    """Result of a unit conversion attempt."""

    success: bool
    value: float | None = None
    target_unit: str | None = None
    method: str | None = None  # "direct", "density", "failed"
    error: str | None = None


class UnitConverter:
    """Converts between cooking units, including volume <-> weight. 🔄

    Uses a density database for common ingredients to convert
    between incompatible unit types (e.g., cups to grams).

    Example:
        >>> converter = UnitConverter()
        >>> converter.convert(1, "cup", "gram", ingredient="flour")
        ConversionResult(success=True, value=120.0, target_unit="gram", method="density")
    """

    # Ingredient densities: grams per cup
    # Sources: USDA, King Arthur Flour
    DENSITY_DB: dict[str, float] = {
        # Flours
        "flour": 120.0,
        "all-purpose flour": 120.0,
        "bread flour": 127.0,
        "whole wheat flour": 113.0,
        "cake flour": 114.0,
        "almond flour": 96.0,
        # Sugars
        "sugar": 200.0,
        "granulated sugar": 200.0,
        "brown sugar": 220.0,
        "powdered sugar": 120.0,
        "confectioners sugar": 120.0,
        # Dairy
        "milk": 245.0,
        "cream": 240.0,
        "heavy cream": 240.0,
        "sour cream": 230.0,
        "yogurt": 245.0,
        "butter": 227.0,  # 2 sticks
        # Oils
        "oil": 218.0,
        "olive oil": 216.0,
        "vegetable oil": 218.0,
        "coconut oil": 218.0,
        # Liquids
        "water": 237.0,
        "honey": 340.0,
        "maple syrup": 312.0,
        "molasses": 328.0,
        # Grains
        "rice": 185.0,
        "oats": 80.0,
        "rolled oats": 80.0,
        # Nuts
        "almonds": 143.0,
        "walnuts": 120.0,
        "pecans": 109.0,
        "peanuts": 146.0,
        # Other
        "cocoa powder": 86.0,
        "cornstarch": 128.0,
        "salt": 288.0,
        "baking powder": 230.0,
        "baking soda": 220.0,
    }

    # Aliases for ingredient names
    INGREDIENT_ALIASES: dict[str, str] = {
        "ap flour": "all-purpose flour",
        "white flour": "all-purpose flour",
        "plain flour": "all-purpose flour",
        "white sugar": "granulated sugar",
        "caster sugar": "granulated sugar",
        "icing sugar": "powdered sugar",
        "unsalted butter": "butter",
        "salted butter": "butter",
        "evoo": "olive oil",
        "extra virgin olive oil": "olive oil",
        "veg oil": "vegetable oil",
        "canola oil": "vegetable oil",
        "whole milk": "milk",
        "2% milk": "milk",
        "skim milk": "milk",
        "quick oats": "rolled oats",
        "old fashioned oats": "rolled oats",
        "kosher salt": "salt",
        "sea salt": "salt",
        "table salt": "salt",
    }

    def __init__(self, unit_registry: UnitRegistry | None = None) -> None:
        """Initialize the converter.

        Args:
            unit_registry: Optional unit registry (creates one if not provided).
        """
        self.unit_registry = unit_registry or UnitRegistry()

    def convert(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
        *,
        ingredient: str | None = None,
    ) -> ConversionResult:
        """Convert a quantity between units.

        Args:
            value: The quantity to convert.
            from_unit: Source unit.
            to_unit: Target unit.
            ingredient: Optional ingredient name for density lookup.

        Returns:
            ConversionResult with converted value or error.
        """
        from_unit = self.unit_registry.normalize_unit(from_unit)
        to_unit = self.unit_registry.normalize_unit(to_unit)

        # Same unit, no conversion needed
        if from_unit == to_unit:
            return ConversionResult(
                success=True,
                value=value,
                target_unit=to_unit,
                method="direct",
            )

        # Try direct conversion first (same dimension)
        if self.unit_registry.are_compatible(from_unit, to_unit):
            converted = self.unit_registry.convert(value, from_unit, to_unit)
            if converted is not None:
                return ConversionResult(
                    success=True,
                    value=converted,
                    target_unit=to_unit,
                    method="direct",
                )

        # Try density-based conversion (volume <-> weight)
        if ingredient:
            density_result = self._convert_via_density(
                value, from_unit, to_unit, ingredient
            )
            if density_result.success:
                return density_result

        # Conversion failed
        return ConversionResult(
            success=False,
            method="failed",
            error=f"Cannot convert {from_unit} to {to_unit}"
            + (f" for '{ingredient}'" if ingredient else ""),
        )

    def _convert_via_density(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
        ingredient: str,
    ) -> ConversionResult:
        """Convert between volume and weight using density.

        Args:
            value: The quantity to convert.
            from_unit: Source unit.
            to_unit: Target unit.
            ingredient: Ingredient name for density lookup.

        Returns:
            ConversionResult with converted value or error.
        """
        # Normalize ingredient name
        ingredient_lower = ingredient.lower().strip()
        if ingredient_lower in self.INGREDIENT_ALIASES:
            ingredient_lower = self.INGREDIENT_ALIASES[ingredient_lower]

        # Look up density (grams per cup)
        density = self._get_density(ingredient_lower)
        if density is None:
            return ConversionResult(
                success=False,
                method="failed",
                error=f"No density data for '{ingredient}'",
            )

        # Determine conversion direction
        from_is_volume = self._is_volume_unit(from_unit)
        to_is_volume = self._is_volume_unit(to_unit)

        if from_is_volume == to_is_volume:
            # Both same type, shouldn't need density
            return ConversionResult(
                success=False,
                method="failed",
                error="Density conversion not applicable",
            )

        try:
            if from_is_volume:
                # Volume -> Weight
                # First convert to cups, then multiply by density for grams
                cups = self.unit_registry.convert(value, from_unit, "cup")
                if cups is None:
                    return ConversionResult(
                        success=False,
                        method="failed",
                        error=f"Cannot convert {from_unit} to cups",
                    )
                grams = cups * density

                # Convert grams to target unit
                result = self.unit_registry.convert(grams, "gram", to_unit)
                if result is None:
                    return ConversionResult(
                        success=False,
                        method="failed",
                        error=f"Cannot convert grams to {to_unit}",
                    )
                return ConversionResult(
                    success=True,
                    value=result,
                    target_unit=to_unit,
                    method="density",
                )
            else:
                # Weight -> Volume
                # First convert to grams, then divide by density for cups
                grams = self.unit_registry.convert(value, from_unit, "gram")
                if grams is None:
                    return ConversionResult(
                        success=False,
                        method="failed",
                        error=f"Cannot convert {from_unit} to grams",
                    )
                cups = grams / density

                # Convert cups to target unit
                result = self.unit_registry.convert(cups, "cup", to_unit)
                if result is None:
                    return ConversionResult(
                        success=False,
                        method="failed",
                        error=f"Cannot convert cups to {to_unit}",
                    )
                return ConversionResult(
                    success=True,
                    value=result,
                    target_unit=to_unit,
                    method="density",
                )
        except Exception as e:
            return ConversionResult(
                success=False,
                method="failed",
                error=str(e),
            )

    def _get_density(self, ingredient: str) -> float | None:
        """Get density for an ingredient (grams per cup).

        Tries exact match first, then partial match.
        """
        # Exact match
        if ingredient in self.DENSITY_DB:
            return self.DENSITY_DB[ingredient]

        # Partial match (ingredient contains a known key)
        for known, density in self.DENSITY_DB.items():
            if known in ingredient or ingredient in known:
                return density

        return None

    def _is_volume_unit(self, unit: str) -> bool:
        """Check if a unit is a volume unit."""
        volume_units = {
            "cup", "tablespoon", "teaspoon", "liter", "milliliter",
            "fluid_ounce", "pint", "quart", "gallon",
        }
        return unit in volume_units

    def _is_weight_unit(self, unit: str) -> bool:
        """Check if a unit is a weight unit."""
        weight_units = {"gram", "kilogram", "ounce", "pound"}
        return unit in weight_units

    def get_known_ingredients(self) -> list[str]:
        """Get list of ingredients with known densities."""
        return sorted(set(self.DENSITY_DB.keys()) | set(self.INGREDIENT_ALIASES.keys()))
