from flask import render_template, flash, redirect, url_for
from bson import ObjectId
from models.product_model import ProductModel


class ProductController:
    def __init__(self, mongo):
        # Store MongoDB connection and initialize ProductModel
        self.mongo = mongo
        self.products = ProductModel(mongo)

    # ---------------------------------------------------------
    # PRODUCT DETAIL PAGE
    #
    # Steps:
    #   1. Normalize cart to avoid old/broken formats.
    #   2. Validate the product_id and fetch the product.
    #   3. Compute MRP (original price before discount).
    #   4. Fetch reviews (supporting both ObjectId & string IDs).
    #   5. Compute average rating & review count.
    #   6. Render the product page.
    #
    # normalize_cart_func → passed from CartController to ensure
    # cart cleanup happens before rendering product page.
    # ---------------------------------------------------------
    def product_detail(self, product_id, normalize_cart_func):
        normalize_cart_func()  # Ensure cart stays in valid format

        # Validate and fetch product from DB
        try:
            product = self.mongo.db.products.find_one({"_id": ObjectId(product_id)})
        except:
            flash("Invalid product ID.", "danger")
            return redirect(url_for("main.home"))

        if not product:
            flash("Product not found.", "warning")
            return redirect(url_for("main.home"))

        # -----------------------------------------------------
        # Calculate MRP (Original Price)
        # If discount exists:
        #     price = MRP * (1 - discount/100)
        # So:
        #     MRP = price / (1 - discount/100)
        # -----------------------------------------------------
        mrp = None
        if product.get("discount"):
            mrp = int(product["price"] / (1 - product["discount"] / 100))

        # -----------------------------------------------------
        # Fetch Reviews
        #
        # Reviews may store product_id as:
        #   - ObjectId
        #   - String version of ObjectId
        #
        # We search using both formats for maximum compatibility.
        # -----------------------------------------------------
        product_oid = ObjectId(product_id)
        product_str = str(product["_id"])

        reviews = list(self.mongo.db.reviews.find({
            "$or": [
                {"product_id": product_oid},
                {"product_id": product_str}
            ]
        }))

        # -----------------------------------------------------
        # Rating Summary
        # Compute:
        #   - average rating
        #   - total number of reviews
        # -----------------------------------------------------
        if reviews:
            total_rating = sum(int(r["rating"]) for r in reviews)
            avg_rating = round(total_rating / len(reviews), 1)
            review_count = len(reviews)
        else:
            avg_rating = None
            review_count = 0

        # Render template with all processed data
        return render_template(
            "product_detail.html",
            product=product,
            mrp=mrp,
            reviews=reviews,
            avg_rating=avg_rating,
            review_count=review_count
        )

    # ---------------------------------------------------------
    # CATEGORY VIEW
    #
    # Loads all products under the given category.
    # normalize_cart_func ensures the cart stays clean before
    # showing product listings.
    # ---------------------------------------------------------
    def category_view(self, category_name, normalize_cart_func):
        normalize_cart_func()
        products = self.products.get_by_category(category_name)
        return render_template("category.html", category=category_name, products=products)
