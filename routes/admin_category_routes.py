# routes/admin_category_routes.py

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash
)
from utils.auth_decorators import admin_required
from database.connection import get_collection
from bson import ObjectId
from bson.errors import InvalidId
from werkzeug.utils import secure_filename
import os


# ---------------------------------------------------------
# BLUEPRINT SETUP
# ---------------------------------------------------------
admin_category_bp = Blueprint(
    "admin_category",
    __name__,
    url_prefix="/admin/categories"
)


# ---------------------------------------------------------
# FILE UPLOAD PATH
# ---------------------------------------------------------
UPLOAD_FOLDER = "static/uploads/categories"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------------------------------------------
# SAFE SLUG GENERATOR
# ---------------------------------------------------------
def generate_slug(name: str):
    try:
        slug = (
            name.lower()
            .strip()
            .replace(" ", "-")
            .replace("/", "-")
        )
        return slug
    except Exception:
        return None


# ---------------------------------------------------------
# SAFE OBJECTID PARSER
# ---------------------------------------------------------
def safe_oid(value):
    try:
        return ObjectId(value)
    except InvalidId:
        print(f"⚠ WARNING: Invalid ObjectId → {value}")
        return None
    except Exception as e:
        print("⚠ WARNING: ObjectId parse error:", e)
        return None


# ---------------------------------------------------------
# LIST CATEGORIES
# ---------------------------------------------------------
@admin_category_bp.route("/")
@admin_required
def list_categories():
    try:
        categories = list(get_collection("categories").find().sort("name", 1))
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
        name = (request.form.get("name") or "").strip()

        if not name:
            flash("Category name is required.", "danger")
            return redirect(url_for("admin_category.add_category"))

        slug = generate_slug(name)

        # Prevent duplicate slugs
        col = get_collection("categories")
        if col.find_one({"slug": slug}):
            flash("Category already exists!", "danger")
            return redirect(url_for("admin_category.add_category"))

        # Image upload (optional)
        image_filename = None
        image_file = request.files.get("image")

        if image_file and image_file.filename:
            try:
                image_filename = secure_filename(image_file.filename)
                image_path = os.path.join(UPLOAD_FOLDER, image_filename)
                image_file.save(image_path)
            except Exception as e:
                print("⚠ WARNING: Image upload failed:", e)
                flash("Image upload failed.", "warning")

        # Insert category
        try:
            col.insert_one({
                "name": name,
                "slug": slug,
                "image": image_filename
            })
            flash("Category added successfully!", "success")
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
    oid = safe_oid(id)

    if not oid:
        flash("Invalid category ID.", "danger")
        return redirect(url_for("admin_category.list_categories"))

    try:
        category = col.find_one({"_id": oid})
    except Exception as e:
        print("❌ ERROR: Failed to load category:", e)
        category = None

    if not category:
        flash("Category not found.", "danger")
        return redirect(url_for("admin_category.list_categories"))

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()

        if not name:
            flash("Category name is required.", "danger")
            return redirect(url_for("admin_category.edit_category", id=id))

        slug = generate_slug(name)

        # Optional image replacement
        image_file = request.files.get("image")
        current_image = category.get("image")

        if image_file and image_file.filename:
            try:
                new_filename = secure_filename(image_file.filename)
                new_path = os.path.join(UPLOAD_FOLDER, new_filename)
                image_file.save(new_path)

                # Remove old image safely
                if current_image:
                    old_path = os.path.join(UPLOAD_FOLDER, current_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)

                current_image = new_filename

            except Exception as e:
                print("⚠ WARNING: Failed saving new category image:", e)
                flash("Image upload failed.", "warning")

        # Update category document
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
    oid = safe_oid(id)

    if not oid:
        flash("Invalid category ID.", "danger")
        return redirect(url_for("admin_category.list_categories"))

    # Load category before deleting
    try:
        category = col.find_one({"_id": oid})
    except Exception as e:
        print("⚠ WARNING: Failed to load category:", e)
        category = None

    # Delete image safely
    if category:
        try:
            filename = category.get("image")
            if filename:
                path = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.exists(path):
                    os.remove(path)
        except Exception as e:
            print("⚠ WARNING: Failed to delete image:", e)

    # Delete DB record
    try:
        col.delete_one({"_id": oid})
        flash("Category deleted successfully!", "success")
    except Exception as e:
        print("❌ ERROR: Failed to delete category:", e)
        flash("Failed to delete category.", "danger")

    return redirect(url_for("admin_category.list_categories"))
