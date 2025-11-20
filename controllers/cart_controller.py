from flask import render_template, session, flash, redirect, url_for
from bson import ObjectId
from datetime import datetime


class CartController:
    def __init__(self, mongo):
        # Store Mongo reference for DB operations
        self.mongo = mongo

    # ---------------------------------------------------------
    # NORMALIZE CART
    # Ensures the cart always follows a consistent structure:
    # Each item becomes a dict with:
    #   - product_id (str)
    #   - quantity (int)
    #   - size (str | None)
    #   - color (str | None)
    #
    # Also converts old formats where item was simply a string.
    # ---------------------------------------------------------
    def normalize_cart(self):
        cart = session.get("cart", [])
        normalized = []
        changed = False

        for item in cart:

            # OLD FORMAT → item was just product_id string
            if isinstance(item, str):
                normalized.append({
                    "product_id": item,
                    "quantity": 1,
                    "size": None,
                    "color": None
                })
                changed = True

            # PROPER dict format
            elif isinstance(item, dict) and "product_id" in item:
                normalized.append({
                    "product_id": str(item["product_id"]),
                    "quantity": int(item.get("quantity", 1)),
                    "size": item.get("size"),
                    "color": item.get("color")
                })

            # Invalid item → skip but mark cart as changed
            else:
                changed = True

        # Save updated cart into session only if changes happened
        if changed:
            session["cart"] = normalized
            session.modified = True

    # ---------------------------------------------------------
    # ADD ITEM TO CART
    # Handles:
    #   - Product validation
    #   - Variant matching (size + color)
    #   - Increasing quantity if item exists
    #   - Cosmetics category bypassing size/color requirement
    # ---------------------------------------------------------
    def add_to_cart(self, product_id, quantity, size, color):

        # Validate product ID and fetch product
        try:
            product = self.mongo.db.products.find_one({"_id": ObjectId(product_id)})
        except:
            flash("Invalid product.", "danger")
            return redirect(url_for("main.home"))

        if not product:
            flash("Product not found.", "danger")
            return redirect(url_for("main.home"))

        # Cosmetics never require size or color
        is_cosmetics = (product.get("category") == "cosmetics")

        # Validate size selection for non-cosmetics
        if not is_cosmetics:
            if product.get("sizes") and not size:
                flash("Please select a size.", "warning")
                return redirect(url_for("product.product_detail", product_id=product_id))

            if product.get("colors") and not color:
                flash("Please select a color.", "warning")
                return redirect(url_for("product.product_detail", product_id=product_id))

        cart = session.get("cart", [])

        # -----------------------------------------------------
        # MATCH EXISTING ITEM (same product + same variant)
        # If found → increase quantity instead of adding new row
        # -----------------------------------------------------
        for item in cart:
            if (
                item["product_id"] == product_id
                and (item.get("size") or None) == (size if not is_cosmetics else None)
                and (item.get("color") or None) == (color if not is_cosmetics else None)
            ):
                item["quantity"] += quantity
                session["cart"] = cart
                session.modified = True
                flash("Quantity updated!", "success")
                return redirect(url_for("product.product_detail", product_id=product_id))

        # -----------------------------------------------------
        # ADD AS NEW CART ITEM
        # -----------------------------------------------------
        cart.append({
            "product_id": product_id,
            "quantity": quantity,
            "size": size if not is_cosmetics else None,
            "color": color if not is_cosmetics else None,
            "added_at": datetime.utcnow()
        })

        session["cart"] = cart
        session.modified = True
        flash("Added to cart!", "success")
        return redirect(url_for("product.product_detail", product_id=product_id))

    # ---------------------------------------------------------
    # VIEW CART
    # Builds a structured list of cart items with:
    #   - product details
    #   - computed MRP (original price before discount)
    #   - total price for each line item
    # Then renders the cart page.
    # ---------------------------------------------------------
    def cart_page(self):
        cart_items = []
        cart = session.get("cart", [])

        for entry in cart:

            # Fetch product details safely
            try:
                product = self.mongo.db.products.find_one({"_id": ObjectId(entry["product_id"])})
            except:
                continue

            if not product:
                continue

            # Calculate original price (MRP) from discounted price
            if product.get("discount"):
                mrp = int(product["price"] / (1 - product["discount"] / 100))
            else:
                mrp = product["price"]

            cart_items.append({
                "product": product,                         # entire product document
                "quantity": entry["quantity"],
                "size": entry.get("size"),
                "color": entry.get("color"),
                "total": product["price"] * entry["quantity"],  # final price * quantity
                "mrp": mrp                                  # original price
            })

        return render_template("cart.html", cart_items=cart_items)

    # ---------------------------------------------------------
    # REMOVE AN ITEM FROM CART
    # Matches the exact variant (size + color) and removes only one.
    # ---------------------------------------------------------
    def remove_from_cart(self, product_id, size, color):

        # Convert "none" back to None for accurate matching
        if size == "none":
            size = None
        if color == "none":
            color = None

        cart = session.get("cart", [])
        new_cart = []
        removed = False

        for item in cart:
            is_match = (
                item["product_id"] == product_id and
                (item.get("size") or None) == size and
                (item.get("color") or None) == color
            )

            # Skip only the first matching item
            if is_match and not removed:
                removed = True
            else:
                new_cart.append(item)

        session["cart"] = new_cart
        session.modified = True

        flash("Item removed." if removed else "Item not found.",
              "info" if removed else "warning")

        return redirect(url_for("product.cart"))

    # ---------------------------------------------------------
    # CHECKOUT (placeholder)
    # Full checkout flow can later include:
    #   - Address selection
    #   - Payment gateway
    #   - Order creation
    # For now it loads a placeholder page.
    # ---------------------------------------------------------
    def checkout(self):
        return render_template("checkout_placeholder.html")
