import pytest
from flask import Flask, abort
from backend.errors import register_error_handlers
import logging

@pytest.fixture
def client():
    """Create an isolated Flask application for testing."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = False
    register_error_handlers(app)

    @app.route("/api/test-bad-request")
    def trigger_bad_request():
        abort(400)

    @app.route("/api/test-server-error")
    def trigger_server_error():
        raise RuntimeError("Simulated server failure")

    return app.test_client()


def test_not_found(client):
    """Verify that nonexistent endpoints return a JSON 404 error."""
    response = client.get("/api/nonexistent")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": {
            "code": "NOT_FOUND",
            "message": "The requested resource was not found."
        }
    }

def test_method_not_allowed(client):
    """Verify that unsupported HTTP methods return JSON 405."""
    response = client.post("/api/test-bad-request")

    assert response.status_code == 405
    assert response.get_json() == {
        "error": {
            "code": "METHOD_NOT_ALLOWED",
            "message": "The HTTP method is not allowed."
        }
    }


def test_internal_server_error(client):
    """Verify that unexpected exceptions return JSON 500."""
    response = client.get("/api/test-server-error")

    assert response.status_code == 500
    assert response.get_json() == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An internal server error occurred."
        }
    }

def test_bad_request(client):
    """Verify that invalid requests return a standardized JSON 400 error."""
    response = client.get("/api/test-bad-request")

    assert response.status_code == 400
    assert response.get_json() == {
        "error": {
            "code": "BAD_REQUEST",
            "message": "The request is invalid."
        }
    }

def test_internal_server_error_is_logged(client, caplog):
    """Verify unexpected server errors are logged."""
    with caplog.at_level(logging.ERROR):
        response = client.get("/api/test-server-error")

    assert response.status_code == 500
    assert "Internal server error" in caplog.text

def test_actual_app_returns_standardized_404():
    """Verify centralized error handlers are registered in real app."""
    from backend.app import create_app

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    client = app.test_client()
    response = client.get("/api/nonexistent")

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "NOT_FOUND"