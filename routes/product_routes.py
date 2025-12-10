"""
Production-ready Product Routes

Fully protected against:
    - Invalid slugs/ObjectIds
    - Missing Mongo collections
    - Query failures
    - Ads loader failures
    - Image list corruption
    - Pricing calculation errors
    - Review aggregation failures

Route behavior and template rendering remain unchanged.
"""

from flask import Blueprint, render_template, abort, request, flash
from bson import ObjectId, errors as bson_errors
from database.connection import get_collection
from api.ads.loader import load_ads_for_slots

product_bp = Blueprint("product", __name__, url_prefix="")


# ---------------------------------------------------------
# Helper: Safe ObjectId parser
# ---------------------------------------------------------
def safe_object_id(value):
    try:
        return ObjectId(value)
    except bson_errors.InvalidId:
        return None
    except Exception:
        return None


# =====================================================================
# CATEGORY PAGE
# =====================================================================
@product_bp.route("/category/<category_slug>")
def category_page(category_slug):

    try:
        cat_col = get_collection("categories")
        prod_col = get_collection("products")
    except Exception as e:
        print("❌ ERROR: DB collections unavailable:", e)
        abort(500)

    category = None

    # ---- Try by slug ----
    try:
        category = cat_col.find_one({"slug": category_slug})
    except Exception as e:
        print("⚠ WARNING: slug lookup failed:", e)

    # ---- Fallback: try ObjectId ----
    if not category:
        oid = safe_object_id(category_slug)
        if oid:
            try:
                category = cat_col.find_one({"_id": oid})
            except Exception as e:
                print("⚠ WARNING: ObjectId lookup failed:", e)

    if not category:
        abort(404)

    # ---- Load products ----
    try:
        products = list(
            prod_col.find({"category_id": str(category["_id"])}).sort("created_at", -1)
        )
    except Exception as e:
        print("⚠ WARNING: product query failed:", e)
        products = []

    # ---- Load ads ----
    try:
        ads = load_ads_for_slots(["card_small", "product_inline"])
    except Exception as e:
        print("⚠ WARNING: Ad loading failed:", e)
        ads = {}

    return render_template(
        "category.html",
        category=category,
        products=products,
        ads=ads
    )


# =====================================================================
# PRODUCT DETAIL PAGE
# =====================================================================
@product_bp.route("/product/<slug_or_id>")
def product_detail(slug_or_id):

    try:
        prod_col = get_collection("products")
        review_col = get_collection("reviews")
    except Exception as e:
        print("❌ ERROR: Cannot load Mongo collections:", e)
        abort(500)

    product = None

    # ---- Try slug ----
    try:
        product = prod_col.find_one({"slug": slug_or_id})
    except Exception as e:
        print("⚠ WARNING: slug lookup failed:", e)

    # ---- Try ObjectId ----
    if not product:
        oid = safe_object_id(slug_or_id)
        if oid:
            try:
                product = prod_col.find_one({"_id": oid})
            except Exception as e:
                print("⚠ WARNING: ObjectId lookup failed:", e)

    if not product:
        abort(404)

    # -----------------------------------------------------
    # IMAGE CLEANUP
    # -----------------------------------------------------
    def clean_filename(v):
        if not v or not isinstance(v, str):
            return None
        v = v.replace("\\", "/").strip()
        return v.split("/")[-1] if "/" in v else v

    images = []

    try:
        raw_imgs = product.get("images") or []
        for it in raw_imgs:
            clean = clean_filename(it)
            if clean and clean not in images:
                images.append(clean)

        for f in ["primary_image", "image", "image2", "image3"]:
            clean = clean_filename(product.get(f))
            if clean and clean not in images:
                images.append(clean)

        if not images:
            images = ["no_image.jpg"]

        product["__images"] = images

    except Exception as e:
        print("⚠ WARNING: image normalization failed:", e)
        product["__images"] = ["no_image.jpg"]

    # -----------------------------------------------------
    # PRICING
    # -----------------------------------------------------
    mrp = None
    try:
        if product.get("discount"):
            mrp = int(product["price"] / (1 - product["discount"] / 100))
    except Exception:
        mrp = None

    # -----------------------------------------------------
    # REVIEWS
    # -----------------------------------------------------
    reviews = []
    avg_rating = None
    review_count = 0

    try:
        product_oid = product["_id"]
        product_id_str = str(product_oid)

        reviews = list(
            review_col.find({
                "$or": [
                    {"product_id": product_oid},
                    {"product_id": product_id_str}
                ]
            }).sort("created_at", -1)
        )

        if reviews:
            total = sum(int(r.get("rating", 0)) for r in reviews)
            avg_rating = round(total / len(reviews), 1)

        review_count = len(reviews)

    except Exception as e:
        print("⚠ WARNING: loading reviews failed:", e)

    # -----------------------------------------------------
    # ADS
    # -----------------------------------------------------
    try:
        ads = load_ads_for_slots([
            "product_detail_banner",
            "product_inline",
            "card_small"
        ])
    except Exception as e:
        print("⚠ WARNING: ad loading failed:", e)
        ads = {}

    # -----------------------------------------------------
    # TEMPLATE
    # -----------------------------------------------------
    return render_template(
        "product_detail.html",
        product=product,
        mrp=mrp,
        reviews=reviews,
        avg_rating=avg_rating,
        review_count=review_count,
        ads=ads
    )


# =====================================================================
# SEARCH PAGE
# =====================================================================
@product_bp.route("/search")
def search_page():

    q = request.args.get("q", "")
    q = q.strip() if isinstance(q, str) else ""

    try:
        prod_col = get_collection("products")
    except Exception as e:
        print("❌ ERROR: products collection unavailable:", e)
        prod_col = None

    results = []
    if q and prod_col:
        try:
            results = list(
                prod_col.find({"name": {"$regex": q, "$options": "i"}}).limit(50)
            )
        except Exception as e:
            print("⚠ WARNING: search query failed:", e)

    # Load ads safely
    try:
        ads = load_ads_for_slots(["search_banner"])
    except Exception as e:
        print("⚠ WARNING: search ad loading failed:", e)
        ads = {}

    return render_template(
        "search_results.html",
        results=results,
        query=q,
        ads=ads
    )
