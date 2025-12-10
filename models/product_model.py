# models/product_model.py

from typing import Optional, List, Any
from bson.objectid import ObjectId
from bson.errors import InvalidId
from database.connection import get_collection


class ProductModel:
    """
    Production-ready model for interacting with the 'products' collection.

    Behaviors:
      - Accepts an optional `mongo` (legacy controllers pass this).
      - Falls back to get_collection() when `mongo` is not provided.
      - Uses explicit `is None` checks so PyMongo collection objects aren't
        used in boolean contexts (avoids "collection objects do not implement
        truth value testing" errors).
      - Always returns predictable types (list or None).
    """

    def __init__(self, mongo: Optional[Any] = None):
        """
        mongo: optional object exposing `db` (legacy code passed `mongo`).
               If not provided, get_collection("products") is used.
        """
        self.col = None

        # Prefer explicit Mongo object if provided (legacy compatibility)
        try:
            if mongo is not None and hasattr(mongo, "db"):
                # mongo.db should behave like a Database object
                self.col = getattr(mongo.db, "products", None)
                # If attribute access didn't yield collection, fall back
                if self.col is None:
                    self.col = get_collection("products")
            else:
                # Normal flow: use centralized get_collection()
                self.col = get_collection("products")
        except Exception as e:
            print("❌ ERROR: Cannot access 'products' collection:", e)
            self.col = None

    # =====================================================================
    # GET ALL PRODUCTS IN A CATEGORY (V2 field: category_slug)
    # =====================================================================
    def get_by_category(self, category_slug: str) -> List[dict]:
        """Return list of products for a given category_slug."""
        if self.col is None:
            return []

        try:
            return list(self.col.find({"category_slug": category_slug}).sort("created_at", -1))
        except Exception as e:
            print(f"⚠ WARNING: Failed to fetch products for category '{category_slug}':", e)
            return []

    # =====================================================================
    # GET PRODUCT BY ID (Safe ObjectId Handling)
    # =====================================================================
    def get_by_id(self, product_id) -> Optional[dict]:
        """Accepts either ObjectId or string. Returns document or None."""
        if self.col is None:
            return None

        try:
            oid = product_id if isinstance(product_id, ObjectId) else ObjectId(product_id)
        except (InvalidId, Exception):
            print(f"⚠ WARNING: Invalid product ID '{product_id}'")
            return None

        try:
            return self.col.find_one({"_id": oid})
        except Exception as e:
            print(f"⚠ WARNING: Failed to fetch product '{product_id}':", e)
            return None

    # =====================================================================
    # LIST PRODUCTS WITH LIMIT
    # =====================================================================
    def list_all(self, limit: int = 100) -> List[dict]:
        """Return latest products up to `limit` (sorted by created_at desc)."""
        if self.col is None:
            return []

        try:
            return list(self.col.find().sort("created_at", -1).limit(int(limit)))
        except Exception as e:
            print("⚠ WARNING: Failed to list products:", e)
            return []

    # =====================================================================
    # INSERT PRODUCT
    # =====================================================================
    def insert(self, product_data: dict) -> Optional[dict]:
        """
        Insert product and return the inserted object (or None on failure).
        """
        if self.col is None:
            return None

        try:
            res = self.col.insert_one(product_data)
            return self.get_by_id(res.inserted_id)
        except Exception as e:
            print("❌ ERROR: Failed to insert product:", e)
            return None

    # =====================================================================
    # UPDATE PRODUCT DOCUMENT
    # =====================================================================
    def update(self, product_id, update_data: dict) -> Optional[dict]:
        """Update and return the updated document (or None)."""
        if self.col is None:
            return None

        try:
            oid = product_id if isinstance(product_id, ObjectId) else ObjectId(product_id)
        except (InvalidId, Exception):
            print(f"⚠ WARNING: Invalid product ID '{product_id}'")
            return None

        try:
            self.col.update_one({"_id": oid}, {"$set": update_data})
            return self.get_by_id(oid)
        except Exception as e:
            print(f"❌ ERROR: Failed to update product '{product_id}':", e)
            return None

    # =====================================================================
    # REMOVE IMAGE FROM IMAGES ARRAY
    # =====================================================================
    def remove_image(self, product_id, filename: str) -> bool:
        if self.col is None:
            return False

        try:
            oid = product_id if isinstance(product_id, ObjectId) else ObjectId(product_id)
        except (InvalidId, Exception):
            print(f"⚠ WARNING: Invalid product ID '{product_id}'")
            return False

        try:
            self.col.update_one({"_id": oid}, {"$pull": {"images": filename}})
            return True
        except Exception as e:
            print(f"⚠ WARNING: Failed to remove image for '{product_id}':", e)
            return False

    # =====================================================================
    # SET PRIMARY IMAGE
    # =====================================================================
    def set_primary_image(self, product_id, filename: str) -> bool:
        if self.col is None:
            return False

        try:
            oid = product_id if isinstance(product_id, ObjectId) else ObjectId(product_id)
        except (InvalidId, Exception):
            print(f"⚠ WARNING: Invalid product ID '{product_id}'")
            return False

        try:
            self.col.update_one({"_id": oid}, {"$set": {"primary_image": filename}})
            return True
        except Exception as e:
            print(f"⚠ WARNING: Failed to set primary image for '{product_id}':", e)
            return False

    # =====================================================================
    # UPDATE PRODUCT DETAILS
    # =====================================================================
    def update_details(self, product_id, details_list: list) -> bool:
        if self.col is None:
            return False

        try:
            oid = product_id if isinstance(product_id, ObjectId) else ObjectId(product_id)
        except (InvalidId, Exception):
            print(f"⚠ WARNING: Invalid product ID '{product_id}'")
            return False

        try:
            self.col.update_one({"_id": oid}, {"$set": {"details": details_list}})
            return True
        except Exception as e:
            print(f"⚠ WARNING: Failed to update details for '{product_id}':", e)
            return False

    # =====================================================================
    # SEARCH
    # =====================================================================
    def search(self, keyword: str) -> List[dict]:
        """Safe case-insensitive product search returning a list."""
        if self.col is None:
            return []

        keyword = (keyword or "").strip()
        if not keyword:
            return []

        try:
            return list(self.col.find({"name": {"$regex": keyword, "$options": "i"}}))
        except Exception as e:
            print(f"⚠ WARNING: Search failed for keyword '{keyword}':", e)
            return []
