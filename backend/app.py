from flask import Flask, jsonify
from backend.config import Config
from backend.extensions import db, migrate

def create_app(test_config = None):
    """Create and configure the application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Register the db models for SQLAlchemy and migrations
    from backend import models

    @app.route("/api/health")
    def health():
        return jsonify(status="ok")

    return app

app = create_app()