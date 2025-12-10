"""
Production-ready Review Routes

Protects against:
    - Invalid product_id / review_id
    - Missing form fields
    - Controller failures
    - Mongo connection errors
    - Bad request data

Route paths remain unchanged.
"""

from flask import Blueprint, request, abort
from bson import ObjectId, errors as bson_errors
from database.connection import mongo
from controllers.review_controller import ReviewController


review_bp = Blueprint("review", __name__)


# ---------------------------------------------------------
# Safe controller factory
# ---------------------------------------------------------
def get_controller():
    try:
        return ReviewController(mongo)
    except Exception as e:
        print("❌ ReviewController creation failed:", e)
        abort(500)


# ---------------------------------------------------------
# Helper — Safe ObjectId
# ---------------------------------------------------------
def safe_oid(value):
    try:
        return ObjectId(value)
    except bson_errors.InvalidId:
        return None
    except Exception:
        return None


# ---------------------------------------------------------
# ADD / UPDATE REVIEW
# URL: POST /review/add-review/<product_id>
# ---------------------------------------------------------
@review_bp.route("/add-review/<product_id>", methods=["POST"])
def add_review(product_id):

    # Validate product_id early to avoid unnecessary DB calls
    if not safe_oid(product_id):
        abort(400)   # bad request, not found

    rating = request.form.get("rating")
    review_text = request.form.get("review", "")

    try:
        controller = get_controller()
        return controller.add_review(
            product_id=product_id,
            rating=rating,
            review_text=review_text
        )
    except Exception as e:
        print("❌ ERROR: add_review failed:", e)
        abort(500)


# ---------------------------------------------------------
# DELETE REVIEW
# URL: POST /review/delete-review/<review_id>/<product_id>
# ---------------------------------------------------------
@review_bp.route("/delete-review/<review_id>/<product_id>", methods=["POST"])
def delete_review(review_id, product_id):

    if not safe_oid(review_id) or not safe_oid(product_id):
        abort(400)

    try:
        controller = get_controller()
        return controller.delete_review(
            review_id=review_id,
            product_id=product_id
        )
    except Exception as e:
        print("❌ ERROR: delete_review failed:", e)
        abort(500)
