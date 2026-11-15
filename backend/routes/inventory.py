"""Inventory API Endpoints."""

from flask import Blueprint, jsonify

inventory_bp = Blueprint(
    "inventory",
    __name__,
    url_prefix="/api/inventory",
)

@inventory_bp.get("")
def list_inventory():
    """Return inventory items."""
    return jsonify(items=[]), 200