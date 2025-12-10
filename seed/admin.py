from werkzeug.security import generate_password_hash
from database.connection import get_collection
from flask import current_app

def seed_admin_user():
    print("🔍 Seeding admin user...")

    try:
        admins = get_collection("admins")
    except Exception as e:
        print("❌ ERROR: Could not access 'admins' collection:", e)
        return

    admin_email = current_app.config.get("ADMIN_EMAIL")
    admin_password = current_app.config.get("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        print("⚠ Missing ADMIN_EMAIL or ADMIN_PASSWORD")
        return

    weak = {"admin", "password", "123456", "changeme", "admin123"}
    if admin_password.lower() in weak:
        print("❌ Weak password detected. Abort.")
        return

    exists = admins.find_one({"email": admin_email})
    if exists:
        print(f"✔ Admin already exists: {admin_email}")
        return

    hashed = generate_password_hash(admin_password)

    admins.insert_one({
        "email": admin_email,
        "password": hashed,
        "role": "superadmin",
        "is_active": True,
    })

    print(f"🎉 Admin created: {admin_email}")
