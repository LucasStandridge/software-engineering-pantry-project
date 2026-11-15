"""Inventory API Endpoints."""

from flask import Blueprint, jsonify

from backend.extensions import db
from backend.models import InventoryItem

inventory_bp = Blueprint(
    "inventory",
    __name__,
    url_prefix="/api/inventory",
)

@inventory_bp.get("")
def list_inventory():
    """Retrieve all inventory items from the database."""
    items = db.session.execute(
        db.select(InventoryItem).order_by(InventoryItem.item_id)
    ).scalars().all()

    return jsonify(
        items=[serialize_inventory_item(item) for item in items]
    ), 200

@inventory_bp.get("/<int:item_id>")
def get_inventory_item(item_id):
    """Retrieve a single inventory item by ID."""
    item = db.session.get(InventoryItem, item_id)

    if item is None:
        return jsonify(
            error={
                "code": "not_found",
                "message": "Inventory item not found",
            }
        ), 404

    return jsonify(item=serialize_inventory_item(item)), 200

def serialize_inventory_item(item):
    """Convert an InventoryItem model into a JSON-compatible dictionary."""
    return {
        "item_id": item.item_id,
        "name": item.name,
        "quantity": float(item.quantity),
        "unit": item.unit,
        "storage_location": item.storage_location,
        "expiration_date": (
            item.expiration_date.isoformat()
            if item.expiration_date else None
        ),
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
    }