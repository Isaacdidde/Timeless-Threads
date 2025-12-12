"""
Production-ready User Routes
Handles:
    - Profile view/update
    - Address management
    - Password change
    - Session validation
    - Safe ObjectId handling
"""

from flask import (
    Blueprint, render_template, session, redirect,
    url_for, request, flash
)
from bson import ObjectId
from bson.errors import InvalidId
from werkzeug.security import check_password_hash, generate_password_hash
from database.connection import get_collection
from models.user_model import UserModel


user_bp = Blueprint("user", __name__, url_prefix="/user")


# ---------------------------------------------------------
# Helper: Safe ObjectId parser
# ---------------------------------------------------------
def safe_oid(value):
    try:
        return ObjectId(value)
    except Exception:
        return None


# ---------------------------------------------------------
# PROFILE PAGE
# ---------------------------------------------------------
@user_bp.route("/profile")
def profile_page():
    user_id = session.get("user_id")

    if not user_id:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    oid = safe_oid(user_id)
    if not oid:
        session.clear()
        flash("Session expired. Please login again.", "danger")
        return redirect(url_for("auth.login"))

    users = get_collection("users")

    try:
        user = users.find_one({"_id": oid}) or {}
    except Exception as e:
        print("⚠ WARNING: Failed to load profile:", e)
        user = {}

    return render_template("user/profile.html", user=user)


# ---------------------------------------------------------
# UPDATE PROFILE
# ---------------------------------------------------------
@user_bp.route("/update-profile", methods=["POST"])
def update_profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    oid = safe_oid(user_id)
    if not oid:
        session.clear()
        return redirect(url_for("auth.login"))

    name = (request.form.get("name") or "").strip()
    mobile = (request.form.get("mobile") or "").strip()

    if not name:
        flash("Name cannot be empty.", "warning")
        return redirect(url_for("user.profile_page"))

    users = get_collection("users")

    try:
        users.update_one(
            {"_id": oid},
            {"$set": {"name": name, "mobile": mobile}}
        )
        session["user_name"] = name  # Update navbar name
        flash("Profile updated successfully!", "success")
    except Exception as e:
        print("❌ ERROR: Failed to update profile:", e)
        flash("Could not update profile.", "danger")

    return redirect(url_for("user.profile_page"))


# ---------------------------------------------------------
# ADDRESS PAGE  (Legacy API — no longer used by navbar)
# ---------------------------------------------------------
@user_bp.route("/address")
def address_page():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    oid = safe_oid(user_id)
    if not oid:
        session.clear()
        return redirect(url_for("auth.login"))

    users = get_collection("users")

    try:
        user = users.find_one({"_id": oid}) or {}
    except Exception as e:
        print("⚠ WARNING: Failed to load address page:", e)
        user = {}

    return render_template("user/address.html", user=user)


# ---------------------------------------------------------
# SAVE ADDRESS  (WORKING PATCHED VERSION)
# ---------------------------------------------------------
@user_bp.route("/save-address", methods=["POST"])
def save_address():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    oid = safe_oid(user_id)
    if not oid:
        session.clear()
        return redirect(url_for("auth.login"))

    address = {
        "house": (request.form.get("house") or "").strip(),
        "street": (request.form.get("street") or "").strip(),
        "city": (request.form.get("city") or "").strip(),
        "state": (request.form.get("state") or "").strip(),
        "pincode": (request.form.get("pincode") or "").strip(),
    }

    if not address["city"] or not address["pincode"]:
        flash("City and pincode are required.", "warning")
        return redirect(url_for("user.profile_page"))

    users = get_collection("users")

    try:
        users.update_one(
            {"_id": oid},
            {"$set": {"address": address}}
        )
        flash("Address saved successfully!", "success")
    except Exception as e:
        print("❌ ERROR: Failed to save address:", e)
        flash("Could not save the address.", "danger")

    return redirect(url_for("user.profile_page"))


# ---------------------------------------------------------
# CHANGE PASSWORD PAGE (GET) — *Not used anymore by navbar*
# ---------------------------------------------------------
@user_bp.route("/change-password", methods=["GET"])
def change_password_page():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("user/change_password.html")


# ---------------------------------------------------------
# CHANGE PASSWORD SUBMIT (POST) — FULLY PATCHED
# ---------------------------------------------------------
@user_bp.route("/change-password", methods=["POST"])
def change_password_submit():
    user_id = session.get("user_id")
    if not user_id:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login"))

    user_model = UserModel()
    user = user_model.get_by_id(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("auth.login"))

    old_password = request.form.get("old_password") or ""
    new_password = request.form.get("new_password") or ""

    if len(new_password) < 6:
        flash("New password must be at least 6 characters.", "warning")
        return redirect(url_for("user.profile_page"))

    # Validate old password
    try:
        if not check_password_hash(user.get("password", ""), old_password):
            flash("Old password is incorrect!", "danger")
            return redirect(url_for("user.profile_page"))
    except Exception as e:
        print("⚠ WARNING: Password check failed:", e)
        flash("Password verification failed.", "danger")
        return redirect(url_for("user.profile_page"))

    # Save new password safely
    try:
        hashed = generate_password_hash(new_password)
        user_model.update(user_id, {"password": hashed})
        flash("Password updated successfully!", "success")
    except Exception as e:
        print("❌ ERROR: Failed to update password:", e)
        flash("Could not update password.", "danger")

    return redirect(url_for("user.profile_page"))
