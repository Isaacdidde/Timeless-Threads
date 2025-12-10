"""
Production-ready category routes for Timeless Threads V2.

Handles:
    - Missing DB connection
    - Invalid slugs
    - Invalid ObjectIds
    - Query failures
    - Unknown categories (clean 404)
    
Compatible with:
    - category.slug
    - category._id (fallback)
    - product.category_id (string ObjectId)
"""

from flask import Blueprint, render_template, abort
from bson import ObjectId
from bson.errors import InvalidId
from database.connection import get_collection

category_bp = Blueprint("category", __name__, url_prefix="/category")


# ----------------------------------------------------------------------
# SAFE OBJECTID PARSER
# ----------------------------------------------------------------------
def safe_oid(value):
    """Return ObjectId or None without raising exceptions."""
    try:
        return ObjectId(value)
    except InvalidId:
        return None
    except Exception:
        return None


# ----------------------------------------------------------------------
# CATEGORY PAGE (slug OR ObjectId)
# ----------------------------------------------------------------------
@category_bp.route("/<slug_or_id>")
def show_category(slug_or_id):

    # ------------------------------------------------------
    # Load DB collections safely
    # ------------------------------------------------------
    try:
        cat_col = get_collection("categories")
        prod_col = get_collection("products")
    except Exception as e:
        print("❌ ERROR: Failed to load collections:", e)
        abort(500)

    category = None

    # ------------------------------------------------------
    # 1. Try to match category by slug
    # ------------------------------------------------------
    try:
        category = cat_col.find_one({"slug": slug_or_id})
    except Exception as e:
        print("⚠ WARNING: Category slug lookup failed:", e)

    # ------------------------------------------------------
    # 2. Fallback → try ObjectId
    # ------------------------------------------------------
    if not category:
        oid = safe_oid(slug_or_id)
        if oid:
            try:
                category = cat_col.find_one({"_id": oid})
            except Exception as e:
                print("⚠ WARNING: Category ObjectId lookup failed:", e)

    # ------------------------------------------------------
    # 3. If still not found → clean 404
    # ------------------------------------------------------
    if not category:
        abort(404)

    # ------------------------------------------------------
    # 4. Fetch products in this category
    # ------------------------------------------------------
    products = []
    try:
        products = list(
            prod_col
            .find({"category_id": str(category["_id"])})
            .sort("created_at", -1)
        )
    except Exception as e:
        print(f"⚠ WARNING: Product query failed for category '{slug_or_id}':", e)

    # ------------------------------------------------------
    # 5. Render page safely
    # ------------------------------------------------------
    try:
        return render_template(
            "category.html",
            category=category,
            products=products
        )
    except Exception as e:
        print("❌ ERROR: Failed to render category.html:", e)
        abort(500)
