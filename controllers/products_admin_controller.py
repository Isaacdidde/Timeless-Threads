from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash
)
from bson import ObjectId, errors as bson_errors
from datetime import datetime
from slugify import slugify
from database.connection import get_collection
from utils.file_upload import handle_upload


# ------------------------------------------------------------------------
# BLUEPRINT
# ------------------------------------------------------------------------
admin_product_bp = Blueprint(
    "admin_product",
    __name__,
    url_prefix="/admin/products"
)


# ------------------------------------------------------------------------
# SAFE COLLECTION ACCESS
# ------------------------------------------------------------------------
def products_collection():
    try:
        return get_collection("products")
    except Exception as e:
        print("❌ ERROR: Cannot access products collection:", e)
        return None

def categories_collection():
    try:
        return get_collection("categories")
    except Exception as e:
        print("❌ ERROR: Cannot access categories collection:", e)
        return None


# ========================================================================
# LIST ALL PRODUCTS
# ========================================================================
@admin_product_bp.route("/")
def list_products():
    col = products_collection()
    if not col:
        flash("Failed to load products.", "danger")
        return render_template("admin/products/list.html", products=[])

    try:
        products = list(col.find().sort("created_at", -1))
    except Exception as e:
        print("⚠ WARNING: Product listing failed:", e)
        products = []

    return render_template("admin/products/list.html", products=products)



# ========================================================================
# HELPER — PARSE MULTILINE DETAILS (Production-Safe)
# ========================================================================
def parse_details(form):
    """
    detail_title[] = list of titles
    detail_items[] = list of newline-separated bullet items
    """
    try:
        titles = form.getlist("detail_title[]")
        items_blocks = form.getlist("detail_items[]")
    except Exception:
        return []

    details = []

    for i in range(len(titles)):
        title = (titles[i] or "").strip()
        if not title:
            continue

        raw_items = (items_blocks[i] or "").strip()
        items = [
            line.strip()
            for line in raw_items.split("\n")
            if line.strip()
        ]

        details.append({
            "title": title,
            "items": items,
        })

    return details



# ========================================================================
# ADD PRODUCT
# ========================================================================
@admin_product_bp.route("/add", methods=["GET", "POST"])
def add_product():
    cats = categories_collection()
    if not cats:
        flash("Cannot load categories.", "danger")
        return render_template("admin/products/add.html", categories=[])

    if request.method == "POST":
        upload_path = "static/uploads/products"

        # ------- IMAGE UPLOADS -------
        try:
            img1 = handle_upload(request.files.get("image_file"), upload_path, {"jpg", "jpeg", "png", "webp"})
            img2 = handle_upload(request.files.get("image_file2"), upload_path, {"jpg", "jpeg", "png", "webp"})
            img3 = handle_upload(request.files.get("image_file3"), upload_path, {"jpg", "jpeg", "png", "webp"})
        except Exception as e:
            print("⚠ WARNING: Image upload failed:", e)
            img1 = img2 = img3 = None

        # ------- CATEGORY -------
        category_id = request.form.get("category_id")

        try:
            cat = cats.find_one({"_id": ObjectId(category_id)})
        except bson_errors.InvalidId:
            cat = None
        except Exception as e:
            print("⚠ WARNING: Category lookup failed:", e)
            cat = None

        if not cat:
            flash("Invalid category selected!", "danger")
            return redirect(url_for("admin_product.add_product"))

        # ------- SIZES & COLORS -------
        sizes = [
            s.strip() for s in request.form.get("sizes", "").split(",")
            if s.strip()
        ]
        colors = [
            c.strip() for c in request.form.get("colors", "").split(",")
            if c.strip()
        ]

        # ------- PRODUCT DETAILS -------
        details = parse_details(request.form)

        # ------- BUILD PRODUCT DOCUMENT -------
        try:
            product_doc = {
                "name": request.form.get("name", "").strip(),
                "slug": slugify(request.form.get("name", "")),

                "category_id": str(cat["_id"]),
                "category_name": cat.get("name"),
                "category_slug": cat.get("slug"),

                "price": float(request.form.get("price", 0) or 0),
                "discount": float(request.form.get("discount", 0) or 0),
                "stock": int(request.form.get("stock", 0) or 0),
                "description": request.form.get("description"),

                "sizes": sizes,
                "colors": colors,
                "details": details,

                "image": img1,
                "image2": img2,
                "image3": img3,

                "published": True,
                "created_at": datetime.utcnow()
            }
        except Exception as e:
            print("❌ ERROR: Failed to build product document:", e)
            flash("Invalid input data.", "danger")
            return redirect(url_for("admin_product.add_product"))

        col = products_collection()
        if not col:
            flash("Database unavailable.", "danger")
            return redirect(url_for("admin_product.add_product"))

        try:
            col.insert_one(product_doc)
        except Exception as e:
            print("❌ ERROR: Failed to insert product:", e)
            flash("Could not save product.", "danger")
            return redirect(url_for("admin_product.add_product"))

        flash("Product added successfully!", "success")
        return redirect(url_for("admin_product.list_products"))

    categories = list(cats.find()) if cats else []
    return render_template("admin/products/add.html", categories=categories)



