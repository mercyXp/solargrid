from flask import Blueprint, flash, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

from app.extensions import db
from app.models.staff import Staff
from app.security.decorators import permission_required, write_required
from app.security.permissions import Permission
from app.security.security_utils import hash_password, validate_password_strength
from app.utils.audit import log_audit
from app.utils.pagination import get_page, get_per_page, pagination_context

staff_bp = Blueprint("staff", __name__, url_prefix="/staff")


class StaffForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=50)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=100)])
    first_name = StringField("First Name", validators=[DataRequired(), Length(max=50)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(max=50)])
    role = SelectField(
        "Role",
        choices=[
            ("Administrator", "Administrator"),
            ("Sales Rep", "Sales Rep"),
            ("Operations Manager", "Operations Manager"),
            ("Technician", "Technician"),
            ("Warehouse Clerk", "Warehouse Clerk"),
            ("Customer Service", "Customer Service"),
            ("Finance Officer", "Finance Officer"),
            ("Auditor", "Auditor"),
        ],
        validators=[DataRequired()],
    )
    password = PasswordField("Password", validators=[Optional(), Length(min=8)])
    is_active = BooleanField("Active", default=True)
    submit = SubmitField("Save Staff Member")


@staff_bp.route("/")
@permission_required(Permission.VIEW_STAFF)
def index():
    page = get_page()
    per_page = get_per_page()
    pagination = Staff.query.order_by(Staff.last_name).paginate(page=page, per_page=per_page, error_out=False)
    return render_template("staff/index.html", **pagination_context(pagination, "staff.index"))


@staff_bp.route("/create", methods=["GET", "POST"])
@write_required
@permission_required(Permission.MANAGE_STAFF)
def create():
    form = StaffForm()
    if form.validate_on_submit():
        valid, msg = validate_password_strength(form.password.data or "")
        if not form.password.data or not valid:
            flash(msg or "Password is required for new staff.", "danger")
            return render_template("staff/form.html", form=form, title="Add Staff")
        staff = Staff(
            username=form.username.data.strip(),
            email=form.email.data.lower(),
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data,
            password_hash=hash_password(form.password.data),
            is_active=form.is_active.data,
        )
        db.session.add(staff)
        db.session.commit()
        log_audit("staff_created", "Staff", staff.staff_id)
        flash("Staff member created.", "success")
        return redirect(url_for("staff.index"))
    return render_template("staff/form.html", form=form, title="Add Staff")


@staff_bp.route("/<int:staff_id>/edit", methods=["GET", "POST"])
@write_required
@permission_required(Permission.MANAGE_STAFF)
def edit(staff_id):
    staff = Staff.query.get_or_404(staff_id)
    form = StaffForm(obj=staff)
    if form.validate_on_submit():
        staff.username = form.username.data.strip()
        staff.email = form.email.data.lower()
        staff.first_name = form.first_name.data
        staff.last_name = form.last_name.data
        staff.role = form.role.data
        staff.is_active = form.is_active.data
        if form.password.data:
            valid, msg = validate_password_strength(form.password.data)
            if not valid:
                flash(msg, "danger")
                return render_template("staff/form.html", form=form, title="Edit Staff", staff=staff)
            staff.password_hash = hash_password(form.password.data)
        db.session.commit()
        log_audit("staff_updated", "Staff", staff.staff_id)
        flash("Staff member updated.", "success")
        return redirect(url_for("staff.index"))
    return render_template("staff/form.html", form=form, title="Edit Staff", staff=staff)
