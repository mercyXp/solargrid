from app.extensions import db


class Payment(db.Model):
    __tablename__ = "payment"
    __table_args__ = (db.CheckConstraint("amount > 0", name="chk_payment_amount"),)

    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    invoice_id = db.Column(
        db.Integer,
        db.ForeignKey("invoice.invoice_id", name="fk_payment_invoice_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    payment_date = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_method = db.Column(
        db.Enum("Cash", "EFT", "Credit Card", "Debit Order", "Cheque", name="payment_method_enum"),
        nullable=False,
    )
    reference_number = db.Column(db.String(50), nullable=True)
    status = db.Column(
        db.Enum("Pending", "Confirmed", "Reversed", name="payment_status_enum"),
        nullable=False,
        default="Confirmed",
    )
    recorded_by = db.Column(
        db.Integer,
        db.ForeignKey("staff.staff_id", name="fk_payment_recorded_by", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )

    invoice = db.relationship("Invoice", back_populates="payments")
    recorder = db.relationship("Staff", back_populates="payments_recorded")
