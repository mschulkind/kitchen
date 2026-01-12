"""Unit Registry - Quantity normalization using Pint. 📏

Wraps the Pint library for unit management and conversion.
Handles cooking-specific units and normalizations.

Fun fact: A "pinch" is approximately 1/16 of a teaspoon! 🤏
"""

import re
from typing import NamedTuple

import pint
from pint import UnitRegistry as PintRegistry


class NormalizedQuantity(NamedTuple):
    """A normalized quantity with unit."""

    value: float
    unit: str
    original_unit: str


class UnitRegistry:
    """Kitchen-aware unit registry for ingredient parsing. 🥄

    Handles:
    - Standard cooking units (cups, tablespoons, teaspoons)
    - Metric units (grams, liters, milliliters)
    - Imperial units (ounces, pounds)
    - Count-based items (each, dozen)
    - Vague quantities (pinch, dash, splash)

    Example:
        >>> registry = UnitRegistry()
        >>> registry.normalize("1/2 cup")
        NormalizedQuantity(value=0.5, unit="cup", original_unit="cup")
        >>> registry.convert(500, "g", "kg")
        0.5
    """

    # Vague units that can't be precisely measured
    VAGUE_UNITS = frozenset(
        {
            "pinch",
            "dash",
            "splash",
            "handful",
            "some",
            "to taste",
            "as needed",
            "n/a",
            "optional",
        }
    )

    # Unit aliases for normalization
    UNIT_ALIASES = {
        # Volume
        "tbsp": "tablespoon",
        "tbs": "tablespoon",
        "T": "tablespoon",
        "tsp": "teaspoon",
        "t": "teaspoon",
        "c": "cup",
        "C": "cup",
        "fl oz": "fluid_ounce",
        "fl. oz": "fluid_ounce",
        "floz": "fluid_ounce",
        # Mass
        "g": "gram",
        "grams": "gram",
        "kg": "kilogram",
        "oz": "ounce",
        "lb": "pound",
        "lbs": "pound",
        # Count
        "pc": "count",
        "pcs": "count",
        "piece": "count",
        "pieces": "count",
        "each": "count",
        "whole": "count",
        "large": "count",
        "medium": "count",
        "small": "count",
        "clove": "count",
        "cloves": "count",
        # Dozen
        "doz": "dozen",
    }

    # Implicit count patterns (no unit = count)
    COUNTABLE_PATTERN = re.compile(
        r"^\d+\s*(large|medium|small|whole)?\s*"
        r"(eggs?|onions?|cloves?|potatoes?|tomatoes?|carrots?|apples?|bananas?|lemons?|limes?|oranges?|avocados?|peppers?|garlic|shallots?)",
        re.IGNORECASE,
    )

    def __init__(self) -> None:
        """Initialize the unit registry with custom definitions."""
        self._ureg = PintRegistry()

        # Add kitchen-specific units
        self._ureg.define("pinch = 0.3 milliliter")
        self._ureg.define("dash = 0.6 milliliter")
        self._ureg.define("splash = 5 milliliter")
        self._ureg.define("handful = 30 gram")
        self._ureg.define("bunch = 1 count")
        self._ureg.define("sprig = 1 count")
        self._ureg.define("clove = 1 count")
        self._ureg.define("head = 1 count")
        self._ureg.define("stalk = 1 count")
        self._ureg.define("can = 400 milliliter")  # Standard can size
        self._ureg.define("dozen = 12 count")

    def parse_fraction(self, text: str) -> float | None:
        """Parse a fraction or mixed number string to float.

        Args:
            text: String like "1/2", "1 1/2", "0.5"

        Returns:
            Float value or None if unparseable.

        Examples:
            >>> registry.parse_fraction("1/2")
            0.5
            >>> registry.parse_fraction("1 1/2")
            1.5
            >>> registry.parse_fraction("2")
            2.0
        """
        text = text.strip()
        if not text:
            return None

        try:
            # Try direct float conversion
            return float(text)
        except ValueError:
            pass

        # Try fraction patterns
        # Mixed number: "1 1/2"
        mixed_match = re.match(r"(\d+)\s+(\d+)/(\d+)", text)
        if mixed_match:
            whole = int(mixed_match.group(1))
            numerator = int(mixed_match.group(2))
            denominator = int(mixed_match.group(3))
            return whole + (numerator / denominator)

        # Simple fraction: "1/2"
        fraction_match = re.match(r"(\d+)/(\d+)", text)
        if fraction_match:
            numerator = int(fraction_match.group(1))
            denominator = int(fraction_match.group(2))
            return numerator / denominator

        # Unicode fractions
        unicode_fractions = {
            "½": 0.5,
            "⅓": 1 / 3,
            "⅔": 2 / 3,
            "¼": 0.25,
            "¾": 0.75,
            "⅕": 0.2,
            "⅖": 0.4,
            "⅗": 0.6,
            "⅘": 0.8,
            "⅙": 1 / 6,
            "⅚": 5 / 6,
            "⅛": 0.125,
            "⅜": 0.375,
            "⅝": 0.625,
            "⅞": 0.875,
        }

        for char, value in unicode_fractions.items():
            if char in text:
                # Handle "1½" pattern
                prefix = text.replace(char, "").strip()
                if prefix:
                    try:
                        return float(prefix) + value
                    except ValueError:
                        return value
                return value

        return None

    def normalize_unit(self, unit: str) -> str:
        """Normalize a unit string to canonical form.

        Args:
            unit: Raw unit string like "tbsp" or "Tablespoons"

        Returns:
            Normalized unit string like "tablespoon"
        """
        unit = unit.strip().lower()

        # Check aliases first
        if unit in self.UNIT_ALIASES:
            return self.UNIT_ALIASES[unit]

        # Handle plurals - strip trailing 's' and check again
        if unit.endswith("s") and len(unit) > 1:
            singular = unit[:-1]
            if singular in self.UNIT_ALIASES:
                return self.UNIT_ALIASES[singular]
            # Common units that should be singular
            common_units = {
                "cup",
                "tablespoon",
                "teaspoon",
                "ounce",
                "pound",
                "gram",
                "kilogram",
                "liter",
                "milliliter",
                "clove",
                "slice",
                "piece",
                "can",
                "package",
                "bunch",
                "stalk",
            }
            if singular in common_units:
                return singular

        # Check if it's a vague unit
        if unit in self.VAGUE_UNITS:
            return unit

        # Return as-is if not recognized
        return unit

    def is_vague_unit(self, unit: str) -> bool:
        """Check if a unit is vague/unmeasurable."""
        return self.normalize_unit(unit) in self.VAGUE_UNITS

    def convert(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
    ) -> float | None:
        """Convert a value between units.

        Args:
            value: The quantity to convert.
            from_unit: Source unit.
            to_unit: Target unit.

        Returns:
            Converted value, or None if conversion not possible.

        Example:
            >>> registry.convert(500, "gram", "kilogram")
            0.5
        """
        try:
            quantity = value * self._ureg(self.normalize_unit(from_unit))
            return quantity.to(self.normalize_unit(to_unit)).magnitude
        except (pint.DimensionalityError, pint.UndefinedUnitError):
            return None

    def are_compatible(self, unit1: str, unit2: str) -> bool:
        """Check if two units are dimensionally compatible.

        Args:
            unit1: First unit.
            unit2: Second unit.

        Returns:
            True if units can be converted between each other.

        Example:
            >>> registry.are_compatible("cup", "milliliter")
            True
            >>> registry.are_compatible("gram", "cup")
            False  # Needs density
        """
        try:
            q1 = 1 * self._ureg(self.normalize_unit(unit1))
            q2 = 1 * self._ureg(self.normalize_unit(unit2))
            q1.to(q2.units)
            return True
        except (pint.DimensionalityError, pint.UndefinedUnitError):
            return False
