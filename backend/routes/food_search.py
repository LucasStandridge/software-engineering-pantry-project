"""HTTP endpoints for searching USDA food data."""

import requests
from flask import Blueprint, jsonify, request

from backend.services.food_search import search_foods


food_search_bp = Blueprint(
    "food_search",
    __name__,
    url_prefix="/api/foods",
)

@food_search_bp.get("/search")
def search_foods_route():
    """Return matching food entries from USDA FoodData Central."""
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify(error={
            "code": "bad_request",
            "message": "Search query cannot be empty",
        }), 400

    try:
        foods = search_foods(query)
    except requests.RequestException:
        return jsonify(error={
            "code": "service_unavailable",
            "message": "USDA food search is temporarily unavailable",
        }), 503
    except RuntimeError:
        return jsonify(error={
            "code": "service_unavailable",
            "message": "Food search is not configured",
        }), 503

    return jsonify(foods=foods), 200
