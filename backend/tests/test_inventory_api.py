"""Tests for inventory REST API endpoints."""

from decimal import Decimal

import pytest

from backend.app import create_app
from backend.extensions import db
from backend.models import InventoryItem


@pytest.fixture
def client(tmp_path):
    """Create a test client with an isolated SQLite database."""
    test_db = tmp_path / "inventory_api.db"

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{test_db}",
    })

    with app.app_context():
        db.create_all()

        yield app.test_client()

        db.session.remove()
        db.drop_all()

def test_list_inventory_empty(client):
    """Verify an empty inventory returns an empty list."""
    response = client.get("/api/inventory")

    assert response.status_code == 200
    assert response.get_json() == {"items": []}

def test_list_inventory_returns_saved_items(client):
    """Verify inventory records are retrieved from the database."""
    with client.application.app_context():
        item = InventoryItem(
            name="Milk",
            quantity=Decimal("2.00"),
            unit="liters",
            storage_location="refrigerator",
        )

        db.session.add(item)
        db.session.commit()

    response = client.get("/api/inventory")

    assert response.status_code == 200

    data = response.get_json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Milk"
    assert data["items"][0]["quantity"] == 2.0
    assert data["items"][0]["unit"] == "liters"
    assert data["items"][0]["storage_location"] == "refrigerator"

def test_get_inventory_item(client):
    """Verify a single inventory item can be retrieved by ID."""
    with client.application.app_context():
        item = InventoryItem(
            name="Eggs",
            quantity=Decimal("12.00"),
            unit="pieces",
            storage_location="refrigerator",
        )

        db.session.add(item)
        db.session.commit()
        item_id = item.item_id

    response = client.get(f"/api/inventory/{item_id}")

    assert response.status_code == 200

    data = response.get_json()
    assert data["item"]["item_id"] == item_id
    assert data["item"]["name"] == "Eggs"
    assert data["item"]["quantity"] == 12.0


def test_get_inventory_item_not_found(client):
    """Verify requesting a nonexistent inventory item returns 404."""
    response = client.get("/api/inventory/999999")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": {
            "code": "not_found",
            "message": "Inventory item not found",
        }
    }