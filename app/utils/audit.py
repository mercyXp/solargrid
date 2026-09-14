from flask import request, session

from app.extensions import db
from app.models.audit import AuditLog


def log_audit(action: str, entity_type: str, entity_id=None, details=None):
    entry = AuditLog(
        staff_id=session.get("staff_id"),
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=request.remote_addr if request else None,
    )
    db.session.add(entry)
    db.session.commit()
