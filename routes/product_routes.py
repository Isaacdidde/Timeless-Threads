from flask import Blueprint, request
from database.connection import mongo
from controllers.product_controller import ProductController
from controllers.cart_controller import CartController

# ---------------------------------------------------------
# PRODUCT BLUEPRINT
#
# Handles:
#   - Product details
#   - Category-based product listing
#   - Cart operations (add, view, remove)
#   - Checkout placeholder
#
# Business logic is offloaded to ProductController
# and CartController for clean separation of concerns.
# ---------------------------------------------------------
product_bp = Blueprint("product", __name__)

# Controllers initialized with MongoDB connection
product_controller = ProductController(mongo)
cart_controller = CartController(mongo)


# ---------------------------------------------------------
# PRODUCT DETAIL PAGE
#
# URL: /product/<product_id>
# Shows product info, ratings, reviews, and variation options.
# normalize_cart ensures the session cart stays consistent.
# ---------------------------------------------------------
@product_bp.route("/<product_id>")
def product_detail(product_id):
    return product_controller.product_detail(
        product_id,
        cart_controller.normalize_cart
    )


# ---------------------------------------------------------
# CATEGORY VIEW
#
# URL: /product/category/<category_name>
# Shows all products inside a given category.
# ---------------------------------------------------------
@product_bp.route("/category/<category_name>")
def category_view(category_name):
    return product_controller.category_view(
        category_name,
        cart_controller.normalize_cart
    )


# ---------------------------------------------------------
# ADD TO CART (POST)
#
# URL: /product/add-to-cart
# Handles adding products with selected
# size, color, and quantity into the cart.
#
# normalize_cart prevents old formats from breaking logic.
# ---------------------------------------------------------
@product_bp.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    cart_controller.normalize_cart()
    return cart_controller.add_to_cart(
        request.form.get("product_id"),
        int(request.form.get("quantity", 1)),
        request.form.get("selected_size"),
        request.form.get("selected_color")
    )


# ---------------------------------------------------------
# VIEW CART
#
# URL: /product/cart
# Renders cart.html with all items and pricing details.
# ---------------------------------------------------------
@product_bp.route("/cart")
def cart():
    cart_controller.normalize_cart()
    return cart_controller.cart_page()


# ---------------------------------------------------------
# REMOVE CART ITEM
#
# URL: /product/remove/<product_id>/<size>/<color>
# Removes a cart entry matching the exact variation.
# ---------------------------------------------------------
@product_bp.route("/remove/<product_id>/<size>/<color>")
def remove_item(product_id, size, color):
    cart_controller.normalize_cart()
    return cart_controller.remove_from_cart(product_id, size, color)


# ---------------------------------------------------------
# CHECKOUT
#
# URL: /product/checkout
# Loads a placeholder page for now.
# ---------------------------------------------------------
@product_bp.route("/checkout")
def checkout():
    return cart_controller.checkout()
