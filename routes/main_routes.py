"""
Production-ready Main Routes

Protects against:
    - MongoDB connection failures
    - Controller initialization errors
    - Invalid search queries
    - Unexpected exceptions (no raw 500 errors)

Route paths and template rendering remain unchanged.
"""

from flask import Blueprint, request, flash, redirect, url_for
from database.connection import mongo
from controllers.main_controller import MainController

main_bp = Blueprint("main", __name__)


# ---------------------------------------------------------
# SAFE CONTROLLER FACTORY
# ---------------------------------------------------------
def get_controller():
    try:
        if not hasattr(mongo, "db"):
            print("⚠ WARNING: mongo.db is missing!")
            raise RuntimeError("Database not initialized")
        return MainController(mongo)
    except Exception as e:
        print("❌ ERROR: Failed to create MainController:", e)

        # Fallback dummy that prevents total app crash
        class SafeFallbackController:
            def home(self):
                flash("Homepage temporarily unavailable.", "danger")
                return redirect(url_for("main.faq"))

            def search(self, query):
                flash("Search is temporarily unavailable.", "danger")
                return redirect(url_for("main.home"))

            def faq(self):
                return redirect(url_for("main.home"))

            def contact(self):
                flash("Contact page unavailable.", "warning")
                return redirect(url_for("main.home"))

            def policies(self):
                flash("Policies page unavailable.", "warning")
                return redirect(url_for("main.home"))

        return SafeFallbackController()


# ---------------------------------------------------------
# HOMEPAGE
# ---------------------------------------------------------
@main_bp.route("/")
def home():
    try:
        return get_controller().home()
    except Exception as e:
        print("❌ ERROR: main.home() failed:", e)
        flash("Unable to load homepage.", "danger")
        return redirect(url_for("main.faq"))


# ---------------------------------------------------------
# SEARCH PAGE
# ---------------------------------------------------------
@main_bp.route("/search")
def search():
    try:
        query = request.args.get("q", "") or ""
        query = str(query).strip()

        return get_controller().search(query)

    except Exception as e:
        print("❌ ERROR: main.search() failed:", e)
        flash("Search system error.", "warning")
        return redirect(url_for("main.home"))


# ---------------------------------------------------------
# FAQ PAGE
# ---------------------------------------------------------
@main_bp.route("/faq")
def faq():
    try:
        return get_controller().faq()
    except Exception as e:
        print("❌ ERROR: main.faq() failed:", e)
        flash("FAQ page unavailable.", "warning")
        return redirect(url_for("main.home"))


# ---------------------------------------------------------
# CONTACT PAGE
# ---------------------------------------------------------
@main_bp.route("/contact")
def contact():
    try:
        return get_controller().contact()
    except Exception as e:
        print("❌ ERROR: main.contact() failed:", e)
        flash("Unable to load contact page.", "danger")
        return redirect(url_for("main.home"))


# ---------------------------------------------------------
# POLICIES PAGE
# ---------------------------------------------------------
@main_bp.route("/policies")
def policies():
    try:
        return get_controller().policies()
    except Exception as e:
        print("❌ ERROR: main.policies() failed:", e)
        flash("Policies page unavailable.", "warning")
        return redirect(url_for("main.home"))
