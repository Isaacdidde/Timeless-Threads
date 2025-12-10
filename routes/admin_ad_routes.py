from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash
)
from utils.admin_required import admin_required

# Controller imports
try:
    from controllers.ad_campaign_controller import (
        get_campaigns,
        save_campaign,
        get_slots
    )
except Exception as e:
    print("❌ ERROR: Failed to import ad campaign controller:", e)
    # fallback stubs to prevent crashes
    def get_campaigns(): return []
    def get_slots(): return []
    def save_campaign(*args, **kwargs): return None


# ---------------------------------------------------------
# BLUEPRINT
# ---------------------------------------------------------
admin_ad_bp = Blueprint("admin_ads", __name__, url_prefix="/admin/ads")


# ---------------------------------------------------------
# LIST ALL AD CAMPAIGNS
# ---------------------------------------------------------
@admin_ad_bp.route("/", endpoint="campaigns")
@admin_required
def campaigns():

    try:
        campaigns = get_campaigns() or []
    except Exception as e:
        print("⚠ WARNING: Failed to load campaigns:", e)
        campaigns = []

    return render_template(
        "admin/ads/campaigns.html",
        campaigns=campaigns
    )


# ---------------------------------------------------------
# ADD A NEW AD CAMPAIGN
# ---------------------------------------------------------
@admin_ad_bp.route("/add", methods=["GET", "POST"], endpoint="add_campaign")
@admin_required
def add_campaign():

    # -----------------------------------------------------
    # POST REQUEST — Create Campaign
    # -----------------------------------------------------
    if request.method == "POST":
        try:
            save_campaign(request.form, request.files)
            flash("Campaign created successfully!", "success")
        except Exception as e:
            print("❌ ERROR: Failed to save campaign:", e)
            flash("Failed to save campaign. Check logs.", "danger")

        return redirect(url_for("admin_ads.campaigns"))

    # -----------------------------------------------------
    # GET REQUEST — Load Slots for Form
    # -----------------------------------------------------
    try:
        slots = get_slots() or []
    except Exception as e:
        print("⚠ WARNING: Failed to load ad slots:", e)
        slots = []

    return render_template(
        "admin/ads/add_campaign.html",
        slots=slots
    )
