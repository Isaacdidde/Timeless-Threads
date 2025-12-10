# models/review_model.py

from bson import ObjectId
from bson.errors import InvalidId
import datetime
from database.connection import get_collection


class ReviewModel:
    """
    Production-ready model for interacting with the 'reviews' collection.

    Provides:
        - Find review by user + product
        - Insert review
        - Update review
        - Delete review
        - Fetch all reviews for a product
    """

    def __init__(self, mongo):
        try:
            self.col = get_collection("reviews")
        except Exception as e:
            print("❌ ERROR: Cannot access 'reviews' collection:", e)
            self.col = None

    # =====================================================================
    # FIND USER’S EXISTING REVIEW
    # =====================================================================
    def find_user_review(self, product_oid, product_str, username):
        if not self.col:
            return None

        try:
            return self.col.find_one({
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
        if not self.col:
            return None

        doc = {
            "product_id": product_oid,
            "user": username,
            "rating": rating,
            "review": review_text,
            "created_at": datetime.datetime.utcnow()
        }

        try:
            return self.col.insert_one(doc)
        except Exception as e:
            print("❌ ERROR: Failed to insert review:", e)
            return None

    # =====================================================================
    # UPDATE REVIEW
    # =====================================================================
    def update_review(self, review_id, product_oid, rating, review_text):
        if not self.col:
            return None

        # Validate ObjectId
        try:
            oid = review_id if isinstance(review_id, ObjectId) else ObjectId(review_id)
        except InvalidId:
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
            return self.col.update_one({"_id": oid}, {"$set": update_doc})
        except Exception as e:
            print(f"❌ ERROR: Failed to update review '{review_id}':", e)
            return None

    # =====================================================================
    # DELETE REVIEW
    # =====================================================================
    def delete_review(self, review_id):
        if not self.col:
            return None

        try:
            oid = review_id if isinstance(review_id, ObjectId) else ObjectId(review_id)
        except InvalidId:
            print(f"⚠ WARNING: Invalid review ID '{review_id}'")
            return None
        except Exception as e:
            print("⚠ WARNING: Review ID error on delete:", e)
            return None

        try:
            return self.col.delete_one({"_id": oid})
        except Exception as e:
            print(f"⚠ WARNING: Failed to delete review '{review_id}':", e)
            return None

    # =====================================================================
    # GET ALL REVIEWS FOR A PRODUCT
    # =====================================================================
    def get_product_reviews(self, product_oid, product_str):
        if not self.col:
            return []

        try:
            return list(self.col.find({
                "$or": [
                    {"product_id": product_oid},
                    {"product_id": product_str}
                ]
            }))
        except Exception as e:
            print("⚠ WARNING: Failed to fetch reviews for product:", e)
            return []
