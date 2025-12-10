"""
Central blueprint registry for the Timeless Threads application.
"""

# ---------------------------------------------------------
# SAFE IMPORT WRAPPER
# ---------------------------------------------------------
def safe_import(import_func, name):
    try:
        return import_func()
    except Exception as e:
        print(f"❌ ERROR: Failed to load blueprint '{name}': {e}")
        return None


# ---------------------------------------------------------
# BLUEPRINT GROUP LOADERS
# ---------------------------------------------------------
def load_public_routes():
    # Public-facing routes only
    from .main_routes import main_bp
    from .product_routes import product_bp   # MUST NOT define /category now
    from .auth_routes import auth_bp
    from .review_routes import review_bp
    from .category_routes import category_bp
    from .cart_routes import cart_bp
    from .user_routes import user_bp

    return (
        main_bp,
        product_bp,
        auth_bp,
        review_bp,
        category_bp,
        cart_bp,
        user_bp,
    )


def load_admin_routes():
    from .admin_auth_routes import admin_auth_bp
    from .admin_product_routes import admin_product_bp
    from .admin_category_routes import admin_category_bp
    from .admin_ad_routes import admin_ad_bp
    from .admin.panel import panel_bp

    return (
        admin_auth_bp,
        admin_product_bp,
        admin_category_bp,
        admin_ad_bp,
        panel_bp,
    )


def load_ads_routes():
    from .ads_routes import ads_bp
    return ads_bp


# ---------------------------------------------------------
# BLUEPRINT REGISTRATION
# ---------------------------------------------------------
def register_blueprints(app):

    # ========================================
    # PUBLIC ROUTES
    # ========================================
    public = safe_import(load_public_routes, "public_routes")

    if public:
        (
            main_bp,
            product_bp,
            auth_bp,
            review_bp,
            category_bp,
            cart_bp,
            user_bp,
        ) = public

        if main_bp:
            app.register_blueprint(main_bp)

        if auth_bp:
            app.register_blueprint(auth_bp, url_prefix="/auth")

        # CATEGORY ROUTES ONLY HERE
        if category_bp:
            app.register_blueprint(category_bp, url_prefix="/category")

        # PRODUCT ROUTES (must NOT define /category anymore)
        if product_bp:
            app.register_blueprint(product_bp)

        if review_bp:
            app.register_blueprint(review_bp, url_prefix="/review")

        if cart_bp:
            app.register_blueprint(cart_bp, url_prefix="/cart")

        if user_bp:
            app.register_blueprint(user_bp)  # already has /user


    # ========================================
    # ADMIN ROUTES
    # ========================================
    admin = safe_import(load_admin_routes, "admin_routes")

    if admin:
        (
            admin_auth_bp,
            admin_product_bp,
            admin_category_bp,
            admin_ad_bp,
            panel_bp,
        ) = admin

        # Dashboard container
        if panel_bp:
            app.register_blueprint(panel_bp)

        # Admin modules
        if admin_auth_bp:
            app.register_blueprint(admin_auth_bp)

        if admin_product_bp:
            app.register_blueprint(admin_product_bp)

        if admin_category_bp:
            app.register_blueprint(admin_category_bp)

        if admin_ad_bp:
            app.register_blueprint(admin_ad_bp)

    # ========================================
    # ADS ENGINE
    # ========================================
    ads_bp = safe_import(load_ads_routes, "ads_routes")
    if ads_bp:
        app.register_blueprint(ads_bp, url_prefix="/ads")

    return app
