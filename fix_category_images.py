# fix_category_images.py

from app_factory import AppFactory
from database.connection import get_collection
import os


def fix_image_filenames():
    categories = get_collection("categories")

    updated_count = 0

    for cat in categories.find():
        image = cat.get("image")

        if not image:
            continue

        # Extract filename only
        filename = os.path.basename(image)

        # If already correct, skip
        if filename == image:
            continue

        # Update DB
        categories.update_one(
            {"_id": cat["_id"]},
            {"$set": {"image": filename}}
        )

        updated_count += 1
        print(f"✔ Fixed: {image}  →  {filename}")

    print(f"\n🎉 Completed! Updated {updated_count} category image paths.")


if __name__ == "__main__":
    print("🔧 Initializing Flask app...\n")

    # Load your app (same way app.py does)
    app = AppFactory().create_app()

    # Run inside app context
    with app.app_context():
        fix_image_filenames()
