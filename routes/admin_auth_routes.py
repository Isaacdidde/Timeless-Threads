from flask import Blueprint, request, redirect, url_for, flash

# -------------------------------------------------------------------
# SAFE CONTROLLER IMPORT
# -------------------------------------------------------------------
try:
    from controllers.admin_auth_controller import AdminAuthController
except Exception as e:
    print("❌ ERROR: Failed to import AdminAuthController:", e)

    # fallback stub (prevents app from crashing)
    class AdminAuthController:
        def login_page(self):
            flash("Admin authentication temporarily unavailable.", "danger")
            return redirect(url_for("main.home"))

        def login_action(self, *args, **kwargs):
            flash("Admin authentication unavailable.", "danger")
            return redirect(url_for("main.home"))

        def logout(self):
            flash("Logged out.", "info")
            return redirect(url_for("main.home"))


# -------------------------------------------------------------------
# BLUEPRINT
# -------------------------------------------------------------------
admin_auth_bp = Blueprint("admin_auth", __name__, url_prefix="/admin")


# -------------------------------------------------------------------
# CONTROLLER FACTORY WRAPPER
# -------------------------------------------------------------------
def get_controller():
    try:
        return AdminAuthController()
    except Exception as e:
        print("❌ ERROR: Failed to initialize AdminAuthController:", e)
        return AdminAuthController()  # fallback stub


# -------------------------------------------------------------------
# LOGIN PAGE
# -------------------------------------------------------------------
@admin_auth_bp.route("/login", methods=["GET"])
def login():
    try:
        return get_controller().login_page()
    except Exception as e:
        print("❌ ERROR: login_page() failed:", e)
        flash("Unable to load admin login page.", "danger")
        return redirect(url_for("main.home"))


# -------------------------------------------------------------------
# HANDLE LOGIN (POST)
# -------------------------------------------------------------------
@admin_auth_bp.route("/login", methods=["POST"])
def login_action():
    try:
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "warning")
            return redirect(url_for("admin_auth.login"))

        return get_controller().login_action(email, password)

    except Exception as e:
        print("❌ ERROR: login_action() failed:", e)
        flash("Login failed due to a system error.", "danger")
        return redirect(url_for("admin_auth.login"))


# -------------------------------------------------------------------
# LOGOUT
# -------------------------------------------------------------------
@admin_auth_bp.route("/logout")
def logout():
    try:
        return get_controller().logout()
    except Exception as e:
        print("❌ ERROR: logout() failed:", e)
        flash("Logout failed. Try again.", "warning")
        return redirect(url_for("admin_auth.login"))
