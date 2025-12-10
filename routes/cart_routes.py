"""
Production-ready Cart Routes
Safe against:
    - Missing form data
    - Invalid product IDs
    - Controller exceptions
    - Session errors
    - Unexpected crashes (returns safe redirects)

Does not modify route paths or controller logic.
"""

from flask import Blueprint, request, flash, redirect, url_for
from controllers.cart_controller import CartController

cart_bp = Blueprint("cart", __name__, url_prefix="/cart")

# Global controller instance
try:
    controller = CartController()
except Exception as e:
    print("❌ ERROR: Failed to initialize CartController:", e)

    # fallback dummy prevents server crash
    class CartController:
        def view_cart(self): 
            flash("Cart unavailable.", "danger")
            return redirect(url_for("main.home"))
        def add_to_cart(self, *a, **k):
            flash("Cannot add to cart.", "danger")
            return redirect(url_for("main.home"))
        def update_quantity(self, *a, **k):
            flash("Cannot update cart.", "danger")
            return redirect(url_for("main.home"))
        def remove_from_cart(self, *a, **k):
            flash("Cannot remove from cart.", "danger")
            return redirect(url_for("main.home"))
        def checkout_page(self):
            flash("Checkout unavailable.", "danger")
            return redirect(url_for("main.home"))

    controller = CartController()


# ======================================================
# VIEW CART
# ======================================================
@cart_bp.route("/", methods=["GET"])
def view_cart():
    try:
        return controller.view_cart()
    except Exception as e:
        print("❌ ERROR: view_cart() failed:", e)
        flash("Unable to load cart.", "danger")
        return redirect(url_for("main.home"))


# ======================================================
# ADD TO CART
# ======================================================
@cart_bp.route("/add/<product_id>", methods=["POST"])
def add_to_cart(product_id):
    try:
        if not product_id:
            flash("Invalid product.", "danger")
            return redirect(url_for("cart.view_cart"))

        form = request.form or {}
        return controller.add_to_cart(product_id, form)

    except Exception as e:
        print("❌ ERROR: add_to_cart() failed:", e)
        flash("Unable to add item to cart.", "danger")
        return redirect(url_for("cart.view_cart"))


# ======================================================
# UPDATE QUANTITY
# ======================================================
@cart_bp.route("/update", methods=["POST"])
def update_quantity():
    try:
        form = request.form or {}

        if not form.get("product_id"):
            flash("Invalid product update.", "warning")
            return redirect(url_for("cart.view_cart"))

        return controller.update_quantity(form)

    except Exception as e:
        print("❌ ERROR: update_quantity() failed:", e)
        flash("Unable to update cart.", "danger")
        return redirect(url_for("cart.view_cart"))


# ======================================================
# REMOVE FROM CART
# ======================================================
@cart_bp.route("/remove", methods=["POST"])
def remove_from_cart():
    try:
        form = request.form or {}

        if not form.get("product_id"):
            flash("Invalid remove request.", "warning")
            return redirect(url_for("cart.view_cart"))

        return controller.remove_from_cart(form)

    except Exception as e:
        print("❌ ERROR: remove_from_cart() failed:", e)
        flash("Unable to remove item.", "danger")
        return redirect(url_for("cart.view_cart"))


# ======================================================
# CHECKOUT PAGE
# ======================================================
@cart_bp.route("/checkout", methods=["GET"])
def checkout():
    try:
        return controller.checkout_page()
    except Exception as e:
        print("❌ ERROR: checkout_page() failed:", e)
        flash("Checkout unavailable.", "danger")
        return redirect(url_for("cart.view_cart"))
