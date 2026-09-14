from decimal import Decimal

from app.extensions import db
from app.models.installation import InstallationDetail
from app.models.invoice import Invoice
from app.utils.audit import log_audit


class InvoiceServiceError(Exception):
    pass


class InvoiceService:
    @staticmethod
    def validate_installation_amount(installation_id: int, total_amount: Decimal) -> None:
        if not installation_id:
            return
        details = InstallationDetail.query.filter_by(installation_id=installation_id).all()
        if not details:
            return
        min_amount = sum(Decimal(str(d.unit_price_at_install)) * d.quantity for d in details)
        if Decimal(str(total_amount)) < min_amount:
            raise InvoiceServiceError(
                f"Invoice total must be at least ZMK {min_amount:,.2f} (installation equipment value)."
            )

    @staticmethod
    def create_invoice(data: dict, created_by) -> Invoice:
        total = Decimal(str(data["total_amount"]))
        if total <= 0:
            raise InvoiceServiceError("Invoice total must be greater than zero.")
        if data["due_date"] < data["date_issued"]:
            raise InvoiceServiceError("Due date must be on or after issue date.")

        InvoiceService.validate_installation_amount(data.get("installation_id"), total)

        invoice = Invoice(
            invoice_number=data["invoice_number"],
            customer_id=data["customer_id"],
            installation_id=data.get("installation_id"),
            request_id=data.get("request_id"),
            date_issued=data["date_issued"],
            due_date=data["due_date"],
            total_amount=total,
            status=data.get("status", "Draft"),
            created_by=created_by.staff_id,
        )
        db.session.add(invoice)
        db.session.commit()
        log_audit("invoice_created", "Invoice", invoice.invoice_id, invoice.invoice_number)
        return invoice
