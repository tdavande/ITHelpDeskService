
from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You need to log in to access this page.', 'warning')
            return redirect(url_for('routes.login')) # Redirect non-authenticated users
        if not current_user.is_admin():  # Check if user is admin
            flash('You do not have permission to access this page.', 'danger')
            abort(403) # Return a 403 Forbidden error
        return f(*args, **kwargs)
    return decorated_function