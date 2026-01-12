"""Store scraper tests. 🔍

Tests for store scrapers - fetching aisle data from stores.

Fun fact: Shaw's was founded in 1860 in Portland, Maine! 🦞
"""

import pytest

from src.api.app.domain.store.models import StoreAisleMapping
from src.api.app.domain.store.scraper import (
    InstacartScraper,
    MockStoreScraper,
    ShawsScraper,
)


class TestMockStoreScraper:
    """Tests for MockStoreScraper."""

    @pytest.fixture
    def scraper(self) -> MockStoreScraper:
        """Create mock scraper instance."""
        return MockStoreScraper()

    @pytest.mark.asyncio
    async def test_search_product_found(self, scraper: MockStoreScraper):
        """Test searching for a known product."""
        results = await scraper.search_product("oreos")

        assert len(results) == 1
        assert results[0]["name"] == "Oreos"
        assert "Aisle 9" in results[0]["aisle"]
        assert results[0]["in_stock"] is True

    @pytest.mark.asyncio
    async def test_search_product_partial_match(self, scraper: MockStoreScraper):
        """Test partial match returns results."""
        results = await scraper.search_product("milk")

        assert len(results) == 1
        assert results[0]["name"] == "Milk"

    @pytest.mark.asyncio
    async def test_search_product_not_found(self, scraper: MockStoreScraper):
        """Test searching for unknown product returns empty."""
        results = await scraper.search_product("xyzzy_nonexistent")

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_search_product_case_insensitive(self, scraper: MockStoreScraper):
        """Test search is case insensitive."""
        results = await scraper.search_product("CHEERIOS")

        assert len(results) == 1
        assert results[0]["name"] == "Cheerios"

    @pytest.mark.asyncio
    async def test_get_aisle_mapping_found(self, scraper: MockStoreScraper):
        """Test getting aisle mapping for known product."""
        mapping = await scraper.get_aisle_mapping("bananas")

        assert mapping is not None
        assert isinstance(mapping, StoreAisleMapping)
        assert mapping.aisle == "Produce"
        assert mapping.confidence == 0.9

    @pytest.mark.asyncio
    async def test_get_aisle_mapping_partial_match(self, scraper: MockStoreScraper):
        """Test aisle mapping with partial match."""
        mapping = await scraper.get_aisle_mapping("olive oil extra virgin")

        assert mapping is not None
        assert "Aisle 5" in mapping.aisle

    @pytest.mark.asyncio
    async def test_get_aisle_mapping_not_found(self, scraper: MockStoreScraper):
        """Test aisle mapping returns None for unknown product."""
        mapping = await scraper.get_aisle_mapping("dragon fruit from mars")

        assert mapping is None

    @pytest.mark.asyncio
    async def test_mock_products_coverage(self, scraper: MockStoreScraper):
        """Test all mock products are searchable."""
        expected_products = [
            "oreos",
            "cheerios",
            "milk",
            "bread",
            "chicken breast",
            "salmon",
            "bananas",
            "olive oil",
            "pasta",
            "tomato sauce",
        ]

        for product in expected_products:
            results = await scraper.search_product(product)
            assert len(results) >= 1, f"Expected to find {product}"


class TestShawsScraper:
    """Tests for ShawsScraper."""

    @pytest.fixture
    def scraper(self) -> ShawsScraper:
        """Create Shaw's scraper instance."""
        return ShawsScraper(store_id="test-store-123")

    @pytest.mark.asyncio
    async def test_init_with_store_id(self, scraper: ShawsScraper):
        """Test scraper initializes with store ID."""
        assert scraper.store_id == "test-store-123"

    @pytest.mark.asyncio
    async def test_init_without_store_id(self):
        """Test scraper initializes without store ID."""
        scraper = ShawsScraper()
        assert scraper.store_id is None

    @pytest.mark.asyncio
    async def test_search_product_delegates_to_mock(self, scraper: ShawsScraper):
        """Test search delegates to mock (placeholder implementation)."""
        # Current implementation uses mock - this tests the delegation
        results = await scraper.search_product("milk")

        assert len(results) >= 1
        assert results[0]["name"] == "Milk"

    @pytest.mark.asyncio
    async def test_get_aisle_mapping_delegates_to_mock(self, scraper: ShawsScraper):
        """Test aisle mapping delegates to mock."""
        mapping = await scraper.get_aisle_mapping("bananas")

        assert mapping is not None
        assert mapping.aisle == "Produce"


class TestInstacartScraper:
    """Tests for InstacartScraper."""

    @pytest.fixture
    def scraper(self) -> InstacartScraper:
        """Create Instacart scraper instance."""
        return InstacartScraper(
            retailer_id="test-retailer",
            api_key="test-api-key",
        )

    @pytest.mark.asyncio
    async def test_init_with_credentials(self, scraper: InstacartScraper):
        """Test scraper initializes with credentials."""
        assert scraper.retailer_id == "test-retailer"
        assert scraper.api_key == "test-api-key"

    @pytest.mark.asyncio
    async def test_init_without_credentials(self):
        """Test scraper initializes without credentials."""
        scraper = InstacartScraper()
        assert scraper.retailer_id is None
        assert scraper.api_key is None

    @pytest.mark.asyncio
    async def test_search_product_delegates_to_mock(self, scraper: InstacartScraper):
        """Test search delegates to mock (placeholder implementation)."""
        results = await scraper.search_product("pasta")

        assert len(results) >= 1
        assert results[0]["name"] == "Pasta"

    @pytest.mark.asyncio
    async def test_get_aisle_mapping_delegates_to_mock(self, scraper: InstacartScraper):
        """Test aisle mapping delegates to mock."""
        mapping = await scraper.get_aisle_mapping("salmon")

        assert mapping is not None
        assert "Seafood" in mapping.aisle


class TestScraperIntegration:
    """Integration tests for scraper workflows."""

    @pytest.mark.asyncio
    async def test_search_then_get_mapping(self):
        """Test typical workflow: search then get mapping."""
        scraper = MockStoreScraper()

        # Search for product
        results = await scraper.search_product("bread")
        assert len(results) >= 1

        # Get mapping for found product
        product_name = results[0]["name"]
        mapping = await scraper.get_aisle_mapping(product_name)

        assert mapping is not None
        assert mapping.aisle == "Bakery"

    @pytest.mark.asyncio
    async def test_multiple_scrapers_same_results(self):
        """Test different scrapers return consistent results (mock-based)."""
        mock = MockStoreScraper()
        shaws = ShawsScraper()
        instacart = InstacartScraper()

        # All should return same results since they delegate to mock
        mock_results = await mock.search_product("milk")
        shaws_results = await shaws.search_product("milk")
        instacart_results = await instacart.search_product("milk")

        assert len(mock_results) == len(shaws_results) == len(instacart_results)
        assert mock_results[0]["name"] == shaws_results[0]["name"]
        assert shaws_results[0]["name"] == instacart_results[0]["name"]
