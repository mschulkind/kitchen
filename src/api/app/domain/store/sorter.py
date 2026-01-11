"""Store Sorter - Aisle-based list optimization. 🏪

Sorts shopping lists by store aisle for efficient traversal.

Fun fact: Following a sorted list can reduce shopping time by 30%! ⏱️
"""

from uuid import UUID

from src.api.app.domain.shopping.models import ShoppingItem
from src.api.app.domain.store.models import (
    AisleConfig,
    SortedShoppingItem,
    SortedShoppingList,
    StoreAisleMapping,
)

# Default aisle mappings for common items
# This is a fallback when no store-specific data is available
DEFAULT_AISLE_MAP: dict[str, str] = {
    # Produce
    "apple": "Produce",
    "banana": "Produce",
    "orange": "Produce",
    "lemon": "Produce",
    "lime": "Produce",
    "onion": "Produce",
    "garlic": "Produce",
    "potato": "Produce",
    "carrot": "Produce",
    "celery": "Produce",
    "tomato": "Produce",
    "lettuce": "Produce",
    "spinach": "Produce",
    "kale": "Produce",
    "broccoli": "Produce",
    "bell pepper": "Produce",
    "cucumber": "Produce",
    "avocado": "Produce",
    "ginger": "Produce",
    "herbs": "Produce",
    "cilantro": "Produce",
    "parsley": "Produce",
    "basil": "Produce",
    "mushroom": "Produce",
    # Bakery
    "bread": "Bakery",
    "rolls": "Bakery",
    "buns": "Bakery",
    "bagel": "Bakery",
    "croissant": "Bakery",
    "muffin": "Bakery",
    "tortilla": "Bakery",
    # Dairy
    "milk": "Dairy",
    "butter": "Dairy",
    "cheese": "Dairy",
    "yogurt": "Dairy",
    "cream": "Dairy",
    "eggs": "Dairy",
    "sour cream": "Dairy",
    "cottage cheese": "Dairy",
    # Meat
    "chicken": "Meat",
    "beef": "Meat",
    "pork": "Meat",
    "ground": "Meat",
    "bacon": "Meat",
    "sausage": "Meat",
    "turkey": "Meat",
    "steak": "Meat",
    # Seafood
    "fish": "Seafood",
    "salmon": "Seafood",
    "shrimp": "Seafood",
    "tuna": "Seafood",
    # Frozen
    "frozen": "Frozen",
    "ice cream": "Frozen",
    "pizza": "Frozen",
    # Canned goods
    "canned": "Canned Goods",
    "beans": "Canned Goods",
    "soup": "Canned Goods",
    "broth": "Canned Goods",
    "stock": "Canned Goods",
    "tomato sauce": "Canned Goods",
    "diced tomatoes": "Canned Goods",
    # Pasta & Grains
    "pasta": "Pasta & Grains",
    "spaghetti": "Pasta & Grains",
    "rice": "Pasta & Grains",
    "quinoa": "Pasta & Grains",
    "couscous": "Pasta & Grains",
    "noodles": "Pasta & Grains",
    # Baking
    "flour": "Baking",
    "sugar": "Baking",
    "baking soda": "Baking",
    "baking powder": "Baking",
    "vanilla": "Baking",
    "chocolate chips": "Baking",
    "yeast": "Baking",
    # Condiments
    "ketchup": "Condiments",
    "mustard": "Condiments",
    "mayonnaise": "Condiments",
    "soy sauce": "Condiments",
    "hot sauce": "Condiments",
    "vinegar": "Condiments",
    "olive oil": "Condiments",
    "vegetable oil": "Condiments",
    # Spices
    "salt": "Spices",
    "pepper": "Spices",
    "cumin": "Spices",
    "paprika": "Spices",
    "oregano": "Spices",
    "cinnamon": "Spices",
    "garlic powder": "Spices",
    "onion powder": "Spices",
    # Beverages
    "coffee": "Beverages",
    "tea": "Beverages",
    "juice": "Beverages",
    "soda": "Beverages",
    "water": "Beverages",
    # Snacks
    "chips": "Snacks",
    "crackers": "Snacks",
    "cookies": "Snacks",
    "nuts": "Snacks",
    "popcorn": "Snacks",
}

