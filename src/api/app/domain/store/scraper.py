"""Store Scraper - Fetch aisle data from stores. 🔍

Retrieves product locations from grocery store APIs/websites.

Note: Store scraping may have legal/ToS implications.
See open-questions.md Q10 for discussion.

Fun fact: Shaw's was founded in 1860 in Portland, Maine! 🦞
"""

from abc import ABC, abstractmethod

from src.api.app.domain.store.models import StoreAisleMapping


class StoreScraper(ABC):
    """Abstract base class for store scrapers. 🔍"""

    @abstractmethod
    async def search_product(
        self,
        query: str,
    ) -> list[dict]:
        """Search for a product.

        Args:
            query: Search term.

        Returns:
            List of product results with aisle info.
        """
        ...

    @abstractmethod
    async def get_aisle_mapping(
        self,
        product_name: str,
    ) -> StoreAisleMapping | None:
        """Get aisle mapping for a product.

        Args:
            product_name: Product to look up.

        Returns:
            Aisle mapping or None if not found.
        """
        ...


class MockStoreScraper(StoreScraper):
    """Mock scraper for testing. 🧪

    Returns realistic sample data without hitting real APIs.
    """

    # Sample product data
    MOCK_PRODUCTS: dict[str, str] = {
        "oreos": "Aisle 9 - Cookies",
        "cheerios": "Aisle 7 - Cereals",
        "milk": "Dairy - Aisle 14",
        "bread": "Bakery",
        "chicken breast": "Meat - Fresh",
        "salmon": "Seafood",
        "bananas": "Produce",
        "olive oil": "Aisle 5 - Oils",
        "pasta": "Aisle 6 - Pasta",
        "tomato sauce": "Aisle 6 - Pasta",
    }

    async def search_product(
        self,
        query: str,
    ) -> list[dict]:
        """Search mock product database."""
        query_lower = query.lower()
        results = []

        for product, aisle in self.MOCK_PRODUCTS.items():
            if query_lower in product:
                results.append(
                    {
                        "name": product.title(),
                        "aisle": aisle,
                        "price": 3.99,  # Mock price
                        "in_stock": True,
                    }
                )

        return results

    async def get_aisle_mapping(
        self,
        product_name: str,
    ) -> StoreAisleMapping | None:
        """Get mock aisle mapping."""
        from datetime import datetime
        from uuid import uuid4

        product_lower = product_name.lower()

        for product, aisle in self.MOCK_PRODUCTS.items():
            if product in product_lower or product_lower in product:
                return StoreAisleMapping(
                    id=uuid4(),
                    store_id=uuid4(),
                    item_keyword=product,
                    aisle=aisle,
                    confidence=0.9,
                    last_verified=datetime.now(),
                )

        return None


class ShawsScraper(StoreScraper):
    """Shaw's supermarket scraper. 🦞

    Uses Shaw's website/API to fetch product locations.

    Note: This is a placeholder for actual implementation.
    Real implementation would require:
    - Selenium/Playwright for dynamic content
    - Or reverse-engineering their mobile API
    """

    def __init__(self, store_id: str | None = None) -> None:
        """Initialize with store ID.

        Args:
            store_id: The Shaw's store location ID.
        """
        self.store_id = store_id

    async def search_product(
        self,
        query: str,
    ) -> list[dict]:
        """Search Shaw's product database.

        In production, this would make HTTP requests.
        """
        # Placeholder - use mock for now
        mock = MockStoreScraper()
        return await mock.search_product(query)

    async def get_aisle_mapping(
        self,
        product_name: str,
    ) -> StoreAisleMapping | None:
        """Get aisle mapping from Shaw's."""
        # Placeholder - use mock for now
        mock = MockStoreScraper()
        return await mock.get_aisle_mapping(product_name)


class InstacartScraper(StoreScraper):
    """Instacart-based scraper. 🛒

    Uses Instacart's product data which often includes aisle info.
    Works for many stores: Shaw's, Whole Foods, etc.

    Note: Requires Instacart account/API access.
    """

    def __init__(
        self,
        retailer_id: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """Initialize with retailer info.

        Args:
            retailer_id: Instacart retailer ID.
            api_key: API key if using official API.
        """
        self.retailer_id = retailer_id
        self.api_key = api_key

    async def search_product(
        self,
        query: str,
    ) -> list[dict]:
        """Search via Instacart."""
        # Placeholder implementation
        mock = MockStoreScraper()
        return await mock.search_product(query)

    async def get_aisle_mapping(
        self,
        product_name: str,
    ) -> StoreAisleMapping | None:
        """Get aisle from Instacart product data."""
        mock = MockStoreScraper()
        return await mock.get_aisle_mapping(product_name)
