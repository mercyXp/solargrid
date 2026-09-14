from datetime import datetime

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional

from app.extensions import db
from app.models.equipment import Equipment
from app.models.service_request import ServiceRequest
from app.models.site import Site
from app.models.technician import Technician
from app.security.decorators import permission_required, write_required
from app.security.permissions import Permission
from app.services.service_request_service import ServiceRequestService, ServiceRequestServiceError
from app.utils.audit import log_audit
from app.utils.pagination import get_page, get_per_page, pagination_context

services_bp = Blueprint("services", __name__, url_prefix="/service-requests")


class ServiceRequestForm(FlaskForm):
    site_id = SelectField("Site", coerce=int, validators=[DataRequired()])
    equipment_id = SelectField("Equipment (optional)", coerce=int, validators=[Optional()])
    description = TextAreaField("Description", validators=[DataRequired()])
    priority = SelectField(
        "Priority",
        choices=[("Low", "Low"), ("Medium", "Medium"), ("High", "High"), ("Critical", "Critical")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Create Service Request")


@services_bp.route("/")
@permission_required(Permission.VIEW_SERVICE_REQUESTS)
def index():
    page = get_page()
    per_page = get_per_page()
    query = ServiceRequest.query.join(Site)
    status = request.args.get("status", "")
    priority = request.args.get("priority", "")
    if status:
        query = query.filter(ServiceRequest.status == status)
    if priority:
        query = query.filter(ServiceRequest.priority == priority)
    pagination = query.order_by(ServiceRequest.date_raised.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template(
        "services/index.html",
        **pagination_context(pagination, "services.index"),
        status=status,
        priority=priority,
    )


@services_bp.route("/<int:request_id>")
@permission_required(Permission.VIEW_SERVICE_REQUESTS)
def detail(request_id):
    sr = ServiceRequest.query.get_or_404(request_id)
    technicians = Technician.query.filter_by(is_active=True).all()
    return render_template("services/detail.html", service_request=sr, technicians=technicians)


@services_bp.route("/create", methods=["GET", "POST"])
@write_required
@permission_required(Permission.CREATE_SERVICE_REQUESTS)
def create():
    form = ServiceRequestForm()
    form.site_id.choices = [(s.site_id, s.site_name) for s in Site.query.all()]
    form.equipment_id.choices = [(0, "— None —")] + [
        (e.equipment_id, e.serial_number) for e in Equipment.query.filter(Equipment.site_id.isnot(None)).all()
    ]
    if form.validate_on_submit():
        sr = ServiceRequest(
            site_id=form.site_id.data,
            equipment_id=form.equipment_id.data if form.equipment_id.data else None,
            reported_by=g.current_user.staff_id,
            description=form.description.data,
            priority=form.priority.data,
        )
        db.session.add(sr)
        db.session.commit()
        log_audit("service_request_created", "ServiceRequest", sr.request_id)
        flash("Service request created.", "success")
        return redirect(url_for("services.detail", request_id=sr.request_id))
    return render_template("services/form.html", form=form, title="Create Service Request")


@services_bp.route("/<int:request_id>/assign", methods=["POST"])
@write_required
@permission_required(Permission.MANAGE_SERVICE_REQUESTS)
def assign(request_id):
    technician_id = request.form.get("technician_id", type=int)
    try:
        ServiceRequestService.assign_technician(request_id, technician_id)
        flash("Technician assigned.", "success")
    except ServiceRequestServiceError as e:
        flash(str(e), "danger")
    return redirect(url_for("services.detail", request_id=request_id))


@services_bp.route("/<int:request_id>/status", methods=["POST"])
@write_required
@permission_required(Permission.MANAGE_SERVICE_REQUESTS)
def update_status(request_id):
    new_status = request.form.get("status")
    try:
        ServiceRequestService.update_status(request_id, new_status)
        flash(f"Status updated to {new_status}.", "success")
    except ServiceRequestServiceError as e:
        flash(str(e), "danger")
    return redirect(url_for("services.detail", request_id=request_id))
