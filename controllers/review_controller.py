from flask import flash, redirect, url_for, session
from bson import ObjectId
import datetime
from models.review_model import ReviewModel


class ReviewController:
    def __init__(self, mongo):
        # ReviewModel handles all review-related database operations
        self.model = ReviewModel(mongo)
        self.mongo = mongo

    # --------------------------------------------------
    # ADD / UPDATE REVIEW
    #
    # Handles both creating a new review and updating an
    # existing one. The logic automatically detects whether
    # the user already reviewed the product.
    #
    # Steps:
    #   1. User must be logged in.
    #   2. Validate rating (1–5).
    #   3. Normalize product_id to ObjectId + string.
    #   4. Check if user has already reviewed.
    #   5. Update if exists, insert if new.
    #   6. Redirect back to product page.
    # --------------------------------------------------
    def add_review(self, product_id, rating, review_text):

        # Ensure user is logged in
        if "user" not in session:
            flash("Please log in to review.", "warning")
            return redirect(url_for("auth.login"))

        username = session["user"]

        # --------------------------------------------------
        # Validate rating input
        # Rating must be convertible to int and in range 1–5
        # --------------------------------------------------
        if not rating:
            flash("Please select a rating.", "warning")
            return redirect(url_for("product.product_detail", product_id=product_id))

        try:
            rating = int(rating)
        except ValueError:
            flash("Invalid rating.", "danger")
            return redirect(url_for("product.product_detail", product_id=product_id))

        if rating < 1 or rating > 5:
            flash("Rating must be between 1 and 5 stars.", "danger")
            return redirect(url_for("product.product_detail", product_id=product_id))

        # Clean up review text (optional)
        review_text = review_text.strip() if review_text else None

        # --------------------------------------------------
        # Convert product_id to ObjectId safely
        # --------------------------------------------------
        try:
            product_oid = ObjectId(product_id)
        except:
            flash("Invalid product ID.", "danger")
            return redirect(url_for("main.home"))

        # Support reviews stored with ID as string OR ObjectId
        product_str = str(product_oid)

        # --------------------------------------------------
        # Check if this user has already reviewed this product
        # --------------------------------------------------
        existing_review = self.model.find_user_review(
            product_oid,
            product_str,
            username
        )

        # --------------------------------------------------
        # UPDATE EXISTING REVIEW
        # --------------------------------------------------
        if existing_review:
            self.model.update_review(
                existing_review["_id"],  # review document ID
                product_oid,
                rating,
                review_text
            )
            flash("Review updated!", "success")

        # --------------------------------------------------
        # INSERT NEW REVIEW
        # --------------------------------------------------
        else:
            self.model.insert_review(
                product_oid,
                username,
                rating,
                review_text
            )
            flash("Review submitted!", "success")

        return redirect(url_for("product.product_detail", product_id=product_id))

    # --------------------------------------------------
    # DELETE REVIEW
    #
    # Deletes a review by its ID. Only checks that user
    # is logged in; permission checks (if needed) should
    # be implemented inside ReviewModel or added later.
    #
    # Steps:
    #   1. User must be logged in.
    #   2. Convert review_id to ObjectId.
    #   3. Delete review.
    #   4. Redirect back to product page.
    # --------------------------------------------------
    def delete_review(self, review_id, product_id):

        # User must be logged in to delete
        if "user" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))

        # Validate review ID
        try:
            review_oid = ObjectId(review_id)
        except:
            flash("Invalid review ID.", "danger")
            return redirect(url_for("product.product_detail", product_id=product_id))

        # Perform deletion through ReviewModel
        self.model.delete_review(review_oid)

        flash("Review deleted.", "success")
        return redirect(url_for("product.product_detail", product_id=product_id))
