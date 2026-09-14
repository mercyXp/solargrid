from datetime import date

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from sqlalchemy.exc import IntegrityError
from wtforms import DateField, SelectField, StringField, SubmitField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Length, Optional

from app.extensions import db
from app.models.equipment import Equipment, EquipmentType
from app.models.site import Site
from app.security.decorators import permission_required, write_required
from app.security.permissions import Permission
from app.utils.audit import log_audit
from app.utils.pagination import get_page, get_per_page, pagination_context

equipment_bp = Blueprint("equipment", __name__, url_prefix="/equipment")


class EquipmentTypeForm(FlaskForm):
    category = SelectField(
        "Category",
        choices=[
            ("Solar Panel", "Solar Panel"),
            ("Battery", "Battery"),
            ("Inverter", "Inverter"),
            ("Charge Controller", "Charge Controller"),
            ("Mounting", "Mounting"),
            ("Accessory", "Accessory"),
        ],
        validators=[DataRequired()],
    )
    manufacturer = StringField("Manufacturer", validators=[DataRequired(), Length(max=100)])
    model_name = StringField("Model Name", validators=[DataRequired(), Length(max=100)])
    model_number = StringField("Model Number", validators=[Optional(), Length(max=50)])
    specifications = TextAreaField("Specifications", validators=[Optional()])
    unit_price = DecimalField("Unit Price (ZMK)", validators=[DataRequired()], places=2)
    default_warranty_months = StringField("Default Warranty (months)", validators=[DataRequired()])
    submit = SubmitField("Save Equipment Type")


class EquipmentForm(FlaskForm):
    equipment_type_id = SelectField("Equipment Type", coerce=int, validators=[DataRequired()])
    serial_number = StringField("Serial Number", validators=[DataRequired(), Length(max=50)])
    site_id = SelectField("Site", coerce=int, validators=[Optional()])
    status = SelectField(
        "Status",
        choices=[
            ("Available", "Available"),
            ("Reserved", "Reserved"),
            ("Installed", "Installed"),
            ("Faulty", "Faulty"),
            ("Decommissioned", "Decommissioned"),
        ],
        validators=[DataRequired()],
    )
    date_received = DateField("Date Received", validators=[DataRequired()], default=date.today)
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Save Equipment")


@equipment_bp.route("/types")
@permission_required(Permission.VIEW_EQUIPMENT_TYPES)
def types_index():
    types = EquipmentType.query.order_by(EquipmentType.manufacturer, EquipmentType.model_name).all()
    return render_template("equipment/types_index.html", types=types)


@equipment_bp.route("/types/create", methods=["GET", "POST"])
@write_required
@permission_required(Permission.MANAGE_EQUIPMENT_TYPES)
def type_create():
    form = EquipmentTypeForm()
    if form.validate_on_submit():
        et = EquipmentType(
            category=form.category.data,
            manufacturer=form.manufacturer.data,
            model_name=form.model_name.data,
            model_number=form.model_number.data or None,
            specifications=form.specifications.data,
            unit_price=form.unit_price.data,
            default_warranty_months=int(form.default_warranty_months.data),
        )
        db.session.add(et)
        db.session.commit()
        flash("Equipment type created.", "success")
        return redirect(url_for("equipment.types_index"))
    return render_template("equipment/type_form.html", form=form, title="Create Equipment Type")


@equipment_bp.route("/")
@permission_required(Permission.VIEW_EQUIPMENT)
def index():
    page = get_page()
    per_page = get_per_page()
    query = Equipment.query.join(EquipmentType)
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "")
    if search:
        like = f"%{search}%"
        query = query.filter(
            db.or_(
                Equipment.serial_number.ilike(like),
                EquipmentType.manufacturer.ilike(like),
                EquipmentType.model_name.ilike(like),
            )
        )
    if status:
        query = query.filter(Equipment.status == status)
    pagination = query.order_by(Equipment.date_received.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template(
        "equipment/index.html",
        **pagination_context(pagination, "equipment.index"),
        search=search,
        status=status,
    )


@equipment_bp.route("/create", methods=["GET", "POST"])
@write_required
@permission_required(Permission.MANAGE_EQUIPMENT)
def create():
    form = EquipmentForm()
    form.equipment_type_id.choices = [(t.equipment_type_id, f"{t.manufacturer} {t.model_name}") for t in EquipmentType.query.filter_by(is_active=True).all()]
    form.site_id.choices = [(0, "— Warehouse —")] + [(s.site_id, s.site_name) for s in Site.query.all()]
    if form.validate_on_submit():
        eq = Equipment(
            equipment_type_id=form.equipment_type_id.data,
            serial_number=form.serial_number.data,
            site_id=form.site_id.data if form.site_id.data else None,
            status=form.status.data,
            date_received=form.date_received.data,
            notes=form.notes.data,
        )
        try:
            db.session.add(eq)
            db.session.commit()
            log_audit("equipment_created", "Equipment", eq.equipment_id)
            flash("Equipment registered.", "success")
            return redirect(url_for("equipment.index"))
        except IntegrityError:
            db.session.rollback()
            flash("Serial number already exists.", "danger")
    return render_template("equipment/form.html", form=form, title="Register Equipment")
