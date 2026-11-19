"""Tests for the inventory expiration summary API."""

import pytest

from backend.app import create_app
from backend.extensions import db
from datetime import date, timedelta
from backend.models import InventoryItem


@pytest.fixture
def client():
    """Create an isolated application with an empty inventory database."""
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_expiration_summary_empty_inventory(client):
    """An empty inventory should return zero counts."""
    response = client.get("/api/inventory/expiration-summary")

    assert response.status_code == 200
    assert response.get_json() == {
        "total": 0,
        "counts": {
            "expired": 0,
            "expiring_soon": 0,
            "fresh": 0,
            "unknown": 0,
        },
        "items": [],
    }

def test_expiration_summary_classifies_stored_items(client):
    """Verify the endpoint summarizes actual database records."""
    today = date.today()

    records = [
        ("Expired Milk", today - timedelta(days=1)),
        ("Expiring Eggs", today + timedelta(days=2)),
        ("Fresh Bread", today + timedelta(days=10)),
        ("Unknown Rice", None),
    ]

    for name, expiration_date in records:
        item = InventoryItem(
            name=name,
            quantity=1,
            unit="item",
            storage_location="Pantry",
            expiration_date=expiration_date,
        )

        with client.application.app_context():
            db.session.add(item)
            db.session.commit()

    response = client.get("/api/inventory/expiration-summary")

    assert response.status_code == 200

    result = response.get_json()

    assert result["total"] == 4
    assert result["counts"] == {
        "expired": 1,
        "expiring_soon": 1,
        "fresh": 1,
        "unknown": 1,
    }

    statuses = {
        item["name"]: item["expiration_status"]
        for item in result["items"]
    }

    assert statuses == {
        "Expired Milk": "expired",
        "Expiring Eggs": "expiring_soon",
        "Fresh Bread": "fresh",
        "Unknown Rice": "unknown",
    }

def test_expiration_summary_warning_boundary(client):
    """Items expiring in 3 days are warnings; 4 days are fresh."""
    today = date.today()

    with client.application.app_context():
        db.session.add_all([
            InventoryItem(
                name="Three Day Item",
                quantity=1,
                unit="item",
                storage_location="Pantry",
                expiration_date=today + timedelta(days=3),
            ),
            InventoryItem(
                name="Four Day Item",
                quantity=1,
                unit="item",
                storage_location="Pantry",
                expiration_date=today + timedelta(days=4),
            ),
        ])
        db.session.commit()

    response = client.get("/api/inventory/expiration-summary")

    assert response.status_code == 200

    result = response.get_json()

    assert result["counts"]["expiring_soon"] == 1
    assert result["counts"]["fresh"] == 1