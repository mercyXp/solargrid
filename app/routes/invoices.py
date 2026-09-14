from datetime import date

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional

from app.extensions import db
from app.models.customer import Customer
from app.models.installation import Installation
from app.models.invoice import Invoice
from app.models.service_request import ServiceRequest
from app.security.decorators import permission_required, write_required
from app.security.permissions import Permission
from app.services.invoice_service import InvoiceService, InvoiceServiceError
from app.utils.pagination import get_page, get_per_page, pagination_context

invoices_bp = Blueprint("invoices", __name__, url_prefix="/invoices")


class InvoiceForm(FlaskForm):
    invoice_number = StringField("Invoice Number", validators=[DataRequired()])
    customer_id = SelectField("Customer", coerce=int, validators=[DataRequired()])
    installation_id = SelectField("Installation (optional)", coerce=int, validators=[Optional()])
    request_id = SelectField("Service Request (optional)", coerce=int, validators=[Optional()])
    date_issued = DateField("Date Issued", validators=[DataRequired()], default=date.today)
    due_date = DateField("Due Date", validators=[DataRequired()])
    total_amount = DecimalField("Total Amount (ZAR)", validators=[DataRequired()], places=2)
    status = SelectField(
        "Status",
        choices=[("Draft", "Draft"), ("Issued", "Issued")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Create Invoice")


@invoices_bp.route("/")
@permission_required(Permission.VIEW_INVOICES)
def index():
    page = get_page()
    per_page = get_per_page()
    query = Invoice.query.join(Customer)
    status = request.args.get("status", "")
    overdue = request.args.get("overdue", "")
    if status:
        query = query.filter(Invoice.status == status)
    if overdue == "1":
        query = query.filter(Invoice.due_date < date.today(), Invoice.status.notin_(["Paid", "Cancelled"]))
    pagination = query.order_by(Invoice.date_issued.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template(
        "invoices/index.html",
        **pagination_context(pagination, "invoices.index"),
        status=status,
        overdue=overdue,
    )


@invoices_bp.route("/<int:invoice_id>")
@permission_required(Permission.VIEW_INVOICES)
def detail(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template("invoices/detail.html", invoice=invoice)


@invoices_bp.route("/create", methods=["GET", "POST"])
@write_required
@permission_required(Permission.MANAGE_INVOICES)
def create():
    form = InvoiceForm()
    form.customer_id.choices = [(c.customer_id, c.full_name) for c in Customer.query.all()]
    form.installation_id.choices = [(0, "— None —")] + [
        (i.installation_id, f"#{i.installation_id} - {i.site.site_name}") for i in Installation.query.all()
    ]
    form.request_id.choices = [(0, "— None —")] + [
        (sr.request_id, f"#{sr.request_id}") for sr in ServiceRequest.query.all()
    ]
    if form.validate_on_submit():
        try:
            invoice = InvoiceService.create_invoice(
                {
                    "invoice_number": form.invoice_number.data,
                    "customer_id": form.customer_id.data,
                    "installation_id": form.installation_id.data or None,
                    "request_id": form.request_id.data or None,
                    "date_issued": form.date_issued.data,
                    "due_date": form.due_date.data,
                    "total_amount": form.total_amount.data,
                    "status": form.status.data,
                },
                g.current_user,
            )
            flash("Invoice created.", "success")
            return redirect(url_for("invoices.detail", invoice_id=invoice.invoice_id))
        except InvoiceServiceError as e:
            flash(str(e), "danger")
    return render_template("invoices/form.html", form=form, title="Create Invoice")
