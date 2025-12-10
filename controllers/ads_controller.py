# controllers/ads_controller.py

from flask import current_app, render_template, request
import datetime

from database.ads_models import (
    get_slot,
    impressions_col   # lazy-loaded getter
)
from utils.ads_engine import pick_ad_for_slot


def render_ad_slot(slot_name):
    """
    Render an ad for a given slot.
    Production-ready:
    - Protects against config errors
    - Protects against DB failures
    - Ignores ad rendering errors silently (ads should never break user pages)
    - Ensures impressions are logged safely
    """

    try:
        settings = current_app.config.get("SETTINGS")
    except RuntimeError:
        # No app context: fail quietly
        return ""
    except Exception as e:
        print("❌ ERROR: SETTINGS missing or corrupted:", e)
        return ""

    # ----------------------------------------------------
    # Global ON / OFF switch
    # ----------------------------------------------------
    try:
        if not getattr(settings, "ADS_SYSTEM_ENABLED", False):
            return ""
    except Exception:
        return ""

    # ----------------------------------------------------
    # Validate Slot
    # ----------------------------------------------------
    try:
        slot = get_slot(slot_name)
    except Exception as e:
        print(f"❌ ERROR: Failed to fetch slot '{slot_name}':", e)
        return ""

    if not slot:
        return ""

    # ----------------------------------------------------
    # Pick an ad for the slot
    # ----------------------------------------------------
    try:
        ad = pick_ad_for_slot(slot_name)
    except Exception as e:
        print(f"❌ ERROR: pick_ad_for_slot() failed for slot '{slot_name}':", e)
        return ""

    if not ad:
        return ""

    # ----------------------------------------------------
    # Log the impression (never allowed to break site)
    # ----------------------------------------------------
    try:
        impressions_col().insert_one({
            "ad_id": ad.get("_id"),
            "slot": slot_name,
            "timestamp": datetime.datetime.utcnow(),
            "ref": request.referrer,
            "ua": request.headers.get("User-Agent")
        })
    except Exception as e:
        print("⚠ WARNING: Failed to log ad impression:", e)

    # ----------------------------------------------------
    # Render HTML snippet
    # ----------------------------------------------------
    try:
        return render_template("ads/ad_snippet.html", ad=ad)
    except Exception as e:
        print("❌ ERROR: Failed to render ad template:", e)
        return ""
