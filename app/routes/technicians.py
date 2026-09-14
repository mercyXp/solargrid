from datetime import date

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

from app.extensions import db
from app.models.technician import Technician
from app.security.decorators import permission_required, write_required
from app.security.permissions import Permission
from app.utils.audit import log_audit
from app.utils.pagination import get_page, get_per_page, pagination_context

technicians_bp = Blueprint("technicians", __name__, url_prefix="/technicians")


class TechnicianForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=50)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=100)])
    phone = StringField("Phone", validators=[DataRequired(), Length(max=20)])
    specialisation = StringField("Specialisation", validators=[Optional(), Length(max=100)])
    hire_date = DateField("Hire Date", validators=[DataRequired()], default=date.today)
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save Technician")


@technicians_bp.route("/")
@permission_required(Permission.VIEW_TECHNICIANS)
def index():
    page = get_page()
    per_page = get_per_page()
    pagination = Technician.query.order_by(Technician.last_name).paginate(page=page, per_page=per_page, error_out=False)
    return render_template("technicians/index.html", **pagination_context(pagination, "technicians.index"))


@technicians_bp.route("/create", methods=["GET", "POST"])
@write_required
@permission_required(Permission.MANAGE_TECHNICIANS)
def create():
    form = TechnicianForm()
    if form.validate_on_submit():
        tech = Technician(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data.lower(),
            phone=form.phone.data,
            specialisation=form.specialisation.data,
            hire_date=form.hire_date.data,
            is_active=form.is_active.data,
        )
        db.session.add(tech)
        db.session.commit()
        log_audit("technician_created", "Technician", tech.technician_id)
        flash("Technician created.", "success")
        return redirect(url_for("technicians.index"))
    return render_template("technicians/form.html", form=form, title="Add Technician")


@technicians_bp.route("/<int:technician_id>/edit", methods=["GET", "POST"])
@write_required
@permission_required(Permission.MANAGE_TECHNICIANS)
def edit(technician_id):
    tech = Technician.query.get_or_404(technician_id)
    form = TechnicianForm(obj=tech)
    if form.validate_on_submit():
        tech.first_name = form.first_name.data
        tech.last_name = form.last_name.data
        tech.email = form.email.data.lower()
        tech.phone = form.phone.data
        tech.specialisation = form.specialisation.data
        tech.hire_date = form.hire_date.data
        tech.is_active = form.is_active.data
        db.session.commit()
        flash("Technician updated.", "success")
        return redirect(url_for("technicians.index"))
    return render_template("technicians/form.html", form=form, title="Edit Technician", technician=tech)
