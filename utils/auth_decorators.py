from functools import wraps
from flask import session, redirect, url_for, flash

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        # Must match admin_auth_controller session key
        if "admin" not in session:
            flash("Admin access required. Please log in.", "warning")
            return redirect(url_for("admin_auth.login"))

        return f(*args, **kwargs)
    return decorated
