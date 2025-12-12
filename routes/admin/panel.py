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

    # Existing users collection
    users_col = safe_col("db.users")

    # New required collections
    categories_col = safe_col("categories")
    products_col = safe_col("products")
    orders_col = safe_col("orders")

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
    total_categories = safe_count(categories_col)
    total_products = safe_count(products_col)
    total_orders = safe_count(orders_col)

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
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$created_at"
                            }
                        },
                        "count": {"$sum": 1}
                    }
                },
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
        total_categories=total_categories,
        total_products=total_products,
        total_orders=total_orders,
        users_days=users_days,
        users_counts=users_counts
    )
