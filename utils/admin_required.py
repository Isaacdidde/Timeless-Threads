"""
admin_required.py
-----------------

Middleware decorator for restricting routes to authenticated admins.

If ADMIN_AUTH is not found in session:
    → redirect to /admin/login
    → optional ?next=<requested_url> for smooth redirect after login
"""

from functools import wraps
from flask import session, redirect, url_for, request, flash


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):

        # Check admin session flag
        if not session.get("ADMIN_AUTH"):
            # Optional flash message (safe for production)
            flash("Admin login required.", "warning")

            # Preserve requested URL for redirect-after-login
            next_url = request.url
            login_url = url_for("admin_auth.login", next=next_url)

            return redirect(login_url)

        # If admin authenticated → proceed
        return view_func(*args, **kwargs)

    return wrapper
