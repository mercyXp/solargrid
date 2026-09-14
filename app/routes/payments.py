from datetime import datetime

from flask import Blueprint, flash, g, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import DateTimeField, DecimalField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional

from app.extensions import db
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.security.decorators import permission_required, write_required
from app.security.permissions import Permission
from app.services.payment_service import PaymentService, PaymentServiceError
from app.utils.pagination import get_page, get_per_page, pagination_context

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")


class PaymentForm(FlaskForm):
    invoice_id = SelectField("Invoice", coerce=int, validators=[DataRequired()])
    payment_date = DateTimeField("Payment Date", validators=[DataRequired()], default=datetime.utcnow)
    amount = DecimalField("Amount (ZMK)", validators=[DataRequired()], places=2)
    payment_method = SelectField(
        "Payment Method",
        choices=[
            ("Cash", "Cash"),
            ("EFT", "EFT"),
            ("Credit Card", "Credit Card"),
            ("Debit Order", "Debit Order"),
            ("Cheque", "Cheque"),
        ],
        validators=[DataRequired()],
    )
    reference_number = StringField("Reference Number", validators=[Optional()])
    submit = SubmitField("Record Payment")


@payments_bp.route("/")
@permission_required(Permission.VIEW_PAYMENTS)
def index():
    page = get_page()
    per_page = get_per_page()
    pagination = Payment.query.order_by(Payment.payment_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template("payments/index.html", **pagination_context(pagination, "payments.index"))


@payments_bp.route("/create", methods=["GET", "POST"])
@write_required
@permission_required(Permission.MANAGE_PAYMENTS)
def create():
    form = PaymentForm()
    form.invoice_id.choices = [
        (inv.invoice_id, f"{inv.invoice_number} - ZMK {inv.outstanding:,.2f} outstanding")
        for inv in Invoice.query.filter(Invoice.status.notin_(["Paid", "Cancelled"])).all()
    ]
    if form.validate_on_submit():
        try:
            payment = PaymentService.confirm_payment(
                form.invoice_id.data,
                form.amount.data,
                form.payment_method.data,
                g.current_user,
                payment_date=form.payment_date.data,
                reference_number=form.reference_number.data,
            )
            flash("Payment recorded and invoice updated.", "success")
            return redirect(url_for("invoices.detail", invoice_id=payment.invoice_id))
        except PaymentServiceError as e:
            flash(str(e), "danger")
    return render_template("payments/form.html", form=form, title="Record Payment")
