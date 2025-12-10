# models/user_model.py

from datetime import datetime
from typing import Optional, Any

from bson import ObjectId
from bson.errors import InvalidId

from database.connection import get_collection


class UserModel:
    """
    Production-ready User model.
    Fixes:
      - Accepts optional `mongo` argument (backwards compatibility)
      - Avoids PyMongo truth-value errors
      - Safe ObjectId handling
      - Predictable return types
    """

    def __init__(self, mongo: Optional[Any] = None):
        """
        mongo: Optional legacy parameter — some controllers pass mongo.
               If provided, try mongo.db.users, else fallback to get_collection().
        """
        self.col = None

        try:
            # LEGACY: If a mongo object is passed (e.g., CartController passes it)
            if mongo is not None and hasattr(mongo, "db"):
                self.col = getattr(mongo.db, "users", None)

                # If mongo.db.users doesn't exist → fallback
                if self.col is None:
                    self.col = get_collection("users")
            else:
                # Normal case: always use our connection manager
                self.col = get_collection("users")

        except Exception as e:
            print("❌ ERROR: Cannot access 'users' collection:", e)
            self.col = None

    # =====================================================================
    # FIND BY EMAIL
    # =====================================================================
    def find_by_email(self, email: str):
        if self.col is None or not email:
            return None

        try:
            return self.col.find_one({"email": email.lower()})
        except Exception as e:
            print(f"⚠ WARNING: Failed to lookup email '{email}':", e)
            return None

    # =====================================================================
    # FIND BY MOBILE
    # =====================================================================
    def find_by_mobile(self, mobile: str):
        if self.col is None or not mobile:
            return None

        try:
            return self.col.find_one({"mobile": mobile})
        except Exception as e:
            print(f"⚠ WARNING: Failed to lookup mobile '{mobile}':", e)
            return None

    # =====================================================================
    # CREATE USER
    # =====================================================================
    def create(self, **fields):
        if self.col is None:
            print("❌ ERROR: users collection unavailable — cannot create user")
            return None

        try:
            # Normalize email
            if "email" in fields and isinstance(fields["email"], str):
                fields["email"] = fields["email"].lower()

            # Add timestamp
            fields.setdefault("created_at", datetime.utcnow())

            result = self.col.insert_one(fields)
            return self.get_by_id(result.inserted_id)

        except Exception as e:
            print("❌ ERROR: Failed to create user:", e)
            return None

    # =====================================================================
    # GET USER BY ID
    # =====================================================================
    def get_by_id(self, user_id):
        if self.col is None or not user_id:
            return None

        # Convert to valid ObjectId
        try:
            oid = user_id if isinstance(user_id, ObjectId) else ObjectId(user_id)
        except InvalidId:
            print(f"⚠ WARNING: Invalid user_id '{user_id}'")
            return None
        except Exception as e:
            print("⚠ WARNING: Error converting user_id to ObjectId:", e)
            return None

        try:
            return self.col.find_one({"_id": oid})
        except Exception as e:
            print(f"⚠ WARNING: Failed to load user '{user_id}':", e)
            return None

    # =====================================================================
    # UPDATE USER
    # =====================================================================
    def update(self, user_id, fields: dict):
        if self.col is None:
            return False

        try:
            oid = user_id if isinstance(user_id, ObjectId) else ObjectId(user_id)
        except InvalidId:
            print(f"⚠ WARNING: Invalid user_id '{user_id}'")
            return False
        except Exception as e:
            print("⚠ WARNING: Error parsing user_id:", e)
            return False

        try:
            self.col.update_one({"_id": oid}, {"$set": fields})
            return True
        except Exception as e:
            print(f"❌ ERROR: Failed to update user '{user_id}':", e)
            return False

    # =====================================================================
    # DELETE USER
    # =====================================================================
    def delete(self, user_id):
        if self.col is None:
            return False

        try:
            oid = user_id if isinstance(user_id, ObjectId) else ObjectId(user_id)
        except InvalidId:
            print(f"⚠ WARNING: Invalid user_id '{user_id}'")
            return False
        except Exception as e:
            print("⚠ WARNING: Error converting user_id:", e)
            return False

        try:
            self.col.delete_one({"_id": oid})
            return True
        except Exception as e:
            print(f"⚠ WARNING: Failed to delete user '{user_id}':", e)
            return False
