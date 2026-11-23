"""Tests for Alembic database migrations."""

import pytest
from flask_migrate import upgrade, downgrade
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from backend.app import create_app
from backend.extensions import db


@pytest.fixture
def migration_app(tmp_path):
    """Configure an isolated SQLite database for migration tests."""
    test_db = tmp_path / "migration_test.db"

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{test_db}",
    })

    yield app


def test_initial_migration_creates_inventory_table(migration_app):
    """Verify Alembic creates the inventory table."""
    with migration_app.app_context():
        upgrade()

        inspector = inspect(db.engine)

        assert "inventory_items" in inspector.get_table_names()

        columns = {
            column["name"]: column
            for column in inspector.get_columns("inventory_items")
        }

        expected_columns = {
            "item_id",
            "name",
            "quantity",
            "unit",
            "storage_location",
            "expiration_date",
            "created_at",
            "updated_at",
        }

        assert set(columns) == expected_columns

        required_columns = {
            "item_id",
            "name",
            "quantity",
            "unit",
            "storage_location",
            "created_at",
            "updated_at",
        }

        for name in required_columns:
            assert columns[name]["nullable"] is False

        assert columns["expiration_date"]["nullable"] is True

def test_migration_downgrade_and_reapply(migration_app):
    """Verify migrations can be rolled back and reapplied."""
    with migration_app.app_context():
        upgrade()

        assert "inventory_items" in inspect(db.engine).get_table_names()

        downgrade(revision="base")

        assert "inventory_items" not in inspect(db.engine).get_table_names()

        upgrade()

        assert "inventory_items" in inspect(db.engine).get_table_names()

def test_migration_enforces_positive_quantity(migration_app):
    """Verify migrated inventory rejects nonpositive quantities."""
    with migration_app.app_context():
        upgrade()

        with pytest.raises(IntegrityError):
            with db.engine.begin() as connection:
                connection.execute(
                    text("""
                        INSERT INTO inventory_items
                        (name, quantity, unit, storage_location,
                         created_at, updated_at)
                        VALUES
                        ('Milk', 0, 'liters', 'refrigerator',
                         CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """)
                )

def test_migration_records_revision(migration_app):
    """Verify Alembic records the applied migration revision."""
    with migration_app.app_context():
        upgrade()

        with db.engine.connect() as connection:
            revision = connection.execute(
                text("SELECT version_num FROM alembic_version")
            ).scalar_one()

        assert revision == "b8f2b0f64084"
