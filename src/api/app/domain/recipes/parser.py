"""Ingredient Parser - Converting text to structured data. 🔍

The core logic engine for parsing ingredient strings like
"1 large onion, diced" into structured data.

Uses a pipeline approach:
1. Clean string (normalize whitespace, unicode)
2. Rule-based extraction (regex patterns)
3. LLM fallback if confidence is low (Phase 2B+)

Fun fact: The average recipe has 9 ingredients! 📊
"""

import re
from dataclasses import dataclass
from typing import Protocol

from src.api.app.domain.recipes.models import ParsedIngredient
from src.api.app.domain.recipes.unit_registry import UnitRegistry


class LLMAdapter(Protocol):
    """Protocol for LLM-based ingredient parsing fallback."""

    async def parse_ingredient(self, text: str) -> ParsedIngredient | None:
        """Parse an ingredient string using an LLM."""
        ...


@dataclass
class ParserConfig:
    """Configuration for the ingredient parser."""

    min_confidence_threshold: float = 0.6
    use_llm_fallback: bool = True
    normalize_items: bool = True


class IngredientParser:
    """Parser for converting ingredient text to structured data. 🧪

    Example:
        >>> parser = IngredientParser()
        >>> result = parser.parse("1/2 cup flour")
        >>> print(result)
        ParsedIngredient(raw_text="1/2 cup flour", quantity=0.5, unit="cup", item_name="flour")
    """

    # Regex patterns for parsing
    # Matches: "1", "1.5", "1/2", "1 1/2", "500g", unicode fractions
    # Group 1: Quantity (including fractions and decimals)
    # Order matters: try mixed fractions first, then simple fractions, then decimals
    QUANTITY_PATTERN = re.compile(
        r"^(\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?[½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]?|[½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞])\s*",
        re.UNICODE,
    )

    # Common cooking units (must come after quantity)
    UNIT_PATTERN = re.compile(
        r"^(cups?|tablespoons?|tbsp?|teaspoons?|tsp?|ounces?|oz|pounds?|lbs?|"
        r"grams?|g|kilograms?|kg|milliliters?|ml|liters?|l|"
        r"pinch(?:es)?|dash(?:es)?|bunch(?:es)?|sprigs?|cloves?|heads?|stalks?|"
        r"cans?|packages?|pkgs?|slices?|pieces?|pcs?|whole|"
        r"fluid\s*(?:ounces?|oz))(?:\s+|$)",
        re.IGNORECASE,
    )
    
    # Size descriptors that can appear before units (like "large")
    SIZE_PATTERN = re.compile(
        r"^(large|medium|small|extra-large|extra large|jumbo)\s+",
        re.IGNORECASE,
    )

    # Parenthetical notes pattern
    NOTES_PATTERN = re.compile(r"\(([^)]+)\)")

    # Size/preparation descriptors
    DESCRIPTOR_PATTERN = re.compile(
        r"\b(large|medium|small|finely|roughly|thinly|thickly|"
        r"diced|chopped|minced|sliced|julienned|crushed|grated|"
        r"fresh|frozen|dried|canned|packed|loosely|"
        r"room temperature|cold|warm|hot|melted|softened)\b",
        re.IGNORECASE,
    )

    # Words to strip from item names
    STRIP_WORDS = frozenset({
        "of", "the", "a", "an", "some", "about", "approximately",
        "or", "to", "for", "optional",
    })

    def __init__(
        self,
        config: ParserConfig | None = None,
        llm_adapter: LLMAdapter | None = None,
    ) -> None:
        """Initialize the parser.

        Args:
            config: Parser configuration.
            llm_adapter: Optional LLM adapter for fallback parsing.
        """
        self.config = config or ParserConfig()
        self.llm_adapter = llm_adapter
        self.unit_registry = UnitRegistry()

    def parse(self, text: str) -> ParsedIngredient:
        """Parse an ingredient string into structured data.

        Args:
            text: Raw ingredient text like "1 large onion, diced"

        Returns:
            ParsedIngredient with extracted fields.
        """
        # Step 1: Clean the input
        cleaned = self._clean_text(text)
        original = text.strip()

        # Step 2: Extract parenthetical notes first
        notes_parts = []
        parenthetical = self.NOTES_PATTERN.findall(cleaned)
        if parenthetical:
            notes_parts.extend(parenthetical)
            cleaned = self.NOTES_PATTERN.sub("", cleaned).strip()

        # Step 3: Extract quantity
        quantity = None
        quantity_match = self.QUANTITY_PATTERN.match(cleaned)
        if quantity_match:
            quantity_str = quantity_match.group(1)
            quantity = self.unit_registry.parse_fraction(quantity_str)
            cleaned = cleaned[quantity_match.end():].strip()

        # Step 4: Extract size descriptor (large, medium, small) before unit check
        size_descriptor = None
        size_match = self.SIZE_PATTERN.match(cleaned)
        if size_match:
            size_descriptor = size_match.group(1)
            notes_parts.append(size_descriptor)
            cleaned = cleaned[size_match.end():].strip()

        # Step 5: Extract unit
        unit = None
        unit_match = self.UNIT_PATTERN.match(cleaned)
        if unit_match:
            unit = self.unit_registry.normalize_unit(unit_match.group(1))
            cleaned = cleaned[unit_match.end():].strip()

        # Step 6: Handle "of" after unit (e.g., "cup of flour")
        if cleaned.lower().startswith("of "):
            cleaned = cleaned[3:].strip()

        # Step 7: Extract descriptors from remaining text
        descriptors = self.DESCRIPTOR_PATTERN.findall(cleaned)
        if descriptors:
            notes_parts.extend(descriptors)
            # Remove descriptors from the item name
            for desc in descriptors:
                cleaned = re.sub(rf"\b{re.escape(desc)}\b", "", cleaned, flags=re.IGNORECASE)

        # Step 8: Handle commas (often separate item from preparation)
        if "," in cleaned:
            parts = [p.strip() for p in cleaned.split(",", 1)]
            item_name = parts[0]
            if len(parts) > 1 and parts[1]:
                notes_parts.append(parts[1])
        else:
            item_name = cleaned

        # Step 9: Clean up item name
        item_name = self._normalize_item_name(item_name)

        # Step 10: Handle implicit count (e.g., "3 eggs" with no unit)
        if quantity is not None and not unit and item_name:
            # Check if this is a countable item
            if self._is_countable_item(item_name):
                unit = "count"

        # Step 11: Handle "to taste" and similar
        if quantity is None and self._is_to_taste(original):
            quantity = 0
            unit = "to taste"

        # Step 12: Combine notes
        notes = ", ".join(filter(None, notes_parts)) if notes_parts else None

        # Calculate confidence based on what we extracted
        confidence = self._calculate_confidence(quantity, unit, item_name, original)

        return ParsedIngredient(
            raw_text=original,
            quantity=quantity,
            unit=unit,
            item_name=item_name or original,  # Fallback to original if parsing failed
            notes=notes,
            confidence=confidence,
        )

    async def parse_with_fallback(self, text: str) -> ParsedIngredient:
        """Parse with optional LLM fallback for low-confidence results.

        Args:
            text: Raw ingredient text.

        Returns:
            ParsedIngredient from rules or LLM.
        """
        result = self.parse(text)

        # Use LLM fallback if confidence is low
        if (
            self.config.use_llm_fallback
            and self.llm_adapter
            and result.confidence < self.config.min_confidence_threshold
        ):
            llm_result = await self.llm_adapter.parse_ingredient(text)
            if llm_result:
                # LLM results have slightly lower confidence
                llm_result.confidence = min(llm_result.confidence, 0.85)
                return llm_result

        return result

    def parse_many(self, texts: list[str]) -> list[ParsedIngredient]:
        """Parse multiple ingredient strings.

        Args:
            texts: List of ingredient strings.

        Returns:
            List of ParsedIngredients.
        """
        return [self.parse(text) for text in texts]

    def _clean_text(self, text: str) -> str:
        """Clean and normalize ingredient text."""
        # Normalize unicode
        text = text.strip()

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove leading bullets/list markers (but not quantities!)
        # Only strip if followed by "." or ")" to indicate list numbers
        text = re.sub(r"^[•\-–—*]\s*", "", text)
        text = re.sub(r"^\d+[.)]\s+", "", text)

        return text

    def _normalize_item_name(self, name: str) -> str:
        """Normalize an item name."""
        # Clean whitespace
        name = re.sub(r"\s+", " ", name).strip()

        # Remove strip words from start
        words = name.split()
        while words and words[0].lower() in self.STRIP_WORDS:
            words.pop(0)

        name = " ".join(words)

        # Title case if configured
        if self.config.normalize_items:
            name = name.strip().lower()

        return name

    def _is_countable_item(self, item: str) -> bool:
        """Check if an item is typically counted (not measured)."""
        countable = {
            "egg", "eggs", "onion", "onions", "clove", "cloves",
            "potato", "potatoes", "tomato", "tomatoes", "carrot", "carrots",
            "apple", "apples", "banana", "bananas", "lemon", "lemons",
            "lime", "limes", "orange", "oranges", "avocado", "avocados",
            "pepper", "peppers", "garlic", "shallot", "shallots",
            "chicken breast", "chicken breasts", "steak", "steaks",
            "slice", "slices", "piece", "pieces",
        }
        return item.lower() in countable

    def _is_to_taste(self, text: str) -> bool:
        """Check if ingredient is 'to taste' type."""
        patterns = ["to taste", "as needed", "optional", "for garnish"]
        text_lower = text.lower()
        return any(p in text_lower for p in patterns)

    def _calculate_confidence(
        self,
        quantity: float | None,
        unit: str | None,
        item_name: str,
        original: str,
    ) -> float:
        """Calculate parser confidence score."""
        score = 0.0

        # Base score for having an item name
        if item_name and len(item_name) > 1:
            score += 0.4

        # Quantity parsed successfully
        if quantity is not None:
            score += 0.3

        # Unit parsed successfully
        if unit:
            score += 0.2

        # Item name is reasonable (not too long, not just the original)
        if item_name and item_name != original and len(item_name) < 50:
            score += 0.1

        return min(score, 1.0)
