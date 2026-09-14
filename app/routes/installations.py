from datetime import date

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional

from app.extensions import db
from app.models.equipment import Equipment, EquipmentType
from app.models.installation import Installation
from app.models.site import Site
from app.models.technician import Technician
from app.security.decorators import permission_required, write_required
from app.security.permissions import Permission
from app.services.installation_service import InstallationService, InstallationServiceError
from app.utils.audit import log_audit
from app.utils.pagination import get_page, get_per_page, pagination_context

installations_bp = Blueprint("installations", __name__, url_prefix="/installations")


class InstallationForm(FlaskForm):
    site_id = SelectField("Site", coerce=int, validators=[DataRequired()])
    planned_date = DateField("Planned Date", validators=[DataRequired()], default=date.today)
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Schedule Installation")


@installations_bp.route("/")
@permission_required(Permission.VIEW_INSTALLATIONS)
def index():
    page = get_page()
    per_page = get_per_page()
    query = Installation.query.join(Site)
    status = request.args.get("status", "")
    site_id = request.args.get("site_id", type=int)
    if status:
        query = query.filter(Installation.status == status)
    if site_id:
        query = query.filter(Installation.site_id == site_id)
    pagination = query.order_by(Installation.planned_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template(
        "installations/index.html",
        **pagination_context(pagination, "installations.index"),
        status=status,
        sites=Site.query.all(),
        site_id=site_id,
    )


@installations_bp.route("/<int:installation_id>")
@permission_required(Permission.VIEW_INSTALLATIONS)
def detail(installation_id):
    installation = Installation.query.get_or_404(installation_id)
    available_equipment = Equipment.query.filter_by(status="Available").all()
    technicians = Technician.query.filter_by(is_active=True).all()
    return render_template(
        "installations/detail.html",
        installation=installation,
        available_equipment=available_equipment,
        technicians=technicians,
    )


@installations_bp.route("/create", methods=["GET", "POST"])
@write_required
@permission_required(Permission.MANAGE_INSTALLATIONS)
def create():
    form = InstallationForm()
    form.site_id.choices = [(s.site_id, f"{s.site_name} ({s.customer.full_name})") for s in Site.query.all()]
    if form.validate_on_submit():
        inst = Installation(
            site_id=form.site_id.data,
            planned_date=form.planned_date.data,
            notes=form.notes.data,
            created_by=g.current_user.staff_id,
        )
        db.session.add(inst)
        db.session.commit()
        log_audit("installation_created", "Installation", inst.installation_id)
        flash("Installation scheduled.", "success")
        return redirect(url_for("installations.detail", installation_id=inst.installation_id))
    return render_template("installations/form.html", form=form, title="Schedule Installation")


@installations_bp.route("/<int:installation_id>/status", methods=["POST"])
@write_required
@permission_required(Permission.MANAGE_INSTALLATIONS)
def update_status(installation_id):
    new_status = request.form.get("status")
    try:
        InstallationService.update_status(installation_id, new_status, g.current_user)
        flash(f"Installation status updated to {new_status}.", "success")
    except InstallationServiceError as e:
        flash(str(e), "danger")
    return redirect(url_for("installations.detail", installation_id=installation_id))


@installations_bp.route("/<int:installation_id>/assign-equipment", methods=["POST"])
@write_required
@permission_required(Permission.MANAGE_INSTALLATIONS)
def assign_equipment(installation_id):
    equipment_id = request.form.get("equipment_id", type=int)
    equipment = Equipment.query.get_or_404(equipment_id)
    try:
        InstallationService.add_equipment(installation_id, equipment_id, float(equipment.equipment_type.unit_price))
        flash("Equipment assigned.", "success")
    except InstallationServiceError as e:
        flash(str(e), "danger")
    return redirect(url_for("installations.detail", installation_id=installation_id))


@installations_bp.route("/<int:installation_id>/assign-technician", methods=["POST"])
@write_required
@permission_required(Permission.MANAGE_INSTALLATIONS)
def assign_technician(installation_id):
    technician_id = request.form.get("technician_id", type=int)
    role = request.form.get("role_in_team", "Assistant")
    try:
        InstallationService.assign_technician(installation_id, technician_id, role)
        flash("Technician assigned.", "success")
    except InstallationServiceError as e:
        flash(str(e), "danger")
    return redirect(url_for("installations.detail", installation_id=installation_id))


@installations_bp.route("/<int:installation_id>/complete", methods=["POST"])
@write_required
@permission_required(Permission.COMPLETE_INSTALLATIONS)
def complete(installation_id):
    try:
        InstallationService.complete_installation(installation_id, g.current_user)
        flash("Installation completed successfully. Equipment updated and warranties created.", "success")
    except InstallationServiceError as e:
        flash(str(e), "danger")
    return redirect(url_for("installations.detail", installation_id=installation_id))
