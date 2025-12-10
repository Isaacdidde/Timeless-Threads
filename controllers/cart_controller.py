# controllers/cart_controller.py

from flask import render_template, session, redirect, url_for, flash
from bson import ObjectId
from bson.errors import InvalidId
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
        try:
            s = str(value).strip()
        except Exception:
            return None
        low = s.lower()
        if low in ("", "none", "null"):
            return None
        return s

    # ----------------------------------------------------------------
    # INTERNAL HELPERS
    # ----------------------------------------------------------------
    def _get_cart(self):
        """
        Always returns a safe list, never crashes.
        Ensures session['cart'] is always a list.
        """
        cart = session.get("cart")
        if not isinstance(cart, list):
            session["cart"] = []
            return []
        return cart

    def _products(self):
        """
        Returns the products collection or None on failure.
        """
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

        # NOTE: test for None explicitly (PyMongo collections cannot be used in boolean checks)
        if products_col is None:
            flash("Unable to load products.", "danger")
            return render_template("cart.html", cart_items=[])

        cart_items = []

        for item in cart:
            product_id = item.get("product_id")
            if not product_id:
                continue

            # Try to use ObjectId if possible, else try as string key
            product = None
            try:
                oid = ObjectId(product_id)
            except (InvalidId, Exception):
                oid = None

            try:
                if oid is not None:
                    product = products_col.find_one({"_id": oid})
                else:
                    # fallback: try finding by string id or slug
                    product = products_col.find_one({"_id": product_id}) or \
                              products_col.find_one({"slug": product_id}) or \
                              products_col.find_one({"sku": product_id})
            except Exception as e:
                print("⚠ WARNING: Product lookup failed:", e)
                product = None

            if product is None:
                # skip items pointing to deleted/invalid products
                continue

            # Compute qty safely
            try:
                qty = int(item.get("quantity", 1))
                if qty < 1:
                    qty = 1
            except Exception:
                qty = 1   # fallback safe value

            # Compute price safely (price could be string in DB)
            try:
                raw_price = product.get("price", 0) or 0
                price = float(raw_price)
            except Exception:
                price = 0.0

            total = qty * price

            cart_items.append({
                "product": product,
                "size": item.get("size"),
                "color": item.get("color"),
                "quantity": qty,
                "unit_price": price,
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
            quantity = int(form.get("quantity", 1))
            if quantity < 1:
                quantity = 1
        except Exception:
            quantity = 1

        size = self._normalize(form.get("selected_size") or form.get("size"))
        color = self._normalize(form.get("selected_color") or form.get("color"))

        # Merge with existing cart item
        merged = False
        for item in cart:
            if (
                item.get("product_id") == product_id and
                self._normalize(item.get("size")) == size and
                self._normalize(item.get("color")) == color
            ):
                try:
                    current = int(item.get("quantity", 0))
                    item["quantity"] = current + quantity
                except Exception:
                    item["quantity"] = quantity
                merged = True
                break

        if not merged:
            cart.append({
                "product_id": product_id,
                "quantity": quantity,
                "size": size,
                "color": color
            })

        # persist
        session["cart"] = cart
        flash("Added to cart!" if not merged else "Updated quantity in cart!", "success")
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
            quantity = int(form.get("quantity", 1))
            if quantity < 1:
                quantity = 1
        except Exception:
            quantity = 1

        changed = False
        for item in cart:
            if (
                item.get("product_id") == product_id and
                self._normalize(item.get("size")) == size and
                self._normalize(item.get("color")) == color
            ):
                item["quantity"] = quantity
                changed = True

        session["cart"] = cart
        if changed:
            flash("Cart updated!", "success")
        else:
            flash("No matching item found to update.", "warning")
        return redirect(url_for("cart.view_cart"))

    # ----------------------------------------------------------------
    # REMOVE FROM CART
    # ----------------------------------------------------------------
    def remove_from_cart(self, form):
        cart = self._get_cart()

        product_id = form.get("product_id")
        size = self._normalize(form.get("size"))
        color = self._normalize(form.get("color"))

        before = len(cart)
        cleaned = [
            item for item in cart
            if not (
                item.get("product_id") == product_id and
                self._normalize(item.get("size")) == size and
                self._normalize(item.get("color")) == color
            )
        ]
        after = len(cleaned)

        session["cart"] = cleaned
        if after < before:
            flash("Item removed!", "info")
        else:
            flash("Item not found in cart.", "warning")
        return redirect(url_for("cart.view_cart"))

    # ----------------------------------------------------------------
    # CHECKOUT PAGE
    # ----------------------------------------------------------------
    def checkout_page(self):
        cart = self._get_cart()

        # empty cart → redirect to cart page
        if not cart:
            flash("Your cart is empty!", "warning")
            return redirect(url_for("cart.view_cart"))

        # Basic check: ensure products collection accessible
        products_col = self._products()
        if products_col is None:
            flash("Unable to proceed to checkout: product service unavailable.", "danger")
            return redirect(url_for("cart.view_cart"))

        # Optionally we could re-validate cart items here (availability/stock),
        # but for now render checkout page.
        return render_template("checkout.html")
