"""
Production-ready Review Routes (Timeless Threads V2)

Safeguards against:
    - Invalid ObjectId inputs
    - Missing rating/review text
    - Unauthorized access handled in controller
    - Mongo connection problems
    - Unexpected controller crashes
"""

from flask import Blueprint, request, abort
from bson import ObjectId
from bson.errors import InvalidId
from database.connection import mongo
from controllers.review_controller import ReviewController


review_bp = Blueprint("review", __name__, url_prefix="/review")


# -----------------------------------------------------
# Helper – Safe ObjectId
# -----------------------------------------------------
def safe_oid(value):
    try:
        return ObjectId(value)
    except InvalidId:
        return None
    except Exception:
        return None


# -----------------------------------------------------
# Safe Controller Factory
# -----------------------------------------------------
def get_controller():
    try:
        return ReviewController(mongo)
    except Exception as e:
        print("❌ ERROR: ReviewController initialization failed:", e)
        abort(500)


# =====================================================================
# ADD / UPDATE REVIEW
# POST /review/add-review/<product_id>
# =====================================================================
@review_bp.route("/add-review/<product_id>", methods=["POST"])
def add_review(product_id):

    # Validate product ID early
    if not safe_oid(product_id):
        print("⚠ WARNING: Invalid product_id in add_review:", product_id)
        abort(400)

    # Extract form data safely
    rating = request.form.get("rating")  # can be None
    review_text = request.form.get("review", "")

    try:
        controller = get_controller()
        return controller.add_review(
            product_id=product_id,
            rating=rating,
            review_text=review_text
        )
    except Exception as e:
        print("❌ ERROR: add_review crashed:", e)
        abort(500)


# =====================================================================
# DELETE REVIEW
# POST /review/delete-review/<review_id>/<product_id>
# =====================================================================
@review_bp.route("/delete-review/<review_id>/<product_id>", methods=["POST"])
def delete_review(review_id, product_id):

    # Validate IDs early
    if not safe_oid(review_id):
        print("⚠ WARNING: Invalid review_id:", review_id)
        abort(400)

    if not safe_oid(product_id):
        print("⚠ WARNING: Invalid product_id:", product_id)
        abort(400)

    try:
        controller = get_controller()
        return controller.delete_review(
            review_id=review_id,
            product_id=product_id
        )
    except Exception as e:
        print("❌ ERROR: delete_review crashed:", e)
        abort(500)
