from flask import Blueprint, render_template
from utils.auth_decorators import admin_required
from database.connection import get_collection
from datetime import datetime, timedelta

panel_bp = Blueprint("admin_panel", __name__, url_prefix="/admin")


@panel_bp.route("/dashboard")
@admin_required
def dashboard():

    # -------------------------------------------------------------------
    # SAFE COLLECTION GETTERS
    # -------------------------------------------------------------------
    def safe_col(name):
        try:
            return get_collection(name)
        except Exception as e:
            print(f"⚠ WARNING: Failed to load collection '{name}':", e)
            return None

    users_col = safe_col("db.users")
    advertisers_col = safe_col("advertisers")
    campaigns_col = safe_col("campaigns")
    clicks_col = safe_col("ad_clicks")

    # -------------------------------------------------------------------
    # SAFE COUNT FUNCTION
    # -------------------------------------------------------------------
    def safe_count(col, query=None):
        if col is None:
            return 0
        try:
            return col.count_documents(query or {})
        except Exception as e:
            print(f"⚠ WARNING: count_documents failed: {e}")
            return 0

    # -------------------------------------------------------------------
    # BASIC COUNTS
    # -------------------------------------------------------------------
    total_customers = safe_count(users_col)
    total_advertisers = safe_count(advertisers_col)
    total_campaigns = safe_count(campaigns_col)
    total_clicks = safe_count(clicks_col)

    # -------------------------------------------------------------------
    # TODAY'S CLICKS
    # -------------------------------------------------------------------
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        today_clicks = clicks_col.count_documents({"date": today}) if clicks_col else 0
    except Exception as e:
        print("⚠ WARNING: Failed to count today's clicks:", e)
        today_clicks = 0

    # -------------------------------------------------------------------
    # SLOT PERFORMANCE
    # -------------------------------------------------------------------
    slot_names = []
    slot_clicks = []

    if clicks_col is not None:
        try:
            slot_data = clicks_col.aggregate([
                {"$group": {"_id": "$slot", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ])

            for s in slot_data:
                slot_names.append(s.get("_id", "unknown"))
                slot_clicks.append(s.get("count", 0))
        except Exception as e:
            print("⚠ WARNING: Slot performance aggregation failed:", e)
    else:
        print("⚠ WARNING: clicks_col unavailable for slot performance.")

    # -------------------------------------------------------------------
    # NEW USERS IN LAST 7 DAYS
    # -------------------------------------------------------------------
    users_days = []
    users_counts = []

    if users_col is not None:
        try:
            last7 = datetime.now() - timedelta(days=7)

            user_stats = users_col.aggregate([
                {"$match": {"created_at": {"$gte": last7}}},
                {"$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ])

            for day in user_stats:
                users_days.append(day.get("_id"))
                users_counts.append(day.get("count", 0))

        except Exception as e:
            print("⚠ WARNING: Failed to fetch last 7 days user stats:", e)
    else:
        print("⚠ WARNING: users_col unavailable for user stats.")

    # -------------------------------------------------------------------
    # RENDER DASHBOARD
    # -------------------------------------------------------------------
    return render_template(
        "admin/dashboard.html",
        total_customers=total_customers,
        total_advertisers=total_advertisers,
        total_campaigns=total_campaigns,
        total_clicks=total_clicks,
        today_clicks=today_clicks,
        slot_names=slot_names,
        slot_clicks=slot_clicks,
        users_days=users_days,
        users_counts=users_counts
    )
