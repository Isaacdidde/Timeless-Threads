import os
import uuid
from datetime import datetime

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, current_app, jsonify
)
from bson import ObjectId
from bson.errors import InvalidId
from database.connection import get_collection
from utils.file_upload import handle_upload

# Optional slugify dependency
try:
    from slugify import slugify as lib_slugify
except Exception:
    lib_slugify = None


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def slugify(name: str) -> str:
    if not name:
        return ""
    if lib_slugify:
        return lib_slugify(name)
    return "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")


def safe_oid(value):
    try:
        return ObjectId(value)
    except InvalidId:
        print(f"⚠ WARNING: Invalid ObjectId: {value}")
        return None
    except Exception as e:
        print(f"⚠ WARNING: ObjectId parse error: {e}")
        return None


def images_to_fields(images):
    img = images[0] if len(images) > 0 else None
    img2 = images[1] if len(images) > 1 else None
    img3 = images[2] if len(images) > 2 else None
    return img, img2, img3


def new_section_id():
    return uuid.uuid4().hex


# ---------------------------------------------------------------------------
# BLUEPRINT
# ---------------------------------------------------------------------------
admin_product_bp = Blueprint("admin_product", __name__, url_prefix="/admin/products")


# ---------------------------------------------------------------------------
# COLLECTION SHORTCUTS
# ---------------------------------------------------------------------------
def products_collection():
    try:
        return get_collection("products")
    except Exception as e:
        print("❌ ERROR: Cannot load products collection:", e)
        return None


def categories_collection():
    try:
        return get_collection("categories")
    except Exception as e:
        print("❌ ERROR: Cannot load categories collection:", e)
        return None


# ---------------------------------------------------------------------------
# LIST PRODUCTS
# ---------------------------------------------------------------------------
@admin_product_bp.route("/")
def list_products():
    try:
        categories = list(categories_collection().find().sort("name", 1))
    except Exception as e:
        print("⚠ WARNING: Failed to fetch categories:", e)
        categories = []

    try:
        products = list(products_collection().find().sort("created_at", -1))
    except Exception as e:
        print("⚠ WARNING: Failed to fetch products:", e)
        products = []

    for p in products:
        p["images"] = p.get("images", []) or []
        p["primary_image"] = p.get("primary_image") or (p["images"][0] if p["images"] else None)
        p["image"], p["image2"], p["image3"] = images_to_fields(p["images"])

        normalized = []
        for i, d in enumerate(p.get("details", [])):
            normalized.append({
                "id": d.get("id") or new_section_id(),
                "title": d.get("title", ""),
                "items": d.get("items", []),
                "order": i
            })
        p["details"] = normalized

    return render_template("admin/products/list.html",
                           categories=categories,
                           products=products)


