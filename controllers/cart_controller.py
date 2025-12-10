from flask import render_template, session, redirect, url_for, flash
from bson import ObjectId, errors as bson_errors
from database.connection import get_collection


class CartController:

    # ----------------------------------------------------------------
    # Helper: Normalize variant values
    # ----------------------------------------------------------------
    def _normalize(self, value):
        """
        Converts '', 'none', 'None', 'null', None → None
        """
        if value is None:
            return None
        value = str(value).strip().lower()
        if value in ("", "none", "null"):
            return None
        return value

    # ----------------------------------------------------------------
    # INTERNAL HELPERS
    # ----------------------------------------------------------------
    def _get_cart(self):
        """
        Always returns a safe list, never crashes.
        """
        cart = session.get("cart")
        if not isinstance(cart, list):
            session["cart"] = []
            return []
        return cart

    def _products(self):
        try:
            return get_collection("products")
        except Exception as e:
            print("❌ ERROR: Cannot get products collection:", e)
            return None

    # ----------------------------------------------------------------
    # VIEW CART
    # ----------------------------------------------------------------
    def view_cart(self):
        cart = self._get_cart()
        products_col = self._products()

        if not products_col:
            flash("Unable to load products.", "danger")
            return render_template("cart.html", cart_items=[])

        cart_items = []

        for item in cart:
            product_id = item.get("product_id")
            try:
                oid = ObjectId(product_id)
            except bson_errors.InvalidId:
                print("⚠ WARNING: Invalid product ID in cart:", product_id)
                continue

            try:
                product = products_col.find_one({"_id": oid})
            except Exception as e:
                print("⚠ WARNING: Product lookup failed:", e)
                continue

            if not product:
                continue

            # Compute totals safely
            try:
                qty = int(item.get("quantity", 1))
                total = qty * int(product.get("price", 0))
            except Exception:
                total = 0

            cart_items.append({
                "product": product,
                "size": item.get("size"),
                "color": item.get("color"),
                "quantity": qty,
                "total": total,
            })

        return render_template("cart.html", cart_items=cart_items)

    # ----------------------------------------------------------------
    # ADD TO CART
    # ----------------------------------------------------------------
    def add_to_cart(self, product_id, form):
        cart = self._get_cart()

        # quantity safe parse
        try:
            quantity = max(1, int(form.get("quantity", 1)))
        except ValueError:
            quantity = 1

        size = self._normalize(form.get("selected_size"))
        color = self._normalize(form.get("selected_color"))

        # Merge with existing cart item
        for item in cart:
            if (
                item.get("product_id") == product_id and
                self._normalize(item.get("size")) == size and
                self._normalize(item.get("color")) == color
            ):
                try:
                    item["quantity"] += quantity
                except Exception:
                    item["quantity"] = quantity

                session["cart"] = cart
                flash("Updated quantity in cart!", "success")
                return redirect(url_for("cart.view_cart"))

        # Add new entry
        cart.append({
            "product_id": product_id,
            "quantity": quantity,
            "size": size,
            "color": color
        })

        session["cart"] = cart
        flash("Added to cart!", "success")
        return redirect(url_for("cart.view_cart"))

    # ----------------------------------------------------------------
    # UPDATE QUANTITY
    # ----------------------------------------------------------------
    def update_quantity(self, form):
        cart = self._get_cart()

        product_id = form.get("product_id")
        size = self._normalize(form.get("size"))
        color = self._normalize(form.get("color"))

        try:
            quantity = max(1, int(form.get("quantity", 1)))
        except ValueError:
            quantity = 1

        for item in cart:
            if (
                item.get("product_id") == product_id and
                self._normalize(item.get("size")) == size and
                self._normalize(item.get("color")) == color
            ):
                item["quantity"] = quantity

        session["cart"] = cart
        flash("Cart updated!", "success")
        return redirect(url_for("cart.view_cart"))

    # ----------------------------------------------------------------
    # REMOVE FROM CART
    # ----------------------------------------------------------------
    def remove_from_cart(self, form):
        cart = self._get_cart()

        product_id = form.get("product_id")
        size = self._normalize(form.get("size"))
        color = self._normalize(form.get("color"))

        cleaned = [
            item for item in cart
            if not (
                item.get("product_id") == product_id and
                self._normalize(item.get("size")) == size and
                self._normalize(item.get("color")) == color
            )
        ]

        session["cart"] = cleaned
        flash("Item removed!", "info")
        return redirect(url_for("cart.view_cart"))

    # ----------------------------------------------------------------
    # CHECKOUT PAGE
    # ----------------------------------------------------------------
    def checkout_page(self):
        cart = self._get_cart()

        if not cart:
            flash("Your cart is empty!", "warning")
            return redirect(url_for("cart.view_cart"))

        return render_template("checkout.html")
