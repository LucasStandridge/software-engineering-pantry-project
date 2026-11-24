# Backend API Reference

PantryPlanner's Flask API provides grocery-list management, USDA food search, and (in pending PRs) persistent inventory and expiration tracking. This reference describes the implemented contracts for frontend integration.

## 1. API Overview

**Base path:** `/api`. Responses are JSON except `204 No Content` responses.

| Feature | Availability | Storage |
| --- | --- | --- |
| Grocery list | On `master` | In-memory; resets when the app restarts |
| USDA search | On `master` | USDA FoodData Central (external service) |
| Inventory CRUD | Pending PR #35 | SQLAlchemy database |
| Expiration summary | Pending PR #38 (depends on #35) | Computed from inventory records |

The grocery list and inventory are separate. Checking off a grocery item does **not** currently transfer it to inventory. Authentication and per-user inventory isolation are not included in PR #35.

## 2. Grocery List API

Grocery items use **string UUIDs**. They are stored in memory and are not the same records as inventory items.

| Method | Endpoint | Behavior | Success |
| --- | --- | --- | --- |
| `GET` | `/api/items` | List items as `{"items": [...]}`; empty list if none | 200 |
| `POST` | `/api/items` | Add item; increment quantity if name matches an existing item | 201 new / 200 duplicate |
| `POST` | `/api/items/{item_id}/increment` | Increase quantity by 1; returns `{"quantity": n}` | 200 |
| `POST` | `/api/items/{item_id}/decrement` | Decrease by 1; if quantity is 1, remove and return `{"quantity": 0}` | 200 |
| `POST` | `/api/items/{item_id}/toggle-checked` | Flip checked state; returns `{"checked_off": true/false}` | 200 |
| `DELETE` | `/api/items/{item_id}/delete` | Remove item at any quantity; empty response body | 204 |

The four item-specific mutation endpoints return `404 {"error": "Item not found"}` for an unknown UUID.

### Create an item

`POST /api/items` accepts a JSON object with a required `name` and optional `data`:

```json
{
  "name": "Whole Milk",
  "data": {
    "fdc_id": 123456,
    "description": "Whole Milk",
    "brand": "Example Brand"
  }
}
```

- `name`: nonempty text, maximum **100 characters before whitespace normalization**. Whitespace is collapsed; duplicate matching is case-insensitive.
- If `data` is omitted, it defaults to the supplied name string. If `data` is an object, it must contain a **positive integer** `fdc_id`.
- Matching names increment the existing item's quantity, even if product data or package sizes differ.
- Invalid requests return `400 {"error": "..."}`.

New-item response (`201`; illustrative UUID and product data):

```json
{
  "created": true,
  "item": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Whole Milk",
    "quantity": 1,
    "checked_off": false,
    "data": {"fdc_id": 123456, "description": "Whole Milk", "brand": "Example Brand"}
  }
}
```

On a duplicate, the response has the same shape with `"created": false` and the incremented quantity (`200`). `GET /api/items` returns these item objects in an `items` array. The `data` field is retained from creation; `insertion_order` is not included in responses.

## 3. USDA Food Search API

**`GET /api/foods/search?q=milk`** searches USDA FoodData Central. The required `q` parameter must not be blank (whitespace is trimmed). The HTTP endpoint returns at most **10** results; it does not expose the service function's optional limit argument.

Successful response (`200`; illustrative values):

```json
{
  "foods": [
    {"fdc_id": 123456, "description": "Whole Milk", "brand": "Example Brand"}
  ]
}
```

`foods` is `[]` if no matches are found. Each result contains an integer `fdc_id`, a description, and a brand name or `null`. The frontend may pass a selected result as the `data` object in `POST /api/items`.

| Error | Response |
| --- | --- |
| Missing/blank `q` (400) | `{"error":{"code":"bad_request","message":"Search query cannot be empty"}}` |
| USDA request failure (503) | `{"error":{"code":"service_unavailable","message":"USDA food search is temporarily unavailable"}}` |
| Missing server API key (503) | `{"error":{"code":"service_unavailable","message":"Food search is not configured"}}` |

**Configuration:** Set `USDA_API_KEY` on the backend; do not expose it in frontend code. USDA results do not include inventory quantity, unit, storage location, or expiration date.

## 4. Inventory API — Pending PR #35

Inventory records are persisted through SQLAlchemy and use **integer `item_id` values**, not grocery-list UUIDs. These endpoints are **not yet on `master`**.

| Method | Endpoint | Behavior | Success |
| --- | --- | --- | --- |
| `GET` | `/api/inventory` | List items ordered by `item_id` as `{"items": [...]}` | 200 |
| `GET` | `/api/inventory/{item_id}` | Return `{"item": {...}}` | 200 |
| `POST` | `/api/inventory` | Create and persist an item; return `{"item": {...}}` | 201 |
| `PATCH` | `/api/inventory/{item_id}` | Update only provided fields; return `{"item": {...}}` | 200 |
| `DELETE` | `/api/inventory/{item_id}` | Delete item; empty response body | 204 |