# ---------------------------------------------------------------------------
# ADD PRODUCT
# ---------------------------------------------------------------------------
@admin_product_bp.route("/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":

        upload_path = "static/uploads/products"
        uploaded = []

        for f in request.files.getlist("images[]"):
            if f and f.filename:
                try:
                    filename = handle_upload(f, upload_path, {"jpg", "jpeg", "png", "webp"})
                    if filename:
                        uploaded.append(filename)
                except Exception as e:
                    print("⚠ WARNING: Failed to upload image:", e)
                    flash("Some images failed to upload.", "warning")

        primary = uploaded[0] if uploaded else None

        category_key = request.form.get("category")
        category = None

        if category_key:
            try:
                category = categories_collection().find_one({"slug": category_key}) or \
                           categories_collection().find_one({"name": category_key})
            except Exception as e:
                print("⚠ WARNING: Failed to fetch category:", e)

        if not category:
            flash("Invalid category selection.", "danger")
            return redirect(url_for("admin_product.add_product"))

        def parse_list(field):
            raw = request.form.get(field, "")
            return [x.strip() for x in raw.split(",") if x.strip()]

        sizes = parse_list("sizes")
        colors = parse_list("colors")

        name = request.form.get("name", "").strip()
        slugged = slugify(name)

        img, img2, img3 = images_to_fields(uploaded)

        doc = {
            "name": name,
            "slug": slugged,
            "category_id": str(category["_id"]),
            "category_slug": category.get("slug"),
            "category_name": category.get("name"),

            "price": float(request.form.get("price", 0) or 0),
            "discount": float(request.form.get("discount", 0) or 0),
            "stock": int(request.form.get("stock", 0) or 0),
            "description": request.form.get("description", ""),

            "sizes": sizes,
            "colors": colors,

            "images": uploaded,
            "primary_image": primary,
            "image": img,
            "image2": img2,
            "image3": img3,

            "published": True,
            "featured": False,
            "created_at": datetime.utcnow()
        }

        try:
            products_collection().insert_one(doc)
            flash("Product added successfully!", "success")
        except Exception as e:
            print("❌ ERROR: Failed to insert product:", e)
            flash("Error saving product. Check logs.", "danger")

        return redirect(url_for("admin_product.list_products"))

    try:
        categories = list(categories_collection().find().sort("name", 1))
    except Exception:
        categories = []

    return render_template("admin/products/add.html", categories=categories)


# ---------------------------------------------------------------------------
# EDIT PRODUCT
# ---------------------------------------------------------------------------
@admin_product_bp.route("/edit/<id>", methods=["GET", "POST"])
def edit_product(id):
    oid = safe_oid(id)
    if not oid:
        flash("Invalid product ID.", "danger")
        return redirect(url_for("admin_product.list_products"))

    try:
        product = products_collection().find_one({"_id": oid})
    except Exception as e:
        print("❌ ERROR: Failed to load product:", e)
        product = None

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("admin_product.list_products"))

    if request.method == "POST":

        upload_path = "static/uploads/products"
        new_images = []

        for f in request.files.getlist("images[]"):
            if f and f.filename:
                try:
                    filename = handle_upload(f, upload_path, {"jpg", "jpeg", "png", "webp"})
                    if filename:
                        new_images.append(filename)
                except Exception as e:
                    print("⚠ WARNING: Failed to upload image:", e)
                    flash("Some images failed to upload.", "warning")

        final_images = (product.get("images") or []) + new_images

        primary = request.form.get("primary_image")
        if primary not in final_images:
            primary = product.get("primary_image")

        category_key = request.form.get("category")
        category = None

        try:
            category = categories_collection().find_one({"slug": category_key}) or \
                       categories_collection().find_one({"name": category_key})
        except Exception as e:
            print("⚠ WARNING: Category lookup failed:", e)

        def parse_list(field):
            raw = request.form.get(field, "")
            return [x.strip() for x in raw.split(",") if x.strip()]

        sizes = parse_list("sizes")
        colors = parse_list("colors")

        name = request.form.get("name", "").strip()
        slugged = slugify(name)

        img, img2, img3 = images_to_fields(final_images)

        update = {
            "name": name,
            "slug": slugged,

            "category_id": str(category["_id"]) if category else product.get("category_id"),
            "category_slug": category.get("slug") if category else product.get("category_slug"),
            "category_name": category.get("name") if category else product.get("category_name"),

            "price": float(request.form.get("price", 0) or 0),
            "discount": float(request.form.get("discount", 0) or 0),
            "stock": int(request.form.get("stock", 0) or 0),
            "description": request.form.get("description", ""),

            "sizes": sizes,
            "colors": colors,

            "images": final_images,
            "primary_image": primary,
            "image": img,
            "image2": img2,
            "image3": img3,

            "updated_at": datetime.utcnow()
        }

        try:
            products_collection().update_one({"_id": oid}, {"$set": update})
            flash("Product updated.", "success")
        except Exception as e:
            print("❌ ERROR: Failed to update product:", e)
            flash("Failed to update product.", "danger")

        return redirect(url_for("admin_product.edit_product", id=id))

    # Preprocess product for UI
    product["images"] = product.get("images") or []
    product["primary_image"] = product.get("primary_image") or (
        product["images"][0] if product["images"] else None
    )
    product["image"], product["image2"], product["image3"] = images_to_fields(product["images"])

    normalized = []
    for i, d in enumerate(product.get("details", [])):
        normalized.append({
            "id": d.get("id") or new_section_id(),
            "title": d.get("title", ""),
            "items": d.get("items", []),
            "order": i
        })

    product["details"] = normalized
    product["deleted_details"] = product.get("deleted_details", [])

    try:
        categories = list(categories_collection().find().sort("name", 1))
    except Exception:
        categories = []

    return render_template("admin/products/edit.html",
                           product=product,
                           categories=categories)


# ---------------------------------------------------------------------------
# FEATURED TOGGLE
# ---------------------------------------------------------------------------
@admin_product_bp.route("/featured/<product_id>", methods=["POST"])
def toggle_featured(product_id):
    oid = safe_oid(product_id)
    if not oid:
        return jsonify({"success": False, "error": "Invalid ID"}), 400

    try:
        product = products_collection().find_one({"_id": oid})
    except Exception:
        product = None

    if not product:
        return jsonify({"success": False, "error": "Not found"}), 404

    new_value = not product.get("featured", False)

    try:
        products_collection().update_one({"_id": oid},
                                         {"$set": {"featured": new_value}})
    except Exception as e:
        print("❌ ERROR: Failed to update featured status:", e)
        return jsonify({"success": False}), 500

    return jsonify({"success": True, "featured": new_value})


