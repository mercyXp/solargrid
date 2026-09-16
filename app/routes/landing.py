from datetime import datetime

from flask import Blueprint, redirect, render_template, session, url_for

landing_bp = Blueprint("landing", __name__)


@landing_bp.route("/")
def index():
    if session.get("staff_id"):
        return redirect(url_for("dashboard.index"))
    return render_template("landing/index.html", current_year=datetime.now().year)
