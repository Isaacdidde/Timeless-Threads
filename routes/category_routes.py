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
from flask import current_app
from bson import ObjectId
from bson.errors import InvalidId
from database.connection import get_collection
from api.ads.loader import load_ads_for_slots   # ⭐ Fetch ads via ads_client (Dcorp API)

# 🔥 This is the ONLY category route prefix
category_bp = Blueprint("category", __name__, url_prefix="/category")


# ----------------------------------------------------------------------
# SAFE OBJECTID PARSER
# ----------------------------------------------------------------------
def safe_oid(value):
    """Safely returns ObjectId or None."""
    try:
        return ObjectId(value)
    except InvalidId:
        return None
    except Exception:
        return None


# ----------------------------------------------------------------------
# CATEGORY PAGE — official endpoint = category.show_category
# ----------------------------------------------------------------------
@category_bp.route("/<slug_or_id>")
def show_category(slug_or_id):

    # ------------------------------------------------------------------
    # Load MongoDB collections
    # ------------------------------------------------------------------
    try:
        cat_col = get_collection("categories")
        prod_col = get_collection("products")
    except Exception as e:
        print("❌ ERROR: Failed to load Mongo collections:", e)
        abort(500)

    # ------------------------------------------------------------------
    # Lookup category by slug
    # ------------------------------------------------------------------
    category = None
    try:
        category = cat_col.find_one({"slug": slug_or_id})
    except Exception as e:
        print("⚠ WARNING: Category slug lookup failed:", e)

    # ------------------------------------------------------------------
    # Fallback: lookup by ObjectId
    # ------------------------------------------------------------------
    if not category:
        oid = safe_oid(slug_or_id)
        if oid:
            try:
                category = cat_col.find_one({"_id": oid})
            except Exception as e:
                print("⚠ WARNING: Category ObjectId lookup failed:", e)

    # ------------------------------------------------------------------
    # If still not found → 404
    # ------------------------------------------------------------------
    if not category:
        abort(404)

    # ------------------------------------------------------------------
    # Load products for this category
    # ------------------------------------------------------------------
    products = []
    try:
        products = list(
            prod_col
            .find({"category_id": str(category["_id"])})
            .sort("created_at", -1)
        )
    except Exception as e:
        print(f"⚠ WARNING: Failed fetching products for category '{slug_or_id}':", e)

    # ------------------------------------------------------------------
    # LOAD ADS FROM DCORP (using ads_client under the hood)
    # ------------------------------------------------------------------
    try:
        ads = load_ads_for_slots([
            "product_inline",
            "card_small",
        ])

        # Get the card_small ad directly
        small_ad = ads.get("card_small")

        # If your Dcorp API returns None → no eligible ads
        # If ad exists → will be a dict with full creative details

    except Exception as e:
        print("⚠ WARNING: Failed loading ads for category:", e)
        ads = {}
        small_ad = None

    # ------------------------------------------------------------------
    # Render template
    # ------------------------------------------------------------------
    try:
        return render_template(
            "category.html",
            category=category,
            products=products,
            ads=ads,
            small_ad=small_ad,
            dcorp_api=current_app.config.get("DCORP_API_URL", "")
)

    except Exception as e:
        print("❌ ERROR: Failed to render category.html:", e)
        abort(500)
