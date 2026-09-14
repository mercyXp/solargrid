from datetime import date
from decimal import Decimal

from app.extensions import db
from app.models.customer import Customer
from app.models.invoice import Invoice
from app.models.staff import Staff
from app.services.payment_service import PaymentService, PaymentServiceError


def _invoice(app, total="1000.00", paid="0", status="Issued"):
    with app.app_context():
        c = Customer(first_name="P", last_name="T", email="pay@test.com", phone="1", address="a", customer_type="Individual")
        db.session.add(c)
        db.session.flush()
        staff = Staff.query.filter_by(username="testadmin").first()
        inv = Invoice(
            invoice_number="INV-TEST-001",
            customer_id=c.customer_id,
            date_issued=date.today(),
            due_date=date.today(),
            total_amount=Decimal(total),
            amount_paid=Decimal(paid),
            status=status,
            created_by=staff.staff_id,
        )
        db.session.add(inv)
        db.session.commit()
        return inv, staff


def test_overpayment_blocked(app):
    inv, staff = _invoice(app)
    with app.app_context():
        inv = Invoice.query.get(inv.invoice_id)
        staff = Staff.query.get(staff.staff_id)
        with pytest.raises(PaymentServiceError):
            PaymentService.confirm_payment(inv.invoice_id, Decimal("1500.00"), "EFT", staff)


def test_paid_invoice_rejects_payment(app):
    inv, staff = _invoice(app, paid="1000.00", status="Paid")
    with app.app_context():
        inv = Invoice.query.get(inv.invoice_id)
        staff = Staff.query.get(staff.staff_id)
        with pytest.raises(PaymentServiceError):
            PaymentService.confirm_payment(inv.invoice_id, Decimal("100.00"), "EFT", staff)


import pytest
