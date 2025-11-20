from flask import Blueprint
from database.connection import mongo
from controllers.category_controller import CategoryController

# ---------------------------------------------------------
# CATEGORY BLUEPRINT
#
# Handles URLs related to product categories.
# Example:
#     /category/shoes
#     /category/mens-wear
#
# The actual logic for fetching products is inside
# CategoryController, keeping route files clean.
# ---------------------------------------------------------
category_bp = Blueprint("category", __name__)

# Initialize controller with MongoDB connection
controller = CategoryController(mongo)


# ---------------------------------------------------------
# CATEGORY PAGE ROUTE
#
# Dynamic route that accepts a category name from the URL.
# Calls the CategoryController to fetch and render all products
# in that category.
#
# Example:
#     GET /category/electronics
# ---------------------------------------------------------
@category_bp.route("/<name>")
def show_category(name):
    return controller.show_category(name)
