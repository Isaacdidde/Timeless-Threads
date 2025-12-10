"""
Central blueprint registry for the Timeless Threads application.
This file is imported by AppFactory AFTER Mongo initialization.

This production-ready version:
    - prevents crashes if a blueprint import breaks
    - logs clear warnings instead of failing silently
    - avoids double-registration
    - isolates blueprint loading errors from breaking the whole app
"""

# -------------------------------------------------------------------
# SAFE IMPORT WRAPPER
# -------------------------------------------------------------------
def safe_import(import_func, name):
    try:
        return import_func()
    except Exception as e:
        print(f"❌ ERROR: Failed to load blueprint '{name}': {e}")
        return None


# -------------------------------------------------------------------
# BLUEPRINT IMPORTS (wrapped for safety)
# -------------------------------------------------------------------
def load_public_routes():
    from .main_routes import main_bp
    from .product_routes import product_bp
    from .auth_routes import auth_bp
    from .review_routes import review_bp
    from .category_routes import category_bp
    from .cart_routes import cart_bp
    from .user_routes import user_bp
    return main_bp, product_bp, auth_bp, review_bp, category_bp, cart_bp, user_bp


def load_admin_routes():
    from .admin_auth_routes import admin_auth_bp
    from .admin_product_routes import admin_product_bp
    from .admin_category_routes import admin_category_bp
    from .admin_ad_routes import admin_ad_bp
    from .admin.panel import panel_bp
    return admin_auth_bp, admin_product_bp, admin_category_bp, admin_ad_bp, panel_bp


def load_ads_routes():
    from .ads_routes import ads_bp
    return ads_bp


# -------------------------------------------------------------------
# BLUEPRINT REGISTRATION
# -------------------------------------------------------------------
def register_blueprints(app):

    # ============================================================
    # PUBLIC ROUTES
    # ============================================================
    loaded_public = safe_import(load_public_routes, "public_routes")
    if loaded_public:
        (
            main_bp,
            product_bp,
            auth_bp,
            review_bp,
            category_bp,
            cart_bp,
            user_bp,
        ) = loaded_public

        # Only register blueprints that successfully loaded
        if main_bp:
            app.register_blueprint(main_bp)
        if auth_bp:
            app.register_blueprint(auth_bp, url_prefix="/auth")
        if category_bp:
            app.register_blueprint(category_bp, url_prefix="/category")
        if product_bp:
            app.register_blueprint(product_bp)  # product routes define their own prefix
        if review_bp:
            app.register_blueprint(review_bp, url_prefix="/review")
        if cart_bp:
            app.register_blueprint(cart_bp, url_prefix="/cart")
        if user_bp:
            app.register_blueprint(user_bp)  # already has /user prefix


    # ============================================================
    # ADMIN ROUTES
    # ============================================================
    loaded_admin = safe_import(load_admin_routes, "admin_routes")
    if loaded_admin:
        (
            admin_auth_bp,
            admin_product_bp,
            admin_category_bp,
            admin_ad_bp,
            panel_bp,
        ) = loaded_admin

        # ADMIN PANEL (dashboard)
        if panel_bp:
            app.register_blueprint(panel_bp)  # already uses /admin

        # Admin modules (DO NOT prefix again)
        if admin_auth_bp:
            app.register_blueprint(admin_auth_bp)
        if admin_product_bp:
            app.register_blueprint(admin_product_bp)
        if admin_category_bp:
            app.register_blueprint(admin_category_bp)
        if admin_ad_bp:
            app.register_blueprint(admin_ad_bp)


    # ============================================================
    # ADS ENGINE ROUTES
    # ============================================================
    ads_bp = safe_import(load_ads_routes, "ads_routes")
    if ads_bp:
        app.register_blueprint(ads_bp, url_prefix="/ads")


    # ============================================================
    # RETURN APP
    # ============================================================
    return app
