from datetime import datetime

from app.extensions import db


class Staff(db.Model):
    __tablename__ = "staff"
    __table_args__ = (
        db.UniqueConstraint("username", name="uk_staff_username"),
        db.UniqueConstraint("email", name="uk_staff_email"),
    )

    staff_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    role = db.Column(
        db.Enum(
            "Administrator",
            "Sales Rep",
            "Operations Manager",
            "Technician",
            "Warehouse Clerk",
            "Customer Service",
            "Finance Officer",
            "Auditor",
            name="staff_role_enum",
        ),
        nullable=False,
    )
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    installations_created = db.relationship("Installation", back_populates="creator", lazy="dynamic")
    service_requests_reported = db.relationship("ServiceRequest", back_populates="reporter", lazy="dynamic")
    invoices_created = db.relationship("Invoice", back_populates="creator", lazy="dynamic")
    payments_recorded = db.relationship("Payment", back_populates="recorder", lazy="dynamic")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Staff {self.username}>"
