from uuid import UUID
TEST_USER_ID = "00000000-0000-0000-0000-000000000001"
TEST_CATEGORY = "Dairy"

"""Tests for inventory REST API endpoints."""

from decimal import Decimal
from datetime import date
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
            category="Dairy",
            user_id=UUID("00000000-0000-0000-0000-000000000001")
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
            category="Dairy",
            user_id=UUID("00000000-0000-0000-0000-000000000001")
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
        "category": "Dairy",
        "expiration_date": "2026-12-01",
        "user_id": "00000000-0000-0000-0000-000000000001",

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

def test_update_inventory_item(client):
    """Verify PATCH updates only the requested fields."""
    with client.application.app_context():
        item = InventoryItem(
            name="Milk",
            quantity=Decimal("2.00"),
            unit="liters",
            storage_location="refrigerator",
            category="Dairy",
            user_id=UUID("00000000-0000-0000-0000-000000000001")
        )

        db.session.add(item)
        db.session.commit()
        item_id = item.item_id

    response = client.patch(
        f"/api/inventory/{item_id}",
        json={
            "quantity": 1.5,
            "storage_location": "freezer",
        },
    )

    assert response.status_code == 200

    data = response.get_json()["item"]

    assert data["item_id"] == item_id
    assert data["name"] == "Milk"
    assert data["quantity"] == 1.5
    assert data["unit"] == "liters"
    assert data["storage_location"] == "freezer"

    # Verify changes persisted to the database.
    with client.application.app_context():
        db.session.remove()
        updated_item = db.session.get(InventoryItem, item_id)

        assert updated_item.quantity == Decimal("1.50")
        assert updated_item.storage_location == "freezer"
        assert updated_item.name == "Milk"

def test_update_inventory_item_clear_expiration(client):
    """Verify PATCH can clear an existing expiration date."""
    with client.application.app_context():
        item = InventoryItem(
            name="Milk",
            quantity=Decimal("2.00"),
            unit="liters",
            storage_location="refrigerator",
            expiration_date=date(2026, 12, 1),
            category="Dairy",
            user_id=UUID("00000000-0000-0000-0000-000000000001")
        )

        db.session.add(item)
        db.session.commit()
        item_id = item.item_id

    response = client.patch(
        f"/api/inventory/{item_id}",
        json={"expiration_date": None},
    )

    assert response.status_code == 200
    assert response.get_json()["item"]["expiration_date"] is None

    # Verify the change persists in the database.
    with client.application.app_context():
        db.session.remove()
        saved_item = db.session.get(InventoryItem, item_id)

        assert saved_item is not None
        assert saved_item.expiration_date is None

def test_update_inventory_item_not_found(client):
    """Verify PATCH returns 404 for a nonexistent item."""
    response = client.patch(
        "/api/inventory/999999",
        json={"quantity": 2},
    )

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "not_found"

@pytest.mark.parametrize(
    "invalid_payload",
    [
        {},
        {"quantity": 0},
        {"quantity": -1},
        {"quantity": 1.234},
        {"quantity": True},
        {"name": ""},
        {"storage_location": "A" * 51},
        {"expiration_date": "invalid-date"},
        {"item_id": 999},
        {"created_at": "2026-01-01"},
    ],
)
def test_update_inventory_item_invalid_payload(client, invalid_payload):
    """Verify invalid PATCH requests do not modify inventory records."""
    with client.application.app_context():
        item = InventoryItem(
            name="Milk",
            quantity=Decimal("2.00"),
            unit="liters",
            storage_location="refrigerator",
            category="Dairy",
            user_id=UUID("00000000-0000-0000-0000-000000000001")
        )

        db.session.add(item)
        db.session.commit()
        item_id = item.item_id

    response = client.patch(
        f"/api/inventory/{item_id}",
        json=invalid_payload,
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "bad_request"

    # Confirm the original record remains unchanged.
    with client.application.app_context():
        db.session.remove()
        saved_item = db.session.get(InventoryItem, item_id)

        assert saved_item is not None
        assert saved_item.name == "Milk"
        assert saved_item.quantity == Decimal("2.00")
        assert saved_item.storage_location == "refrigerator"

def test_delete_inventory_item(client):
    """Verify DELETE permanently removes an inventory item."""
    with client.application.app_context():
        item = InventoryItem(
            name="Milk",
            quantity=Decimal("2.00"),
            unit="liters",
            storage_location="refrigerator",
            category="Dairy",
            user_id=UUID("00000000-0000-0000-0000-000000000001")
        )

        db.session.add(item)
        db.session.commit()
        item_id = item.item_id

    response = client.delete(f"/api/inventory/{item_id}")

    assert response.status_code == 204
    assert response.data == b""

    # Verify the record was actually deleted.
    with client.application.app_context():
        db.session.remove()
        deleted_item = db.session.get(InventoryItem, item_id)

        assert deleted_item is None


def test_delete_inventory_item_not_found(client):
    """Verify DELETE returns 404 for a nonexistent item."""
    response = client.delete("/api/inventory/999999")

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "not_found"