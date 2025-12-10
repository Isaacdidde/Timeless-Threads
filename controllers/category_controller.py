from flask import render_template, abort
from models.product_model import ProductModel


class CategoryController:
    def __init__(self, mongo):
        try:
            self.products = ProductModel(mongo)
            self.mongo = mongo
        except Exception as e:
            print("❌ ERROR: Failed to initialize ProductModel:", e)
            self.products = None
            self.mongo = None

    # ---------------------------------------------------------
    # SHOW CATEGORY PAGE (Production-Safe)
    # ---------------------------------------------------------
    def show_category(self, name):
        """
        Render a category page with product listings.
        - Ensures DB availability
        - Validates category name
        - Handles model failures
        - Ensures template never crashes
        """

        # ----------- Validate category name -----------
        if not name or not isinstance(name, str):
            abort(404, "Invalid category name")

        clean_name = name.strip().lower()
        if not clean_name:
            abort(404, "Category not found")

        # ----------- Ensure DB connection -----------
        if not self.mongo or not self.products:
            print("❌ ERROR: MongoDB or ProductModel unavailable.")
            abort(500, "Database not initialized")

        # ----------- Fetch products safely -----------
        try:
            products = self.products.get_by_category(clean_name)
            if products is None:
                products = []
        except Exception as e:
            print(f"❌ ERROR: Failed to fetch products for '{clean_name}':", e)
            products = []

        # ----------- Render template safely -----------
        try:
            return render_template(
                "category.html",
                category=clean_name,
                products=products
            )
        except Exception as e:
            print("❌ ERROR: Failed to render category template:", e)
            abort(500, "Page render error")
