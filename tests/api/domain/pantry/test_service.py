"""Tests for Pantry Service Business Logic. 🧪

Tests the service layer independent of database.
Uses mocked repositories.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.api.app.domain.pantry.models import (
    CreatePantryItemDTO,
    PantryItem,
    PantryLocation,
    UpdatePantryItemDTO,
)
from src.api.app.domain.pantry.service import (
    PantryItemNotFoundError,
    PantryService,
)


@pytest.fixture
def mock_repository():
    """Create a mock PantryRepository."""
    return AsyncMock()


@pytest.fixture
def service(mock_repository):
    """Create a PantryService with mocked repository."""
    return PantryService(mock_repository)


@pytest.fixture
def sample_item():
    """Create a sample PantryItem for testing."""
    return PantryItem(
        id=uuid4(),
        household_id=uuid4(),
        name="Rice",
        quantity=1.0,
        unit="kg",
        location=PantryLocation.PANTRY,
        expiry_date=None,
        notes=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


class TestPantryServiceGetItem:
    """Tests for get_item method."""

    @pytest.mark.asyncio
    async def test_get_existing_item(self, service, mock_repository, sample_item):
        """Test getting an existing item."""
        mock_repository.get_by_id.return_value = sample_item

        result = await service.get_item(sample_item.id, sample_item.household_id)

        assert result == sample_item
        mock_repository.get_by_id.assert_called_once_with(
            sample_item.id, sample_item.household_id
        )

    @pytest.mark.asyncio
    async def test_get_nonexistent_item_raises(self, service, mock_repository):
        """Test that getting a nonexistent item raises an error."""
        mock_repository.get_by_id.return_value = None
        item_id = uuid4()
        household_id = uuid4()

        with pytest.raises(PantryItemNotFoundError) as exc_info:
            await service.get_item(item_id, household_id)

        assert exc_info.value.item_id == item_id


class TestPantryServiceCreateItem:
    """Tests for create_item method."""

    @pytest.mark.asyncio
    async def test_create_normalizes_name(self, service, mock_repository, sample_item):
        """Test that item names are normalized (title case)."""
        mock_repository.create.return_value = sample_item

        dto = CreatePantryItemDTO(
            name="  brown rice  ",
            quantity=1.0,
            unit="KG",
        )
        household_id = uuid4()

        await service.create_item(household_id, dto)

        # Check the DTO passed to repository has normalized values
        call_args = mock_repository.create.call_args
        normalized_dto = call_args[0][1]
        assert normalized_dto.name == "Brown Rice"
        assert normalized_dto.unit == "kg"

    @pytest.mark.asyncio
    async def test_create_returns_item(self, service, mock_repository, sample_item):
        """Test that create returns the created item."""
        mock_repository.create.return_value = sample_item

        dto = CreatePantryItemDTO(name="Rice", quantity=1.0, unit="kg")
        result = await service.create_item(uuid4(), dto)

        assert result == sample_item


class TestPantryServiceUpdateItem:
    """Tests for update_item method."""

    @pytest.mark.asyncio
    async def test_update_existing_item(self, service, mock_repository, sample_item):
        """Test updating an existing item."""
        mock_repository.update.return_value = sample_item

        dto = UpdatePantryItemDTO(quantity=2.0)
        result = await service.update_item(
            sample_item.id, sample_item.household_id, dto
        )

        assert result == sample_item
        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_nonexistent_item_raises(self, service, mock_repository):
        """Test that updating a nonexistent item raises an error."""
        mock_repository.update.return_value = None
        item_id = uuid4()
        household_id = uuid4()

        with pytest.raises(PantryItemNotFoundError):
            await service.update_item(
                item_id, household_id, UpdatePantryItemDTO(quantity=2.0)
            )


class TestPantryServiceDeleteItem:
    """Tests for delete_item method."""

    @pytest.mark.asyncio
    async def test_delete_existing_item(self, service, mock_repository):
        """Test deleting an existing item."""
        mock_repository.delete.return_value = True
        item_id = uuid4()
        household_id = uuid4()

        await service.delete_item(item_id, household_id)

        mock_repository.delete.assert_called_once_with(item_id, household_id)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_item_raises(self, service, mock_repository):
        """Test that deleting a nonexistent item raises an error."""
        mock_repository.delete.return_value = False
        item_id = uuid4()
        household_id = uuid4()

        with pytest.raises(PantryItemNotFoundError):
            await service.delete_item(item_id, household_id)


class TestPantryServiceConfirmPossession:
    """Tests for confirm_possession method (Lazy Discovery - D13). 🔍"""

    @pytest.mark.asyncio
    async def test_returns_existing_item(self, service, mock_repository, sample_item):
        """Test that existing items are returned without creating new ones."""
        mock_repository.search_by_name.return_value = [sample_item]
        household_id = uuid4()

        result = await service.confirm_possession(household_id, "Rice")

        assert result == sample_item
        mock_repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_creates_new_item_if_not_found(self, service, mock_repository, sample_item):
        """Test that new items are created via Lazy Discovery."""
        mock_repository.search_by_name.return_value = []
        mock_repository.create.return_value = sample_item
        household_id = uuid4()

        result = await service.confirm_possession(household_id, "Cumin")

        mock_repository.create.assert_called_once()
        call_args = mock_repository.create.call_args
        dto = call_args[0][1]
        assert dto.name == "Cumin"
        assert dto.quantity == 1.0
        assert dto.unit == "count"
