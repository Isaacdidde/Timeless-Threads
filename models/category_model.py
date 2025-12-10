from database.connection import get_collection
from bson import ObjectId, errors as bson_errors


class CategoryModel:
    def __init__(self):
        try:
            self.col = get_collection("categories")
        except Exception as e:
            print("❌ ERROR: Failed to access 'categories' collection:", e)
            self.col = None

    # ---------------------------------------------------------
    # GET ALL CATEGORIES
    # ---------------------------------------------------------
    def all(self):
        if not self.col:
            return []

        try:
            return list(self.col.find())
        except Exception as e:
            print("⚠ WARNING: Failed to fetch categories:", e)
            return []

    # ---------------------------------------------------------
    # GET CATEGORY BY ID
    # ---------------------------------------------------------
    def get(self, id):
        if not self.col:
            return None

        try:
            oid = ObjectId(id)
        except bson_errors.InvalidId:
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

    # ---------------------------------------------------------
    # CREATE CATEGORY
    # ---------------------------------------------------------
    def create(self, data):
        if not self.col:
            print("❌ ERROR: categories collection unavailable for create()")
            return None

        try:
            return self.col.insert_one(data)
        except Exception as e:
            print("❌ ERROR: Failed to create category:", e)
            return None

    # ---------------------------------------------------------
    # UPDATE CATEGORY
    # ---------------------------------------------------------
    def update(self, id, data):
        if not self.col:
            print("❌ ERROR: categories collection unavailable for update()")
            return None

        try:
            oid = ObjectId(id)
        except bson_errors.InvalidId:
            print(f"⚠ WARNING: Invalid category ID '{id}'")
            return None
        except Exception as e:
            print("⚠ WARNING: Category ID error on update:", e)
            return None

        try:
            return self.col.update_one({"_id": oid}, {"$set": data})
        except Exception as e:
            print(f"❌ ERROR: Failed to update category '{id}':", e)
            return None

    # ---------------------------------------------------------
    # DELETE CATEGORY
    # ---------------------------------------------------------
    def delete(self, id):
        if not self.col:
            print("❌ ERROR: categories collection unavailable for delete()")
            return None

        try:
            oid = ObjectId(id)
        except bson_errors.InvalidId:
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
