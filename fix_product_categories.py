from app_factory import AppFactory
from database.connection import get_collection

factory = AppFactory()
app = factory.create_app()

with app.app_context():
    print("🔧 Normalizing product.category values...")

    # Get all categories
    cats = list(get_collection("categories").find())
    slug_map = {c["name"].strip().lower(): c["slug"].strip().lower() for c in cats}

    products = get_collection("products")
    updated = 0

    for p in products.find():
        raw = (p.get("category") or "").strip().lower()

        # Match category name → slug
        if raw in slug_map:
            correct_slug = slug_map[raw]

            if p.get("category") != correct_slug:
                products.update_one(
                    {"_id": p["_id"]},
                    {"$set": {"category": correct_slug}}
                )
                updated += 1

    print(f"✔ Updated {updated} product categories.")
