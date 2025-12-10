# database/ads_models.py

from bson import ObjectId, errors as bson_errors
import datetime
from database.connection import get_collection


# ---------------------------------------------------------
# SAFE COLLECTION ACCESSORS (lazy-loaded)
# ---------------------------------------------------------
def slots_col():
    try:
        return get_collection("ads_slots")
    except Exception as e:
        print("❌ ERROR: Could not load ads_slots collection:", e)
        return None

def campaigns_col():
    try:
        return get_collection("ads_campaigns")
    except Exception as e:
        print("❌ ERROR: Could not load ads_campaigns collection:", e)
        return None

def impressions_col():
    try:
        return get_collection("ads_impressions")
    except Exception as e:
        print("❌ ERROR: Could not load ads_impressions collection:", e)
        return None


# ---------------------------------------------------------
# CREATE SLOT
# ---------------------------------------------------------
def create_slot(name, description):
    col = slots_col()
    if not col:
        print("❌ ERROR: slots_col unavailable in create_slot()")
        return None

    try:
        return col.insert_one({
            "name": name,
            "description": description,
            "created_at": datetime.datetime.utcnow()
        })
    except Exception as e:
        print("❌ ERROR: Failed to create ad slot:", e)
        return None


# ---------------------------------------------------------
# GET SLOT BY NAME
# ---------------------------------------------------------
def get_slot(name):
    col = slots_col()
    if not col:
        return None

    try:
        return col.find_one({"name": name})
    except Exception as e:
        print(f"⚠ WARNING: Failed to fetch slot '{name}':", e)
        return None


# ---------------------------------------------------------
# CREATE CAMPAIGN
# ---------------------------------------------------------
def create_campaign(data):
    col = campaigns_col()
    if not col:
        print("❌ ERROR: campaigns_col unavailable in create_campaign()")
        return None

    try:
        data["created_at"] = datetime.datetime.utcnow()
        return col.insert_one(data)
    except Exception as e:
        print("❌ ERROR: Failed to create ad campaign:", e)
        return None


# ---------------------------------------------------------
# GET ACTIVE CAMPAIGNS FOR A SLOT
# ---------------------------------------------------------
def get_active_campaigns(slot_name):
    col = campaigns_col()
    if not col:
        return []

    try:
        return list(
            col.find({
                "status": "live",
                "creative.target_slots": slot_name
            })
        )
    except Exception as e:
        print(f"⚠ WARNING: Failed to get active campaigns for slot '{slot_name}':", e)
        return []


# ---------------------------------------------------------
# LOG IMPRESSION (SAFE FOR HIGH-TRAFFIC)
# ---------------------------------------------------------
def log_impression(ad_id, slot_name, ref):
    col = impressions_col()
    if not col:
        print("⚠ WARNING: impressions_col unavailable — impression not logged")
        return

    # Validate ad_id
    try:
        oid = ObjectId(ad_id)
    except bson_errors.InvalidId:
        print(f"⚠ WARNING: Invalid ad_id '{ad_id}' — impression skipped")
        return
    except Exception as e:
        print("⚠ WARNING: Failed to build ObjectId for impression:", e)
        return

    # Attempt to insert impression
    try:
        col.insert_one({
            "ad_id": oid,
            "slot": slot_name,
            "timestamp": datetime.datetime.utcnow(),
            "ref": ref
        })
    except Exception as e:
        print("⚠ WARNING: Failed to log ad impression:", e)
