# app.py

from app_factory import AppFactory

"""
============================================================
 Production Entry Point for Timeless Threads
------------------------------------------------------------
• Gunicorn will import:  app = factory.create_app()
• Local development uses the __main__ block.
• Context processors are already loaded inside AppFactory,
  so no need to call them again here.
============================================================
"""

# -------------------------------------------------------------
# CREATE APPLICATION (used by Gunicorn / Render)
# -------------------------------------------------------------
factory = AppFactory()
app = factory.create_app()     # Gunicorn loads this:  gunicorn app:app


# -------------------------------------------------------------
# LOCAL DEVELOPMENT SERVER
# -------------------------------------------------------------
if __name__ == "__main__":
    # Running locally with Flask's development server
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=app.config.get("DEBUG", True)
    )
