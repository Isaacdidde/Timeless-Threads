"""
utils/ads_engine.py
----------------------------------------
Core ad-selection logic for Timeless Threads.

Responsibilities:
    • Pick 1 active campaign for a slot
    • Handle selection randomness (future: weighting)
    • Log impressions safely
    • Ensure ObjectId correctness
"""

import random
from datetime import datetime
from bson import ObjectId

from database.ads_models import (
    campaigns_col,
    impressions_col,
)


# ============================================================
# AD SELECTION ENGINE
# ============================================================
def pick_ad_for_slot(slot_name: str):
    """
    Selects a single active ad for a slot.

    Current logic:
        - Filter campaigns by:
              status="live"
              creative.target_slots contains slot
        - Randomly choose one

    Returns:
        dict | None
    """

    if not slot_name:
        return None

    try:
        # Fetch live, correctly targeted campaigns
        campaigns = list(
            campaigns_col().find({
                "status": "live",
                "creative.target_slots": slot_name,
            })
        )

        if not campaigns:
            return None

        # Random selection for now (can replace with weighted scoring)
        return random.choice(campaigns)

    except Exception as e:
        print("[ads_engine ERROR] pick_ad_for_slot:", e)
        return None


# ============================================================
# IMPRESSION LOGGER
# ============================================================
def log_impression(ad_id, slot_name: str, ref: str = None):
    """
    Log an impression in the database.

    Args:
        ad_id: str or ObjectId
        slot_name: the slot where the ad rendered
        ref: optional page slug, product ID, etc.

    Never throws — safe for frontend rendering.
    """

    try:
        # Normalize ad_id → ObjectId
        if isinstance(ad_id, str):
            try:
                ad_id = ObjectId(ad_id)
            except Exception:
                # Invalid ID → skip logging
                print("[ads_engine] Invalid ad_id:", ad_id)
                return

        impressions_col().insert_one({
            "ad_id": ad_id,
            "slot": slot_name,
            "ref": ref,
            "timestamp": datetime.utcnow(),
        })

    except Exception as e:
        # Do not allow impression logging to break page rendering
        print("[ads_engine ERROR] log_impression:", e)
