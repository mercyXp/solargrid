from datetime import datetime
from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.utils.audit import log_audit


class PaymentServiceError(Exception):
    pass


class PaymentService:
    @staticmethod
    def recalculate_invoice_status(invoice: Invoice) -> None:
        paid = Decimal(str(invoice.amount_paid))
        total = Decimal(str(invoice.total_amount))
        if invoice.status == "Cancelled":
            return
        if paid <= 0:
            if invoice.status not in ("Draft", "Cancelled"):
                invoice.status = "Issued"
        elif paid >= total:
            invoice.status = "Paid"
        else:
            invoice.status = "Partially Paid"

    @staticmethod
    def confirm_payment(invoice_id: int, amount: Decimal, payment_method: str, recorded_by, **kwargs) -> Payment:
        try:
            invoice = (
                db.session.query(Invoice)
                .filter_by(invoice_id=invoice_id)
                .with_for_update()
                .first()
            )
            if not invoice:
                raise PaymentServiceError("Invoice not found.")
            if invoice.status in ("Paid", "Cancelled"):
                raise PaymentServiceError("Invoice cannot receive additional payments.")

            amount = Decimal(str(amount))
            if amount <= 0:
                raise PaymentServiceError("Payment amount must be greater than zero.")

            new_paid = Decimal(str(invoice.amount_paid)) + amount
            if new_paid > Decimal(str(invoice.total_amount)):
                raise PaymentServiceError("Payment would exceed invoice total (overpayment blocked).")

            payment = Payment(
                invoice_id=invoice_id,
                amount=amount,
                payment_method=payment_method,
                reference_number=kwargs.get("reference_number"),
                status=kwargs.get("status", "Confirmed"),
                payment_date=kwargs.get("payment_date") or datetime.utcnow(),
                recorded_by=recorded_by.staff_id,
            )
            db.session.add(payment)

            if payment.status == "Confirmed":
                invoice.amount_paid = new_paid
                PaymentService.recalculate_invoice_status(invoice)

            db.session.commit()
            log_audit("payment_confirmed", "Payment", payment.payment_id, f"Invoice {invoice.invoice_number}")
            return payment
        except PaymentServiceError:
            db.session.rollback()
            raise
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise PaymentServiceError(f"Transaction failed: {exc}") from exc

    @staticmethod
    def reverse_payment(payment_id: int, current_user) -> Payment:
        try:
            payment = (
                db.session.query(Payment)
                .filter_by(payment_id=payment_id)
                .with_for_update()
                .first()
            )
            if not payment:
                raise PaymentServiceError("Payment not found.")
            if payment.status == "Reversed":
                raise PaymentServiceError("Payment is already reversed.")

            invoice = (
                db.session.query(Invoice)
                .filter_by(invoice_id=payment.invoice_id)
                .with_for_update()
                .first()
            )
            payment.status = "Reversed"
            if invoice:
                invoice.amount_paid = max(
                    Decimal("0"),
                    Decimal(str(invoice.amount_paid)) - Decimal(str(payment.amount)),
                )
                PaymentService.recalculate_invoice_status(invoice)

            db.session.commit()
            log_audit("payment_reversed", "Payment", payment_id, f"By staff {current_user.staff_id}")
            return payment
        except PaymentServiceError:
            db.session.rollback()
            raise
        except SQLAlchemyError as exc:
            db.session.rollback()
            raise PaymentServiceError(f"Transaction failed: {exc}") from exc
