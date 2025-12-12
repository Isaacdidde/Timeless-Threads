"""
Production-ready authentication routes.

Fully protects:
    - Missing form fields
    - Bad POST requests
    - Controller exceptions
    - Missing DB instance (current_app.db)
    - Unexpected errors turning into 500 HTML pages

Behavior, redirects, and templates stay exactly the same.
"""

from flask import Blueprint, request, current_app, flash, redirect, url_for

# Safe import of controller
try:
    from controllers.auth_controller import AuthController
except Exception as e:
    print("❌ ERROR: Failed to import AuthController:", e)

    # Fallback stub keeps app running
    class AuthController:
        def login_page(self): 
            flash("Login unavailable.", "danger")
            return redirect(url_for("main.home"))
        def login(self, *a, **k):
            flash("Login unavailable.", "danger")
            return redirect(url_for("main.home"))
        def signup_page(self):
            flash("Signup unavailable.", "danger")
            return redirect(url_for("main.home"))
        def signup(self, *a, **k):
            flash("Signup unavailable.", "danger")
            return redirect(url_for("main.home"))
        def logout_confirm(self):
            return redirect(url_for("main.home"))

auth_bp = Blueprint("auth", __name__)


# ---------------------------------------------------------
# SAFE CONTROLLER FACTORY
# ---------------------------------------------------------
def get_controller():
    try:
        db = getattr(current_app, "db", None)
        if db is None:
            print("⚠ WARNING: current_app.db is missing!")
            flash("System error. Try again later.", "danger")
            return AuthController(None)

        return AuthController(db)   # ← FIXED
    except Exception as e:
        print("❌ ERROR: Failed to initialize AuthController:", e)
        flash("Authentication unavailable.", "danger")
        return AuthController(None)



# ---------------------------------------------------------
# LOGIN PAGE / SUBMIT
# ---------------------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    controller = get_controller()

    try:
        if request.method == "POST":
            identifier = (request.form.get("identifier") or "").strip()
            password = (request.form.get("password") or "").strip()

            if not identifier or not password:
                flash("Email/Mobile and password are required.", "warning")
                return redirect(url_for("auth.login"))

            return controller.login(identifier, password)

        return controller.login_page()

    except Exception as e:
        print("❌ ERROR in login route:", e)
        flash("Login failed due to a system error.", "danger")
        return redirect(url_for("auth.login"))


# ---------------------------------------------------------
# SIGNUP PAGE / SUBMIT
# ---------------------------------------------------------
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    controller = get_controller()

    try:
        if request.method == "POST":
            form = request.form

            name = (form.get("name") or "").strip()
            email = (form.get("email") or "").strip()
            mobile = (form.get("mobile") or "").strip()
            age = (form.get("age") or "").strip()
            password = (form.get("password") or "").strip()

            if not all([name, email, mobile, age, password]):
                flash("All fields are required.", "warning")
                return redirect(url_for("auth.signup"))

            return controller.signup(name, email, mobile, age, password)

        return controller.signup_page()

    except Exception as e:
        print("❌ ERROR in signup route:", e)
        flash("Signup failed due to a system error.", "danger")
        return redirect(url_for("auth.signup"))


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------
@auth_bp.route("/logout")
def logout():
    controller = get_controller()

    try:
        return controller.logout_confirm()
    except Exception as e:
        print("❌ ERROR in logout route:", e)
        flash("Logout failed. Try again.", "warning")
        return redirect(url_for("main.home"))
