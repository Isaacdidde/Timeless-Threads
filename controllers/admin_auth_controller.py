# controllers/admin_auth_controller.py

from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from database.connection import get_collection


class AdminAuthController:
    """
    Handles admin login/logout flow (production-ready with safety checks).
    """

    def __init__(self):
        try:
            self.admins = get_collection("admins")
        except Exception as e:
            print("❌ ERROR: Cannot access admins collection:", e)
            self.admins = None

    # -------------------------------------------------
    # LOGIN PAGE
    # -------------------------------------------------
    def login_page(self):
        # Already logged in?
        if session.get("admin"):
            return redirect(url_for("admin_panel.dashboard"))

        return render_template("admin/auth/login.html")

    # -------------------------------------------------
    # HANDLE LOGIN FORM (Production-ready)
    # -------------------------------------------------
    def login_action(self, email, password):
        if not self.admins:
            flash("Internal error: database not available.", "danger")
            return redirect(url_for("admin_auth.login"))

        # Sanitize input
        email = (email or "").strip().lower()
        password = password or ""

        if not email or not password:
            flash("Email and Password are required.", "danger")
            return redirect(url_for("admin_auth.login"))

        # Fetch admin
        try:
            admin = self.admins.find_one({"email": email})
        except Exception as e:
            print("❌ ERROR: Failed to query admins:", e)
            flash("Internal server error.", "danger")
            return redirect(url_for("admin_auth.login"))

        if not admin:
            flash("Admin account not found!", "danger")
            return redirect(url_for("admin_auth.login"))

        # Optional: allow disabling admin accounts safely
        if not admin.get("is_active", True):
            flash("This admin account is disabled.", "danger")
            return redirect(url_for("admin_auth.login"))

        # Password check
        try:
            valid = check_password_hash(admin.get("password", ""), password)
        except Exception as e:
            print("❌ ERROR: Password check failed:", e)
            valid = False

        if not valid:
            flash("Incorrect password!", "danger")
            return redirect(url_for("admin_auth.login"))

        # Login success: store minimal info
        session.clear()
        session["admin"] = admin["email"]  # keep it lightweight

        flash("Welcome Admin!", "success")
        return redirect(url_for("admin_panel.dashboard"))

    # -------------------------------------------------
    # LOGOUT
    # -------------------------------------------------
    def logout(self):
        session.pop("admin", None)
        flash("Logged out successfully", "info")
        return redirect(url_for("admin_auth.login"))
