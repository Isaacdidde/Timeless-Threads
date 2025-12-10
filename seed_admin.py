# config/seed_admin.py

from werkzeug.security import generate_password_hash
from database.connection import get_collection
from flask import current_app


def seed_admin_user():
    """
    Seeds the admin user into MongoDB ONLY if it does not already exist.
    Must be called inside app.app_context().
    Production-safe version with strict environment validation.
    """

    # --- Validate DB connection ---
    try:
        admins = get_collection("admins")
    except Exception as e:
        print("❌ ERROR: Could not connect to MongoDB in seed_admin_user:", e)
        return

    # --- Read admin credentials from environment ---
    admin_email = current_app.config.get("ADMIN_EMAIL")
    admin_password = current_app.config.get("ADMIN_PASSWORD")

    # --- Production safety checks ---
    if not admin_email or not admin_password:
        print("⚠ Skipping admin seed — ADMIN_EMAIL or ADMIN_PASSWORD missing from environment.")
        return

    # Do not allow weak, default or placeholder values in production
    forbidden_passwords = {"admin", "password", "123456", "admin123", "changeme"}
    if admin_password.lower() in forbidden_passwords:
        print("❌ ERROR: ADMIN_PASSWORD is too weak for production. Seed aborted.")
        return

    # --- Check if admin already exists ---
    existing = admins.find_one({"email": admin_email})
    if existing:
        print(f"✔ Admin already exists: {admin_email}")
        return

    # --- Insert new admin ---
    hashed_pw = generate_password_hash(admin_password)

    admins.insert_one({
        "email": admin_email,
        "password": hashed_pw,
        "role": "superadmin",
        "is_active": True,
    })

    print(f"🎉 Admin user created successfully: {admin_email}")
