from app_factory import AppFactory

# -------------------------------------------------------------
# Application Entry Point (Production + Development)
# -------------------------------------------------------------
# This file must expose a top-level variable named `app`
# so Gunicorn (Render) can import it using: gunicorn app:app
# -------------------------------------------------------------

# Create the factory and initialize the Flask application
factory = AppFactory()
app = factory.create_app()   # <-- Gunicorn needs THIS


# -------------------------------------------------------------
# Development server (only runs in local development)
# -------------------------------------------------------------
if __name__ == "__main__":
    # Local development server only
    app.run(
        debug=app.config.get("DEBUG", True),
        host="0.0.0.0",
        port=5000
    )
