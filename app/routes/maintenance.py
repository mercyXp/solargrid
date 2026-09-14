from datetime import datetime

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import DateTimeField, DecimalField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional

from app.extensions import db
from app.models.maintenance import MaintenanceRecord
from app.models.service_request import ServiceRequest
from app.models.technician import Technician
from app.security.decorators import permission_required, write_required
from app.security.permissions import Permission
from app.utils.audit import log_audit
from app.utils.pagination import get_page, get_per_page, pagination_context

maintenance_bp = Blueprint("maintenance", __name__, url_prefix="/maintenance")


class MaintenanceForm(FlaskForm):
    request_id = SelectField("Service Request", coerce=int, validators=[DataRequired()])
    technician_id = SelectField("Technician", coerce=int, validators=[DataRequired()])
    maintenance_date = DateTimeField("Maintenance Date", validators=[DataRequired()], default=datetime.utcnow)
    work_description = TextAreaField("Work Description", validators=[DataRequired()])
    hours_worked = DecimalField("Hours Worked", validators=[DataRequired()], places=2)
    parts_used = TextAreaField("Parts Used", validators=[Optional()])
    resolution_notes = TextAreaField("Resolution Notes", validators=[Optional()])
    submit = SubmitField("Save Maintenance Record")


@maintenance_bp.route("/")
@permission_required(Permission.VIEW_MAINTENANCE)
def index():
    page = get_page()
    per_page = get_per_page()
    query = MaintenanceRecord.query
    site_id = request.args.get("site_id", type=int)
    if site_id:
        query = query.join(ServiceRequest).filter(ServiceRequest.site_id == site_id)
    pagination = query.order_by(MaintenanceRecord.maintenance_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template("maintenance/index.html", **pagination_context(pagination, "maintenance.index"))


@maintenance_bp.route("/create", methods=["GET", "POST"])
@write_required
@permission_required(Permission.MANAGE_MAINTENANCE)
def create():
    form = MaintenanceForm()
    form.request_id.choices = [
        (sr.request_id, f"#{sr.request_id} - {sr.site.site_name}") for sr in ServiceRequest.query.filter(ServiceRequest.status != "Closed").all()
    ]
    form.technician_id.choices = [(t.technician_id, t.full_name) for t in Technician.query.filter_by(is_active=True).all()]
    if form.validate_on_submit():
        record = MaintenanceRecord(
            request_id=form.request_id.data,
            technician_id=form.technician_id.data,
            maintenance_date=form.maintenance_date.data,
            work_description=form.work_description.data,
            hours_worked=form.hours_worked.data,
            parts_used=form.parts_used.data,
            resolution_notes=form.resolution_notes.data,
        )
        db.session.add(record)
        db.session.commit()
        log_audit("maintenance_record_created", "MaintenanceRecord", record.maintenance_id)
        flash("Maintenance record saved.", "success")
        return redirect(url_for("maintenance.index"))
    request_id = request.args.get("request_id", type=int)
    if request_id:
        form.request_id.data = request_id
    return render_template("maintenance/form.html", form=form, title="Record Maintenance")
