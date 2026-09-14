from datetime import datetime

from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_log"

    audit_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    staff_id = db.Column(
        db.Integer,
        db.ForeignKey("staff.staff_id", name="fk_audit_staff_id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    action = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    staff = db.relationship("Staff")
