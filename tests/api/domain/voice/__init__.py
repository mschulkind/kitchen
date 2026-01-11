"""Voice parser tests. 🎙️"""

import pytest

from src.api.app.domain.voice.models import VoiceCommandType
from src.api.app.domain.voice.parser import VoiceParser


class TestVoiceParser:
    """Tests for VoiceParser."""

    @pytest.fixture
    def parser(self) -> VoiceParser:
        """Create parser instance."""
        return VoiceParser()

    def test_parse_simple_add(self, parser: VoiceParser):
        """Test parsing simple add command."""
        result = parser.parse("Add bread")
        assert result.command_type == VoiceCommandType.ADD_ITEM
        assert len(result.items) == 1
        assert result.items[0].name == "bread"

    def test_parse_add_with_quantity(self, parser: VoiceParser):
        """Test parsing add with quantity."""
        result = parser.parse("Add 2 gallons of milk")
        assert result.command_type == VoiceCommandType.ADD_ITEM
        assert len(result.items) == 1
        assert result.items[0].name == "milk"
        assert result.items[0].quantity == 2.0
        assert result.items[0].unit == "gallons"

    def test_parse_multiple_items(self, parser: VoiceParser):
        """Test parsing multiple items."""
        result = parser.parse("Add bread and milk")
        assert result.command_type == VoiceCommandType.ADD_ITEM
        assert len(result.items) == 2
        assert {item.name for item in result.items} == {"bread", "milk"}

    def test_parse_comma_separated(self, parser: VoiceParser):
        """Test parsing comma-separated items."""
        result = parser.parse("Add eggs, butter, and cheese")
        assert len(result.items) == 3

    def test_parse_remove_command(self, parser: VoiceParser):
        """Test parsing remove command."""
        result = parser.parse("Remove milk from the list")
        assert result.command_type == VoiceCommandType.REMOVE_ITEM

    def test_parse_check_command(self, parser: VoiceParser):
        """Test parsing check command."""
        result = parser.parse("Check off the milk")
        assert result.command_type == VoiceCommandType.CHECK_ITEM

    def test_parse_inventory_question(self, parser: VoiceParser):
        """Test parsing inventory question."""
        result = parser.parse("Do we have eggs?")
        assert result.command_type == VoiceCommandType.ASK_INVENTORY

    def test_parse_pantry_add(self, parser: VoiceParser):
        """Test parsing pantry add."""
        result = parser.parse("Add milk to the pantry")
        assert result.command_type == VoiceCommandType.ADD_PANTRY

    def test_confidence_higher_with_items(self, parser: VoiceParser):
        """Test confidence increases with parsed items."""
        result_with = parser.parse("Add bread and milk")
        result_without = parser.parse("Hmm maybe something")
        assert result_with.confidence > result_without.confidence

    def test_parse_handles_filler_words(self, parser: VoiceParser):
        """Test filler words are stripped."""
        result = parser.parse("Please add some bread to the list")
        assert len(result.items) == 1
        assert result.items[0].name == "bread"


class TestVoiceParserEdgeCases:
    """Edge case tests for VoiceParser."""

    @pytest.fixture
    def parser(self) -> VoiceParser:
        return VoiceParser()

    def test_empty_string(self, parser: VoiceParser):
        """Test empty string handling."""
        result = parser.parse("")
        assert result.command_type == VoiceCommandType.UNKNOWN

    def test_just_whitespace(self, parser: VoiceParser):
        """Test whitespace handling."""
        result = parser.parse("   ")
        assert result.command_type == VoiceCommandType.UNKNOWN

    def test_single_item_no_command(self, parser: VoiceParser):
        """Test single item without command word."""
        result = parser.parse("milk")
        # Should default to ADD_ITEM for short commands
        assert result.command_type == VoiceCommandType.ADD_ITEM
        assert len(result.items) == 1
