"""
utils/cart_helper.py

Helper functions for cart normalization and session safety.
Ensures Timeless Threads cart is always a valid structure:

cart = {
    "<product_id>": {
        "size": "M",
        "color": "Blue",
        "quantity": 1
    }
}
"""

from flask import session


def normalize_cart():
    """
    Ensures session['cart'] always exists and is well-formed.

    - Creates cart if missing.
    - Rewrites corrupted or invalid data.
    - Guarantees the controller receives a clean dictionary.
    """
    cart = session.get("cart")

    # If cart missing OR not a dict → reset
    if not isinstance(cart, dict):
        cart = {}
        session["cart"] = cart
        return cart

    # Validate each cart entry to avoid broken session data
    cleaned = {}
    for key, item in cart.items():
        if not isinstance(item, dict):
            continue

        # Normalize each field
        size = item.get("size")
        color = item.get("color")
        qty = item.get("quantity", 1)

        # Ensure valid quantity
        try:
            qty = int(qty)
            if qty < 1:
                qty = 1
        except Exception:
            qty = 1

        cleaned[key] = {
            "size": size,
            "color": color,
            "quantity": qty,
        }

    # Overwrite with cleaned structure
    session["cart"] = cleaned
    return cleaned
