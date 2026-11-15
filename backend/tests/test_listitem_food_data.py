"""Tests for structured USDA food data stored in ListItem and GroceryList."""

from backend.ListItem import ListItem
from backend.GroceryList import GroceryList


def test_listitem_returns_structured_food_data():
    """Verify ListItem exposes its stored USDA food information."""

    food_data = {
        "fdc_id": 123456,
        "canonical_name": "Whole Milk",
        "brand": None,
        "nutrition": {
            "calories": 61,
            "protein": 3.2,
        },
    }

    item = ListItem("Milk", food_data)

    result = item.read_information()

    assert result["name"] == "Milk"
    assert result["data"] == food_data
    assert result["data"]["fdc_id"] == 123456


def test_listitem_food_data_is_independent_snapshot():
    """Changing returned food data must not modify the stored data."""

    food_data = {
        "fdc_id": 123456,
        "canonical_name": "Whole Milk",
        "nutrition": {
            "calories": 61,
            "protein": 3.2,
        },
    }

    item = ListItem("Milk", food_data)

    result = item.read_information()

    result["data"]["nutrition"]["calories"] = 999

    assert item.data["nutrition"]["calories"] == 61


def test_grocerylist_accepts_structured_usda_food_data():
    """Verify GroceryList stores valid structured USDA data."""

    grocery_list = GroceryList()

    food_data = {
        "fdc_id": 123456,
        "canonical_name": "Whole Milk",
        "brand": None,
        "nutrition": {
            "calories": 61,
            "protein": 3.2,
        },
    }

    created, item_id = grocery_list.add_item("Milk", food_data)

    assert created is True

    item = grocery_list.read_item_by_id(item_id)

    assert item["data"] == food_data
    assert item["data"]["fdc_id"] == 123456