Unknown inventory IDs return `404` with `{"error":{"code":"not_found","message":"Inventory item not found"}}`.

### Create and update payloads

Example creation request (`POST /api/inventory`):

```json
{
  "name": "Milk",
  "quantity": 2,
  "unit": "liters",
  "storage_location": "refrigerator",
  "expiration_date": "2026-12-01"
}
```

| Field | Required on POST | Validation |
| --- | --- | --- |
| `name` | Yes | Nonblank string, max 100 characters |
| `quantity` | Yes | Positive number below 100,000,000; at most 2 decimal places; not boolean |
| `unit` | Yes | Nonblank string, max 20 characters |
| `storage_location` | Yes | Nonblank string, max 50 characters |
| `expiration_date` | No | Valid `YYYY-MM-DD` string or `null` |

Text fields are trimmed. Unknown fields, invalid values, missing required POST fields, and empty PATCH objects produce `400` errors. A PATCH may supply any nonempty subset of allowed fields. For example, `{"quantity": 1.5}` changes only quantity; `{"expiration_date": null}` clears the date.

### Inventory response shape

`GET /api/inventory/{item_id}`, POST, and PATCH wrap the record in `{"item": ...}`. The list endpoint wraps records in `{"items": [...]}`. Example record (illustrative ID and timestamps):

```json
{
  "item_id": 1,
  "name": "Milk",
  "quantity": 2.0,
  "unit": "liters",
  "storage_location": "refrigerator",
  "expiration_date": "2026-12-01",
  "created_at": "2026-11-21T10:00:00",
  "updated_at": "2026-11-21T10:00:00"
}
```

`expiration_date` may be `null`. Timestamps are ISO-formatted strings. There is currently no automatic grocery-list-to-inventory transfer; frontend integration must supply all required inventory fields. Per-user ownership is separate work.

## 5. Expiration Tracking — Pending PR #38

**`GET /api/inventory/expiration-summary`** returns a status count and all inventory records with an added `expiration_status` field. No request body or query parameters are required. Depends on PR #35 and is **not on `master`**.

Example response (`200`; illustrative items, assuming November 21, 2026):

```json
{
  "total": 2,
  "counts": {"expired": 0, "expiring_soon": 1, "fresh": 1, "unknown": 0},
  "items": [
    {
      "item_id": 1, "name": "Milk", "quantity": 2.0, "unit": "liters",
      "storage_location": "refrigerator", "expiration_date": "2026-11-23",
      "created_at": "2026-11-21T10:00:00", "updated_at": "2026-11-21T10:00:00",
      "expiration_status": "expiring_soon"
    },
    {
      "item_id": 2, "name": "Rice", "quantity": 1.0, "unit": "bags",
      "storage_location": "pantry", "expiration_date": "2027-05-01",
      "created_at": "2026-11-21T10:00:00", "updated_at": "2026-11-21T10:00:00",
      "expiration_status": "fresh"
    }
  ]
}
```

| Status | Rule relative to backend server's current date |
| --- | --- |
| `expired` | Date before today |
| `expiring_soon` | Today through 3 days from today, inclusive |
| `fresh` | More than 3 days away |
| `unknown` | No expiration date |

`total` counts all items; `counts` totals by category. Statuses are calculated on request, not stored as a field. The API's warning window is fixed at 3 days, and this endpoint does **not** send notifications.

## 6. Error Responses

Global Flask handlers provide the following format when a route does not return its own error:

```json
{"error": {"code": "NOT_FOUND", "message": "The requested resource was not found."}}
```

| HTTP status | Global code | Global message |
| --- | --- | --- |
| 400 | `BAD_REQUEST` | The request is invalid. |
| 404 | `NOT_FOUND` | The requested resource was not found. |
| 405 | `METHOD_NOT_ALLOWED` | The HTTP method is not allowed. |
| 500 | `INTERNAL_SERVER_ERROR` | An internal server error occurred. |

Endpoint-specific errors differ:

- **Grocery list:** `{"error":"Item not found"}` for missing item IDs, and simple string errors for invalid creation requests.
- **Inventory (PR #35):** `{"error":{"code":"bad_request","message":"Missing required field: quantity"}}` (example); missing item uses lowercase `not_found`.
- **USDA:** structured lowercase `bad_request` or `service_unavailable` (see section 3).

Frontend code should inspect HTTP status and handle `error` as either a string or an object containing `code` and `message`. Do not parse `204 No Content` responses as JSON. Error-code capitalization is currently inconsistent; this reference records existing behavior rather than proposing changes.