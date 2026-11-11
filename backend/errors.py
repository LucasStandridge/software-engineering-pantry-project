from flask import jsonify

def error_response(status_code, message, error_code):
    """Create a standardized JSON API error response."""
    response = jsonify({
        "error": {
            "code": error_code,
            "message": message
        }
    })

    return response, status_code

def register_error_handlers(app):
    """Register centralized error handlers with Flask."""

    @app.errorhandler(400)
    def bad_request(error):
        return error_response(
            400, "The request is invalid.", "BAD_REQUEST"
        )

    @app.errorhandler(404)
    def not_found(error):
        return error_response(
            404, "The requested resource was not found.", "NOT_FOUND"
        )

    @app.errorhandler(405)
    def method_not_allowed(error):
        return error_response(
            405, "The HTTP method is not allowed.", "METHOD_NOT_ALLOWED"
        )

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error("Internal server error", exc_info=error)
        return error_response(
            500, "An internal server error occurred.", "INTERNAL_SERVER_ERROR"
        )