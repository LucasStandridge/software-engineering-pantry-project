from flask import Flask, jsonify, request

from GroceryList import GroceryList

app = Flask(__name__)

# One list shared across all requests and stored in process memory
# Needs persistence and ability to create multiple lists in future sprints
# Resets whenever the server restarts
g_list = GroceryList()

# Guards against absurdly long input. The GroceryList does not limit length.
MAX_NAME_LENGTH = 100


@app.route("/api/health")
def health():
    return jsonify(status="ok")


@app.get("/api/items")
def list_items():
    """Returns all items in the grocery list inside of an object.
    This allows fields to be added later"""

    return jsonify(items=g_list.read_all_items())


@app.post("/api/items")
def create_item():
    """Passes name as data stub to add_item(). Which either adds an item or increments an existing quantity
    (see GrocerList for documentation)
    Returns 201 if the item is new and 200 if it was a dupe
    Takes JSON object with name string, returns {item = {...} on success and {error = ".."} on 400}
    JSON objects with name > 100 characters are rejected   
    Returns 400 on failure of providing a clean name (see GroceryList for documentation of clean_name())
    """

    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify(error="Request body must be a JSON object"), 400

    name = body.get("name")
    if not isinstance(name, str) or len(name) > MAX_NAME_LENGTH:
        return jsonify(
            error=f"'name' must be text of at most {MAX_NAME_LENGTH} characters"
        ), 400

    try:
        #TODO: Add actual data instead of the name (expiration time, food group, etc)
        created, item_id = g_list.add_item(name, name)
    except ValueError as err:
        return jsonify(error=str(err)), 400
    return (
        jsonify(item=g_list.read_item_by_id(item_id), created=created),
        (201 if created else 200),
    )

@app.post("/api/items/<item_id>/decrement")
def decrement_item_route(item_id):
    try:
        new_quantity = g_list.decrement_item(item_id)
    except KeyError: 
        return jsonify(error="Item not found"), 404
    return (jsonify( quantity=new_quantity), 200)

@app.post("/api/items/<item_id>/increment")
def increment_item_route(item_id):
    try:
        new_quantity = g_list.increment_item(item_id)
    except KeyError:
        return jsonify(error="Item not found"), 404
    return (jsonify(quantity = new_quantity), 200)

@app.post("/api/items/<item_id>/toggle-checked")
def toggle_item_checked_route(item_id):
    try:
        new_status = g_list.toggle_item(item_id)
    except KeyError:
        return jsonify(error = "Item not found"), 404
    return (jsonify(checked_off = new_status), 200)

@app.delete("/api/items/<item_id>/delete")
def remove_item_route(item_id):
    try:
        g_list.remove_item(item_id)
    except KeyError:
        return jsonify(error="Item not found"), 404
    return "", 204