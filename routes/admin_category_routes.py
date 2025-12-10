from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash
)
from utils.auth_decorators import admin_required
from database.connection import get_collection
from bson import ObjectId, errors as bson_errors
import os
from werkzeug.utils import secure_filename

admin_category_bp = Blueprint("admin_category", __name__, url_prefix="/admin/categories")

# Image upload folder
UPLOAD_FOLDER = "static/uploads/categories"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------------------------------------------
# HELPER: SAFE SLUG CREATOR
# ---------------------------------------------------------
def generate_slug(name):
    try:
        return name.lower().strip().replace(" ", "-")
    except Exception:
        return None


# ---------------------------------------------------------
# HELPER: SAFE OBJECT ID
# ---------------------------------------------------------
def safe_object_id(value):
    try:
        return ObjectId(value)
    except bson_errors.InvalidId:
        print(f"⚠ WARNING: Invalid ObjectId: {value}")
        return None
    except Exception as e:
        print(f"⚠ WARNING: ObjectId parse error: {e}")
        return None


# ---------------------------------------------------------
# LIST CATEGORIES
# ---------------------------------------------------------
@admin_category_bp.route("/")
@admin_required
def list_categories():
    try:
        categories = list(get_collection("categories").find())
    except Exception as e:
        print("⚠ WARNING: Failed to fetch categories:", e)
        categories = []

    return render_template("admin/categories/list.html", categories=categories)


# ---------------------------------------------------------
# ADD CATEGORY
# ---------------------------------------------------------
@admin_category_bp.route("/add", methods=["GET", "POST"])
@admin_required
def add_category():

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        slug = generate_slug(name)

        if not name:
            flash("Category name is required.", "danger")
            return redirect(url_for("admin_category.add_category"))

        image_filename = None
        image_file = request.files.get("image")

        # Image upload with safety
        if image_file and image_file.filename:
            try:
                image_filename = secure_filename(image_file.filename)
                image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                image_file.save(image_path)
            except Exception as e:
                print("⚠ WARNING: Category image upload failed:", e)
                flash("Image upload failed.", "warning")

        try:
            get_collection("categories").insert_one({
                "name": name,
                "slug": slug,
                "image": image_filename
            })
            flash("Category created successfully!", "success")
        except Exception as e:
            print("❌ ERROR: Failed to insert category:", e)
            flash("Failed to create category.", "danger")

        return redirect(url_for("admin_category.list_categories"))

    return render_template("admin/categories/add.html")


# ---------------------------------------------------------
# EDIT CATEGORY
# ---------------------------------------------------------
@admin_category_bp.route("/edit/<id>", methods=["GET", "POST"])
@admin_required
def edit_category(id):

    col = get_collection("categories")
    oid = safe_object_id(id)

    if not oid:
        flash("Invalid category ID.", "danger")
        return redirect(url_for("admin_category.list_categories"))

    try:
        category = col.find_one({"_id": oid})
    except Exception as e:
        print("❌ ERROR: Failed to fetch category:", e)
        category = None

    if not category:
        flash("Category not found.", "danger")
        return redirect(url_for("admin_category.list_categories"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        slug = generate_slug(name)

        if not name:
            flash("Category name is required.", "danger")
            return redirect(url_for("admin_category.edit_category", id=id))

        image_file = request.files.get("image")
        current_image = category.get("image")

        # Replace image if new file given
        if image_file and image_file.filename:
            try:
                new_filename = secure_filename(image_file.filename)
                new_path = os.path.join(UPLOAD_FOLDER, new_filename)
                image_file.save(new_path)

                # delete old file safely
                if current_image:
                    old_path = os.path.join(UPLOAD_FOLDER, current_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                current_image = new_filename

            except Exception as e:
                print("⚠ WARNING: Failed saving replacement category image:", e)
                flash("Image upload error.", "warning")

        # Update DB record safely
        try:
            col.update_one(
                {"_id": oid},
                {"$set": {
                    "name": name,
                    "slug": slug,
                    "image": current_image
                }}
            )
            flash("Category updated successfully!", "success")

        except Exception as e:
            print("❌ ERROR: Failed to update category:", e)
            flash("Error updating category.", "danger")

        return redirect(url_for("admin_category.list_categories"))

    return render_template("admin/categories/edit.html", category=category)


# ---------------------------------------------------------
# DELETE CATEGORY
# ---------------------------------------------------------
@admin_category_bp.route("/delete/<id>")
@admin_required
def delete_category(id):

    col = get_collection("categories")
    oid = safe_object_id(id)

    if not oid:
        flash("Invalid category ID.", "danger")
        return redirect(url_for("admin_category.list_categories"))

    try:
        category = col.find_one({"_id": oid})
    except Exception as e:
        print("⚠ WARNING: Could not load category for delete:", e)
        category = None

    if category:
        # Remove image file safely
        try:
            img_filename = category.get("image")
            if img_filename:
                img_path = os.path.join(UPLOAD_FOLDER, img_filename)
                if os.path.exists(img_path):
                    os.remove(img_path)
        except Exception as e:
            print("⚠ WARNING: Failed to delete category image:", e)

        # Delete category record
        try:
            col.delete_one({"_id": oid})
        except Exception as e:
            print("❌ ERROR: Failed to delete category from DB:", e)

    flash("Category deleted successfully!", "success")
    return redirect(url_for("admin_category.list_categories"))
