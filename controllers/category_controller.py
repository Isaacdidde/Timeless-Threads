from flask import render_template, abort
from models.product_model import ProductModel


class CategoryController:
    def __init__(self, mongo):
        # Store MongoDB connection and initialize ProductModel
        # ProductModel handles all product-related DB operations
        self.products = ProductModel(mongo)
        self.mongo = mongo

    # ---------------------------------------------------------
    # SHOW CATEGORY PAGE
    #
    # This function:
    #   1. Ensures MongoDB connection exists.
    #   2. Fetches all products from a given category.
    #   3. Renders the category page with product listing.
    #
    # Route will look like:
    #   /category/<name>
    #
    # Example: /category/shoes → loads all "shoes" products
    # ---------------------------------------------------------
    def show_category(self, name):
        # Safety check for database connection
        if self.mongo is None:
            # abort() sends an HTTP error response (here: 500)
            abort(500, "Database not initialized")

        # Fetch all products belonging to this category
        products = self.products.get_by_category(name)

        # Render category page with the product listing
        return render_template("category.html", category=name, products=products)
