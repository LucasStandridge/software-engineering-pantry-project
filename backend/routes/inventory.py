"""Inventory API Endpoints."""

from datetime import date
from decimal import Decimal, InvalidOperation
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint, jsonify, request

from backend.extensions import db
from backend.models import InventoryItem

import re

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

@inventory_bp.post("")
def create_inventory_item():
    """Create and persist a new inventory item."""
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error={
            "code": "bad_request",
            "message": "Request body must be a JSON object",
        }), 400

    required_fields = ("name", "quantity", "unit", "storage_location")

    for field in required_fields:
        if field not in data:
            return jsonify(error={
                "code": "bad_request",
                "message": f"Missing required field: {field}",
            }), 400

    # Validate text fields against the database model.
    text_limits = {
        "name": 100,
        "unit": 20,
        "storage_location": 50,
    }

    for field, max_length in text_limits.items():
        value = data[field]

        if (
            not isinstance(value, str)
            or not value.strip()
            or len(value) > max_length
        ):
            return jsonify(error={
                "code": "bad_request",
                "message": f"Invalid value for {field}",
            }), 400

    # Use Decimal to preserve numeric precision.
    try:
        if isinstance(data["quantity"], bool):
            raise ValueError

        quantity = Decimal(str(data["quantity"]))

        if not quantity.is_finite() or quantity <= 0:
            raise ValueError

        if quantity.as_tuple().exponent < -2 or quantity >= Decimal("100000000"):
            raise ValueError

    except (InvalidOperation, ValueError, TypeError):
        return jsonify(error={
            "code": "bad_request",
            "message": "Quantity must be a positive number with at most two decimal places",
        }), 400

    expiration_date = None

    if data.get("expiration_date") is not None:
        value = data["expiration_date"]

        if not isinstance(value, str) or not re.fullmatch(
                r"\d{4}-\d{2}-\d{2}", value
        ):
            return jsonify(error={
                "code": "bad_request",
                "message": "Expiration date must use YYYY-MM-DD format",
            }), 400

        try:
            expiration_date = date.fromisoformat(value)
        except ValueError:
            return jsonify(error={
                "code": "bad_request",
                "message": "Expiration date must use YYYY-MM-DD format",
            }), 400

    item = InventoryItem(
        name=data["name"].strip(),
        quantity=quantity,
        unit=data["unit"].strip(),
        storage_location=data["storage_location"].strip(),
        expiration_date=expiration_date,
    )

    try:
        db.session.add(item)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise

    return jsonify(item=serialize_inventory_item(item)), 201

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