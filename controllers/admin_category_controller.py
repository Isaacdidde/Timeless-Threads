import os
import uuid
from werkzeug.utils import secure_filename
from models.category_model import CategoryModel

UPLOAD_FOLDER = "static/uploads/categories"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class AdminCategoryController:
    """
    Production-ready version of category controller.
    Logic preserved, but with stronger safety + stability.
    """

    def __init__(self):
        try:
            self.categories = CategoryModel()
        except Exception as e:
            print("❌ ERROR: Cannot initialize CategoryModel:", e)
            self.categories = None

    # --------------------------------------------------------------
    # Helper: Safe slug generator
    # --------------------------------------------------------------
    def _make_slug(self, name):
        if not name:
            return ""
        return (
            name.strip()
            .lower()
            .replace("&", "and")
            .replace(" ", "-")
        )

    # --------------------------------------------------------------
    # Helper: Safe file save
    # --------------------------------------------------------------
    def _save_image(self, image_file):
        """
        Saves uploaded image with collision-safe filename.
        Returns filename or None.
        """

        if not image_file or not image_file.filename:
            return None

        try:
            original = secure_filename(image_file.filename)
            ext = os.path.splitext(original)[1].lower()

            # Strong filename uniqueness
            filename = f"{uuid.uuid4().hex}{ext}"
            path = os.path.join(UPLOAD_FOLDER, filename)

            image_file.save(path)
            return filename

        except Exception as e:
            print("❌ ERROR: Failed to save image:", e)
            return None

    # --------------------------------------------------------------
    # CREATE CATEGORY
    # --------------------------------------------------------------
    def create_category(self, name, image_file):
        if not self.categories:
            print("❌ ERROR: CategoryModel unavailable.")
            return False

        name = (name or "").strip()
        if not name:
            print("❌ ERROR: Category name is required.")
            return False

        slug = self._make_slug(name)
        image_filename = self._save_image(image_file)

        data = {
            "name": name,
            "slug": slug,
            "image": image_filename,
        }

        try:
            self.categories.create(data)
            return True
        except Exception as e:
            print("❌ ERROR: Failed to create category:", e)
            return False

    # --------------------------------------------------------------
    # UPDATE CATEGORY
    # --------------------------------------------------------------
    def update_category(self, id, name, image_file, old_image):
        if not self.categories:
            print("❌ ERROR: CategoryModel unavailable.")
            return False

        name = (name or "").strip()
        slug = self._make_slug(name)

        filename = old_image  # Default keep old

        # If new file uploaded → replace
        new_image = self._save_image(image_file)
        if new_image:
            filename = new_image

            # Delete old image safely
            if old_image:
                try:
                    old_path = os.path.join(UPLOAD_FOLDER, old_image)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except Exception as e:
                    print("⚠ WARNING: Failed to delete old image:", e)

        try:
            self.categories.update(id, {
                "name": name,
                "slug": slug,
                "image": filename
            })
            return True
        except Exception as e:
            print("❌ ERROR: Failed to update category:", e)
            return False

    # --------------------------------------------------------------
    # DELETE CATEGORY
    # --------------------------------------------------------------
    def delete_category(self, id, image_filename):
        if not self.categories:
            print("❌ ERROR: CategoryModel unavailable.")
            return False

        # Delete image file
        if image_filename:
            try:
                file_path = os.path.join(UPLOAD_FOLDER, image_filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                print("⚠ WARNING: Failed to delete image file:", e)

        try:
            self.categories.delete(id)
            return True
        except Exception as e:
            print("❌ ERROR: Failed to delete category:", e)
            return False
