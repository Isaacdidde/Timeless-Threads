# controllers/ad_campaign_controller.py

import datetime
from bson import ObjectId
from database.connection import get_collection
from utils.file_upload import handle_upload


# ---------------------------------------------------------
# SAFE COLLECTION GETTERS (Lazy-loaded)
# ---------------------------------------------------------
def campaigns_col():
    return get_collection("ads_campaigns")

def slots_col():
    return get_collection("ads_slots")


# ---------------------------------------------------------
# FETCH ALL CAMPAIGNS (Production-Safe)
# ---------------------------------------------------------
def get_campaigns():
    try:
        return list(campaigns_col().find().sort("_id", -1))
    except Exception as e:
        print("❌ ERROR: Failed to fetch campaigns:", e)
        return []


# ---------------------------------------------------------
# FETCH SLOTS (Production-Safe)
# ---------------------------------------------------------
def get_slots():
    try:
        return list(slots_col().find().sort("name", 1))
    except Exception as e:
        print("❌ ERROR: Failed to fetch ad slots:", e)
        return []


# ---------------------------------------------------------
# SAVE CAMPAIGN (Production-Ready & Validated)
# ---------------------------------------------------------
def save_campaign(form, files):
    """
    Create a new ad campaign document.
    Logic preserved exactly, but now with safety checks.
    """

    # Required fields
    name = form.get("name", "").strip()

    if not name:
        print("❌ ERROR: Campaign name missing.")
        return None

    # Slots
    target_slots = form.getlist("target_slots") or []

    # Budget handling
    try:
        budget = float(form.get("budget", 0))
        if budget < 0:
            budget = 0
    except:
        budget = 0

    redirect_url = form.get("redirect_url", "").strip()
    status = form.get("status", "paused")

    # Parse start & end dates
    try:
        start_date = datetime.datetime.strptime(form.get("start_date"), "%Y-%m-%d")
    except:
        start_date = datetime.datetime.utcnow()

    try:
        end_date_raw = form.get("end_date")
        end_date = datetime.datetime.strptime(end_date_raw, "%Y-%m-%d") if end_date_raw else None
    except:
        end_date = None

    # File Upload
    creative_file = files.get("creative")
    creative_filename = None

    if creative_file:
        try:
            creative_filename = handle_upload(
                creative_file,
                "static/uploads/ads",
                {"jpg", "jpeg", "png", "webp", "gif", "mp4"}
            )
        except Exception as e:
            print("❌ ERROR: Failed to upload creative file:", e)

    # Support using a direct URL
    creative_url = creative_filename or form.get("creative_url", "").strip()

    # Final document
    document = {
        "name": name,
        "creative": {
            "filename": creative_url,
            "target_slots": target_slots,
        },
        "budget": budget,
        "redirect_url": redirect_url,
        "status": status,
        "start_date": start_date,
        "end_date": end_date,
        "created_at": datetime.datetime.utcnow(),
    }

    try:
        campaigns_col().insert_one(document)
        return document
    except Exception as e:
        print("❌ ERROR: Failed to save campaign:", e)
        return None


# ---------------------------------------------------------
# DELETE CAMPAIGN (Production-Safe)
# ---------------------------------------------------------
def delete_campaign(campaign_id):
    try:
        cid = ObjectId(campaign_id)
        campaigns_col().delete_one({"_id": cid})
    except Exception as e:
        print(f"❌ ERROR: Failed to delete campaign ({campaign_id}):", e)


# ---------------------------------------------------------
# GET SINGLE CAMPAIGN
# ---------------------------------------------------------
def get_campaign_by_id(campaign_id):
    try:
        return campaigns_col().find_one({"_id": ObjectId(campaign_id)})
    except Exception as e:
        print(f"❌ ERROR: Failed to fetch campaign ({campaign_id}):", e)
        return None
