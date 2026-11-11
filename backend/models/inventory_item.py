from datetime import datetime, timezone
from sqlalchemy import CheckConstraint
from backend.extensions import db

class InventoryItem(db.Model):
    __tablename__ = "inventory_items"

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_inventory_quantity_positive"),
    )

    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity= db.Column(db.Numeric(10, 2), nullable= False)
    unit = db.Column(db.String(20), nullable=False)
    storage_location = db.Column(db.String(50), nullable=False)
    expiration_date = db.Column(db.Date, nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )