from datetime import datetime

from app.extensions import db


class Customer(db.Model):
    __tablename__ = "customer"
    __table_args__ = (db.UniqueConstraint("email", name="uk_customer_email"),)

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    company_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    customer_type = db.Column(
        db.Enum("Individual", "Business", "Government", "NGO", name="customer_type_enum"),
        nullable=False,
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)

    sites = db.relationship("Site", back_populates="customer", lazy="dynamic")
    invoices = db.relationship("Invoice", back_populates="customer", lazy="dynamic")

    @property
    def full_name(self):
        if self.company_name:
            return self.company_name
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Customer {self.email}>"
