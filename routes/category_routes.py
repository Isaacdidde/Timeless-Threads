"""
Production-ready category routes.
Safe against:
    - Invalid slugs / ObjectIds
    - Missing DB collections
    - Query failures
    - Unexpected exceptions

Does NOT change route paths or template behavior.
"""

from flask import Blueprint, render_template, abort, flash
from bson import ObjectId, errors as bson_errors
from database.connection import get_collection

category_bp = Blueprint("category", __name__, url_prefix="/category")


# ----------------------------------------------------------------------
# Helper — safely parse ObjectId
# ----------------------------------------------------------------------
def safe_object_id(value):
    try:
        return ObjectId(value)
    except bson_errors.InvalidId:
        return None
    except Exception:
        return None


# ----------------------------------------------------------------------
# CATEGORY PAGE (slug OR ObjectId fallback)
# ----------------------------------------------------------------------
@category_bp.route("/<category_slug>")
def show_category(category_slug):

    try:
        cat_col = get_collection("categories")
        prod_col = get_collection("products")
    except Exception as e:
        print("❌ ERROR: failed to load Mongo collections:", e)
        abort(500)

    category = None

    # ---------------------------------------------------------------
    # 1. Try slug lookup first
    # ---------------------------------------------------------------
    try:
        category = cat_col.find_one({"slug": category_slug})
    except Exception as e:
        print("⚠ WARNING: category slug lookup failed:", e)

    # ---------------------------------------------------------------
    # 2. Fallback to ObjectId lookup
    # ---------------------------------------------------------------
    if not category:
        oid = safe_object_id(category_slug)
        if oid:
            try:
                category = cat_col.find_one({"_id": oid})
            except Exception as e:
                print("⚠ WARNING: category ObjectId lookup failed:", e)

    # ---------------------------------------------------------------
    # 3. If still not found → return clean 404
    # ---------------------------------------------------------------
    if not category:
        abort(404)

    # ---------------------------------------------------------------
    # 4. Fetch products inside this category
    # ---------------------------------------------------------------
    try:
        products = list(
            prod_col.find({"category_id": str(category["_id"])}).sort("created_at", -1)
        )
    except Exception as e:
        print("⚠ WARNING: product query failed:", e)
        products = []

    # ---------------------------------------------------------------
    # 5. Render page
    # ---------------------------------------------------------------
    return render_template(
        "category.html",
        category=category,
        products=products
    )