# ---------------------------------------------------------------------------
# SECTION MANAGEMENT (SAFE AJAX)
# ---------------------------------------------------------------------------
@admin_product_bp.route("/section/add/<product_id>", methods=["POST"])
def ajax_add_section(product_id):
    oid = safe_oid(product_id)
    if not oid:
        return jsonify({"success": False, "error": "Invalid ID"}), 400

    try:
        title = (request.form.get("title") or "").strip()
        items_raw = request.form.get("items") or ""
        items = [x.strip() for x in items_raw.split("\n") if x.strip()]
    except Exception:
        return jsonify({"success": False, "error": "Invalid input"}), 400

    if not title:
        return jsonify({"success": False, "error": "Title required"}), 400

    section = {
        "id": new_section_id(),
        "title": title,
        "items": items,
        "order": 999,
        "created_at": datetime.utcnow()
    }

    try:
        products_collection().update_one({"_id": oid}, {"$push": {"details": section}})
        return jsonify({"success": True, "section": section})
    except Exception as e:
        current_app.logger.exception(e)
        return jsonify({"success": False}), 500


# ---------------------------------------------------------------------------
# UPDATE SECTION
# ---------------------------------------------------------------------------
@admin_product_bp.route("/section/update/<product_id>/<section_id>", methods=["POST"])
def ajax_update_section(product_id, section_id):
    oid = safe_oid(product_id)
    if not oid:
        return jsonify({"success": False}), 400

    try:
        data = request.json if request.is_json else request.form
        title = (data.get("title") or "").strip()
        items_raw = data.get("items") or ""
        items = [x.strip() for x in str(items_raw).split("\n") if x.strip()]
    except Exception:
        return jsonify({"success": False, "error": "Invalid input"}), 400

    if not title:
        return jsonify({"success": False, "error": "Missing title"}), 400

    try:
        res = products_collection().update_one(
            {"_id": oid, "details.id": section_id},
            {"$set": {
                "details.$.title": title,
                "details.$.items": items,
                "details.$.updated_at": datetime.utcnow()
            }}
        )
    except Exception as e:
        current_app.logger.exception(e)
        return jsonify({"success": False}), 500

    if res.matched_count == 0:
        return jsonify({"success": False, "error": "Not found"}), 404

    return jsonify({"success": True})


# ---------------------------------------------------------------------------
# DELETE SECTION (SOFT DELETE)
# ---------------------------------------------------------------------------
@admin_product_bp.route("/section/delete/<product_id>/<section_id>", methods=["POST"])
def ajax_delete_section(product_id, section_id):
    oid = safe_oid(product_id)
    if not oid:
        return jsonify({"success": False, "error": "Invalid ID"}), 400

    try:
        product = products_collection().find_one({"_id": oid})
    except Exception:
        product = None

    if not product:
        return jsonify({"success": False, "error": "Not found"}), 404

    section = next((d for d in product.get("details", []) if d["id"] == section_id), None)
    if not section:
        return jsonify({"success": False, "error": "Section not found"}), 404

    section["deleted_at"] = datetime.utcnow()

    try:
        products_collection().update_one(
            {"_id": oid},
            {"$pull": {"details": {"id": section_id}},
             "$push": {"deleted_details": section}}
        )
        return jsonify({"success": True})
    except Exception as e:
        current_app.logger.exception(e)
        return jsonify({"success": False}), 500


# ---------------------------------------------------------------------------
# RESTORE SECTION
# ---------------------------------------------------------------------------
@admin_product_bp.route("/section/restore/<product_id>/<section_id>", methods=["POST"])
def ajax_restore_section(product_id, section_id):
    oid = safe_oid(product_id)
    if not oid:
        return jsonify({"success": False}), 400

    try:
        product = products_collection().find_one({"_id": oid})
    except Exception:
        product = None

    if not product:
        return jsonify({"success": False, "error": "Not found"}), 404

    deleted = next((d for d in product.get("deleted_details", []) if d["id"] == section_id), None)
    if not deleted:
        return jsonify({"success": False, "error": "Not found in deleted"}), 404

    deleted["restored_at"] = datetime.utcnow()

    try:
        products_collection().update_one(
            {"_id": oid},
            {"$pull": {"deleted_details": {"id": section_id}},
             "$push": {"details": deleted}}
        )
        return jsonify({"success": True})
    except Exception as e:
        current_app.logger.exception(e)
        return jsonify({"success": False}), 500


