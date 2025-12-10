#!/usr/bin/env python3
"""
scripts/migrate_products.py

Purpose:
--------
Normalize all product documents to the newer schema:

- Ensure slug exists + normalized
- Normalize category reference → category_id (string)
- Ensure images fields exist: image, image2, image3
- Add created_at if missing
- Ensure 'published' exists
- Standardize numeric types for price, discount

Usage:
------
    python scripts/migrate_products.py --dry-run
    python scripts/migrate_products.py
"""

import os
import sys
import json
import argparse
from datetime import datetime
from bson import ObjectId, json_util

# ------------------------------------------------------
# Load Project Root
# ------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from app import app
from database.connection import get_collection

# Optional slugify
try:
    from slugify import slugify as lib_slugify
except Exception:
    lib_slugify = None


# ------------------------------------------------------
# Helpers
# ------------------------------------------------------
def slugify(name: str) -> str:
    """Safe slug generator."""
    if not name:
        return ""
    if lib_slugify:
        return lib_slugify(name)
    return "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")


def oid_string(value):
    """Return value as string if it's a valid ObjectId-like value, else None."""
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, str):
        v = value.strip()
        return v if ObjectId.is_valid(v) else None
    return None


def normalize_category(cat_field, cat_collection):
    """
    Normalize ANY old category reference into a clean category_id string.

    Accepts:
        - ObjectId
        - string slug
        - string ObjectId
        - string name
        - dict with "_id" or "id"

    Returns:
        category_id string or None
    """
    if cat_field is None:
        return None

    # Case 1 — direct ObjectId
    if isinstance(cat_field, ObjectId):
        return str(cat_field)

    # Case 2 — dict { "_id": ObjectId, ... }
    if isinstance(cat_field, dict):
        cid = cat_field.get("_id") or cat_field.get("id")
        if isinstance(cid, ObjectId):
            return str(cid)
        if isinstance(cid, str) and ObjectId.is_valid(cid):
            return cid
        return None  # no usable identifier

    # Case 3 — string: could be slug, name, or ObjectId
    if isinstance(cat_field, str):
        value = cat_field.strip()

        # If it is already a valid ObjectId string
        if ObjectId.is_valid(value):
            return value

        # Try slug
        found = cat_collection.find_one({"slug": value})
        if found:
            return str(found["_id"])

        # Try exact name
        found = cat_collection.find_one({"name": value})
        if found:
            return str(found["_id"])

        # Try case-insensitive name
        found = cat_collection.find_one({"name": {"$regex": f"^{value}$", "$options": "i"}})
        if found:
            return str(found["_id"])

    return None  # unable to normalize


def safe_number(value, default=0.0):
    """Convert field to float safely."""
    try:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str) and value.strip():
            return float(value)
    except Exception:
        pass
    return default


def backup_products(products, out_dir="backups"):
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_path = os.path.join(out_dir, f"products_backup_{ts}.json")

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(json_util.dumps(products, indent=2))

    return out_path


# ------------------------------------------------------
# Migration Process
# ------------------------------------------------------
def run_migration(dry_run=False, backup=True):

    with app.app_context():

        prod_col = get_collection("products")
        cat_col = get_collection("categories")

        products = list(prod_col.find({}))
        total = len(products)
        print(f"🔍 Loaded {total} product documents.")

        # ------------ Backup ------------
        if backup:
            path = backup_products(products)
            print(f"🟦 Backup saved → {path}")

        updates_preview = []
        updated_count = 0

        for p in products:

            pid = str(p["_id"])
            updates = {}

            # --------------------------
            # 1. Slug normalization
            # --------------------------
            if not p.get("slug") and p.get("name"):
                updates["slug"] = slugify(p["name"])

            # --------------------------
            # 2. Category normalization
            # --------------------------
            cat_field = p.get("category_id", None)
            if not cat_field:
                cat_field = p.get("category", None)

            new_cat_id = normalize_category(cat_field, cat_col)
            if new_cat_id and p.get("category_id") != new_cat_id:
                updates["category_id"] = new_cat_id

            # --------------------------
            # 3. Image normalization
            # --------------------------
            # Never override existing valid images.
            if not p.get("image"):
                # Best fallback order
                primary = p.get("primary_image")
                images = p.get("images") or []

                if primary:
                    updates["image"] = primary
                elif images:
                    updates["image"] = images[0]
                else:
                    updates["image"] = "no_image.jpg"

            if "image2" not in p:
                updates["image2"] = None

            if "image3" not in p:
                updates["image3"] = None

            # --------------------------
            # 4. created_at default
            # --------------------------
            if not p.get("created_at"):
                updates["created_at"] = datetime.utcnow()

            # --------------------------
            # 5. published default
            # --------------------------
            if "published" not in p:
                updates["published"] = True

            # --------------------------
            # 6. price / discount types
            # --------------------------
            if "price" in p:
                updates["price"] = safe_number(p.get("price"), default=0.0)

            if "discount" in p:
                updates["discount"] = safe_number(p.get("discount"), default=0.0)

            # --------------------------
            # APPLY OR PREVIEW
            # --------------------------
            if updates:
                preview = {"_id": pid, "updates": updates}
                updates_preview.append(preview)

                if dry_run:
                    print(json.dumps(preview, indent=2))
                else:
                    prod_col.update_one({"_id": p["_id"]}, {"$set": updates})
                    updated_count += 1

        # ------------------------------
        # Summary
        # ------------------------------
        print("\n===== MIGRATION SUMMARY =====")
        print(f"Total scanned: {total}")
        print(f"Products needing fixes: {len(updates_preview)}")
        if dry_run:
            print("Mode: DRY RUN (no changes applied)")
        else:
            print(f"Products updated: {updated_count}")
        print("=============================\n")

        return {
            "scanned": total,
            "preview_count": len(updates_preview),
            "applied": updated_count
        }


# ------------------------------------------------------
# CLI
# ------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate and normalize product documents.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing to DB")
    parser.add_argument("--no-backup", action="store_true", help="Skip JSON backup before applying")
    args = parser.parse_args()

    run_migration(dry_run=args.dry_run, backup=not args.no_backup)
    sys.exit(0)
