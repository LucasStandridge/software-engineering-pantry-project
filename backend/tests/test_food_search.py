"""Tests for USDA food search integration."""
import pytest
import requests

from unittest.mock import patch
from backend.services.food_search import search_foods


@patch.dict("os.environ", {"USDA_API_KEY": "test-key"})
@patch("backend.services.food_search.requests.get")
def test_search_foods_returns_multiple_matches(mock_get):
    """Verify search returns selectable USDA food matches."""

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "foods": [
            {
                "fdcId": 123456,
                "description": "Whole Milk",
                "brandOwner": None,
            },
            {
                "fdcId": 789012,
                "description": "Reduced Fat Milk",
                "brandOwner": "Example Dairy",
            },
        ]
    }

    results = search_foods("milk")

    assert results == [
        {
            "fdc_id": 123456,
            "description": "Whole Milk",
            "brand": None,
        },
        {
            "fdc_id": 789012,
            "description": "Reduced Fat Milk",
            "brand": "Example Dairy",
        },
    ]

@pytest.mark.parametrize(
    "query",
    ["", "   ", None, 123],
)
def test_search_foods_rejects_invalid_queries(query):
    """Verify empty or invalid search queries are rejected."""
    with pytest.raises(ValueError):
        search_foods(query)


@pytest.mark.parametrize("limit", [0, -1, 26, 1.5, True])
def test_search_foods_rejects_invalid_limits(limit):
    """Verify search limits must be valid integers."""
    with pytest.raises(ValueError):
        search_foods("milk", limit=limit)


@patch.dict("os.environ", {}, clear=True)
def test_search_foods_requires_api_key():
    """Verify missing API configuration is handled."""
    with pytest.raises(RuntimeError, match="USDA API key"):
        search_foods("milk")


@patch.dict("os.environ", {"USDA_API_KEY": "test-key"})
@patch("backend.services.food_search.requests.get")
def test_search_foods_handles_empty_results(mock_get):
    """Verify searches without matches return an empty list."""
    mock_get.return_value.json.return_value = {"foods": []}

    assert search_foods("unknown food") == []


@patch.dict("os.environ", {"USDA_API_KEY": "test-key"})
@patch("backend.services.food_search.requests.get")
def test_search_foods_propagates_network_errors(mock_get):
    """Verify network failures are not mistaken for empty results."""
    mock_get.side_effect = requests.Timeout("Request timed out")

    with pytest.raises(requests.Timeout):
        search_foods("milk")

@patch.dict("os.environ", {"USDA_API_KEY": "test-key"})
@patch("backend.services.food_search.requests.get")
def test_search_foods_uses_correct_request_parameters(mock_get):
    """Verify USDA search requests use the expected parameters."""
    mock_get.return_value.json.return_value = {"foods": []}

    search_foods("  milk  ", limit=5)

    mock_get.assert_called_once_with(
        "https://api.nal.usda.gov/fdc/v1/foods/search",
        params={
            "api_key": "test-key",
            "query": "milk",
            "pageSize": 5,
        },
        timeout=10,
    )