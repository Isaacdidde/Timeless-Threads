from bson.objectid import ObjectId, errors as bson_errors
from datetime import datetime


class UserModel:
    """
    Hardened UserModel for interacting with the 'users' collection.
    Provides safe access, predictable returns, and isolation from DB failures.
    """

    def __init__(self, mongo):
        try:
            self.col = mongo.db.users
        except Exception as e:
            print("❌ ERROR: Cannot access 'users' collection:", e)
            self.col = None

    # =====================================================================
    # FIND USER BY EMAIL
    # =====================================================================
    def find_by_email(self, email: str):
        if not self.col or not email:
            return None

        try:
            return self.col.find_one({"email": email.lower()})
        except Exception as e:
            print(f"⚠ WARNING: find_by_email failed for '{email}':", e)
            return None

    # =====================================================================
    # FIND USER BY MOBILE
    # =====================================================================
    def find_by_mobile(self, mobile: str):
        if not self.col or not mobile:
            return None

        try:
            return self.col.find_one({"mobile": mobile})
        except Exception as e:
            print(f"⚠ WARNING: find_by_mobile failed for '{mobile}':", e)
            return None

    # =====================================================================
    # CREATE NEW USER
    # =====================================================================
    def create(self, **fields):
        if not self.col:
            print("❌ ERROR: 'users' collection unavailable — cannot create user")
            return None

        try:
            # Normalize email
            if "email" in fields and isinstance(fields["email"], str):
                fields["email"] = fields["email"].lower()

            # Add timestamp if missing
            fields.setdefault("created_at", datetime.utcnow())

            result = self.col.insert_one(fields)
            return self.get_by_id(result.inserted_id)
        except Exception as e:
            print("❌ ERROR: Failed to create user:", e)
            return None

    # =====================================================================
    # GET USER BY ID (Safe)
    # =====================================================================
    def get_by_id(self, user_id):
        if not self.col:
            return None

        # Validate ObjectId
        try:
            oid = ObjectId(user_id)
        except bson_errors.InvalidId:
            print(f"⚠ WARNING: Invalid user_id '{user_id}'")
            return None
        except Exception as e:
            print("⚠ WARNING: Error parsing user_id:", e)
            return None

        try:
            return self.col.find_one({"_id": oid})
        except Exception as e:
            print(f"⚠ WARNING: Failed to fetch user '{user_id}':", e)
            return None
