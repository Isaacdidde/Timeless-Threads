from flask import render_template, flash, redirect, url_for, abort
from bson import ObjectId, errors as bson_errors
from models.product_model import ProductModel

# 🔥 AD SYSTEM
from api.ads.loader import load_ads_for_slots
from database.connection import get_collection


class ProductController:
    def __init__(self, mongo):
        try:
            self.mongo = mongo
            self.products = ProductModel(mongo)
        except Exception as e:
            print("❌ ERROR: Failed to initialize ProductModel:", e)
            self.mongo = None
            self.products = None

    # ==================================================================
    # PRODUCT DETAIL PAGE (Production-Hardened)
    # ==================================================================
    def product_detail(self, product_id, normalize_cart_func):
        # Normalize cart session safely
        try:
            normalize_cart_func()
        except Exception as e:
            print("⚠ WARNING: normalize_cart_func failed:", e)

        # ---------------------------------------------------------------
        # Validate / Fetch Product
        # ---------------------------------------------------------------
        if not self.mongo:
            abort(500, "Database unavailable")

        # Validate ObjectId
        try:
            oid = ObjectId(product_id)
        except bson_errors.InvalidId:
            flash("Invalid product ID.", "danger")
            return redirect(url_for("main.home"))

        # DB lookup
        try:
            product = self.mongo.db.products.find_one({"_id": oid})
        except Exception as e:
            print("❌ ERROR: Product lookup failed:", e)
            flash("Unable to load product.", "danger")
            return redirect(url_for("main.home"))

        if not product:
            flash("Product not found.", "warning")
            return redirect(url_for("main.home"))

        # ---------------------------------------------------------------
        # IMAGE NORMALIZATION
        # ---------------------------------------------------------------
        def normalize_filename(v):
            if not v or not isinstance(v, str):
                return None
            v = v.strip().replace("\\", "/")
            fname = v.split("/")[-1]
            return fname if len(fname) > 3 else None

        images = []

        # A) list field
        raw_imgs = product.get("images") or []
        if isinstance(raw_imgs, list):
            for it in raw_imgs:
                fname = normalize_filename(it)
                if fname and fname not in images:
                    images.append(fname)

        # B) single fields
        for field in ["primary_image", "image", "image2", "image3"]:
            fname = normalize_filename(product.get(field))
            if fname and fname not in images:
                images.append(fname)

        # C) fallback
        if not images:
            images = ["no_image.jpg"]

        product["__images"] = images

        # ---------------------------------------------------------------
        # PRICING CALCULATION
        # ---------------------------------------------------------------
        mrp = None
        try:
            if product.get("discount"):
                mrp = int(product["price"] / (1 - product["discount"] / 100))
        except Exception:
            mrp = None

        # ---------------------------------------------------------------
        # REVIEWS
        # ---------------------------------------------------------------
        try:
            review_col = get_collection("reviews")
        except Exception as e:
            print("⚠ WARNING: reviews collection unavailable:", e)
            review_col = None

        reviews = []
        avg_rating = None
        review_count = 0

        if review_col:
            try:
                reviews = list(
                    review_col.find({
                        "$or": [
                            {"product_id": oid},
                            {"product_id": str(oid)}
                        ]
                    }).sort("created_at", -1)
                )
            except Exception as e:
                print("⚠ WARNING: Could not fetch reviews:", e)
                reviews = []

        # Rating summary
        if reviews:
            try:
                total = sum(int(r.get("rating", 0)) for r in reviews)
                review_count = len(reviews)
                avg_rating = round(total / review_count, 1)
            except Exception:
                avg_rating = None
                review_count = len(reviews)

        # ---------------------------------------------------------------
        # LOAD ADS (Fault-Tolerant)
        # ---------------------------------------------------------------
        try:
            ads = load_ads_for_slots([
                "product_detail_banner",
                "product_inline",
            ])
        except Exception as e:
            print("⚠ WARNING: Failed to load ads for product detail:", e)
            ads = {}

        # ---------------------------------------------------------------
        # RENDER PAGE (Safe)
        # ---------------------------------------------------------------
        try:
            return render_template(
                "product_detail.html",
                product=product,
                mrp=mrp,
                reviews=reviews,
                avg_rating=avg_rating,
                review_count=review_count,
                ads=ads
            )
        except Exception as e:
            print("❌ ERROR: Failed to render product detail template:", e)
            abort(500, "Rendering error")

    # ==================================================================
    # CATEGORY VIEW (Same Logic, Production Safety Added)
    # ==================================================================
    def category_view(self, category_name, normalize_cart_func):
        try:
            normalize_cart_func()
        except Exception as e:
            print("⚠ WARNING: normalize_cart_func failed:", e)

        if not self.products:
            abort(500, "Database unavailable")

        # Load products safely
        try:
            products = self.products.get_by_category(category_name)
        except Exception as e:
            print("⚠ WARNING: Failed to fetch category products:", e)
            products = []

        # Load ads safely
        try:
            ads = load_ads_for_slots([
                "card_small",
                "product_inline"
            ])
        except Exception as e:
            print("⚠ WARNING: Failed to load category ads:", e)
            ads = {}

        # Safe render
        try:
            return render_template(
                "category.html",
                category=category_name,
                products=products,
                ads=ads
            )
        except Exception as e:
            print("❌ ERROR: Failed to render category template:", e)
            abort(500, "Rendering error")
