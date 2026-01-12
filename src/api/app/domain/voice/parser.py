"""Voice Parser - NLP for voice commands. 🎙️

Parses natural language voice commands into structured actions.

Fun fact: Natural Language Processing has improved 10x in accuracy
since the introduction of transformer models in 2017! 🤖
"""

import re
from re import Pattern

from src.api.app.domain.voice.models import (
    ParsedVoiceCommand,
    ParsedVoiceItem,
    VoiceCommandType,
)

# Regex patterns for parsing
QUANTITY_PATTERN: Pattern[str] = re.compile(
    r"(\d+(?:\.\d+)?)\s*",
    re.IGNORECASE,
)

UNIT_PATTERN: Pattern[str] = re.compile(
    r"(gallons?|quarts?|pints?|cups?|liters?|ml|oz|ounces?|"
    r"pounds?|lbs?|kg|grams?|g|dozen|bottles?|cans?|boxes?|bags?|packages?)",
    re.IGNORECASE,
)


class VoiceParser:
    """Parser for voice commands. 🎤

    Converts natural language to structured commands.

    Example:
        >>> parser = VoiceParser()
        >>> result = parser.parse("Add bread and 2 gallons of milk")
        >>> print(result.command_type)  # ADD_ITEM
        >>> print(result.items)  # [bread, milk x2]
    """

    # Command trigger words
    ADD_TRIGGERS = frozenset(
        {
            "add",
            "put",
            "get",
            "buy",
            "need",
            "pick up",
            "grab",
        }
    )

    REMOVE_TRIGGERS = frozenset(
        {
            "remove",
            "delete",
            "take off",
            "cross off",
            "cancel",
        }
    )

    CHECK_TRIGGERS = frozenset(
        {
            "check",
            "mark",
            "got",
            "checked",
            "done",
            "complete",
            "crossed",
        }
    )

    ASK_TRIGGERS = frozenset(
        {
            "do we have",
            "is there",
            "how much",
            "do i have",
            "check if",
            "have any",
        }
    )

    PANTRY_TRIGGERS = frozenset(
        {
            "pantry",
            "inventory",
            "fridge",
            "freezer",
        }
    )

    # Words to strip from item names
    FILLER_WORDS = frozenset(
        {
            "a",
            "an",
            "the",
            "some",
            "of",
            "to",
            "my",
            "our",
            "list",
            "shopping",
            "please",
            "thanks",
            "okay",
            "hey",
        }
    )

    def parse(self, text: str) -> ParsedVoiceCommand:
        """Parse a voice command.

        Args:
            text: The voice command text.

        Returns:
            ParsedVoiceCommand with type and items.
        """
        text_lower = text.lower().strip()

        # Handle empty input
        if not text_lower:
            return ParsedVoiceCommand(
                raw_text=text,
                command_type=VoiceCommandType.UNKNOWN,
                items=[],
                confidence=0.0,
            )

        text_clean = self._clean_text(text_lower)

        # Determine command type
        command_type = self._detect_command_type(text_lower)

        # Parse items from text
        items = self._parse_items(text_clean, command_type)

        # Calculate confidence based on parsing success
        confidence = self._calculate_confidence(command_type, items)

        return ParsedVoiceCommand(
            raw_text=text,
            command_type=command_type,
            items=items,
            confidence=confidence,
        )

    def _detect_command_type(self, text: str) -> VoiceCommandType:
        """Detect the type of command.

        Args:
            text: Lowercase command text.

        Returns:
            VoiceCommandType.
        """
        # Check for question patterns first
        for trigger in self.ASK_TRIGGERS:
            if trigger in text:
                return VoiceCommandType.ASK_INVENTORY

        # Check for pantry-specific adds
        for trigger in self.PANTRY_TRIGGERS:
            if trigger in text:
                for add in self.ADD_TRIGGERS:
                    if add in text:
                        return VoiceCommandType.ADD_PANTRY

        # Check for check/complete
        for trigger in self.CHECK_TRIGGERS:
            if text.startswith(trigger) or f" {trigger} " in text:
                return VoiceCommandType.CHECK_ITEM

        # Check for remove
        for trigger in self.REMOVE_TRIGGERS:
            if text.startswith(trigger) or f" {trigger} " in text:
                return VoiceCommandType.REMOVE_ITEM

        # Check for add (default for shopping)
        for trigger in self.ADD_TRIGGERS:
            if text.startswith(trigger) or f" {trigger} " in text:
                return VoiceCommandType.ADD_ITEM

        # Default to add_item for simple item mentions
        if len(text.split()) <= 5:
            return VoiceCommandType.ADD_ITEM

        return VoiceCommandType.UNKNOWN

    def _clean_text(self, text: str) -> str:
        """Remove filler words and command triggers.

        Args:
            text: Input text.

        Returns:
            Cleaned text with just item references.
        """
        # Remove command triggers
        for triggers in [
            self.ADD_TRIGGERS,
            self.REMOVE_TRIGGERS,
            self.CHECK_TRIGGERS,
        ]:
            for trigger in triggers:
                text = text.replace(trigger, " ")

        # Remove common filler words
        words = text.split()
        cleaned = [w for w in words if w not in self.FILLER_WORDS]

        return " ".join(cleaned)

    def _parse_items(
        self,
        text: str,
        command_type: VoiceCommandType,
    ) -> list[ParsedVoiceItem]:
        """Parse items from cleaned text.

        Handles:
        - "bread and milk" -> [bread, milk]
        - "2 gallons of milk" -> [milk x2 gallons]
        - "eggs, butter, and cheese" -> [eggs, butter, cheese]

        Args:
            text: Cleaned command text.
            command_type: Type of command.

        Returns:
            List of parsed items.
        """
        items: list[ParsedVoiceItem] = []

        # Split on common separators
        separators = [" and ", ",", "&", " plus "]
        parts = [text]

        for sep in separators:
            new_parts = []
            for part in parts:
                new_parts.extend(part.split(sep))
            parts = new_parts

        # Parse each part
        for part in parts:
            part = part.strip()
            if not part:
                continue

            item = self._parse_single_item(part)
            if item:
                items.append(item)

        return items

    def _parse_single_item(self, text: str) -> ParsedVoiceItem | None:
        """Parse a single item from text.

        Args:
            text: Text for one item.

        Returns:
            ParsedVoiceItem or None.
        """
        text = text.strip()
        if not text:
            return None

        quantity = 1.0
        unit = None
        name = text

        # Try to extract quantity
        qty_match = QUANTITY_PATTERN.match(text)
        if qty_match:
            quantity = float(qty_match.group(1))
            text = text[qty_match.end() :].strip()

        # Try to extract unit
        unit_match = UNIT_PATTERN.search(text)
        if unit_match:
            unit = unit_match.group(1).lower()
            text = text.replace(unit_match.group(0), "").strip()

        # Clean up remaining text as item name
        name = text.strip()

        # Remove "of" at the start
        if name.startswith("of "):
            name = name[3:]

        name = name.strip()

        if not name:
            return None

        return ParsedVoiceItem(
            name=name,
            quantity=quantity,
            unit=unit,
        )

    def _calculate_confidence(
        self,
        command_type: VoiceCommandType,
        items: list[ParsedVoiceItem],
    ) -> float:
        """Calculate parsing confidence.

        Args:
            command_type: Detected command type.
            items: Parsed items.

        Returns:
            Confidence score 0-1.
        """
        if command_type == VoiceCommandType.UNKNOWN:
            return 0.3

        if not items:
            return 0.4

        # Higher confidence with more items parsed
        base = 0.7
        bonus = min(len(items) * 0.1, 0.3)

        return min(base + bonus, 1.0)
