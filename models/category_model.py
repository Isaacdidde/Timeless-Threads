# models/category_model.py

from database.connection import get_collection
from bson import ObjectId
from bson.errors import InvalidId


class CategoryModel:
    def __init__(self):
        """Initialize categories collection safely."""
        try:
            self.col = get_collection("categories")
        except Exception as e:
            print("❌ ERROR: Failed to access 'categories' collection:", e)
            self.col = None

    # ==============================================================
    # GET ALL CATEGORIES
    # ==============================================================
    def all(self):
        """Return all categories safely."""
        if not self.col:
            return []

        try:
            return list(self.col.find().sort("name", 1))
        except Exception as e:
            print("⚠ WARNING: Failed to fetch categories:", e)
            return []

    # ==============================================================
    # GET CATEGORY BY ID
    # ==============================================================
    def get(self, id):
        """Return a category by its ID."""
        if not self.col:
            return None

        try:
            oid = ObjectId(id)
        except InvalidId:
            print(f"⚠ WARNING: Invalid category ID '{id}'")
            return None
        except Exception as e:
            print("⚠ WARNING: Category ID error:", e)
            return None

        try:
            return self.col.find_one({"_id": oid})
        except Exception as e:
            print(f"⚠ WARNING: Failed to fetch category '{id}':", e)
            return None

    # ==============================================================
    # GET CATEGORY BY SLUG (for URLs)
    # ==============================================================
    def get_by_slug(self, slug):
        """Return category based on slug field."""
        if not self.col:
            return None

        try:
            return self.col.find_one({"slug": slug})
        except Exception as e:
            print(f"⚠ WARNING: Failed to fetch category by slug '{slug}':", e)
            return None

    # ==============================================================
    # CREATE CATEGORY
    # ==============================================================
    def create(self, data):
        """Insert a new category into DB."""
        if not self.col:
            print("❌ ERROR: categories collection unavailable for create()")
            return None

        try:
            data.setdefault("slug", data.get("name", "").strip().lower())
            return self.col.insert_one(data)
        except Exception as e:
            print("❌ ERROR: Failed to create category:", e)
            return None

    # ==============================================================
    # UPDATE CATEGORY
    # ==============================================================
    def update(self, id, data):
        """Update category fields safely."""
        if not self.col:
            print("❌ ERROR: categories collection unavailable for update()")
            return None

        try:
            oid = ObjectId(id)
        except InvalidId:
            print(f"⚠ WARNING: Invalid category ID '{id}'")
            return None
        except Exception as e:
            print("⚠ WARNING: Category ID error on update:", e)
            return None

        try:
            if "name" in data and "slug" not in data:
                data["slug"] = data["name"].strip().lower()

            return self.col.update_one({"_id": oid}, {"$set": data})
        except Exception as e:
            print(f"❌ ERROR: Failed to update category '{id}':", e)
            return None

    # ==============================================================
    # DELETE CATEGORY
    # ==============================================================
    def delete(self, id):
        """Delete category by ID safely."""
        if not self.col:
            print("❌ ERROR: categories collection unavailable for delete()")
            return None

        try:
            oid = ObjectId(id)
        except InvalidId:
            print(f"⚠ WARNING: Invalid category ID '{id}'")
            return None
        except Exception as e:
            print("⚠ WARNING: Category ID error on delete:", e)
            return None

        try:
            return self.col.delete_one({"_id": oid})
        except Exception as e:
            print(f"❌ ERROR: Failed to delete category '{id}':", e)
            return None
