from app_factory import AppFactory

# -------------------------------------------------------------
# Application Entry Point
# -------------------------------------------------------------
# This file is responsible for:
#   ▸ Creating the Flask application instance using the AppFactory
#   ▸ Running the development server when executed directly
# -------------------------------------------------------------

if __name__ == "__main__":
    # Create an AppFactory instance (uses DevelopmentConfig by default)
    factory = AppFactory()

    # Build the fully configured Flask app
    app = factory.create_app()

    # Start the Flask development server
    # Values pulled from config if available, otherwise fallback defaults
    app.run(
        debug=app.config.get("DEBUG", True),  # Enables auto-reload + debug logs
        host="0.0.0.0",                       # Makes the server accessible on local network
        port=5000                             # Standard development port
    )
