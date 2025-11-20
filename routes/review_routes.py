from flask import Blueprint, request
from database.connection import mongo
from controllers.review_controller import ReviewController

# ---------------------------------------------------------
# REVIEW BLUEPRINT
#
# Handles user-generated product reviews:
#   - Adding a new review
#   - Updating existing review (handled inside controller)
#   - Deleting a review
#
# All logic is delegated to ReviewController to keep routes clean.
# ---------------------------------------------------------
review_bp = Blueprint("review", __name__)
controller = ReviewController(mongo)


# ---------------------------------------------------------
# ADD OR UPDATE REVIEW
#
# URL: POST /review/add-review/<product_id>
#
# Sends the following data to the controller:
#   - product_id       (from URL)
#   - rating           (from form)
#   - review text      (from form, optional)
#
# The controller automatically:
#   - Validates rating
#   - Ensures user is logged in
#   - Determines if this is a NEW review or UPDATE
#   - Stores data in MongoDB
#
# After submission, user is redirected to product detail page.
# ---------------------------------------------------------
@review_bp.route("/add-review/<product_id>", methods=["POST"])
def add_review(product_id):
    return controller.add_review(
        product_id,
        request.form.get("rating"),
        request.form.get("review", "")  # default empty string if no review text provided
    )


# ---------------------------------------------------------
# DELETE REVIEW
#
# URL: POST /review/delete-review/<review_id>/<product_id>
#
# Steps handled by controller:
#   - Validates login
#   - Validates review_id format
#   - Deletes review from MongoDB
#   - Redirects back to product detail page
#
# review_id → ID of the review to delete  
# product_id → Used for redirecting after deletion
# ---------------------------------------------------------
@review_bp.route("/delete-review/<review_id>/<product_id>", methods=["POST"])
def delete_review(review_id, product_id):
    return controller.delete_review(review_id, product_id)
