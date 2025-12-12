"""
ads_client.py
------------------------------------
Client for fetching ads from DCORP backend with:
    - Memory caching
    - Normalized URLs
    - Timeouts & network safety
    - Structured debug logging
    - Future multi-ad support

This file is intentionally dependency-light so it works inside
Flask request context OR background tasks.
"""

import requests
import time
from flask import current_app
from urllib.parse import urljoin


# ============================================================
# IN-MEMORY CACHE (per process)
# ============================================================
AD_CACHE = {}           # { slot_id: (ad_dict_or_none, timestamp) }
CACHE_TTL = 20          # seconds
MAX_CACHE_SIZE = 50     # safety cap


# ============================================================
# NORMALIZATION HELPERS
# ============================================================
def _normalize_ad(ad: dict, base_url: str):
    """
    Ensures ad fields are safe and image URL is absolute.
    Returns None for invalid/broken ads.
    """
    if not ad or not isinstance(ad, dict):
        return None

    # campaign_id required
    campaign_id = ad.get("campaign_id")
    if not campaign_id:
        return None

    img = ad.get("image_url")

    # Make image absolute
    if img:
        img = img.strip()

        # /static/uploads/... → join with base URL
        if img.startswith("/"):
            ad["image_url"] = urljoin(base_url, img)

        # relative filename → assume DCORP uploads dir
        elif not img.startswith("http"):
            ad["image_url"] = urljoin(base_url, f"/static/uploads/{img}")

        else:
            ad["image_url"] = img
    else:
        ad["image_url"] = None

    return ad


# ============================================================
# CORE FETCH FUNCTION (with caching)
# ============================================================
def fetch_ad(slot_id: str):
    """
    Fetch a SINGLE ad for a slot from DCORP backend.
    Cached for 20 seconds per slot for performance.

    Returns:
        dict | None
    """
    now = time.time()

    try:
        base_url = current_app.config.get(
            "DCORP_API_URL",
            "http://127.0.0.1:5000"
        )

        # ----------------------------------------------------
        # CACHE LOOKUP
        # ----------------------------------------------------
        cached = AD_CACHE.get(slot_id)
        if cached:
            ad, ts = cached
            if now - ts < CACHE_TTL:
                return ad  # may be None or a valid ad

        # Cache overflow guard
        if len(AD_CACHE) > MAX_CACHE_SIZE:
            AD_CACHE.clear()

        # ----------------------------------------------------
        # SAFE NETWORK CALL
        # ----------------------------------------------------
        url = f"{base_url}/api/ads/slot/{slot_id}"

        try:
            response = requests.get(url, timeout=5)
        except Exception:
            # Network unreachable → store temporary None
            AD_CACHE[slot_id] = (None, now)
            return None

        if response.status_code != 200:
            AD_CACHE[slot_id] = (None, now)
            return None

        data = response.json() if response.content else {}
        raw_ad = data.get("ad")

        if not raw_ad:
            AD_CACHE[slot_id] = (None, now)
            return None

        # Normalize
        ad = _normalize_ad(raw_ad, base_url)

        # Cache result
        AD_CACHE[slot_id] = (ad, now)
        return ad

    except Exception as e:
        print("[ads_client ERROR]", e)
        return None


# ============================================================
# MULTI-AD SUPPORT (future-safe)
# ============================================================
def fetch_ads(slot_id: str, limit=3):
    """
    Returns a LIST of ads for a slot.
    Timeless Threads currently uses only 1 per slot.
    """
    ad = fetch_ad(slot_id)
    return [ad] if ad else []
