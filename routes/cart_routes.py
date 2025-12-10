"""
Production-ready Cart Routes

Hardened against:
    - Missing form data
    - Invalid product IDs
    - Controller initialization errors
    - Mongo truth-value errors
    - Session failures
    - Unexpected crashes

Route paths and controller APIs remain unchanged.
"""

from flask import Blueprint, request, flash, redirect, url_for

# Try to load real controller
try:
    from controllers.cart_controller import CartController
    controller = CartController()
except Exception as e:
    print("❌ ERROR: Failed to initialize CartController:", e)

    # Fallback dummy controller (prevents app crash)
    class CartController:
        def view_cart(self):
            flash("Cart temporarily unavailable.", "danger")
            return redirect(url_for("main.home"))

        def add_to_cart(self, *args, **kwargs):
            flash("Unable to add items to cart.", "danger")
            return redirect(url_for("main.home"))

        def update_quantity(self, *args, **kwargs):
            flash("Unable to update cart.", "danger")
            return redirect(url_for("main.home"))

        def remove_from_cart(self, *args, **kwargs):
            flash("Unable to remove items from cart.", "danger")
            return redirect(url_for("main.home"))

        def checkout_page(self):
            flash("Checkout is unavailable.", "danger")
            return redirect(url_for("main.home"))

    controller = CartController()


# ======================================================
# BLUEPRINT
# ======================================================
cart_bp = Blueprint("cart", __name__, url_prefix="/cart")


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
        if not product_id or str(product_id).strip() == "":
            flash("Invalid product.", "danger")
            return redirect(url_for("cart.view_cart"))

        form = request.form.to_dict() if request.form else {}

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
        form = request.form.to_dict() if request.form else {}

        product_id = form.get("product_id")
        if not product_id:
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
        form = request.form.to_dict() if request.form else {}

        product_id = form.get("product_id")
        if not product_id:
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
