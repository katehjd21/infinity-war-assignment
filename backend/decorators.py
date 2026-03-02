from functools import wraps
from flask import session, abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            abort(401, description="Authentication required")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            abort(401, description="Authentication required")
        if session.get("role") != "admin":
            abort(403, description="Admin privileges required")
        return f(*args, **kwargs)
    return decorated_function