from bson import ObjectId, errors as bson_errors
import datetime


class ReviewModel:
    """
    Production-ready model for interacting with the 'reviews' collection.

    Provides:
        - Review lookup by user + product
        - Insert review
        - Update review
        - Delete review
        - Fetch all reviews for a product
    """

    def __init__(self, mongo):
        try:
            self.collection = mongo.db.reviews
        except Exception as e:
            print("❌ ERROR: Cannot access 'reviews' collection:", e)
            self.collection = None

    # =====================================================================
    # FIND USER’S EXISTING REVIEW
    # =====================================================================
    def find_user_review(self, product_oid, product_str, username):
        if not self.collection:
            return None

        try:
            return self.collection.find_one({
                "$or": [
                    {"product_id": product_oid},
                    {"product_id": product_str}
                ],
                "user": username
            })
        except Exception as e:
            print(f"⚠ WARNING: Failed to lookup review for user '{username}':", e)
            return None

    # =====================================================================
    # INSERT REVIEW
    # =====================================================================
    def insert_review(self, product_oid, username, rating, review_text):
        if not self.collection:
            return None

        doc = {
            "product_id": product_oid,
            "user": username,
            "rating": rating,
            "review": review_text,
            "created_at": datetime.datetime.utcnow()
        }

        try:
            return self.collection.insert_one(doc)
        except Exception as e:
            print("❌ ERROR: Failed to insert review:", e)
            return None

    # =====================================================================
    # UPDATE REVIEW
    # =====================================================================
    def update_review(self, review_id, product_oid, rating, review_text):
        if not self.collection:
            return None

        # Validate ObjectId
        try:
            oid = review_id if isinstance(review_id, ObjectId) else ObjectId(review_id)
        except bson_errors.InvalidId:
            print(f"⚠ WARNING: Invalid review ID '{review_id}'")
            return None
        except Exception as e:
            print("⚠ WARNING: Review ID error:", e)
            return None

        update_doc = {
            "product_id": product_oid,
            "rating": rating,
            "review": review_text,
            "updated_at": datetime.datetime.utcnow()
        }

        try:
            return self.collection.update_one({"_id": oid}, {"$set": update_doc})
        except Exception as e:
            print(f"❌ ERROR: Failed to update review '{review_id}':", e)
            return None

    # =====================================================================
    # DELETE REVIEW
    # =====================================================================
    def delete_review(self, review_id):
        if not self.collection:
            return None

        try:
            oid = review_id if isinstance(review_id, ObjectId) else ObjectId(review_id)
        except bson_errors.InvalidId:
            print(f"⚠ WARNING: Invalid review ID '{review_id}'")
            return None
        except Exception as e:
            print("⚠ WARNING: Review ID error on delete:", e)
            return None

        try:
            return self.collection.delete_one({"_id": oid})
        except Exception as e:
            print(f"⚠ WARNING: Failed to delete review '{review_id}':", e)
            return None

    # =====================================================================
    # GET ALL REVIEWS FOR PRODUCT
    # =====================================================================
    def get_product_reviews(self, product_oid, product_str):
        if not self.collection:
            return []

        try:
            return list(self.collection.find({
                "$or": [
                    {"product_id": product_oid},
                    {"product_id": product_str}
                ]
            }))
        except Exception as e:
            print("⚠ WARNING: Failed to fetch reviews for product:", e)
            return []