# ---------------------------------------------------------------------------
# REORDER SECTIONS
# ---------------------------------------------------------------------------
@admin_product_bp.route("/section/reorder/<product_id>", methods=["POST"])
def ajax_reorder_sections(product_id):
    oid = safe_oid(product_id)
    if not oid:
        return jsonify({"success": False}), 400

    try:
        order = request.json.get("order") or []
        product = products_collection().find_one({"_id": oid})
    except Exception:
        return jsonify({"success": False}), 400

    if not product:
        return jsonify({"success": False, "error": "Product not found"}), 404

    details = product.get("details", [])
    by_id = {d["id"]: d for d in details}

    new_list = []
    index = 0

    for sid in order:
        if sid in by_id:
            d = by_id[sid]
            d["order"] = index
            new_list.append(d)
            index += 1

    for d in details:
        if d["id"] not in order:
            d["order"] = index
            new_list.append(d)
            index += 1

    try:
        products_collection().update_one({"_id": oid}, {"$set": {"details": new_list}})
        return jsonify({"success": True})
    except Exception as e:
        current_app.logger.exception(e)
        return jsonify({"success": False}), 500


# ---------------------------------------------------------------------------
# DELETE IMAGE
# ---------------------------------------------------------------------------
@admin_product_bp.route("/delete-image/<product_id>/<filename>")
def delete_image(product_id, filename):
    oid = safe_oid(product_id)
    if not oid:
        flash("Invalid product ID.", "danger")
        return redirect(url_for("admin_product.list_products"))

    try:
        product = products_collection().find_one({"_id": oid})
    except Exception:
        product = None

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("admin_product.list_products"))

    imgs = product.get("images", [])
    if filename in imgs:
        imgs.remove(filename)

        primary = product.get("primary_image")
        if filename == primary:
            primary = imgs[0] if imgs else None

        i1, i2, i3 = images_to_fields(imgs)

        try:
            products_collection().update_one(
                {"_id": oid},
                {"$set": {
                    "images": imgs,
                    "primary_image": primary,
                    "image": i1,
                    "image2": i2,
                    "image3": i3
                }}
            )
        except Exception as e:
            print("⚠ WARNING: Failed to update image list:", e)

        try:
            path = os.path.join("static", "uploads", "products", filename)
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

    flash("Image deleted.", "success")
    return redirect(url_for("admin_product.edit_product", id=product_id))


# ---------------------------------------------------------------------------
# SET PRIMARY IMAGE
# ---------------------------------------------------------------------------
@admin_product_bp.route("/set-primary/<product_id>/<filename>")
def set_primary(product_id, filename):
    oid = safe_oid(product_id)
    if not oid:
        flash("Invalid product ID.", "danger")
        return redirect(url_for("admin_product.list_products"))

    try:
        product = products_collection().find_one({"_id": oid})
    except Exception:
        product = None

    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("admin_product.list_products"))

    imgs = product.get("images", [])

    if filename not in imgs:
        flash("Invalid image.", "danger")
        return redirect(url_for("admin_product.edit_product", id=product_id))

    i1, i2, i3 = images_to_fields(imgs)

    try:
        products_collection().update_one(
            {"_id": oid},
            {"$set": {
                "primary_image": filename,
                "image": filename,
                "image2": i2,
                "image3": i3
            }}
        )
    except Exception as e:
        print("❌ ERROR: Failed to update primary image:", e)

    flash("Primary image updated.", "success")
    return redirect(url_for("admin_product.edit_product", id=product_id))


# ---------------------------------------------------------------------------
# DELETE PRODUCT
# ---------------------------------------------------------------------------
@admin_product_bp.route("/delete/<id>")
def delete_product(id):
    oid = safe_oid(id)
    if not oid:
        flash("Invalid product ID.", "danger")
        return redirect(url_for("admin_product.list_products"))

    try:
        product = products_collection().find_one({"_id": oid})
    except Exception:
        product = None

    if product:
        for img in product.get("images", []):
            try:
                path = os.path.join("static/uploads/products", img)
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass

        try:
            products_collection().delete_one({"_id": oid})
        except Exception as e:
            print("⚠ WARNING: Failed to delete product from DB:", e)

    flash("Product deleted.", "danger")
    return redirect(url_for("admin_product.list_products"))
