# controllers/category_controller.py

from flask import render_template, abort
from models.product_model import ProductModel


class CategoryController:
    def __init__(self, mongo):
        """Initialize safely."""
        try:
            self.mongo = mongo
            self.products = ProductModel(mongo)
        except Exception as e:
            print("❌ ERROR: Failed to initialize ProductModel:", e)
            self.mongo = None
            self.products = None

    # ==================================================================
    # SHOW CATEGORY PAGE (Production-Safe)
    # ==================================================================
    def show_category(self, name):
        """
        Renders a category page with product listings.

        - Validates category name
        - Ensures Mongo + ProductModel is available
        - Always returns a safe template response
        """

        # -----------------------------------------------------------
        # Validate category name
        # -----------------------------------------------------------
        if not name or not isinstance(name, str):
            abort(404, "Invalid category name")

        clean_name = name.strip().lower()
        if not clean_name:
            abort(404, "Category not found")

        # -----------------------------------------------------------
        # Ensure DB connection + Model availability
        # -----------------------------------------------------------
        if not self.mongo or not self.products:
            print("❌ ERROR: MongoDB or ProductModel unavailable.")
            abort(500, "Database unavailable")

        # -----------------------------------------------------------
        # Fetch Products Safely
        # -----------------------------------------------------------
        try:
            products = self.products.get_by_category(clean_name)
            if products is None:
                products = []
        except Exception as e:
            print(f"⚠ WARNING: Failed to load category '{clean_name}':", e)
            products = []

        # -----------------------------------------------------------
        # Render Template Safely
        # -----------------------------------------------------------
        try:
            return render_template(
                "category.html",
                category=clean_name,
                products=products
            )
        except Exception as e:
            print("❌ ERROR: Failed to render category template:", e)
            abort(500, "Page rendering error")
