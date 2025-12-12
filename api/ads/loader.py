from utils.ads_client import fetch_ad

def load_ads_for_slots(slots):
    ads = {}

    for slot in slots:
        try:
            ad = fetch_ad(slot)

            if ad:

                # ⭐ Convert BSON / SON / custom objects → dict
                if not isinstance(ad, dict):
                    try:
                        ad = dict(ad)      # safe conversion
                    except Exception:
                        # fallback: force key-value extraction
                        ad = {k: v for k, v in ad.items()}

                # ⭐ Safely inject slot_id only if ad is a dict
                if isinstance(ad, dict):
                    ad["slot_id"] = slot

            # Store final ad (may be None)
            ads[slot] = ad

        except Exception as e:
            print(f"⚠ Loading failed for slot '{slot}':", e)
            ads[slot] = None

    return ads
