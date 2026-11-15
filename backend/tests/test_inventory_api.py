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

def test_create_inventory_item(client):
    """Verify POST creates an inventory record in the database."""
    payload = {
        "name": "Milk",
        "quantity": 2.0,
        "unit": "liters",
        "storage_location": "refrigerator",
        "expiration_date": "2026-12-01",
    }

    response = client.post("/api/inventory", json=payload)

    assert response.status_code == 201

    data = response.get_json()
    assert data["item"]["name"] == "Milk"
    assert data["item"]["quantity"] == 2.0
    assert data["item"]["expiration_date"] == "2026-12-01"

    item_id = data["item"]["item_id"]

    # Verify the record was actually persisted.
    with client.application.app_context():
        saved_item = db.session.get(InventoryItem, item_id)

        assert saved_item is not None
        assert saved_item.name == "Milk"
        assert saved_item.quantity == Decimal("2.00")

@pytest.mark.parametrize(
    "invalid_payload",
    [
        {},  # Missing all required fields
        {"name": "Milk"},  # Missing quantity, unit, and location
        {
            "name": "",
            "quantity": 2,
            "unit": "liters",
            "storage_location": "refrigerator",
        },
        {
            "name": "Milk",
            "quantity": 0,
            "unit": "liters",
            "storage_location": "refrigerator",
        },
        {
            "name": "Milk",
            "quantity": -1,
            "unit": "liters",
            "storage_location": "refrigerator",
        },
        {
            "name": "Milk",
            "quantity": "invalid",
            "unit": "liters",
            "storage_location": "refrigerator",
        },
        {
            "name": "Milk",
            "quantity": 2,
            "unit": "liters",
            "storage_location": "refrigerator",
            "expiration_date": "not-a-date",
        },
    ],
)
def test_create_inventory_item_invalid_payload(client, invalid_payload):
    """Verify invalid inventory data is rejected."""
    response = client.post("/api/inventory", json=invalid_payload)

    assert response.status_code == 400

    data = response.get_json()
    assert "error" in data
    assert data["error"]["code"] == "bad_request"

    # Invalid requests must not create database records.
    with client.application.app_context():
        assert db.session.query(InventoryItem).count() == 0

@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("name", "A" * 101),
        ("unit", "A" * 21),
        ("storage_location", "A" * 51),
        ("quantity", 1.234),
        ("quantity", 100000000),
        ("quantity", True),
        ("quantity", None),
        ("expiration_date", "2026-02-30"),
        ("expiration_date", "20261201"),
    ],
)
def test_create_inventory_item_invalid_boundaries(client, field, invalid_value):
    """Verify inventory fields respect model constraints."""
    payload = {
        "name": "Milk",
        "quantity": 2,
        "unit": "liters",
        "storage_location": "refrigerator",
    }

    payload[field] = invalid_value

    response = client.post("/api/inventory", json=payload)

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "bad_request"

    with client.application.app_context():
        assert db.session.query(InventoryItem).count() == 0