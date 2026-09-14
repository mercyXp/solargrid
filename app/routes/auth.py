import logging
from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.extensions import db, limiter
from app.forms.auth import LoginForm
from app.models.staff import Staff
from app.security.security_utils import verify_password
from app.utils.audit import log_audit

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/health")
def health():
    from sqlalchemy import text

    try:
        db.session.execute(text("SELECT 1"))
        staff_count = Staff.query.count()
        return {
            "status": "ok",
            "staff_count": staff_count,
            "database": "connected",
            "seeded": staff_count > 0,
        }, 200
    except Exception as exc:
        from config import database_connection_label

        logger.exception("Health check failed for %s", database_connection_label())
        return {
            "status": "error",
            "database": "failed",
            "target": database_connection_label(),
            "message": str(exc),
        }, 500


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute", methods=["POST"])
def login():
    if session.get("staff_id"):
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            staff = Staff.query.filter_by(username=form.username.data.strip()).first()
            if staff and staff.is_active and verify_password(form.password.data, staff.password_hash):
                session.clear()
                session.permanent = True
                session["staff_id"] = staff.staff_id
                session["username"] = staff.username
                session["role"] = staff.role
                session["full_name"] = staff.full_name
                session["login_time"] = datetime.utcnow().isoformat()
                log_audit("login", "Staff", staff.staff_id, f"User {staff.username} logged in")
                next_page = request.args.get("next")
                return redirect(next_page or url_for("dashboard.index"))
            log_audit("failed_login", "Staff", None, f"Failed login for {form.username.data}")
            flash("Invalid username or password.", "danger")
        except Exception:
            logger.exception("Login failed with server error")
            db.session.rollback()
            flash("A server error occurred. The database may not be set up yet.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
def logout():
    if session.get("staff_id"):
        log_audit("logout", "Staff", session.get("staff_id"))
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
