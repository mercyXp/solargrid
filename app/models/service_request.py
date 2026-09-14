from datetime import datetime

from app.extensions import db


class ServiceRequest(db.Model):
    __tablename__ = "service_request"

    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    site_id = db.Column(
        db.Integer,
        db.ForeignKey("site.site_id", name="fk_service_request_site_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    equipment_id = db.Column(
        db.Integer,
        db.ForeignKey("equipment.equipment_id", name="fk_service_request_equipment_id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    reported_by = db.Column(
        db.Integer,
        db.ForeignKey("staff.staff_id", name="fk_service_request_reported_by", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    date_raised = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(
        db.Enum("Low", "Medium", "High", "Critical", name="service_priority_enum"),
        nullable=False,
        default="Medium",
    )
    status = db.Column(
        db.Enum("Open", "In Progress", "Resolved", "Closed", name="service_status_enum"),
        nullable=False,
        default="Open",
    )
    date_resolved = db.Column(db.DateTime, nullable=True)

    site = db.relationship("Site", back_populates="service_requests")
    equipment = db.relationship("Equipment", back_populates="service_requests")
    reporter = db.relationship("Staff", back_populates="service_requests_reported")
    assignments = db.relationship("ServiceAssignment", back_populates="service_request", lazy="dynamic", cascade="all, delete-orphan")
    maintenance_records = db.relationship("MaintenanceRecord", back_populates="service_request", lazy="dynamic")
    invoices = db.relationship("Invoice", back_populates="service_request", lazy="dynamic")

    def __repr__(self):
        return f"<ServiceRequest {self.request_id}>"


class ServiceAssignment(db.Model):
    __tablename__ = "service_assignment"
    __table_args__ = (db.UniqueConstraint("request_id", "technician_id", name="uk_service_assignment"),)

    service_assign_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(
        db.Integer,
        db.ForeignKey("service_request.request_id", name="fk_service_assignment_request_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    technician_id = db.Column(
        db.Integer,
        db.ForeignKey("technician.technician_id", name="fk_service_assignment_technician_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    assigned_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    service_request = db.relationship("ServiceRequest", back_populates="assignments")
    technician = db.relationship("Technician", back_populates="service_assignments")
