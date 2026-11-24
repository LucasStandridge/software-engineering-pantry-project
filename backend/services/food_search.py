"""Search USDA FoodData Central for selectable food items."""
import os
import requests

from backend.foodData import BASE


def search_foods(query: str, limit: int = 10) -> list[dict]:
    """Search USDA and return simplified food matches."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query must be a nonempty string")

    if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 25:
        raise ValueError("Search limit must be between 1 and 25")

    api_key = os.environ.get("USDA_API_KEY")

    if not api_key:
        raise RuntimeError("USDA API key is not configured")

    response = requests.get(
        f"{BASE}/foods/search",
        params={
            "api_key": api_key,
            "query": query.strip(),
            "pageSize": limit,
        },
        timeout=10,
    )

    response.raise_for_status()

    foods = response.json().get("foods", [])

    return [
        {
            "fdc_id": food["fdcId"],
            "description": food["description"],
            "brand": food.get("brandOwner"),
        }
        for food in foods
    ]