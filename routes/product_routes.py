"""
Production-ready Product Routes for Timeless Threads V2.

Hardened against:
    - Invalid product/category slugs
    - Bad ObjectId values
    - Missing Mongo collections
    - Product/Category not found errors
    - Ads service failures
    - Broken image arrays
    - Price calculation errors
    - Review aggregation failures

Template behavior remains unchanged.
"""

from flask import Blueprint, render_template, abort, request
from bson import ObjectId
from bson.errors import InvalidId
from database.connection import get_collection
from api.ads.loader import load_ads_for_slots

product_bp = Blueprint("product", __name__, url_prefix="")


# ----------------------------------------------------------------------
# SAFE OBJECTID PARSER
# ----------------------------------------------------------------------
def safe_oid(value):
    try:
        return ObjectId(value)
    except InvalidId:
        return None
    except Exception:
        return None


# ======================================================================
# CATEGORY PAGE
# ======================================================================
@product_bp.route("/category/<slug_or_id>")
def category_page(slug_or_id):

    try:
        categories = get_collection("categories")
        products = get_collection("products")
    except Exception as e:
        print("❌ ERROR: Collections unavailable:", e)
        abort(500)

    category = None

    # First try slug
    try:
        category = categories.find_one({"slug": slug_or_id})
    except Exception as e:
        print("⚠ WARNING: slug category lookup failed:", e)

    # Fallback ObjectId
    if not category:
        oid = safe_oid(slug_or_id)
        if oid:
            try:
                category = categories.find_one({"_id": oid})
            except Exception as e:
                print("⚠ WARNING: category ObjectId lookup failed:", e)

    if not category:
        abort(404)

    # Fetch products in this category
    try:
        items = list(
            products.find({"category_id": str(category["_id"])}).sort("created_at", -1)
        )
    except Exception as e:
        print("⚠ WARNING: product lookup failed:", e)
        items = []

    # Load ads safely
    try:
        ads = load_ads_for_slots(["card_small", "product_inline"])
    except Exception as e:
        print("⚠ WARNING: Ad loader error:", e)
        ads = {}

    return render_template(
        "category.html",
        category=category,
        products=items,
        ads=ads
    )


# ======================================================================
# PRODUCT DETAIL PAGE
# ======================================================================
@product_bp.route("/product/<slug_or_id>")
def product_detail(slug_or_id):

    try:
        products_col = get_collection("products")
        reviews_col = get_collection("reviews")
    except Exception as e:
        print("❌ ERROR: Cannot load Mongo collections:", e)
        abort(500)

    product = None

    # By slug
    try:
        product = products_col.find_one({"slug": slug_or_id})
    except Exception as e:
        print("⚠ WARNING: product slug lookup failed:", e)

    # By ObjectId
    if not product:
        oid = safe_oid(slug_or_id)
        if oid:
            try:
                product = products_col.find_one({"_id": oid})
            except Exception as e:
                print("⚠ WARNING: product ObjectId lookup failed:", e)

    if not product:
        abort(404)

    # ---------------------------------------------------------
    # CLEAN IMAGES
    # ---------------------------------------------------------
    def clean(v):
        if not v or not isinstance(v, str):
            return None
        v = v.replace("\\", "/").strip()
        return v.split("/")[-1]

    images = []
    try:
        raw = product.get("images") or []
        for im in raw:
            fn = clean(im)
            if fn and fn not in images:
                images.append(fn)

        # ensure single-image fields don't get lost
        for f in ["primary_image", "image", "image2", "image3"]:
            fn = clean(product.get(f))
            if fn and fn not in images:
                images.append(fn)

        if not images:
            images = ["no_image.jpg"]

        product["__images"] = images

    except Exception as e:
        print("⚠ WARNING: image normalization failed:", e)
        product["__images"] = ["no_image.jpg"]

    # ---------------------------------------------------------
    # PRICING CALCULATION
    # ---------------------------------------------------------
    mrp = None
    try:
        if product.get("discount"):
            mrp = int(product["price"] / (1 - product["discount"] / 100))
    except Exception:
        mrp = None

    # ---------------------------------------------------------
    # LOAD REVIEWS
    # ---------------------------------------------------------
    reviews = []
    avg_rating = None

    try:
        pid = product["_id"]
        pid_str = str(pid)

        reviews = list(
            reviews_col.find({
                "$or": [
                    {"product_id": pid},
                    {"product_id": pid_str}
                ]
            }).sort("created_at", -1)
        )

        if reviews:
            total = sum(int(r.get("rating", 0)) for r in reviews)
            avg_rating = round(total / len(reviews), 1)

    except Exception as e:
        print("⚠ WARNING: failed loading reviews:", e)

    # ---------------------------------------------------------
    # LOAD ADS
    # ---------------------------------------------------------
    try:
        ads = load_ads_for_slots([
            "product_detail_banner",
            "product_inline",
            "card_small"
        ])
    except Exception as e:
        print("⚠ WARNING: ad loading failed:", e)
        ads = {}

    # ---------------------------------------------------------
    # RENDER TEMPLATE
    # ---------------------------------------------------------
    return render_template(
        "product_detail.html",
        product=product,
        mrp=mrp,
        reviews=reviews,
        avg_rating=avg_rating,
        review_count=len(reviews),
        ads=ads
    )


# ======================================================================
# SEARCH PAGE
# ======================================================================
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
                prod_col.find({
                    "name": {"$regex": q, "$options": "i"}
                }).limit(50)
            )
        except Exception as e:
            print("⚠ WARNING: search query failed:", e)

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
