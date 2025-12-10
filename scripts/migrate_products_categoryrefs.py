#!/usr/bin/env python3
"""
scripts/migrate_products_categoryrefs.py

Purpose:
--------
Fix legacy products where:
    - `category` = string (old format)
    - `category_id` is missing (new format)
Also normalizes:
    - primary image -> product.image

Usage:
------
    # Preview (no DB writes)
    python scripts/migrate_products_categoryrefs.py --dry-run

    # Apply migration
    python scripts/migrate_products_categoryrefs.py

Features:
---------
✔ Safe ObjectId handling
✔ Robust category matching (slug → name → case-insensitive name)
✔ Image fallback logic
✔ JSON preview for auditing
✔ Graceful failure handling
"""

import os
import sys
import argparse
import json
from datetime import datetime
from bson import ObjectId, json_util

# ------------------------------------------------------
# Load Project Root
# ------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from app import app                    # Flask AppFactory
from database.connection import get_collection


# ------------------------------------------------------
# Helper: pretty stringify _id
# ------------------------------------------------------
def oid(doc):
    try:
        return str(doc.get("_id"))
    except Exception:
        return "<invalid-id>"


# ------------------------------------------------------
# Helper: match category safely
# ------------------------------------------------------
def find_category(cat_col, value):
    """
    Attempts to match a category string to a category document.
    Priority:
        1. Exact slug
        2. Exact name (case-sensitive)
        3. Case-insensitive name
    """
    if not value:
        return None

    value = str(value).strip()

    # Try slug
    cat = cat_col.find_one({"slug": value})
    if cat:
        return cat

    # Try exact name
    cat = cat_col.find_one({"name": value})
    if cat:
        return cat

    # Try case-insensitive name
    return cat_col.find_one({"name": {"$regex": f"^{value}$", "$options": "i"}})


# ------------------------------------------------------
# Main Migration Logic
# ------------------------------------------------------
def run(dry_run=True):
    with app.app_context():

        prod_col = get_collection("products")
        cat_col = get_collection("categories")

        # Select legacy products
        query = {
            "category": {"$exists": True},
            "category_id": {"$exists": False}
        }

        candidates = list(prod_col.find(query))
        print(f"🔍 Found {len(candidates)} candidate products.\n")

        preview = []
        applied = 0

        for p in candidates:

            prod_id = oid(p)
            old_cat_value = p.get("category")

            category_doc = find_category(cat_col, old_cat_value)
            if not category_doc:
                print(f"⚠️  No category match for product {prod_id} (value='{old_cat_value}')")
                continue

            updates = {}

            # Add correct category_id
            updates["category_id"] = str(category_doc["_id"])

            # Normalize primary image → image field
            if not p.get("image"):
                primary = p.get("primary_image")
                img_list = p.get("images") or []

                if primary:
                    updates["image"] = primary
                elif isinstance(img_list, list) and img_list:
                    updates["image"] = img_list[0]
                # else: leave empty (app uses fallback)

            preview.append({
                "_id": prod_id,
                "category_was": old_cat_value,
                "category_id_set": updates.get("category_id"),
                "image_set": updates.get("image"),
                "updated_at": datetime.utcnow().isoformat()
            })

            # Apply changes to DB
            if not dry_run and updates:
                try:
                    prod_col.update_one({"_id": p["_id"]}, {"$set": updates})
                    applied += 1
                except Exception as e:
                    print(f"❌ Failed updating product {prod_id}: {e}")

        # --------------------------
        # Summary Output
        # --------------------------
        print("\n========= SUMMARY =========")
        print(f"Preview items: {len(preview)}")
        if dry_run:
            print("\n🟦 DRY RUN — No DB changes applied.")
            print("Preview of first 10 changes:\n")
            print(json.dumps(preview[:10], indent=2, default=json_util.default))
        else:
            print(f"🟩 APPLIED updates to {applied} products.")

        print("===========================\n")


# ------------------------------------------------------
# CLI Entry Point
# ------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview only; no DB writes")
    args = parser.parse_args()

    run(dry_run=args.dry_run)
