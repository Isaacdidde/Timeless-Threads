from flask import flash, redirect, url_for, session
from bson import ObjectId, errors as bson_errors
from models.review_model import ReviewModel


class ReviewController:
    def __init__(self, mongo):
        try:
            self.model = ReviewModel(mongo)
            self.mongo = mongo
        except Exception as e:
            print("❌ ERROR: Failed to initialize ReviewModel:", e)
            self.model = None
            self.mongo = None

    # ======================================================
    # ADD OR UPDATE REVIEW (Production-Safe)
    # ======================================================
    def add_review(self, product_id, rating, review_text):

        # -------------------------------------------------
        # 1. Ensure user is logged in
        # -------------------------------------------------
        username = session.get("user") or session.get("user_name")
        if not username:
            flash("Please log in to review.", "warning")
            return redirect(url_for("auth.login"))

        # -------------------------------------------------
        # 2. Validate rating
        # -------------------------------------------------
        if rating is None or rating == "":
            flash("Please select a rating.", "warning")
            return redirect(url_for("product.product_detail", product_id=product_id))

        try:
            rating = int(rating)
        except Exception:
            flash("Invalid rating.", "danger")
            return redirect(url_for("product.product_detail", product_id=product_id))

        if rating < 1 or rating > 5:
            flash("Rating must be between 1 and 5.", "danger")
            return redirect(url_for("product.product_detail", product_id=product_id))

        review_text = review_text.strip() if review_text else None

        # -------------------------------------------------
        # 3. Normalize product ID
        # -------------------------------------------------
        try:
            product_oid = ObjectId(product_id)
        except bson_errors.InvalidId:
            flash("Invalid product ID.", "danger")
            return redirect(url_for("main.home"))
        except Exception as e:
            print("❌ ERROR: Invalid product ObjectId:", e)
            flash("Invalid product.", "danger")
            return redirect(url_for("main.home"))

        product_str = str(product_oid)

        # -------------------------------------------------
        # 4. Ensure model is available
        # -------------------------------------------------
        if not self.model:
            flash("Review system unavailable.", "danger")
            return redirect(url_for("product.product_detail", product_id=product_id))

        # -------------------------------------------------
        # 5. Check if user already reviewed
        # -------------------------------------------------
        try:
            existing_review = self.model.find_user_review(
                product_oid,
                product_str,
                username
            )
        except Exception as e:
            print("⚠ WARNING: Review lookup failed:", e)
            existing_review = None

        # -------------------------------------------------
        # 6. Update the review
        # -------------------------------------------------
        if existing_review:
            try:
                self.model.update_review(
                    existing_review["_id"],
                    product_oid,
                    rating,
                    review_text
                )
                flash("Review updated!", "success")
            except Exception as e:
                print("❌ ERROR: Failed to update review:", e)
                flash("Failed to update review.", "danger")

        # -------------------------------------------------
        # 7. Insert new review
        # -------------------------------------------------
        else:
            try:
                self.model.insert_review(
                    product_oid,
                    username,
                    rating,
                    review_text
                )
                flash("Review submitted!", "success")
            except Exception as e:
                print("❌ ERROR: Failed to submit review:", e)
                flash("Failed to submit review.", "danger")

        # -------------------------------------------------
        # 8. Redirect back to product page
        # -------------------------------------------------
        return redirect(url_for("product.product_detail", product_id=product_id))

    # ======================================================
    # DELETE REVIEW (Production-Safe)
    # ======================================================
    def delete_review(self, review_id, product_id):

        # Require login
        username = session.get("user") or session.get("user_name")
        if not username:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))

        # Validate ID
        try:
            review_oid = ObjectId(review_id)
        except bson_errors.InvalidId:
            flash("Invalid review ID.", "danger")
            return redirect(url_for("product.product_detail", product_id=product_id))
        except Exception as e:
            print("❌ ERROR: Invalid review ObjectId:", e)
            flash("Invalid review.", "danger")
            return redirect(url_for("product.product_detail", product_id=product_id))

        # Ensure model is usable
        if not self.model:
            flash("Review system unavailable.", "danger")
            return redirect(url_for("product.product_detail", product_id=product_id))

        # Delete review safely
        try:
            self.model.delete_review(review_oid)
            flash("Review deleted.", "success")
        except Exception as e:
            print("⚠ WARNING: Failed to delete review:", e)
            flash("Unable to delete review.", "danger")

        return redirect(url_for("product.product_detail", product_id=product_id))
