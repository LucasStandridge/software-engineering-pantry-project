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

def inventory_error(message):
    """Return a consistent inventory validation error."""
    return jsonify(error={
        "code": "bad_request",
        "message": message,
    }), 400

def validate_inventory_data(data, partial=False):
    """Validate and normalize inventory creation or update data."""
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    required_fields = ("name", "quantity", "unit", "storage_location")
    allowed_fields = set(required_fields) | {"expiration_date"}

    if not partial:
        for field in required_fields:
            if field not in data:
                return None, f"Missing required field: {field}"

    if not data:
        return None, "Request body must contain inventory fields"

    unknown_fields = set(data) - allowed_fields
    if unknown_fields:
        return None, f"Unknown field: {sorted(unknown_fields)[0]}"

    cleaned = {}

    text_limits = {
        "name": 100,
        "unit": 20,
        "storage_location": 50,
    }

    for field, max_length in text_limits.items():
        if field not in data:
            continue

        value = data[field]

        if (
            not isinstance(value, str)
            or not value.strip()
            or len(value) > max_length
        ):
            return None, f"Invalid value for {field}"

        cleaned[field] = value.strip()

    if "quantity" in data:
        try:
            if isinstance(data["quantity"], bool):
                raise ValueError

            quantity = Decimal(str(data["quantity"]))

            if not quantity.is_finite() or quantity <= 0:
                raise ValueError

            if (
                quantity.as_tuple().exponent < -2
                or quantity >= Decimal("100000000")
            ):
                raise ValueError

        except (InvalidOperation, ValueError, TypeError):
            return None, (
                "Quantity must be a positive number "
                "with at most two decimal places"
            )

        cleaned["quantity"] = quantity

    if "expiration_date" in data:
        value = data["expiration_date"]

        if value is None:
            cleaned["expiration_date"] = None
        else:
            if not isinstance(value, str) or not re.fullmatch(
                r"\d{4}-\d{2}-\d{2}", value
            ):
                return None, "Expiration date must use YYYY-MM-DD format"

            try:
                cleaned["expiration_date"] = date.fromisoformat(value)
            except ValueError:
                return None, "Expiration date must use YYYY-MM-DD format"

    return cleaned, None

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

    cleaned, error = validate_inventory_data(data)

    if error:
        return inventory_error(error)

    item = InventoryItem(**cleaned)

    try:
        db.session.add(item)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise

    return jsonify(item=serialize_inventory_item(item)), 201

@inventory_bp.patch("/<int:item_id>")
def update_inventory_item(item_id):
    """Update selected fields of an existing inventory item."""
    item = db.session.get(InventoryItem, item_id)

    if item is None:
        return jsonify(error={
            "code": "not_found",
            "message": "Inventory item not found",
        }), 404

    data = request.get_json(silent=True)

    cleaned, error = validate_inventory_data(data, partial=True)

    if error:
        return inventory_error(error)

    # Modify only the fields provided in the request.
    for field, value in cleaned.items():
        setattr(item, field, value)

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise

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