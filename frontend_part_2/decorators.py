from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get("username"):
                flash("You must be logged in to access this page.", "error")
                return redirect(url_for("login_page"))

            if role and session.get("role") != role:
                flash("You do not have permission to access this page.", "error")
                return redirect(url_for("landing_page"))

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return login_required(role="admin")(f)