from app.extensions import db


class Invoice(db.Model):
    __tablename__ = "invoice"
    __table_args__ = (
        db.UniqueConstraint("invoice_number", name="uk_invoice_number"),
        db.CheckConstraint("total_amount > 0", name="chk_invoice_total_amount"),
        db.CheckConstraint("amount_paid >= 0", name="chk_invoice_amount_paid"),
        db.CheckConstraint("due_date >= date_issued", name="chk_invoice_due_date"),
    )

    invoice_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_number = db.Column(db.String(20), nullable=False)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customer.customer_id", name="fk_invoice_customer_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    installation_id = db.Column(
        db.Integer,
        db.ForeignKey("installation.installation_id", name="fk_invoice_installation_id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    request_id = db.Column(
        db.Integer,
        db.ForeignKey("service_request.request_id", name="fk_invoice_request_id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    date_issued = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    amount_paid = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    status = db.Column(
        db.Enum("Draft", "Issued", "Partially Paid", "Paid", "Overdue", "Cancelled", name="invoice_status_enum"),
        nullable=False,
        default="Draft",
    )
    created_by = db.Column(
        db.Integer,
        db.ForeignKey("staff.staff_id", name="fk_invoice_created_by", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )

    customer = db.relationship("Customer", back_populates="invoices")
    installation = db.relationship("Installation", back_populates="invoices")
    service_request = db.relationship("ServiceRequest", back_populates="invoices")
    creator = db.relationship("Staff", back_populates="invoices_created")
    payments = db.relationship("Payment", back_populates="invoice", lazy="dynamic")

    @property
    def outstanding(self):
        return float(self.total_amount) - float(self.amount_paid)

    def __repr__(self):
        return f"<Invoice {self.invoice_number}>"
