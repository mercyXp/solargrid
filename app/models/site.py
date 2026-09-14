from datetime import datetime

from app.extensions import db


class Site(db.Model):
    __tablename__ = "site"

    site_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customer.customer_id", name="fk_site_customer_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    site_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    province = db.Column(db.String(50), nullable=False)
    postal_code = db.Column(db.String(10), nullable=True)
    latitude = db.Column(db.Numeric(10, 7), nullable=True)
    longitude = db.Column(db.Numeric(10, 7), nullable=True)
    site_type = db.Column(
        db.Enum("Household", "School", "Farm", "Business", "Government", name="site_type_enum"),
        nullable=False,
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    customer = db.relationship("Customer", back_populates="sites")
    installations = db.relationship("Installation", back_populates="site", lazy="dynamic")
    service_requests = db.relationship("ServiceRequest", back_populates="site", lazy="dynamic")
    equipment_items = db.relationship("Equipment", back_populates="site", lazy="dynamic")

    def __repr__(self):
        return f"<Site {self.site_name}>"
