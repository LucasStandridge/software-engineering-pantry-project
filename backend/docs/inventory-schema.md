# PantryPlanner Inventory Database Schema

## Overview

The initial database design for PantryPlanner focuses on storing and managing household grocery inventory.
The schema is intended to support basic inventory operations, including adding, viewing, updating, and removing
grocery items, while also tracking quantities, storage locations, and expiration dates.

For the initial minimum viable product, we will use a relational database with a single ```inventory_items``` table.
As development progresses, the database can be expanded to support additional functionality without
introducing unnecessary complexity into the initial implementation.

## Initial Inventory Table

### **Table:** inventory_items

| Field | Data Type | Constraints | Description |
|---|---|---|---|
| `item_id` | INTEGER | Primary Key | Unique identifier for each inventory record |
| `name` | VARCHAR(100) | NOT NULL | Name of the grocery item |
| `quantity` | DECIMAL(10,2) | NOT NULL, > 0 | Quantity of the item |
| `unit` | VARCHAR(20) | NOT NULL | Measurement unit |
| `storage_location` | VARCHAR(50) | NOT NULL | Pantry, refrigerator, or freezer |
| `expiration_date` | DATE | Optional | Expiration date |
| `created_at` | DATETIME | NOT NULL | Record creation timestamp |
| `updated_at` | DATETIME | NOT NULL | Last modification timestamp |


## Proposed SQL Schema

```sql
CREATE TABLE inventory_items (
    item_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    quantity DECIMAL(10,2) NOT NULL CHECK (quantity > 0),
    unit VARCHAR(20) NOT NULL,
    storage_location VARCHAR(50) NOT NULL,
    expiration_date DATE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
)
```
The SQL above is a proposed initial schema. Application-level validation will be necessary to enforce valid quantities,
measurement units, and date formats.

The updated_at field will need to be updated whenever an existing inventory record is modified.

## Design Considerations

### Quantity and Measurement Units

Quantities are represented using decimal values with a separate measurement unit.
This allows the application to support entries such as 1.5 liters of milk or 2.25 pounds of flour.

Units should eventually be standardized to prevent inconsistent representations of the same measurement.

### Multiple Inventory Records

The database allows multiple records for the same grocery product.

For example, two cartons of milk with different expiration dates can be stored independently. Each record has its own identifier,
quantity, and expiration date.

This approach allows expiration tracking and inventory updates to operate on individual batches rather than combining all quantities of a product.

### Storage Locations

Storage locations are initially represented as text values, such as pantry, refrigerator, or freezer.

Future versions may introduce storage locations table if more detailed location management becomes necessary.

## Future Database Expansion

As PantryPlanner develops, the relational model may be expanded to include additional tables.

| Table | Purpose |
|---|---|
| `products` | Store shared product information, categories, and barcodes |
| `households` | Associate inventory records with households |
| `users` | Support authentication and user accounts |
| `storage_locations` | Manage household-specific storage areas |
| `inventory_history` | Track inventory changes, consumption, and waste |

**Future relationship could include:**

- One household having multiple inventory records.
- One product appearing in multiple inventory records
- Multiple users belonging to the same household.

These additions will be evaluated as their corresponding application features are developed.

## Implementation Notes

The initial database implementation is expected to use SQLite with Flask and SQLAlechemy, pending confirmation from the dev team.

The implementation should include input validation, database constraints, and tests for creating and managing inventory records.

Database schema changes should be managed through migrations as the application evolves.

## Scope

This document defines the proposed database structure for the initial PantryPlanner mvp. Actual database creation,
integration with Flask, and inventory API implementation will be handles as separate development tasks