# Default aisle order for store traversal
DEFAULT_AISLE_ORDER = [
    "Produce",
    "Bakery",
    "Deli",
    "Meat",
    "Seafood",
    "Dairy",
    "Frozen",
    "Canned Goods",
    "Pasta & Grains",
    "Baking",
    "Condiments",
    "Spices",
    "Beverages",
    "Snacks",
    "Unknown",
]


class StoreSorter:
    """Sorts shopping lists by store aisle. 🏪

    Uses aisle mappings to optimize shopping route.

    Example:
        >>> sorter = StoreSorter()
        >>> sorted_list = sorter.sort_list(items, store_id)
        >>> for item in sorted_list.items:
        ...     print(f"{item.aisle}: {item.name}")
    """

    def __init__(
        self,
        mappings: list[StoreAisleMapping] | None = None,
        aisle_config: AisleConfig | None = None,
    ) -> None:
        """Initialize the sorter.

        Args:
            mappings: Store-specific aisle mappings.
            aisle_config: Aisle traversal order config.
        """
        self.mappings = mappings or []
        self.aisle_config = aisle_config

        # Build lookup from mappings
        self._mapping_lookup: dict[str, str] = {}
        for m in self.mappings:
            self._mapping_lookup[m.item_keyword.lower()] = m.aisle

    def sort_list(
        self,
        items: list[ShoppingItem],
        list_id: UUID,
        store_id: UUID | None = None,
    ) -> SortedShoppingList:
        """Sort a shopping list by aisle.

        Args:
            items: Shopping items to sort.
            list_id: The list's ID.
            store_id: Optional store for specific mappings.

        Returns:
            SortedShoppingList with items ordered by aisle.
        """
        sorted_items: list[SortedShoppingItem] = []
        unknown_items: list[SortedShoppingItem] = []

        # Get aisle order
        aisle_order = (
            self.aisle_config.aisle_order
            if self.aisle_config
            else DEFAULT_AISLE_ORDER
        )
        aisle_positions = {aisle: i for i, aisle in enumerate(aisle_order)}

        for item in items:
            aisle = self._find_aisle(item.name)
            order = aisle_positions.get(aisle, 999)

            # Check if item is checked based on status
            from src.api.app.domain.shopping.models import ShoppingItemStatus
            is_checked = item.status == ShoppingItemStatus.CHECKED

            sorted_item = SortedShoppingItem(
                item_id=item.id,
                name=item.name,
                quantity=item.quantity,
                unit=item.unit,
                aisle=aisle,
                aisle_order=order,
                is_checked=is_checked,
            )

            if aisle == "Unknown":
                unknown_items.append(sorted_item)
            else:
                sorted_items.append(sorted_item)

        # Sort by aisle order
        sorted_items.sort(key=lambda x: (x.aisle_order, x.name.lower()))

        return SortedShoppingList(
            list_id=list_id,
            store_id=store_id,
            items=sorted_items,
            unknown_items=unknown_items,
        )

    def _find_aisle(self, item_name: str) -> str:
        """Find the aisle for an item.

        Checks store-specific mappings first, then falls back
        to default mappings.

        Args:
            item_name: The item to look up.

        Returns:
            Aisle name or "Unknown".
        """
        name_lower = item_name.lower()

        # Check store-specific mappings first
        if name_lower in self._mapping_lookup:
            return self._mapping_lookup[name_lower]

        # Check default mappings (partial match)
        for keyword, aisle in DEFAULT_AISLE_MAP.items():
            if keyword in name_lower:
                return aisle

        return "Unknown"

    def get_aisle_summary(
        self,
        sorted_list: SortedShoppingList,
    ) -> dict[str, int]:
        """Get item counts per aisle.

        Args:
            sorted_list: A sorted shopping list.

        Returns:
            Dict of aisle -> item count.
        """
        summary: dict[str, int] = {}
        for item in sorted_list.items:
            summary[item.aisle] = summary.get(item.aisle, 0) + 1
        if sorted_list.unknown_items:
            summary["Unknown"] = len(sorted_list.unknown_items)
        return summary
