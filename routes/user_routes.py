"""
Production-ready User Routes
Includes:
    - Safe ObjectId handling
    - Defensive database operations
    - Form validation
    - Sanitized inputs
    - Clean fallbacks + error protection

Public URLs remain unchanged.
"""

from flask import (
    Blueprint, render_template, session, redirect,
    url_for, request, flash, abort
)
from bson import ObjectId, errors as bson_errors
from werkzeug.security import check_password_hash, generate_password_hash
from database.connection import get_collection


user_bp = Blueprint("user", __name__, url_prefix="/user")


# ---------------------------------------------------------
# Helper: Safe ObjectId
# ---------------------------------------------------------
def safe_oid(value):
    try:
        return ObjectId(value)
    except bson_errors.InvalidId:
        return None
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
        flash("Your session is invalid. Please login again.", "danger")
        session.clear()
        return redirect(url_for("auth.login"))

    users = get_collection("users")
    user = users.find_one({"_id": oid}) or {}

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

    name = request.form.get("name", "").strip()
    mobile = request.form.get("mobile", "").strip()

    if not name:
        flash("Name cannot be empty.", "warning")
        return redirect(url_for("user.profile_page"))

    users = get_collection("users")

    try:
        users.update_one(
            {"_id": oid},
            {"$set": {"name": name, "mobile": mobile}}
        )
        session["user_name"] = name
        flash("Profile updated successfully!", "success")
    except Exception as e:
        print("❌ Profile update failed:", e)
        flash("Failed to update profile. Try again later.", "danger")

    return redirect(url_for("user.profile_page"))


# ---------------------------------------------------------
# ADDRESS PAGE
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
    user = users.find_one({"_id": oid}) or {}

    return render_template("user/address.html", user=user)


# ---------------------------------------------------------
# SAVE ADDRESS
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

    # Sanitized fields
    address = {
        "house": request.form.get("house", "").strip(),
        "street": request.form.get("street", "").strip(),
        "city": request.form.get("city", "").strip(),
        "state": request.form.get("state", "").strip(),
        "pincode": request.form.get("pincode", "").strip(),
    }

    # Minimal validation
    if not address["city"] or not address["pincode"]:
        flash("City and pincode are required.", "warning")
        return redirect(url_for("user.address_page"))

    users = get_collection("users")

    try:
        users.update_one(
            {"_id": oid},
            {"$set": {"address": address}}
        )
        flash("Address saved successfully!", "success")
    except Exception as e:
        print("❌ Address save failed:", e)
        flash("Could not save address. Please try later.", "danger")

    return redirect(url_for("user.address_page"))


# ---------------------------------------------------------
# CHANGE PASSWORD PAGE
# ---------------------------------------------------------
@user_bp.route("/change-password")
def change_password_page():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("user/change_password.html")


# ---------------------------------------------------------
# UPDATE PASSWORD
# ---------------------------------------------------------
@user_bp.route("/update-password", methods=["POST"])
def update_password():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))

    oid = safe_oid(user_id)
    if not oid:
        session.clear()
        return redirect(url_for("auth.login"))

    old_password = request.form.get("old_password") or ""
    new_password = request.form.get("new_password") or ""

    if len(new_password) < 6:
        flash("New password must be at least 6 characters.", "warning")
        return redirect(url_for("user.change_password_page"))

    users = get_collection("users")
    user = users.find_one({"_id": oid})

    if not user:
        flash("User not found.", "danger")
        session.clear()
        return redirect(url_for("auth.login"))

    # Validate old password
    if not check_password_hash(user.get("password", ""), old_password):
        flash("Old password is incorrect!", "danger")
        return redirect(url_for("user.change_password_page"))

    # Update password
    try:
        hashed = generate_password_hash(new_password)
        users.update_one({"_id": oid}, {"$set": {"password": hashed}})
        flash("Password updated successfully!", "success")
    except Exception as e:
        print("❌ Password update failed:", e)
        flash("Could not update password. Try again later.", "danger")

    return redirect(url_for("user.profile_page"))
