from bson.objectid import ObjectId, errors as bson_errors


class ProductModel:
    """
    Production-Ready Model for interacting with the 'products' collection.
    Includes safety wrappers for Mongo access, ObjectId validation,
    and predictable fallback returns so the app never breaks.
    """

    def __init__(self, mongo):
        try:
            self.db = mongo.db.products
        except Exception as e:
            print("❌ ERROR: Cannot access products collection:", e)
            self.db = None

    # =====================================================================
    # GET ALL PRODUCTS IN A CATEGORY
    # =====================================================================
    def get_by_category(self, category_name):
        if not self.db:
            return []

        try:
            return list(self.db.find({"category": category_name}))
        except Exception as e:
            print(f"⚠ WARNING: Failed to fetch products for category '{category_name}':", e)
            return []

    # =====================================================================
    # GET PRODUCT BY ID (Safe ObjectId Handling)
    # =====================================================================
    def get_by_id(self, pid):
        if not self.db:
            return None

        try:
            oid = ObjectId(pid)
        except bson_errors.InvalidId:
            print(f"⚠ WARNING: Invalid product ID '{pid}'")
            return None
        except Exception as e:
            print("⚠ WARNING: Error handling product ID:", e)
            return None

        try:
            return self.db.find_one({"_id": oid})
        except Exception as e:
            print(f"⚠ WARNING: Failed to fetch product '{pid}':", e)
            return None

    # =====================================================================
    # LIST PRODUCTS WITH LIMIT
    # =====================================================================
    def list_all(self, limit=100):
        if not self.db:
            return []

        try:
            return list(self.db.find().limit(limit))
        except Exception as e:
            print("⚠ WARNING: Failed to list products:", e)
            return []

    # =====================================================================
    # INSERT PRODUCT
    # =====================================================================
    def insert(self, product_data):
        if not self.db:
            return None

        try:
            result = self.db.insert_one(product_data)
            return self.get_by_id(result.inserted_id)
        except Exception as e:
            print("❌ ERROR: Failed to insert product:", e)
            return None

    # =====================================================================
    # UPDATE PRODUCT DOCUMENT
    # =====================================================================
    def update(self, product_id, update_data):
        if not self.db:
            return None

        try:
            oid = ObjectId(product_id)
        except bson_errors.InvalidId:
            print(f"⚠ WARNING: Invalid product ID '{product_id}'")
            return None

        try:
            self.db.update_one({"_id": oid}, {"$set": update_data})
            return self.get_by_id(product_id)
        except Exception as e:
            print(f"❌ ERROR: Failed to update product '{product_id}':", e)
            return None

    # =====================================================================
    # REMOVE IMAGE FROM IMAGES ARRAY
    # =====================================================================
    def remove_image(self, product_id, filename):
        if not self.db:
            return False

        try:
            oid = ObjectId(product_id)
        except bson_errors.InvalidId:
            print(f"⚠ WARNING: Invalid product ID '{product_id}'")
            return False

        try:
            self.db.update_one({"_id": oid}, {"$pull": {"images": filename}})
            return True
        except Exception as e:
            print(f"⚠ WARNING: Failed to remove image for '{product_id}':", e)
            return False

    # =====================================================================
    # SET PRIMARY IMAGE
    # =====================================================================
    def set_primary_image(self, product_id, filename):
        if not self.db:
            return False

        try:
            oid = ObjectId(product_id)
        except bson_errors.InvalidId:
            print(f"⚠ WARNING: Invalid product ID '{product_id}'")
            return False

        try:
            self.db.update_one({"_id": oid}, {"$set": {"primary_image": filename}})
            return True
        except Exception as e:
            print(f"⚠ WARNING: Failed to set primary image for '{product_id}':", e)
            return False

    # =====================================================================
    # UPDATE PRODUCT DETAILS
    # =====================================================================
    def update_details(self, product_id, details_list):
        if not self.db:
            return False

        try:
            oid = ObjectId(product_id)
        except bson_errors.InvalidId:
            print(f"⚠ WARNING: Invalid product ID '{product_id}'")
            return False

        try:
            self.db.update_one({"_id": oid}, {"$set": {"details": details_list}})
            return True
        except Exception as e:
            print(f"⚠ WARNING: Failed to update details for '{product_id}':", e)
            return False

    # =====================================================================
    # SEARCH (SAFE REGEX)
    # =====================================================================
    def search(self, keyword):
        if not self.db:
            return []

        if not keyword:
            return []

        try:
            return list(
                self.db.find({
                    "name": {"$regex": keyword, "$options": "i"}
                })
            )
        except Exception as e:
            print(f"⚠ WARNING: Search failed for keyword '{keyword}':", e)
            return []
