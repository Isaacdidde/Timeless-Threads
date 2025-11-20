# Import all blueprints from their respective route modules.
# These blueprints represent separate feature modules of the application.
from .main_routes import main_bp
from .product_routes import product_bp
from .auth_routes import auth_bp
from .review_routes import review_bp
from .category_routes import category_bp


# ------------------------------------------------------------
# BLUEPRINT REGISTRATION (Version 1)
#
# This function attaches all the app’s blueprints to the Flask
# application instance. Blueprints modularize the application
# making routes clean, organized, and maintainable.
#
# Some blueprints use url_prefix to group routes under a path.
# ------------------------------------------------------------
def register_blueprints(app):
    # Main pages (home, search, static pages)
    app.register_blueprint(main_bp)

    # Authentication routes → /auth/*
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Category browsing routes → /category/*
    app.register_blueprint(category_bp, url_prefix="/category")

    # Product routes → /product/*
    app.register_blueprint(product_bp, url_prefix="/product")

    # Review routes without prefix (global endpoints)
    app.register_blueprint(review_bp)



# The duplicate import is preserved exactly as you had it.
# The goal is to improve readability **without altering behavior**.
from .review_routes import review_bp


# ------------------------------------------------------------
# BLUEPRINT REGISTRATION (Version 2)
#
# This appears to be an alternate or overwritten definition.
# Flask will use whichever definition is imported at runtime.
#
# This version attaches a URL prefix for review routes.
# ------------------------------------------------------------
def register_blueprints(app):
    # Main blueprint (home, search)
    app.register_blueprint(main_bp)

    # Auth routes → /auth/*
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Product routes → /product/*
    app.register_blueprint(product_bp, url_prefix="/product")

    # Review routes → /review/*
    # This groups all review-related actions under a dedicated prefix.
    app.register_blueprint(review_bp, url_prefix="/review")
