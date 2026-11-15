"""Tests for the USDA food search API endpoint."""

from unittest.mock import patch

import pytest
import requests

from backend.app import create_app


@pytest.fixture
def client():
    """Create a Flask test client."""
    app = create_app({"TESTING": True})
    return app.test_client()


@patch("backend.routes.food_search.search_foods")
def test_search_foods_endpoint_returns_matches(mock_search, client):
    """Verify the API returns matching USDA food entries."""
    mock_search.return_value = [
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

    response = client.get("/api/foods/search?q=milk")

    assert response.status_code == 200
    assert response.get_json() == {
        "foods": mock_search.return_value
    }

    mock_search.assert_called_once_with("milk")

@pytest.mark.parametrize("url", [
    "/api/foods/search",
    "/api/foods/search?q=",
    "/api/foods/search?q=%20%20%20",
])
def test_search_foods_rejects_empty_query(client, url):
    """Verify empty search queries return HTTP 400."""
    response = client.get(url)

    assert response.status_code == 400
    assert response.get_json() == {
        "error": {
            "code": "bad_request",
            "message": "Search query cannot be empty",
        }
    }


@patch("backend.routes.food_search.search_foods")
def test_search_foods_endpoint_returns_empty_results(mock_search, client):
    """Verify searches with no matches return an empty list."""
    mock_search.return_value = []

    response = client.get("/api/foods/search?q=unknown")

    assert response.status_code == 200
    assert response.get_json() == {"foods": []}


@patch("backend.routes.food_search.search_foods")
def test_search_foods_handles_network_failure(mock_search, client):
    """Verify USDA network failures return HTTP 503."""
    mock_search.side_effect = requests.Timeout("Request timed out")

    response = client.get("/api/foods/search?q=milk")

    assert response.status_code == 503
    assert response.get_json() == {
        "error": {
            "code": "service_unavailable",
            "message": "USDA food search is temporarily unavailable",
        }
    }


@patch("backend.routes.food_search.search_foods")
def test_search_foods_handles_missing_configuration(mock_search, client):
    """Verify missing USDA configuration returns HTTP 503."""
    mock_search.side_effect = RuntimeError("USDA API key is not configured")

    response = client.get("/api/foods/search?q=milk")

    assert response.status_code == 503
    assert response.get_json() == {
        "error": {
            "code": "service_unavailable",
            "message": "Food search is not configured",
        }
    }