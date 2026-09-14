from functools import wraps

from flask import abort, flash, redirect, session, url_for

from app.security.permissions import Permission, has_permission, is_read_only_role


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "staff_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login", next=kwargs.get("next")))
        return view(*args, **kwargs)

    return wrapped


def permission_required(permission: Permission):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "staff_id" not in session:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth.login"))
            role = session.get("role")
            if not has_permission(role, permission):
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def write_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "staff_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        if is_read_only_role(session.get("role")):
            abort(403)
        return view(*args, **kwargs)

    return wrapped
