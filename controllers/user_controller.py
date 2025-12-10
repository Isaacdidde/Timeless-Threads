from flask import render_template, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from bson import ObjectId
from bson.errors import InvalidId
import os
from database.connection import get_collection


class UserController:
    def __init__(self):
        try:
            self.users = get_collection("users")
        except Exception as e:
            print("❌ ERROR: Failed to load users collection:", e)
            self.users = None

    # ==================================================================
    # PROFILE PAGE
    # ==================================================================
    def profile_page(self):
        user_id = session.get("user_id")
        if not user_id:
            flash("Please login first.", "warning")
            return redirect(url_for("auth.login"))

        if not self.users:
            flash("User system unavailable.", "danger")
            return redirect(url_for("auth.login"))

        # Load user safely
        try:
            user = self.users.find_one({"_id": ObjectId(user_id)})
        except InvalidId:
            flash("Invalid user ID.", "danger")
            return redirect(url_for("auth.login"))
        except Exception as e:
            print("⚠ WARNING: Failed to load profile:", e)
            flash("Unable to load profile.", "danger")
            return redirect(url_for("auth.login"))

        return render_template("user/profile.html", user=user)

    # ==================================================================
    # UPDATE PROFILE
    # ==================================================================
    def update_profile(self, form, files):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("auth.login"))

        if not self.users:
            flash("Profile system unavailable.", "danger")
            return redirect(url_for("user.profile_page"))

        name = (form.get("name") or "").strip()
        mobile = (form.get("mobile") or "").strip()

        update_data = {}

        if name:
            update_data["name"] = name

        if mobile:
            update_data["mobile"] = mobile

        # ------------------ Profile Image Upload ------------------
        image_file = files.get("image")
        if image_file and hasattr(image_file, "filename"):
            try:
                filename = f"user_{user_id}.jpg"
                upload_path = os.path.join("static/uploads/profile", filename)

                os.makedirs(os.path.dirname(upload_path), exist_ok=True)
                image_file.save(upload_path)
                update_data["profile_image"] = filename
            except Exception as e:
                print("⚠ WARNING: Failed to upload profile image:", e)
                flash("Profile image upload failed.", "warning")

        # ------------------ Update DB ------------------
        try:
            self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
        except Exception as e:
            print("❌ ERROR: Failed to update profile:", e)
            flash("Could not update profile.", "danger")
            return redirect(url_for("user.profile_page"))

        # Update navbar session name safely
        if name:
            session["user_name"] = name

        flash("Profile updated!", "success")
        return redirect(url_for("user.profile_page"))

    # ==================================================================
    # UPDATE PASSWORD
    # ==================================================================
    def update_password(self, form):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("auth.login"))

        if not self.users:
            flash("Password system unavailable.", "danger")
            return redirect(url_for("user.profile_page"))

        current = form.get("current_password") or ""
        new_pass = form.get("new_password") or ""

        # Load user
        try:
            user = self.users.find_one({"_id": ObjectId(user_id)})
        except Exception as e:
            print("❌ ERROR: Failed to load user for password update:", e)
            flash("Unable to update password.", "danger")
            return redirect(url_for("user.profile_page"))

        if not user or not user.get("password"):
            flash("User not found.", "danger")
            return redirect(url_for("user.profile_page"))

        # Verify password safely
        try:
            if not check_password_hash(user["password"], current):
                flash("Incorrect current password!", "danger")
                return redirect(url_for("user.profile_page"))
        except Exception as e:
            print("⚠ WARNING: Password hash check failed:", e)
            flash("Authentication error.", "danger")
            return redirect(url_for("user.profile_page"))

        # Hash new password
        try:
            hashed = generate_password_hash(new_pass)
        except Exception as e:
            print("❌ ERROR: Password hashing failed:", e)
            flash("Could not update password.", "danger")
            return redirect(url_for("user.profile_page"))

        # Update DB
        try:
            self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"password": hashed}}
            )
        except Exception as e:
            print("❌ ERROR: Failed to write new password:", e)
            flash("Failed to update password.", "danger")
            return redirect(url_for("user.profile_page"))

        flash("Password updated successfully!", "success")
        return redirect(url_for("user.profile_page"))

    # ==================================================================
    # ADD ADDRESS
    # ==================================================================
    def add_address(self, form):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("auth.login"))

        if not self.users:
            flash("Address system unavailable.", "danger")
            return redirect(url_for("user.profile_page"))

        address = {
            "label": (form.get("label") or "").strip(),
            "line1": (form.get("line1") or "").strip(),
            "line2": (form.get("line2") or "").strip(),
            "city": (form.get("city") or "").strip(),
            "state": (form.get("state") or "").strip(),
            "pincode": (form.get("pincode") or "").strip(),
            "address_id": str(ObjectId())
        }

        try:
            self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {"addresses": address}}
            )
        except Exception as e:
            print("❌ ERROR: Failed to add address:", e)
            flash("Failed to add address.", "danger")
            return redirect(url_for("user.profile_page"))

        flash("Address added!", "success")
        return redirect(url_for("user.profile_page"))

    # ==================================================================
    # DELETE ADDRESS
    # ==================================================================
    def delete_address(self, address_id):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("auth.login"))

        if not self.users:
            flash("Address system unavailable.", "danger")
            return redirect(url_for("user.profile_page"))

        try:
            self.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$pull": {"addresses": {"address_id": address_id}}}
            )
        except Exception as e:
            print("⚠ WARNING: Failed to delete address:", e)
            flash("Failed to delete address.", "danger")
            return redirect(url_for("user.profile_page"))

        flash("Address removed!", "info")
        return redirect(url_for("user.profile_page"))
