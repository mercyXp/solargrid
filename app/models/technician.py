from datetime import date

from app.extensions import db


class Technician(db.Model):
    __tablename__ = "technician"
    __table_args__ = (db.UniqueConstraint("email", name="uk_technician_email"),)

    technician_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    specialisation = db.Column(db.String(100), nullable=True)
    hire_date = db.Column(db.Date, nullable=False, default=date.today)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    installation_assignments = db.relationship("InstallationAssignment", back_populates="technician", lazy="dynamic")
    service_assignments = db.relationship("ServiceAssignment", back_populates="technician", lazy="dynamic")
    maintenance_records = db.relationship("MaintenanceRecord", back_populates="technician", lazy="dynamic")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Technician {self.full_name}>"
