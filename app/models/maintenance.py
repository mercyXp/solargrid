from app.extensions import db


class MaintenanceRecord(db.Model):
    __tablename__ = "maintenance_record"
    __table_args__ = (db.CheckConstraint("hours_worked > 0", name="chk_maintenance_hours_worked"),)

    maintenance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(
        db.Integer,
        db.ForeignKey("service_request.request_id", name="fk_maintenance_request_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    technician_id = db.Column(
        db.Integer,
        db.ForeignKey("technician.technician_id", name="fk_maintenance_technician_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    maintenance_date = db.Column(db.DateTime, nullable=False)
    work_description = db.Column(db.Text, nullable=False)
    hours_worked = db.Column(db.Numeric(5, 2), nullable=False)
    parts_used = db.Column(db.Text, nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)

    service_request = db.relationship("ServiceRequest", back_populates="maintenance_records")
    technician = db.relationship("Technician", back_populates="maintenance_records")