# ========================================================================
# EDIT PRODUCT
# ========================================================================
@admin_product_bp.route("/edit/<id>", methods=["GET", "POST"])
def edit_product(id):
    col = products_collection()
    if not col:
        flash("Database unavailable.", "danger")
        return redirect(url_for("admin_product.list_products"))

    # Load product safely
    try:
        product = col.find_one({"_id": ObjectId(id)})
    except bson_errors.InvalidId:
        flash("Invalid product ID.", "danger")
        return redirect(url_for("admin_product.list_products"))
    except Exception as e:
        print("⚠ WARNING: Product lookup failed:", e)
        flash("Unable to load product.", "danger")
        return redirect(url_for("admin_product.list_products"))

    if not product:
        flash("Product not found!", "danger")
        return redirect(url_for("admin_product.list_products"))

    cats = categories_collection()
    if not cats:
        flash("Cannot load categories.", "danger")
        return redirect(url_for("admin_product.list_products"))

    if request.method == "POST":
        upload_path = "static/uploads/products"

        # Upload optional new images
        try:
            new_img1 = handle_upload(request.files.get("image_file"), upload_path, {"jpg", "jpeg", "png", "webp"})
            new_img2 = handle_upload(request.files.get("image_file2"), upload_path, {"jpg", "jpeg", "png", "webp"})
            new_img3 = handle_upload(request.files.get("image_file3"), upload_path, {"jpg", "jpeg", "png", "webp"})
        except Exception as e:
            print("⚠ WARNING: Image upload error:", e)
            new_img1 = new_img2 = new_img3 = None

        # Validate category
        try:
            category_id = request.form.get("category_id")
            cat = cats.find_one({"_id": ObjectId(category_id)})
        except Exception:
            cat = None

        if not cat:
            flash("Invalid category!", "danger")
            return redirect(url_for("admin_product.edit_product", id=id))

        # Sizes & Colors
        sizes = [
            s.strip() for s in request.form.get("sizes", "").split(",")
            if s.strip()
        ]
        colors = [
            c.strip() for c in request.form.get("colors", "").split(",")
            if c.strip()
        ]

        details = parse_details(request.form)

        # Build update document
        try:
            update_doc = {
                "name": request.form.get("name", "").strip(),
                "slug": slugify(request.form.get("name", "")),

                "category_id": str(cat["_id"]),
                "category_name": cat.get("name"),
                "category_slug": cat.get("slug"),

                "price": float(request.form.get("price", 0) or 0),
                "discount": float(request.form.get("discount", 0) or 0),
                "stock": int(request.form.get("stock", 0) or 0),
                "description": request.form.get("description"),

                "sizes": sizes,
                "colors": colors,
                "details": details,

                "image": new_img1 or product.get("image"),
                "image2": new_img2 or product.get("image2"),
                "image3": new_img3 or product.get("image3"),
            }
        except Exception as e:
            print("❌ ERROR: Failed to parse product update:", e)
            flash("Invalid update data.", "danger")
            return redirect(url_for("admin_product.edit_product", id=id))

        try:
            col.update_one({"_id": ObjectId(id)}, {"$set": update_doc})
        except Exception as e:
            print("❌ ERROR: Failed to update product:", e)
            flash("Could not update product.", "danger")
            return redirect(url_for("admin_product.edit_product", id=id))

        flash("Product updated successfully!", "success")
        return redirect(url_for("admin_product.edit_product", id=id))

    categories = list(cats.find()) if cats else []

    return render_template(
        "admin/products/edit.html",
        product=product,
        categories=categories
    )



# ========================================================================
# DELETE PRODUCT
# ========================================================================
@admin_product_bp.route("/delete/<id>")
def delete_product(id):
    col = products_collection()
    if not col:
        flash("Database unavailable.", "danger")
        return redirect(url_for("admin_product.list_products"))

    try:
        oid = ObjectId(id)
    except bson_errors.InvalidId:
        flash("Invalid product ID.", "danger")
        return redirect(url_for("admin_product.list_products"))

    try:
        col.delete_one({"_id": oid})
        flash("Product deleted successfully!", "danger")
    except Exception as e:
        print("⚠ WARNING: Product deletion failed:", e)
        flash("Failed to delete product.", "danger")

    return redirect(url_for("admin_product.list_products"))
