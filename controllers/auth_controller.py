from flask import (
    session, flash, redirect, url_for, render_template
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from models.user_model import UserModel


class AuthController:
    def __init__(self, mongo):
        try:
            self.users = UserModel(mongo)
            self.mongo = mongo
        except Exception as e:
            print("❌ ERROR: Could not initialize UserModel:", e)
            self.users = None

    # ===============================================================
    # LOGIN PAGE
    # ===============================================================
    def login_page(self):
        return render_template("login.html")

    # ===============================================================
    # LOGIN
    # ===============================================================
    def login(self, identifier, password):
        # Sanitize inputs
        identifier = (identifier or "").strip().lower()
        password = (password or "").strip()

        if not identifier or not password:
            flash("Enter both email/mobile and password.", "danger")
            return redirect(url_for("auth.login"))

        # Model availability check
        if not self.users:
            flash("Internal error. Please try again later.", "danger")
            return redirect(url_for("auth.login"))

        # Lookup user
        try:
            user = self.users.find_by_email(identifier)
            if not user:
                user = self.users.find_by_mobile(identifier)
        except Exception as e:
            print("❌ ERROR: User lookup failed:", e)
            flash("Something went wrong. Please try again.", "danger")
            return redirect(url_for("auth.login"))

        if not user:
            flash("Account not found!", "danger")
            return redirect(url_for("auth.login"))

        # Account disabled (optional safety)
        if not user.get("is_active", True):
            flash("This account is disabled.", "danger")
            return redirect(url_for("auth.login"))

        # Password check
        try:
            valid_pw = check_password_hash(user.get("password", ""), password)
        except Exception as e:
            print("❌ ERROR: Password validation failed:", e)
            valid_pw = False

        if not valid_pw:
            flash("Incorrect password!", "danger")
            return redirect(url_for("auth.login"))

        # Safe session handling
        session.clear()
        session["user_id"] = str(user["_id"])
        session["user_name"] = user.get("name")

        flash("Logged in successfully!", "success")
        return redirect(url_for("main.home"))

    # ===============================================================
    # SIGNUP PAGE
    # ===============================================================
    def signup_page(self):
        return render_template("signup.html")

    # ===============================================================
    # SIGNUP (Create User)
    # ===============================================================
    def signup(self, name, email, mobile, age, password):
        if not self.users:
            flash("Internal error. Try again later.", "danger")
            return redirect(url_for("auth.signup"))

        # Sanitize
        name = (name or "").strip()
        email = (email or "").strip().lower()
        mobile = (mobile or "").strip()
        age = (age or "").strip()
        password = (password or "").strip()

        # Validate required fields
        if not all([name, email, mobile, age, password]):
            flash("All fields are required!", "danger")
            return redirect(url_for("auth.signup"))

        # Validate types
        try:
            age_int = int(age)
            if age_int < 0 or age_int > 120:
                raise ValueError
        except ValueError:
            flash("Invalid age.", "danger")
            return redirect(url_for("auth.signup"))

        # Duplicate checks
        try:
            if self.users.find_by_email(email):
                flash("Email already registered!", "warning")
                return redirect(url_for("auth.signup"))

            if self.users.find_by_mobile(mobile):
                flash("Mobile number already registered!", "warning")
                return redirect(url_for("auth.signup"))
        except Exception as e:
            print("❌ ERROR: Duplicate check failed:", e)
            flash("Something went wrong. Try again later.", "danger")
            return redirect(url_for("auth.signup"))

        # Hash password securely
        try:
            hashed_password = generate_password_hash(password)
        except Exception as e:
            print("❌ ERROR: Password hashing failed:", e)
            flash("Something went wrong. Try again.", "danger")
            return redirect(url_for("auth.signup"))

        # Create user safely
        try:
            self.users.create(
                name=name,
                email=email,
                mobile=mobile,
                age=age_int,
                password=hashed_password,
                created_at=datetime.utcnow(),
                is_active=True,
            )
        except Exception as e:
            print("❌ ERROR: Failed to create user:", e)
            flash("Unable to create account right now.", "danger")
            return redirect(url_for("auth.signup"))

        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("auth.login"))

    # ===============================================================
    # LOGOUT PAGE
    # ===============================================================
    def logout_page(self):
        if "user_id" not in session:
            return redirect(url_for("main.home"))

        return render_template("logout_confirm.html")

    # ===============================================================
    # LOGOUT CONFIRM
    # ===============================================================
    def logout_confirm(self):
        session.clear()
        flash("Logged out successfully!", "info")
        return redirect(url_for("main.home"))
