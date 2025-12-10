"""
utils/auth_decorators.py

Common authentication decorators for Timeless Threads.
Used for:
    • Admin protection (@admin_required)
    • Future: user_required, advertiser_required, etc.
"""

from functools import wraps
from flask import session, redirect, url_for, flash


# ============================================================
# ADMIN AUTH CHECK
# ============================================================
def admin_required(f):
    """
    Protects admin routes.
    Requires session["ADMIN_AUTH"] = True
    (Set inside AdminAuthController after successful login.)
    """
    @wraps(f)
    def decorated(*args, **kwargs):

        # Correct production session key
        if not session.get("ADMIN_AUTH"):
            flash("Admin access required. Please log in.", "warning")
            return redirect(url_for("admin_auth.login"))

        return f(*args, **kwargs)

    return decorated
