import pytest
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from backend.app import create_app
from backend.extensions import db
from backend.models import InventoryItem

def test_create_inventory_item(tmp_path):
    """Verify an inventory item can be saved and retrieved."""

    test_db = tmp_path / "test_inventory.db"

    app = create_app({
        "TESTING": True,
        "SQLALCEHEMY_DATABASE_URI": f"sqlite:///{test_db}"
    })

    with app.app_context():
        db.create_all()

        item = InventoryItem(
            name="Milk",
            quantity=Decimal("1.5"),
            unit="liters",
            storage_location="refrigerator",
        )

        db.session.add(item)
        db.session.commit()

        saved_item = db.session.get(InventoryItem, item.item_id)

        assert saved_item is not None
        assert saved_item.name == "Milk"
        assert saved_item.quantity == Decimal("1.50")
        assert saved_item.storage_location == "refrigerator"
        assert saved_item.expiration_date is None
        assert saved_item.created_at is not None
        assert saved_item.updated_at is not None

        db.session.remove()
        db.drop_all()

def test_update_inventory_item(tmp_path):
    """Verify changes to an inventory item persist."""

    test_db = tmp_path / "test_update.db"

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{test_db}",
    })

    with app.app_context():
        db.create_all()

        item = InventoryItem(
            name="Milk",
            quantity=Decimal("2.00"),
            unit="liters",
            storage_location="refrigerator",
        )

        db.session.add(item)
        db.session.commit()

        item_id = item.item_id

        # Update the existing record.
        item.quantity = Decimal("1.25")
        db.session.commit()

        # Clear the session to force a fresh database retrieval.
        db.session.remove()

        updated_item = db.session.get(InventoryItem, item_id)

        assert updated_item is not None
        assert updated_item.quantity == Decimal("1.25")

        db.session.remove()
        db.drop_all()

def test_delete_inventory_item(tmp_path):
    """Verify an inventory item can be deleted."""

    test_db = tmp_path / "test_delete.db"

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{test_db}",
    })

    with app.app_context():
        db.create_all()

        item = InventoryItem(
            name="Eggs",
            quantity=Decimal("12.00"),
            unit="pieces",
            storage_location="refrigerator",
        )

        db.session.add(item)
        db.session.commit()

        item_id = item.item_id

        # Delete the inventory record.
        db.session.delete(item)
        db.session.commit()

        # Use a fresh session to verify database persistence.
        db.session.remove()

        deleted_item = db.session.get(InventoryItem, item_id)

        assert deleted_item is None

        db.session.remove()
        db.drop_all()

@pytest.mark.parametrize("invalid_quantity", [
    Decimal("0.00"),
    Decimal("-1.00"),
])
def test_reject_invalid_quantity(tmp_path, invalid_quantity):
    """Verify the database rejects zero and negative quantities."""

    test_db = tmp_path / "test_invalid_quantity.db"

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{test_db}",
    })

    with app.app_context():
        db.create_all()

        item = InventoryItem(
            name="Milk",
            quantity=invalid_quantity,
            unit="liters",
            storage_location="refrigerator",
        )

        db.session.add(item)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()
        db.session.remove()
        db.drop_all()

@pytest.mark.parametrize("missing_field", [
    "name",
    "quantity",
    "unit",
    "storage_location",
])
def test_reject_missing_required_fields(tmp_path, missing_field):
    """Verify required inventory fields cannot be NULL."""

    test_db = tmp_path / "test_required_fields.db"

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{test_db}",
    })

    with app.app_context():
        db.create_all()

        item_data = {
            "name": "Milk",
            "quantity": Decimal("1.00"),
            "unit": "liters",
            "storage_location": "refrigerator",
        }

        item_data[missing_field] = None

        item = InventoryItem(**item_data)
        db.session.add(item)

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()
        db.session.remove()
        db.drop_all()