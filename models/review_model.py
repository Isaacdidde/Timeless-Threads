from bson import ObjectId
import datetime


class ReviewModel:
    """
    Model layer for interacting with the 'reviews' collection.
    Handles:
        - Finding reviews
        - Creating new reviews
        - Updating reviews
        - Deleting reviews
        - Fetching all reviews for a given product

    Supports both ObjectId and string-based product_id formats
    for backward compatibility.
    """

    def __init__(self, mongo):
        # Bind to the 'reviews' collection in MongoDB
        self.collection = mongo.db.reviews

    # ---------------------------------------------------------
    # FIND USER’S EXISTING REVIEW FOR A PRODUCT
    #
    # Accepts both ObjectId and string versions of product ID
    # because old records might have mixed formats.
    #
    # Returns:
    #   - A single review document if found
    #   - None if the user has not reviewed this product yet
    # ---------------------------------------------------------
    def find_user_review(self, product_oid, product_str, username):
        return self.collection.find_one({
            "$or": [
                {"product_id": product_oid},
                {"product_id": product_str}
            ],
            "user": username
        })

    # ---------------------------------------------------------
    # INSERT NEW REVIEW
    #
    # Stores:
    #   - product ID
    #   - username
    #   - rating (1–5)
    #   - optional text review
    #   - created timestamp
    # ---------------------------------------------------------
    def insert_review(self, product_oid, username, rating, review_text):
        return self.collection.insert_one({
            "product_id": product_oid,
            "user": username,
            "rating": rating,
            "review": review_text,
            "created_at": datetime.datetime.utcnow()
        })

    # ---------------------------------------------------------
    # UPDATE EXISTING REVIEW
    #
    # Updates rating and review text while also recording the
    # update timestamp. Does not modify the username.
    # ---------------------------------------------------------
    def update_review(self, review_id, product_oid, rating, review_text):
        return self.collection.update_one(
            {"_id": review_id},
            {"$set": {
                "product_id": product_oid,
                "rating": rating,
                "review": review_text,
                "updated_at": datetime.datetime.utcnow()
            }}
        )

    # ---------------------------------------------------------
    # DELETE REVIEW
    #
    # Removes a review document from the database using its ID.
    # ---------------------------------------------------------
    def delete_review(self, review_id):
        return self.collection.delete_one({"_id": review_id})

    # ---------------------------------------------------------
    # GET ALL REVIEWS FOR A PRODUCT
    #
    # Supports both ObjectId and string-based product IDs.
    #
    # Returns:
    #   - A list of all matching reviews
    # ---------------------------------------------------------
    def get_product_reviews(self, product_oid, product_str):
        return list(self.collection.find({
            "$or": [
                {"product_id": product_oid},
                {"product_id": product_str}
            ]
        }))
